# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Profesionales tech con residencia en Venezuela que buscan empleo remoto. Antes de invertir tiempo en una postulación, consultan si la empresa acepta o bloquea candidatos desde Venezuela. Llegan sobre todo desde X, LinkedIn y Telegram, muchas veces desde el teléfono.

## Product Purpose

Directorio comunitario, público y factual de empresas que contratan, o rechazan, a candidatos con residencia en Venezuela. Existe para reducir la fricción de buscar trabajo remoto desde el país: saber en segundos si vale la pena postularse. El éxito es que la persona encuentre la empresa, entienda su Status y su fecha de verificación, y decida.

## Positioning

Es la única lista enfocada exclusivamente en la compatibilidad con Venezuela, mantenida por la comunidad mediante issues y PRs en GitHub, con método de verificación y fecha explícitos por empresa. No es un sitio de reseñas ni de ofertas.

## Operating Context

- Contribución por issues de GitHub (`add-company`, `update-status`) que un workflow convierte en PRs.
- Cada empresa es un YAML en `data/companies/`; el sitio estático se genera con Python + Jinja y se despliega en GitHub Pages.
- El sitio expone tools WebMCP (`list_companies`, `get_company`) y `companies.json` para agentes.

## Capabilities and Constraints

- Portada: búsqueda, filtros (verificación, plataforma, etiqueta, archivadas), pestañas por Status, tabla ordenable, enlaces a ficha y web de la empresa.
- Ficha de empresa y página de estadísticas.
- Terminología fija (ver CONTEXT.md): Empresa, Status (`accepts` / `rejects` / `unknown`), Método de verificación, Desactualizada (>180 días), Archivada.
- Los textos (copys) actuales son la referencia: un rediseño los conserva.
- Tema claro/oscuro y densidad de tabla como preferencias del visitante.

## Brand Commitments

- Nombre: Remote Venezuela Hiring.
- Tono neutral y factual. Aviso obligatorio: no es asesoría legal ni declaración oficial de ninguna empresa; siempre verificar directamente.

## Evidence on Hand

- Datos reales: ~100 empresas en `data/companies/` (mayoría `accepts`, pocas `rejects` y `unknown`).
- Demo de WebMCP: `docs/assets/webmcp-demo.gif`.
- No hay testimonios, logos de empresas, métricas de uso ni cobertura de prensa: no inventarlos.

## Product Principles

1. La respuesta primero: Status y fecha de verificación de una empresa deben leerse sin esfuerzo.
2. Hechos, no opiniones: nada de calificaciones, reseñas ni juicios sobre las empresas.
3. La comunidad es la fuente: contribuir debe estar siempre a un clic.
4. La duda es visible: lo desactualizado o desconocido se marca, no se esconde.

## Accessibility & Inclusion

Público mayoritariamente móvil y con conexiones variables: páginas livianas, legibles en pantallas pequeñas, usables sin JavaScript para la lectura básica.
