# Episodio de ejemplo (prueba de extremo a extremo)
Mini episodio de 2 escenas para comprobar que todo el pipeline funciona: escenas.json → plano de Nexo + escena 2D → montaje.
```
python pipeline/validar.py episodios/_ejemplo
python pipeline/verificar.py episodios/_ejemplo/claims.json
python pipeline/render_nexo.py episodios/_ejemplo/planos/e01.json --salida episodios/_ejemplo/render/nexo/e01 --prueba
PYTHONPATH=. manim -qm episodios/_ejemplo/escenas/e01.py E01 --media_dir episodios/_ejemplo/render/2d/manim
PYTHONPATH=. manim -qm episodios/_ejemplo/escenas/e02.py E02 --media_dir episodios/_ejemplo/render/2d/manim
(copia los mp4 a render/2d/e01.mp4 y e02.mp4)
python pipeline/componer.py episodios/_ejemplo --borrador
```
