# Clips pendientes · MAT-1ESO-U1.1

Lo que el guion pide y no está en `nexo/catalogo.json`. Pensado para reutilizarse (varios vídeos de números, estadística y proporcionalidad lo van a necesitar).

## Escenarios
- [ ] **grada** (e01, e12): tramo de grada de recinto (3-4 filas de asientos escalonados, barandilla) por el que Nexo pueda `caminar` en horizontal. Estilo de la marca, fondo `fondo.base`, sin público modelado (se sugiere con siluetas planas o vacío). Recinto ficticio: sin logotipos ni nombres reales. Parámetros útiles: `filas`, `largo`. Alternativa barata si no compensa: fondo 2D de grada y Nexo sobre suelo plano.

## Props
- [ ] **periodico** (e01, e02, e10): periódico doblado, agarre `mano`, con superficie de portada donde el editor incrusta el titular en 2D («Casi 100 000 espectadores», espacio fino de miles). Parámetro: `texto` o zona de incrustación como la `pizarra`. Reutilizable para cualquier noticia/dato.
- [ ] **bloque base 10: barra y placa** (e04): ampliar `bloque` con parámetro `forma` = `unidad` (1×1×1, ya existe) · `barra` (10×1×1) · `placa` (10×10×1) · `cubo_mil` (10×10×10), con color por parámetro (`col`: mates.a/b/c/d). Útil para valor posicional, decimales, áreas y volúmenes.
- [ ] **ticket** (e18): tique de caja, agarre `mano`, con zona de texto incrustable. Se reutiliza en MAT-1ESO-U1.2 (cafetería).
- [ ] **recta numérica en el suelo** (e09, e14): tira en el suelo con marcas sobre la que Nexo camina; las etiquetas las pone la 2D. Si ya se resuelve con `caminar` + capa 2D, marcar como hecho.

## Acciones
- [ ] **colocar** (e04): Nexo se agacha un poco y deja un prop de mano sobre el suelo o la mesa en una posición dada (`prop`, `destino` [x,y,z], `veces` para colocar en fila). Muy reutilizable (contar, repartir, apilar).
- [ ] **sostener periódico / mostrar ticket**: probablemente basta con `sostener`/`mostrar` cuando existan los props; comprobar agarre y que la portada mire a cámara.
