"""Monta el vídeo de un episodio a partir de escenas.json y lo renderizado.

Uso:
    python pipeline/componer.py episodios/<ID>                 # render/final.mp4
    python pipeline/componer.py episodios/<ID> --escena e05    # solo una escena → render/escenas/e05.mp4
    python pipeline/componer.py episodios/<ID> --borrador      # 720p rápido, sin normalizar audio

Por escena (de abajo arriba): fondo (tokens) → 2D (render/2d/eNN.mp4) → Nexo (render/nexo/eNN/####.png con alfa,
o eNN.mov) → audio (audio/eNN.wav). Duración: audio/tiempos.json o, si no hay audio, duracion_s de escenas.json.
Las capas más cortas que la escena congelan su último fotograma. Fundido de 0,2 s entre escenas.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from omnia.marca import VIDEO, color  # noqa: E402

FUNDIDO = 0.2
ZONAS = {  # escala y posición de la capa de Nexo cuando no ocupa el plano entero
    "completa": (1.0, "0", "0"), "izquierda": (1.0, "0", "0"), "derecha": (1.0, "0", "0"), "centro": (1.0, "0", "0"),
    "esquina": (0.38, "W-w-40", "H-h-20"), "abajo": (0.5, "(W-w)/2", "H-h"),
}


def ff(*args):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *map(str, args)], check=True)


def duracion_audio(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def escena(ep, e, dur, w, h, fps, borrador):
    entradas, filtros = [], []
    fondo = next((c.get("color", "fondo.base") for c in e["capas"] if c["tipo"] == "fondo"), "fondo.base")
    entradas += ["-f", "lavfi", "-i", f"color=c={color(fondo).replace('#', '0x')}:s={w}x{h}:r={fps}:d={dur}"]
    base, n = "[0:v]", 1
    eid = e["id"]
    v2d = ep / "render" / "2d" / f"{eid}.mp4"
    if any(c["tipo"] == "2d" for c in e["capas"]) and v2d.exists():
        entradas += ["-i", v2d]
        filtros.append(f"[{n}:v]scale={w}:{h},fps={fps},tpad=stop_mode=clone:stop_duration={dur}[v{n}]")
        filtros.append(f"{base}[v{n}]overlay=0:0:shortest=0[b{n}]")
        base, n = f"[b{n}]", n + 1
    for c in e["capas"]:
        if c["tipo"] != "nexo":
            continue
        carpeta, mov = ep / "render" / "nexo" / eid, ep / "render" / "nexo" / f"{eid}.mov"
        pngs = sorted(carpeta.glob("[0-9][0-9][0-9][0-9].png")) if carpeta.exists() else []
        if pngs:
            meta = json.loads((carpeta / "plano_meta.json").read_text()) if (carpeta / "plano_meta.json").exists() else {}
            entradas += ["-framerate", str(meta.get("fps", VIDEO.get("fps_nexo", 12))), "-i", carpeta / "%04d.png"]
        elif mov.exists():
            entradas += ["-i", mov]
        else:
            print(f"  AVISO {eid}: falta el render de Nexo")
            continue
        esc, x, y = ZONAS[c.get("zona", "completa")]
        retraso = c.get("entra_s", 0)
        filtros.append(f"[{n}:v]format=rgba,scale={int(w * esc)}:-1,fps={fps},"
                       f"tpad=stop_mode=clone:stop_duration={dur},setpts=PTS+{retraso}/TB[v{n}]")
        filtros.append(f"{base}[v{n}]overlay={x}:{y}:shortest=0:eof_action=repeat[b{n}]")
        base, n = f"[b{n}]", n + 1
    filtros.append(f"{base}trim=duration={dur},fade=in:st=0:d={FUNDIDO},fade=out:st={max(0, dur - FUNDIDO)}:d={FUNDIDO},"
                   f"format=yuv420p[vout]")
    wav = ep / "audio" / f"{eid}.wav"
    if wav.exists():
        entradas += ["-i", wav]
        audio = ["-map", f"{n}:a", "-af", f"apad,atrim=0:{dur}"]
    else:
        entradas += ["-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo:d={dur}"]
        audio = ["-map", f"{n}:a"]
    salida = ep / "render" / "escenas" / f"{eid}.mp4"
    salida.parent.mkdir(parents=True, exist_ok=True)
    ff(*entradas, "-filter_complex", ";".join(filtros), "-map", "[vout]", *audio, "-t", dur,
       "-c:v", "libx264", "-preset", "ultrafast" if borrador else "medium", "-crf", "23" if borrador else "18",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", salida)
    return salida


def main(a):
    ep = Path(a[0])
    borrador = "--borrador" in a
    solo = a[a.index("--escena") + 1] if "--escena" in a else None
    plan = json.loads((ep / "escenas.json").read_text(encoding="utf-8"))
    tiempos = json.loads((ep / "audio" / "tiempos.json").read_text()) if (ep / "audio" / "tiempos.json").exists() else {}
    w, h = (1280, 720) if borrador else VIDEO["resolucion"]
    fps = VIDEO["fps"]
    piezas = []
    for e in plan["escenas"]:
        if solo and e["id"] != solo:
            continue
        dur = tiempos.get(e["id"]) or e["duracion_s"]
        print(f"  {e['id']} {e['seccion']:12s} {dur:5.1f} s")
        piezas.append(escena(ep, e, dur, w, h, fps, borrador))
    if solo:
        print("Escena en", piezas[0])
        return
    lista = ep / "render" / "escenas" / "lista.txt"
    lista.write_text("".join(f"file '{p.resolve()}'\n" for p in piezas))
    final = ep / "render" / "final.mp4"
    if borrador or not tiempos:
        ff("-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", final)
    else:
        ff("-f", "concat", "-safe", "0", "-i", lista, "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
           "-c:a", "aac", "-b:a", "192k", final)
    print("Vídeo en", final, f"({duracion_audio(final):.1f} s)")


if __name__ == "__main__":
    if not shutil.which("ffmpeg"):
        raise SystemExit("Falta ffmpeg")
    main(sys.argv[1:])
