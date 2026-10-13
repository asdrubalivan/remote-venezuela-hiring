---
name: Remote Venezuela Hiring
description: Directorio comunitario de empresas que contratan, o rechazan, candidatos con residencia en Venezuela, impreso como un talonario de pasajes de la era jet.
colors:
  navy: "#0D1B3D"
  wallet: "#1E4886"
  tray: "#163A6F"
  red: "#D7262D"
  red-hover: "#B81D24"
  yellow: "#FFCC00"
  on-yellow: "#0D1B3D"
  blue-ink: "#1C47A3"
  red-ink: "#B8141D"
  carbon: "#4B2E83"
  copy-accepts: "#FFF2BF"
  copy-rejects: "#FCE4E6"
  copy-unknown: "#EEE9F8"
  stock: "#FFFFFF"
  stock-hover: "#F5F7FC"
  ground: "#E6EAF1"
  ink: "#0D1B3D"
  ink-2: "#44547F"
  rule: "#CFD5E4"
  perf: "#8C95B2"
  field-line: "#6F7A99"
  tag-bg: "#F3F5FA"
  tab-bg: "#D3DAE7"
  tab-bg-hover: "#C3CCDD"
  on: "#FFFFFF"
  on-2: "#C9D5EE"
  dark-navy: "#070C1C"
  dark-wallet: "#10224D"
  dark-tray: "#13295C"
  dark-ground: "#131417"
  dark-stock: "#1F2127"
  dark-stock-hover: "#262930"
  dark-ink: "#EEF0F4"
  dark-ink-2: "#A9AFBD"
  dark-rule: "#363A44"
  dark-blue-ink: "#9DBBFF"
  dark-red-ink: "#FF8A8A"
  dark-carbon: "#CDBEF7"
  dark-copy-accepts: "#E5CC63"
  dark-copy-rejects: "#E7C3C9"
  dark-copy-unknown: "#CFC6E6"
typography:
  display:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "clamp(2.35rem, 1.05rem + 3.7vw, 4.6rem)"
    fontWeight: 800
    lineHeight: 0.92
    letterSpacing: "0.004em"
  headline:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "clamp(2.2rem, 1.4rem + 2.6vw, 3.6rem)"
    fontWeight: 800
    lineHeight: 0.95
    letterSpacing: "0.005em"
  title:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "25px"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "0.01em"
  title-panel:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "22px"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "0.04em"
  lede:
    fontFamily: "Barlow, system-ui, sans-serif"
    fontSize: "clamp(1.05rem, 0.96rem + 0.3vw, 1.22rem)"
    fontWeight: 400
    lineHeight: 1.5
  body:
    fontFamily: "Barlow, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  value:
    fontFamily: "Barlow, system-ui, sans-serif"
    fontSize: "15.5px"
    fontWeight: 500
    lineHeight: 1.3
  fine-print:
    fontFamily: "Barlow, system-ui, sans-serif"
    fontSize: "13.5px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "11.5px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.13em"
  control:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "15px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.1em"
  stamp:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "15px"
    fontWeight: 700
    lineHeight: 1.08
    letterSpacing: "0.08em"
  numeral:
    fontFamily: "Courier Prime, Courier New, monospace"
    fontSize: "18px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.01em"
    fontFeature: "tnum"
  numeral-lg:
    fontFamily: "Courier Prime, Courier New, monospace"
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "-0.02em"
    fontFeature: "tnum"
rounded:
  hairline: "2px"
  tag: "3px"
  control: "4px"
  coupon: "6px"
  tray: "8px"
  tab: "8px 8px 0 0"
  luggage-tag: "3px 18px 18px 3px"
spacing:
  gutter: "clamp(16px, 3vw, 40px)"
  max: "1400px"
  notch: "9px"
  coupon-gap: "10px"
  coupon-gap-compact: "6px"
  control-gap: "12px"
  section: "32px"
  footer: "56px"
  touch: "44px"
  control-height: "48px"
