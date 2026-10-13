---
version: 1
slug: "templates-index-html"
primary_target: "templates/index.html"
related_targets: ["templates/base.html","templates/_nav.html","templates/company.html","templates/stats.html","static/main.css"]
---

# Portada (directorio de empresas)

## Scope and mode

Portada `templates/index.html`: nav, encabezado (título, lede, resumen, aviso legal), búsqueda y filtros, chips de filtros activos, pestañas por Status, tabla ordenable, enlaces de contribución, pie. Mode: **Operate** (el visitante busca una empresa y lee su Status y fecha).

Decisión tomada: gana la variante 3, **Boleto**, y pasa a producción en todo el sitio. La cabecera, el pie, la ficha de empresa (`templates/company.html`) y Estadísticas (`templates/stats.html`) heredan el mismo mundo. Los textos actuales se conservan al pie de la letra. Code-led (sin generación de imágenes ni comp). Seed key c2f5e2b0 (scope direction, mode operate).

Ajuste pedido por el usuario sobre el prototipo: "demasiado azul" y "falta un color para resaltar". Respuesta: el azul queda en la cabecera, la tapa y la bandeja de cupones; el resto de la página es cartulina gris azulada clara; el amarillo de la bandera entra como color de resalte.

Audiencia: devs con residencia en Venezuela, muchas veces en el teléfono, llegando desde X/LinkedIn/Telegram. Tarea: encontrar una empresa y saber en segundos si acepta Venezuela y qué tan reciente es el dato.

## Direction contract

THESIS: El talonario del pasaje aéreo de la era jet: cada Empresa es un cupón (cuerpo | troquel | talón) y su Status se estampa como un sello en el talón. Rechaza las filas planas indistintas de la tabla SaaS.

OWN-WORLD: Cartulina blanca de cupón sobre una bandeja azul de aerolínea; cabecera azul marino con filete de librea rojo; tapa azul con el título en grotesca condensada en mayúsculas; el resto de la página en cartulina gris azulada clara. Talón en copia al carbón de color según Status: amarillo bandera para "acepta", rosado para "no acepta", lila para "desconocido". Sello azul para acepta, rojo para no acepta, morado con borde punteado para desconocido. Cifras en morado carbón (fechas, IDs, contadores) en máquina de escribir. Troquel perforado con muescas entre cuerpo y talón. Amarillo de la bandera como resalte: papeleta de resumen, foco, contadores activos.

STORY: Reconoce un talonario de pasajes, recorre los cupones, encuentra el sello en el talón y sabe si puede seguir.

FIRST VIEWPORT: Cabecera marino con bandera, marca y navegación; tapa azul a todo lo ancho con el título grande en mayúsculas condensadas, la entrada, la papeleta amarilla de resumen (empresas, probablemente aceptan, actualizado) y el aviso legal como letra pequeña. Debajo, sobre cartulina clara: búsqueda y filtros, pestañas como lengüetas que salen de la bandeja azul y los primeros cupones visibles.

FORM: jet-age-ticket-wallet (catálogo), retador competitivo de la ronda, seed c2f5e2b0. Firma: los sellos de los primeros cupones visibles se estampan una vez, escalonados, al cambiar de pestaña, filtro o búsqueda (nunca con prefers-reduced-motion; el sello es visible por defecto).

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Unresolved

- Ninguna sobre la dirección. Los prototipos descartables quedan en la rama `proto/rediseno-portada`.
