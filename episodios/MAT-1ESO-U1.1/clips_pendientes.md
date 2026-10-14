# Clips pendientes · MAT-1ESO-U1.1

Lo que el guion pide y no está en `nexo/catalogo.json`. Todo está pensado para reutilizarse en otros vídeos.

## Props
- [x] **movil** (e01, e02, e08, e12, e13): teléfono móvil genérico, agarre `mano`, con la pantalla como superficie donde el editor incrusta 2D, como en la `pizarra`. Sin marcas ni interfaces de plataformas reales; un marco neutro en marino y crema, con el triángulo de Nexo en la parte trasera si se ve. Parámetros: `pantalla_encendida` y orientación (vertical u horizontal). Es muy reutilizable: datos, porcentajes, gráficas, temporizadores, código o mensajes.
- [x] **bloque base 10: barra y placa** (e04): ampliar `bloque` con el parámetro `forma` = `unidad` (1×1×1, ya existe) · `barra` (10×1×1) · `placa` (10×10×1) · `cubo_mil` (10×10×10), con color por parámetro (`col`: mates.a/b/c/d). Sirve también para valor posicional, decimales, áreas y volúmenes.
- [x] **ticket** (e17): tique de caja, agarre `mano`, con zona de texto incrustable. Se reutiliza en MAT-1ESO-U1.2 (cafetería).
- [x] **recta numérica en el suelo** (e09, e10, e15): tira con marcas en el suelo sobre la que Nexo camina; las etiquetas las pone la 2D. Si basta con `caminar` y la capa 2D, se marca como hecho.

## Acciones
- [x] **colocar** (e04): Nexo se inclina y deja un prop de mano sobre el suelo o la mesa en una posición dada (`prop`, `destino` [x,y,z], `veces` para colocar en fila). Sirve para contar, repartir y apilar.
- [x] **sostener / mostrar con el móvil**: comprobar el agarre y que la pantalla mire a cámara cuando exista el prop `movil`.

## Resuelto (constructor-props)
- `movil(pantalla_encendida=True, orientacion="vertical"|"horizontal", nivel)`: 7×15×0,8 cm, cuerpo marino con canto crema, emblema de Nexo (color de nivel) detrás. Pantalla = objeto `MovilPantalla` (emisivo oscuro); `ob["pantalla"] = [ancho, alto, z_centro, x_centro]`, `ob["pantalla_objeto"]`. Con `sostener`/`mostrar` la pantalla mira a cámara y asoma sobre los dedos. Es de tamaño real: en plano `completo` se ve pequeño; para leer la 2D usa `camara: "medio"` o `"escala": 1.5`.
- `bloque(forma="unidad"|"barra"|"placa"|"cubo_mil", lado=0.02, col="mates.a", de_pie=False)`: cada cubito biselado con ranura. `de_pie` pone la barra vertical o la placa de cara a cámara (se coge por el borde inferior). Las llamadas antiguas siguen valiendo; el cubo unidad pasa de 10 cm a 2 cm por defecto (`lado=0.1` recupera el anterior).
- `ticket(ancho=0.08, alto=0.18)`: papel con bordes dentados; zona incrustable `TicketTexto`, `ob["pantalla"]`.
- `colocar(prop, destino=[x,y,z], veces, paso="auto", fila="derecha", mano="auto")`: se agacha y deja el prop; con `veces` > 1 coloca p1..pN en fila (cada uno aparece en la mano al cogerlo; con mano auto cambia de mano según el lado). Nexo no puede llegar al suelo con la mano: lo suelta a 4-6 cm y cae (caída libre) hasta quedar quieto; `plano_meta.json` → `colocar` con destino y caída. Alcance cómodo: ±0,2 m en X a 0,12-0,2 m delante de sus pies. Para e04: `{"prop": "b1", "destino": [-0.14, -0.17, 0], "veces": 10}` con 10 bloques `b1..b10`.
- Recta en el suelo: **basta `caminar` + capa 2D** (la 2D dibuja recta, marcas y etiquetas; `caminar` da distancia y dirección exactas). No se crea prop.

## Retirado (cuarta vuelta)
- Escenario **grada** y prop **periódico**: ya no se usan. El ejemplo del festival y del titular se ha cambiado por las visualizaciones de un vídeo ficticio.