components:
  button-red:
    backgroundColor: "{colors.red}"
    textColor: "{colors.on}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0 20px"
    height: "48px"
  button-red-hover:
    backgroundColor: "{colors.red-hover}"
  button-line:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0 20px"
    height: "48px"
  button-line-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.ground}"
  button-quiet:
    backgroundColor: "{colors.tab-bg}"
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0 20px"
    height: "48px"
  button-quiet-hover:
    backgroundColor: "{colors.tab-bg-hover}"
  input-search:
    backgroundColor: "{colors.stock}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0 16px 0 44px"
    height: "48px"
  select-filter:
    backgroundColor: "{colors.stock}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0 40px 0 14px"
    height: "48px"
  status-tab:
    backgroundColor: "{colors.tab-bg}"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.tab}"
    padding: "0 18px 0 20px"
    height: "50px"
  status-tab-active:
    backgroundColor: "{colors.tray}"
    textColor: "{colors.on}"
  status-tab-count-active:
    backgroundColor: "{colors.yellow}"
    textColor: "{colors.on-yellow}"
  filter-chip:
    backgroundColor: "{colors.stock}"
    textColor: "{colors.ink}"
    rounded: "{rounded.luggage-tag}"
    padding: "0 8px 0 14px"
    height: "36px"
  tag-badge:
    backgroundColor: "{colors.tag-bg}"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.tag}"
    padding: "3px 7px"
  tray:
    backgroundColor: "{colors.tray}"
    rounded: "{rounded.tray}"
    padding: "4px 16px 16px"
  coupon-body:
    backgroundColor: "{colors.stock}"
    textColor: "{colors.ink}"
    rounded: "{rounded.coupon}"
    height: "86px"
  coupon-stub-accepts:
    backgroundColor: "{colors.copy-accepts}"
    textColor: "{colors.carbon}"
    width: "412px"
  coupon-stub-rejects:
    backgroundColor: "{colors.copy-rejects}"
    textColor: "{colors.carbon}"
    width: "412px"
  coupon-stub-unknown:
    backgroundColor: "{colors.copy-unknown}"
    textColor: "{colors.carbon}"
    width: "412px"
  stamp-accepts:
    textColor: "{colors.blue-ink}"
    typography: "{typography.stamp}"
    rounded: "{rounded.control}"
    padding: "6px 11px 5px"
  stamp-rejects:
    textColor: "{colors.red-ink}"
    typography: "{typography.stamp}"
    rounded: "{rounded.control}"
    padding: "7px 12px 6px"
  stamp-unknown:
    textColor: "{colors.carbon}"
    typography: "{typography.stamp}"
    rounded: "{rounded.control}"
    padding: "6px 11px 5px"
  slip:
    backgroundColor: "{colors.yellow}"
    textColor: "{colors.carbon}"
    typography: "{typography.numeral-lg}"
    rounded: "{rounded.coupon}"
    padding: "0 10px"
  navbar:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.on}"
    height: "64px"
  cover:
    backgroundColor: "{colors.wallet}"
    textColor: "{colors.on}"
    typography: "{typography.display}"
---

# Design System: Remote Venezuela Hiring

## Overview

**Creative North Star: "El Talonario de la Era Jet"**

Cada Empresa es un cupón de pasaje aéreo: cuerpo de cartulina blanca, troquel perforado con muescas, talón en copia al carbón. El Status se estampa como un sello en el talón, y quien llega desde el teléfono reconoce el objeto, recorre los cupones, encuentra el sello y sabe si puede seguir. El sistema rechaza las filas planas e indistintas de la tabla SaaS: la información es la misma, pero cada registro es una pieza de papel con un sello que se lee de un vistazo.

El mundo tiene dos materiales y una regla de color. El azul de aerolínea vive solo en la cabecera marino (con su filete de librea rojo), la tapa y la bandeja donde se apilan los cupones; el resto de la página es cartulina gris azulada clara con una trama de puntos. El amarillo de la bandera es el único resalte: la papeleta de resumen, el anillo de foco, los contadores activos. La tipografía se reparte en tres voces: grotesca condensada en mayúsculas para titular, rotular y estampar; grotesca de lectura para valores y prosa; máquina de escribir en morado carbón para toda cifra.

La densidad es de directorio operativo: cupones de 86px en la densidad cómoda, 64px en la compacta, con el talón de ancho fijo para que fecha y sello caigan siempre en la misma columna. El movimiento es uno solo y es la firma: el sello se estampa una vez al cambiar lo que se ve.

**Key Characteristics:**
- Cupón = cuerpo | troquel | talón; el talón es papel de color según Status, en ambos temas.
- Sello con tinta irregular (filtros SVG `#ink` / `#ink-fine`) y rotación leve por cupón.
- Azul solo en cabecera, tapa y bandeja; cartulina clara (o grafito neutro de noche) en todo lo demás.
- Amarillo bandera como único color de resalte.
- Cifras en Courier Prime morado carbón, tabulares.
- Rotulación en Barlow Condensed mayúsculas con tracking amplio.

