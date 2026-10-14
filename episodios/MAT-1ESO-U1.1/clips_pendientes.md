# Clips pendientes · MAT-1ESO-U1.1

Lo que el guion pide y no está en `nexo/catalogo.json`. Todo está pensado para reutilizarse en otros vídeos.

## Props
- [ ] **movil** (e01, e02, e08, e12, e13): teléfono móvil genérico, agarre `mano`, con la pantalla como superficie donde el editor incrusta 2D, como en la `pizarra`. Sin marcas ni interfaces de plataformas reales; un marco neutro en marino y crema, con el triángulo de Nexo en la parte trasera si se ve. Parámetros: `pantalla_encendida` y orientación (vertical u horizontal). Es muy reutilizable: datos, porcentajes, gráficas, temporizadores, código o mensajes.
- [ ] **bloque base 10: barra y placa** (e04): ampliar `bloque` con el parámetro `forma` = `unidad` (1×1×1, ya existe) · `barra` (10×1×1) · `placa` (10×10×1) · `cubo_mil` (10×10×10), con color por parámetro (`col`: mates.a/b/c/d). Sirve también para valor posicional, decimales, áreas y volúmenes.
- [ ] **ticket** (e17): tique de caja, agarre `mano`, con zona de texto incrustable. Se reutiliza en MAT-1ESO-U1.2 (cafetería).
- [ ] **recta numérica en el suelo** (e09, e10, e15): tira con marcas en el suelo sobre la que Nexo camina; las etiquetas las pone la 2D. Si basta con `caminar` y la capa 2D, se marca como hecho.

## Acciones
- [ ] **colocar** (e04): Nexo se inclina y deja un prop de mano sobre el suelo o la mesa en una posición dada (`prop`, `destino` [x,y,z], `veces` para colocar en fila). Sirve para contar, repartir y apilar.
- [ ] **sostener / mostrar con el móvil**: comprobar el agarre y que la pantalla mire a cámara cuando exista el prop `movil`.

## Retirado (cuarta vuelta)
- Escenario **grada** y prop **periódico**: ya no se usan. El ejemplo del festival y del titular se ha cambiado por las visualizaciones de un vídeo ficticio.
