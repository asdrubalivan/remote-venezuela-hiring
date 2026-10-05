---
version: 1
slug: "templates-index-html"
primary_target: "templates/index.html"
related_targets: []
---

# Portada (directorio de empresas)

## Scope and mode

Portada `templates/index.html`: nav, encabezado (título, lede, resumen, aviso legal), búsqueda y filtros, pestañas por Status, tabla ordenable, enlaces de contribución, pie. Mode: **Operate** (el visitante busca una empresa y lee su Status y fecha).

Redesign en curso: 5 prototipos descartables en `prototypes/rediseno-portada/` (rama `proto/rediseno-portada`), comparados por votación pública en X (respuestas con el número 1–5). Los textos actuales se conservan al pie de la letra (chequeo automático en `build.py`). Code-led (sin generación de imágenes). Seed key c2f5e2b0 (scope direction, mode operate); asignada: candidata 7 (Clasificados); pick: candidata 1 (Piso de Maiquetía).

Audiencia: devs con residencia en Venezuela, muchas veces en el teléfono, llegando desde X/LinkedIn/Telegram. Tarea: encontrar una empresa y saber en segundos si acepta Venezuela y qué tan reciente es el dato.

Lista ordenada de candidatas: 1 Piso de Maiquetía (franjas cromáticas) · 2 Tablero de salidas de Maiquetía · 3 Guía amarilla CANTV · 4 Sellos y planillas (apostilla, notaría) · 5 Metro de Caracas · 6 Rótulos populares pintados a mano · 7 Clasificados de empleo del periódico.

Veredictos de retadores: variable-font-specimen declinado (aporta: jerarquía solo por escala → v1) · jet-age-ticket-wallet competitivo (se construye como v3) · orienteering-map declinado (aporta: color reservado para un solo estado → v1) · crouwel-grid-specimen declinado (aporta: retícula visible y unidad compartida → v2) · botanical-folio declinado · japanese-high-density-web competitivo, no construido (aporta: coraje de densidad → v4).

## Direction contract

### v1 Clasificados (asignada)
THESIS: La portada como la página dominical de Empleos de los clasificados: buscar trabajo con el periódico abierto y un bolígrafo. Rechaza la tabla SaaS de tarjetas redondeadas con acento azul.
OWN-WORLD: Papel periódico gris (nunca crema), tinta negra, cabezales invertidos (texto blanco sobre banda negra) en grotesca condensada pesada, cuerpo en serif de texto pequeña con cifras tabulares, filetes dobles. Rojo de bolígrafo reservado solo para el marcador. Jerarquía por escala, sin cajas ni sombras.
STORY: Reconoce los clasificados, recorre los avisos, ve encerrado en rojo lo que sí acepta y tachado lo que no.
FIRST VIEWPORT: Banda negra con marca y navegación; título en mayúsculas condensadas a todo lo ancho; tira de fecha entre filetes dobles con el resumen; aviso legal enmarcado como aviso; barra de búsqueda y filtros; pestañas como cabezales invertidos; la tabla empieza dentro del primer viewport.
FORM: Clasificados de empleo, posición 7 de 7, seed c2f5e2b0. Firma: círculo de bolígrafo dibujado a mano (SVG, trazo animado una vez) alrededor del Status al filtrar Acepta o al pasar el cursor; tachado a mano al filtrar No acepta.

### v2 Piso de Maiquetía (pick)
THESIS: El piso cromático del aeropuerto de Maiquetía, donde muchos venezolanos se fotografiaron los pies antes de irse; trabajar en remoto es irse sin irse. Rechaza el directorio gris con un acento.
OWN-WORLD: Blanco puro y franjas paralelas finas de cian, magenta, amarillo y negro; los colores de Status salen de las franjas. Grotesca nítida de carácter geométrico. Retícula visible: franjas y tabla comparten la misma unidad.
STORY: Reconoce el piso, entiende de un vistazo el Status por el color de su franja, filtra y el piso responde.
FIRST VIEWPORT: Banda de franjas a todo lo ancho bajo la navegación; título grande sobre blanco; resumen y aviso; búsqueda; pestañas como franjas de color; tabla dentro del primer viewport, cada fila con su trozo de piso como indicador de Status.
FORM: Piso cromático, posición 1 de 7, seed c2f5e2b0. Firma: inducción cromática, la banda de franjas cambia de color al cambiar de pestaña.

### v3 Boleto (retador competitivo)
THESIS: El talonario del pasaje aéreo: cada empresa es un cupón y su Status se estampa como un sello. Rechaza las filas planas indistintas.
OWN-WORLD: Cartulina blanca de cupón, azul de aerolínea y rojo, cifras en morado carbón para fechas e IDs, cajas de campo con filetes finos y etiquetas pequeñas en versalitas (las etiquetas son los encabezados de columna existentes), troquel perforado entre cuerpo y talón. Sello rojo para "no acepta", sello azul para "acepta".
STORY: Lee cada empresa como un cupón, encuentra el sello, sabe si puede seguir.
FIRST VIEWPORT: Encabezado como cabecera de boleto en azul; título y resumen; aviso; búsqueda y filtros; pestañas como lengüetas de cupón; primeros cupones visibles.
FORM: jet-age-ticket-wallet (catálogo), seed c2f5e2b0. Firma: los sellos se estampan (una vez, escalonados) al cambiar de filtro.

### v4 Metro
THESIS: La señalética del Metro de Caracas que la ciudad leía todos los días; la lista es una línea y cada empresa una estación. Rechaza la tabla sin dirección.
OWN-WORLD: Bandas negras con tipografía suiza blanca, naranja de sistema, colores de línea para Status (verde, rojo, gris), pictogramas de trazo uniforme. Densidad alta sostenida por bandas.
STORY: Se orienta como en una estación, recorre la línea, ve el color de cada parada.
FIRST VIEWPORT: Banda negra de señal con marca y navegación; filete naranja; título como letrero; resumen y aviso; búsqueda; pestañas como viñetas de línea con contador; tabla con la línea vertical y los puntos de estación.
FORM: Metro de Caracas, posición 5 de 7, seed c2f5e2b0. Firma: diagrama de línea vertical con puntos de estación por fila (punto hueco si está desactualizada).

### v5 Guía amarilla
THESIS: La guía telefónica de CANTV, el directorio de todas las casas; esto es una guía. Rechaza el directorio genérico de tarjetas.
OWN-WORLD: Página amarilla saturada de borde a borde, tinta negra, nombres en negrita, fuente de guía condensada y económica, puntos guía entre nombre y Status, encabezados de letra grandes, palabras guía arriba.
STORY: Abre la guía, salta a la letra, sigue los puntos hasta el Status.
FIRST VIEWPORT: Página amarilla; banda negra de marca y navegación; título; resumen y aviso; búsqueda; pestañas; índice A–Z en el borde; primeros listados con su letra.
FORM: Guía telefónica, posición 3 de 7, seed c2f5e2b0. Firma: índice A–Z en el borde que salta a cada letra, más puntos guía Nombre ........ Status.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Unresolved

- Qué dirección gana: la decide la votación en X. DESIGN.md se escribe con la ganadora.
- Ficha de empresa y estadísticas quedan fuera de esta ronda.