## Colors

Una paleta de aerolínea de los sesenta: marino y azul de librea, rojo de filete, amarillo de bandera, y tres papeles de copia al carbón que codifican el Status.

### Primary
- **Azul Bandeja** (tray): fondo de la bandeja de cupones, de la lengüeta activa y de los paneles de estadísticas; es lo que asoma por las muescas del troquel.
- **Azul Tapa** (wallet): la tapa del talonario, a todo lo ancho bajo la cabecera, con trama de puntos blancos al 7,5%.
- **Marino Cabina** (navy): cabecera, pie y fondo de `html`; también tinta principal del tema claro.

### Secondary
- **Rojo Librea** (red): filete de la cabecera (banda de 4px, aire, filete de 2px) y del pie, botón primario de contribuir, `accent-color` de casillas, subrayado de hover en enlaces. Hover del botón: red-hover.
- **Amarillo Bandera** (yellow): papeleta de resumen, halo del foco, contador de la lengüeta activa, subrayado de la sección actual en la navegación, enlace de salto. Texto sobre él: on-yellow.

### Tertiary (tintas y copias al carbón)
- **Tinta Azul de Sello** (blue-ink): sello "acepta", barras y segmento "acepta" en estadísticas, hover de dominios.
- **Tinta Roja de Sello** (red-ink): sello "no acepta" y segmento rayado en estadísticas.
- **Morado Carbón** (carbon): cifras (fechas, contadores, IDs, "+N"), sello "desconocido" y sello pequeño DESACTUALIZADA.
- **Copia Amarilla / Rosada / Lila** (copy-accepts / copy-rejects / copy-unknown): papel del talón para acepta, no acepta y desconocido; también el talón del estado vacío (lila).

### Neutral
- **Cartulina** (stock) y **Cartulina al pasar** (stock-hover): cuerpo del cupón, campos, menú de ajustes.
- **Cartulina Gris Azulada** (ground): fondo de página con trama de puntos de 7px.
- **Tinta** (ink) y **Tinta Secundaria** (ink-2): texto principal; rótulos, dominios, letra pequeña.
- **Filete** (rule), **Perforación** (perf), **Línea de Campo** (field-line): separadores internos del cupón, puntos del troquel, bordes de controles.
- **Lengüeta** (tab-bg / tab-bg-hover) y **Etiqueta** (tag-bg): lengüetas inactivas, botón discreto, fondo de etiquetas.
- **Sobre Azul** (on / on-2): texto sobre cabecera, tapa y bandeja.

