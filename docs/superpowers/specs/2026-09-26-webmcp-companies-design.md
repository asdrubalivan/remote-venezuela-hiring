# Diseño: WebMCP con la lista de empresas

**Fecha:** 2026-09-26
**Estado:** Borrador (pendiente de revisión)

## Problema

Los datos del directorio solo existen como YAML en el repo y como filas HTML en `index.html` (atributos `data-*`). Un agente de IA que navega el sitio en un navegador con WebMCP no tiene una forma estructurada de consultarlos: tendría que raspar el DOM. `agents.txt` describe los campos, pero no ofrece una interfaz invocable.

## Solución

Publicar los datos como un `companies.json` estático en el build, y registrar dos tools de WebMCP en cada página que lo consultan del lado del cliente. El sitio sigue siendo 100% estático.

Términos de dominio (Empresa, Status, Método de verificación, Desactualizada, Archivada) según `CONTEXT.md`.

## Contexto verificado del spec de WebMCP

Verificado contra https://webmachinelearning.github.io/webmcp/ y el README de https://github.com/webmachinelearning/webmcp (las lecturas pasaron por un modelo pequeño, así que conviene reconfirmar al implementar):

- La API está en `document.modelContext` (antes `navigator.modelContext`).
- `registerTool(tool, { exposedTo, signal })`. Una tool tiene `name`, `description` y `execute` obligatorios; `title`, `inputSchema` (JSON Schema) y `annotations` opcionales.
- Se desregistra con `AbortSignal`; no existe `unregisterTool`.
- `execute` devuelve `any`. El README usa `{ content: [{ type: "text", text }] }`.
- Si `execute` lanza o rechaza, el llamador recibe `null` sin mensaje.
- Solo hay tools: el spec no define prompts ni resources.
- Chrome 149 con origin trial o el flag `chrome://flags/#enable-webmcp-testing`.

No confirmado: la detección de soporte en Chrome, el efecto concreto de las annotations en el navegador, `structuredContent` y límites de tamaño de respuesta.

## Arquitectura

### `companies.json` (contrato público)

`build_site.py` lo escribe en la raíz del sitio, junto a `index.html`.

```json
{
  "schema_version": 1,
  "generated_at": "2026-09-26T12:00:00Z",
  "companies": [
    {
      "id": "toptal",
      "name": "Toptal",
      "website": "https://toptal.com/",
      "status": "accepts",
      "last_checked": "2026-08-05",
      "verification_method": "public_job_post",
      "hiring_platform": "other",
      "tags": ["ai", "freelance", "global", "marketplace"],
      "notes": "Vacante indica región 'Anywhere in the World'; ...",
      "archived": false
    }
  ]
}
```

- Incluye todas las empresas, archivadas incluidas, con los diez campos del modelo `Company`, ordenadas por `name`.
- Se serializa desde el modelo `Company` (sin duplicar el esquema), en UTF-8 y sin escapar caracteres no ASCII.
- `hiring_platform` y `notes` son `null` cuando no están definidos.
- `website` es el valor tal cual, sin parámetros UTM.
- `generated_at` es UTC en ISO 8601.
- Cualquier cambio incompatible de forma incrementa `schema_version`.
- `agents.txt` menciona este archivo como fuente estructurada.

### Script `webmcp`

Fuente en `src/ts/webmcp.ts`, compilado por `scripts/build-js.mjs` a `static/webmcp.js` (IIFE, mismo pipeline que `filter` y `theme`). Los tipos van en `src/ts/contracts.ts`. Se carga con `defer` desde `templates/base.html`, para que las tools existan en cualquier página.

- **Detección:** si `"modelContext" in document` es falso, el script no hace nada y no lanza errores.
- **URL de los datos:** se resuelve relativa al propio script (`new URL("../companies.json", <src del script>)`), lo que funciona igual desde `/` y desde `/company/`.
- **Carga:** un solo `fetch`, con la promesa cacheada para todas las llamadas.
- **Registro:** cada `registerTool` se envuelve en un `catch` que emite `console.warn`, para que un fallo de registro no rompa la página.

### Tool `list_companies`

Nombres y descripciones en inglés. La descripción indica que `notes` está en español y que conviene pedir solo los campos necesarios con `fields`, porque la lista completa con `notes` es grande.

Entrada (`inputSchema`), todas las propiedades opcionales:

| Propiedad | Tipo | Comportamiento |
|-----------|------|----------------|
| `query` | string | Texto libre, sin distinguir mayúsculas, sobre `name`, `tags` y `notes` (igual que el buscador de la UI) |
| `status` | enum `accepts`, `rejects`, `unknown` | Coincidencia exacta |
| `verification_method` | enum del modelo | Coincidencia exacta |
| `hiring_platform` | enum del modelo | Coincidencia exacta |
| `tag` | string | Un solo tag, coincidencia exacta |
| `include_archived` | boolean, por defecto `false` | Si es `false`, excluye las Empresas archivadas |
| `fields` | array de enum de los diez campos | Campos a devolver. Si se omite, devuelve los diez. `id` siempre se incluye |

Los filtros se combinan con AND. Orden fijo por `name`. Sin paginación.