### Tema oscuro
Los tokens `dark-*` reemplazan a sus pares por `:root[data-theme="dark"]`. El azul se oscurece pero se queda en cabecera, tapa y bandeja; el fondo de página pasa a grafito neutro (dark-ground) y la cartulina a dark-stock. Las copias al carbón siguen siendo papel de color, solo atenuado (dark-copy-*), y dentro del talón se restablecen las tintas del tema claro (blue-ink, red-ink #A3121B, carbon, ink).

### Named Rules
**La Regla del Azul de Cabina.** El azul (navy, wallet, tray) solo cubre cabecera, tapa, bandeja y pie. El suelo de la página es cartulina clara, y de noche grafito neutro; nunca azul.

**La Regla de la Copia al Carbón.** El color del talón es el Status: amarillo acepta, rosado no acepta, lila desconocido. El talón es papel en ambos temas y lleva siempre las tintas del tema claro.

**La Regla del Amarillo de Bandera.** El amarillo es el único resalte y solo marca resumen, foco, contadores activos y la sección actual. No es fondo de sección ni color de texto.

## Typography

**Display Font:** Barlow Condensed 600/700/800 (con Arial Narrow, sans-serif)
**Body Font:** Barlow 400/500/600 (con system-ui, sans-serif)
**Label/Mono Font:** Courier Prime 400/700 (con Courier New, monospace)

Las tres familias están autoalojadas en `static/fonts/` (subconjunto latin, woff2, `font-display: swap`).

**Character:** La condensada en mayúsculas es la rotulación impresa del boleto y la voz del sello; Barlow la acompaña con la misma estructura en ancho normal para leer; Courier Prime es la máquina de escribir del agente que llenó el pasaje.

### Hierarchy
- **Display** (800, clamp 2.35rem a 4.6rem, 0.92, mayúsculas, `text-wrap: balance`): título de la tapa en portada y Estadísticas. En móvil, clamp(2.1rem, 0.9rem + 6.6vw, 2.9rem).
- **Headline** (800, clamp 2.2rem a 3.6rem, 0.95, mayúsculas): nombre de la empresa en su ficha.
- **Title** (700, 25px, 1.05): nombre de la empresa en el cupón (22px en tableta y móvil, 20px en compacta). Title-panel (700, 22px, mayúsculas, 0.04em) para títulos de paneles de estadísticas.
- **Lede** (Barlow 400, clamp 1.05rem a 1.22rem, 1.5, máx. 54ch): entrada de la tapa.
- **Body / Value** (Barlow 400 1rem/1.5; 500 15.5px/1.3): prosa, notas (máx. 72ch) y valores de campo del cupón.
- **Fine print** (Barlow 400, 13.5px, 1.55): aviso legal en la tapa, a modo de condiciones del pasaje.
- **Label** (Barlow Condensed 600, 11.5px, 0.13em, mayúsculas): rótulos de campo, de papeleta y de menú.
- **Control** (Barlow Condensed 600, 15px, 0.1em, mayúsculas): botones, navegación (16px), lengüetas (17px, 0.08em), encabezados ordenables (12.5px, 0.14em).
- **Stamp** (Barlow Condensed 700, 15px, 0.08em, mayúsculas): texto del sello; "no acepta" sube a 800 y 16px; el sello grande de la ficha a 22px.
- **Numeral** (Courier Prime 700, 18px, tabular): fechas del talón; numeral-lg (28px) en la papeleta; 15px en contadores de lengüeta y métricas de barras.

### Named Rules
**La Regla de la Máquina de Escribir.** Toda cifra (fecha, conteo, porcentaje, "+N", generado el) va en Courier Prime con `tabular-nums`, casi siempre en morado carbón. Ninguna cifra en Barlow.

**La Regla de la Rotulación.** Barlow Condensed se usa en mayúsculas con tracking positivo para títulos, rótulos, controles y sellos. La prosa y los valores nunca van en condensada.

## Layout

Contenedor centrado de 1400px con margen lateral clamp(16px, 3vw, 40px). La página apila, en orden: cabecera (64px), tapa a todo lo ancho, barra de búsqueda y filtros (32px arriba, separación de 12px), lengüetas de Status que salen de la bandeja, la bandeja con los cupones (separación de 10px; 6px en compacta), enlaces de contribución y pie (56px arriba).

El cupón es una rejilla de seis columnas: empresa 1.5fr, verificación 1fr, plataforma 0.85fr, etiquetas 1.45fr, y el talón de ancho fijo (fecha 176px + sello 236px). Encabezados ordenables pegajosos sobre la bandeja; sobre 880px los cupones no repiten los rótulos.

Puntos de quiebre:
- **≤1180px:** talón de 158 + 208px; las etiquetas bajan a una segunda fila del cuerpo; los filtros se pliegan tras el botón "Filtros"; la papeleta de Estadísticas pasa a tres columnas.
- **≤880px:** la tapa pasa a una columna; las lengüetas forman una rejilla de cuatro con el contador debajo; la bandeja va a sangre; el cupón se reorganiza en nombre / verificación + plataforma / etiquetas con el talón (124px) como columna derecha, fecha arriba y sello debajo; los encabezados ordenables se vuelven botones con borde en una fila desplazable.
- **≤760px:** la navegación pasa a segunda línea; la ficha baja el talón debajo del cuerpo con troquel horizontal; Estadísticas en una columna.
- **≤400px / ≤360px:** la papeleta pasa a dos filas; el cupón apila verificación y plataforma.

Densidad compacta (preferencia del visitante): cupón sin altura mínima, nombre a 20px, sello reducido, y cada cupón muestra solo su primera etiqueta más un "+N" calculado en el servidor.

En Estadísticas la bandeja tiene dos columnas; el último panel de cada columna se estira hasta el fondo para que nunca quede bandeja vacía.

## Elevation & Depth

La profundidad es papel sobre bandeja, no sombra. Los cupones son planos y se separan de la bandeja azul por contraste y por las muescas recortadas con máscara, que dejan ver el azul por detrás. La bandeja lleva una sombra interior que sugiere el borde del sobre. Solo lo que flota sobre la página (el menú de ajustes) proyecta sombra.

### Shadow Vocabulary
- **Borde del sobre** (`box-shadow: inset 0 14px 18px -14px rgba(2, 8, 24, 0.55)`): parte superior interior de la bandeja.
- **Menú flotante** (`box-shadow: 0 14px 34px rgba(4, 10, 28, 0.38), 0 2px 6px rgba(4, 10, 28, 0.2)`): menú de ajustes de la cabecera.
- **Filete de lengüeta** (`box-shadow: inset 0 3px 0 #D7262D`): borde superior rojo de la lengüeta activa.
- **Doble filete del sello** (`box-shadow: inset 0 0 0 2px <papel del talón>, inset 0 0 0 3px currentColor`): el marco doble de los sellos acepta y no acepta.

### Named Rules
**La Regla del Papel sobre Bandeja.** Los cupones, paneles y tickets no llevan sombra exterior. Se separan por color, por las muescas y por el troquel.

## Shapes

Esquinas de papel cortado, apenas redondeadas: 6px para cupones, tickets y papeleta; 8px para bandejas y lengüetas (solo arriba); 4px para controles y sellos; 3px para etiquetas; 2px para la bandera y las barras. El filtro activo tiene forma de etiqueta de equipaje (3px a la izquierda, 18px a la derecha).

La forma firma del sistema es el troquel: una columna de puntos de 6 x 7px en el color perf entre cuerpo y talón, con dos muescas circulares de 9px (8px en móvil) recortadas arriba y abajo por máscara. La papeleta amarilla lleva muescas laterales y perforaciones entre campos; los paneles de estadísticas separan su título con una fila de perforaciones y muescas que dejan ver la bandeja.

### Named Rules
**La Regla del Troquel.** Toda superficie que represente un cupón separa sus partes con perforación y muescas, nunca con un filete liso.

## Components

### Buttons
Rotulación impresa, firme y sin adornos.
- **Shape:** esquinas de 4px, altura mínima de 48px.
- **Primary (rojo):** fondo red, texto blanco, Barlow Condensed 600 15px en mayúsculas con 0.1em; hover a red-hover. Reservado a contribuir.
- **Line:** transparente con borde de 1px en ink; hover e `aria-expanded` lo invierten (fondo ink, texto ground). Usado para "Filtros", con contador rojo en Courier.
- **Quiet:** fondo tab-bg, hover tab-bg-hover.
- **Focus:** contorno de 2px en navy con halo de 2px amarillo; sobre superficies azules se invierte (contorno amarillo, halo navy).
- **Transiciones:** color y fondo en 0.15s ease-out.

### Chips
- **Filtro activo:** etiqueta de equipaje en cartulina con borde field-line, 36px de alto, Barlow 500 14px, con un botón circular de 22px para quitarla. Hover: borde rojo y el círculo se vuelve rojo con la x blanca.
- **Etiqueta del cupón:** tag-bg con borde rule, 3px, Barlow 500 12.5px. El "+N" lleva borde discontinuo, fondo transparente y Courier Prime 700 en morado carbón.

### Cards / Containers
- **Cupón:** cartulina blanca, 6px, 86px de alto mínimo, cuerpo con filetes verticales internos de 1px en rule, talón de copia al carbón según Status. Hover: el cuerpo pasa a stock-hover. Los cupones "no acepta" llevan una sobreimpresión diagonal roja en el talón (líneas a -55°): nada desaparece, se anula.
- **Bandeja:** azul tray, 8px (sin la esquina superior izquierda, donde nace la lengüeta), relleno de 4px 16px 16px.
- **Ticket de ficha:** cuerpo de cartulina con campos en rejilla de tres separados por filetes, y un talón de 300px con la fecha y el sello grande.
- **Estado vacío:** un cupón en blanco con talón lila y un marco discontinuo vacío girado -4° donde iría el sello.
- **Papeleta de resumen:** amarillo bandera con muescas laterales, campos separados por perforación, rótulos en Barlow Condensed y valores en Courier Prime 28px morado carbón.

### Inputs / Fields
- **Style:** cartulina, borde de 1px en field-line, 4px, 48px de alto, Barlow 500 16px (15px en selects). La búsqueda lleva el icono de lupa a 14px; los selects un chevrón en `--chevron`.
- **Hover:** el borde pasa a ink.
- **Focus:** el anillo global (navy + halo amarillo).
- **Casillas:** 20px con `accent-color` rojo.

### Navigation
- **Cabecera:** marino, 64px, filete de librea rojo (banda de 4px más filete de 2px a 10px). Marca con bandera de 30 x 20px y la palabra en dos líneas: "Remote Venezuela" en 700 19px y "Hiring" en 600 12px con 0.42em.
- **Enlaces:** Barlow Condensed 600 16px en mayúsculas, on-2; hover y actual en blanco; la sección actual lleva una barra amarilla de 3px abajo.
- **Acciones:** botón de ajustes de 44px (icono de engranaje) que abre un menú de cartulina con dos segmentados (tema, densidad), y el enlace GitHub con borde blanco al 50% que se invierte al pasar.
- **Móvil (≤760px):** los enlaces pasan a una segunda línea a todo lo ancho, de 46px.
- **Lengüetas de Status:** 50px, 8px arriba, tab-bg; activa en azul tray con filete rojo superior de 3px y contador amarillo.

### El Sello (componente firma)
El Status se estampa en el talón: marco de 2px en currentColor con doble filete interior, Barlow Condensed 700 en mayúsculas, centrado y con `text-wrap: balance`, girado alrededor de -3° con una variación determinista por cupón (rotación y desplazamiento horizontal calculados en la plantilla). La tinta pasa por un filtro SVG: `#ink-fine` (desplazamiento 0.3) en cupones y sellos pequeños para que la letra se lea; `#ink` (desplazamiento 1.3, más poros) solo en el sello grande de la ficha.
- **Acepta:** blue-ink, marco doble.
- **No acepta:** red-ink, borde de 3px, 800, más tracking.
- **Desconocido:** carbon, borde discontinuo, sin doble filete.
- **Sellos pequeños:** DESACTUALIZADA (carbon, bajo la fecha) y ARCHIVADA (ink-2, junto al nombre), 11.5px, borde de 1.5px, girados 3.5°. Se escriben completos.
- **Gesto:** al cambiar de lengüeta, filtro o búsqueda (tras 220ms de pausa al escribir), los sellos de hasta 8 cupones visibles se estampan una vez: 300ms con `cubic-bezier(0.16, 1, 0.3, 1)`, entrando desde escala 1.25, 7° más girados y con desenfoque, escalonados 40ms; el sello pequeño entra 170ms después. Ordenar no vuelve a estampar. El sello es visible por defecto; con `prefers-reduced-motion` no hay animación ni transiciones.

### Estadísticas
Paneles como tickets dentro de la bandeja: barra de proporción de 30px en segmentos (acepta azul, no acepta rojo rayado, desconocido carbón), leyenda con cifras en Courier, barras horizontales de 10px con relleno blue-ink sobre tag-bg, y chips de empresas desactualizadas con borde field-line que pasa a rojo al pasar.

## Do's and Don'ts

### Do:
- **Do** representar cada Empresa como un cupón: cuerpo de cartulina, troquel con muescas de 9px y talón de ancho fijo en copia al carbón según su Status.
- **Do** mantener el talón como papel de color en el tema oscuro, con las tintas del tema claro dentro.
- **Do** poner toda cifra en Courier Prime 700 tabular en morado carbón.
- **Do** usar el amarillo bandera solo para resumen, foco, contadores activos y la sección actual.
- **Do** usar `#ink-fine` en cualquier sello por debajo del tamaño de la ficha y reservar `#ink` para el sello grande.
- **Do** estampar solo al cambiar lo que se ve, una vez, con un máximo de 8 sellos escalonados 40ms, y dejar el sello visible por defecto.
- **Do** mantener objetivos táctiles de 44px como mínimo y controles de 48px.

### Don't:
- **Don't** volver a filas planas e indistintas de tabla SaaS: el registro es un cupón con sello.
- **Don't** extender el azul al suelo de la página ni teñir de azul el tema oscuro fuera de cabecera, tapa y bandeja.
- **Don't** ocultar las no aceptantes: se anulan con la sobreimpresión roja del talón, no desaparecen.
- **Don't** abreviar el texto de los sellos (DESACTUALIZADA, ARCHIVADA van completos).
- **Don't** animar sellos al ordenar ni con `prefers-reduced-motion`.
- **Don't** dar sombra exterior a cupones, tickets o paneles; la sombra es solo para lo que flota.
- **Don't** poner prosa ni valores en Barlow Condensed, ni cifras en Barlow.