Salida: `{ content: [{ type: "text", text }] }`, donde `text` es el JSON de `{ "count": N, "companies": [...] }`.

### Tool `get_company`

Entrada: `id` (string, obligatorio) y `fields` (igual que en `list_companies`).

Salida: `{ content: [{ type: "text", text }] }`, donde `text` es el JSON de `{ "company": {...} }`. La búsqueda por `id` incluye Empresas archivadas.

### Annotations y errores

- Ambas tools: `readOnlyHint: true` y `untrustedContentHint: true` (las `notes` vienen de contribuciones de la comunidad). Son declaraciones nuestras; el efecto que tengan en el navegador no está confirmado.
- Los errores de entrada (valor de enum inválido, `id` inexistente, `fields` con un nombre desconocido) no lanzan excepciones. Se devuelve un `content` de texto con el problema y los valores válidos, para que el agente se corrija, como recomienda el README.
- Un fallo al cargar `companies.json` sí puede rechazar la promesa; el mensaje se deja además en `console.warn`.

## Tests (TDD — escritos antes del código)

### `tests/test_build_site.py` (Python)

| Test | Descripción |
|------|-------------|
| `test_build_writes_companies_json` | `build()` genera `companies.json` en la raíz |
| `test_companies_json_shape` | Tiene `schema_version == 1`, `generated_at` en ISO UTC y `companies` |
| `test_companies_json_has_ten_fields` | Cada empresa tiene exactamente los diez campos |
| `test_companies_json_includes_archived` | Las empresas archivadas están presentes |
| `test_companies_json_sorted_by_name` | Orden por `name` |
| `test_companies_json_matches_models` | Todo elemento valida contra `Company` |

### `tests/e2e/test_webmcp.py` (Playwright)

Chromium de Playwright no trae WebMCP. Un `add_init_script` inyecta un `document.modelContext` falso cuyo `registerTool` guarda las tools; los tests invocan luego sus `execute`.

| Test | Descripción |
|------|-------------|
| `test_registers_two_tools` | Se registran `list_companies` y `get_company` |
| `test_tools_are_read_only_and_untrusted` | Ambas con `readOnlyHint` y `untrustedContentHint` en `true` |
| `test_list_filters_by_status` | El filtro por `status` devuelve solo ese status |
| `test_list_excludes_archived_by_default` | `include_archived` en `false` por defecto |
| `test_list_query_matches_name_tags_notes` | La búsqueda cubre los tres campos |
| `test_fields_always_includes_id` | `fields` sin `id` igual devuelve `id` |
| `test_get_company_by_id` | Devuelve la empresa pedida |
| `test_get_company_unknown_id_returns_message` | `id` inexistente devuelve texto, sin lanzar |
| `test_invalid_enum_returns_message` | Un `status` inválido devuelve texto con los valores válidos |
| `test_works_from_company_page` | Las tools funcionan desde `/company/<id>.html` |
| `test_no_errors_without_webmcp` | Sin `document.modelContext`, la página carga sin errores de consola |

### Verificación manual

En Chrome 149 con el flag `chrome://flags/#enable-webmcp-testing` y la extensión WebMCP Inspector. Se anota el resultado en el PR, incluida la forma en que el agente consume la respuesta.

## Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `src/remote_venezuela_hiring/build_site.py` | Escribe `companies.json`; `agents.txt` lo menciona |
| `src/ts/webmcp.ts` | Nuevo: registro y ejecución de las tools |
| `src/ts/contracts.ts` | Tipos de `companies.json`, de las entradas de las tools y del `document.modelContext` |
| `scripts/build-js.mjs` | Añade `webmcp.ts` a los entry points (y actualiza el comentario de cabecera) |
| `templates/base.html` | Carga `{{ static_prefix }}/webmcp.js` con `defer` |
| `.gitignore` | Ignora `static/webmcp.js` y `static/webmcp.js.map` (artefactos compilados, como `filter` y `theme`) |
| `tests/test_build_site.py` | 6 tests nuevos |
| `tests/e2e/test_webmcp.py` | Nuevo: 11 tests |

## Fuera de alcance

- Prompts y resources: el spec de WebMCP no los define.
- Paginación, orden configurable y tools de escritura. Añadir o actualizar empresas sigue siendo por issues de GitHub.
- La API declarativa con formularios HTML.
- UTM en `companies.json`: `website` va sin parámetros.
- Campos derivados como `stale`: `companies.json` tiene solo los diez campos del modelo.
- `static/tweaks.js`: es un artefacto compilado viejo, sin fuente en `src/ts/` y sin referencias. Se deja sin tocar en este PR.

## Riesgos abiertos

- El spec de WebMCP es un borrador en flujo; `document.modelContext`, `registerTool` y las annotations pueden cambiar antes de estabilizarse.
- La respuesta completa de `list_companies` con `notes` (hasta 500 caracteres por empresa) puede rondar los 12k tokens. Se mitiga con `fields` y con la descripción de la tool.
- La forma en que el agente consume el texto JSON, frente a un objeto estructurado, se conoce solo por el ejemplo del README. Hay que verlo en Chrome real.
