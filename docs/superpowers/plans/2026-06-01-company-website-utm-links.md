# Company Website UTM Links — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hacer clicables los dominios de empresa en el índice y en las páginas de detalle, añadiendo parámetros UTM para que las empresas puedan identificar el tráfico procedente de contrataenve.com.

**Architecture:** Se añade la función pura `website_with_utm(url: str) -> str` en `build_site.py`, se registra como global de Jinja2 en `_make_env()`, y se usa en los dos templates afectados. Las pruebas siguen el ciclo TDD: primero el test en rojo, luego la implementación mínima para que pase.

**Tech Stack:** Python 3.12, Jinja2, pytest. Comandos Python siempre via `.venv/bin/python` y `.venv/bin/pytest`.

---

## Mapa de archivos

| Archivo | Acción | Responsabilidad |
|---------|--------|-----------------|
| `src/remote_venezuela_hiring/build_site.py` | Modificar | Nueva función `website_with_utm()` + registro en `_make_env()` |
| `templates/index.html` | Modificar | `<div class="cell-domain">` → `<a class="cell-domain">` con UTM |
| `templates/company.html` | Modificar | `href` del link del website actualizado con UTM |
| `tests/test_build_site.py` | Modificar | 5 tests nuevos (3 unitarios + 2 integración) |

---

## Task 1: Tests unitarios para `website_with_utm` (RED)

**Files:**
- Modify: `tests/test_build_site.py`

- [ ] **Step 1: Añadir los dos tests unitarios al final de `tests/test_build_site.py`**

Abrir `tests/test_build_site.py` y añadir al final:

```python
def test_website_with_utm_plain_url() -> None:
    from remote_venezuela_hiring.build_site import website_with_utm

    result = website_with_utm("https://proxify.io")
    assert result == "https://proxify.io?utm_source=contrataenve.com&utm_medium=referral"


def test_website_with_utm_existing_params() -> None:
    from remote_venezuela_hiring.build_site import website_with_utm

    result = website_with_utm("https://example.com?ref=foo")
    assert result == "https://example.com?ref=foo&utm_source=contrataenve.com&utm_medium=referral"
```

- [ ] **Step 2: Ejecutar los tests y verificar que fallan**

```bash
RVH_SKIP_JS_BUILD=1 .venv/bin/pytest tests/test_build_site.py::test_website_with_utm_plain_url tests/test_build_site.py::test_website_with_utm_existing_params -v
```

Resultado esperado: `ImportError: cannot import name 'website_with_utm' from 'remote_venezuela_hiring.build_site'`

---

## Task 2: Implementar `website_with_utm` (GREEN)

**Files:**
- Modify: `src/remote_venezuela_hiring/build_site.py`

- [ ] **Step 1: Añadir la función `website_with_utm` en `build_site.py`**

En `src/remote_venezuela_hiring/build_site.py`, añadir la función después del bloque de constantes (`SPANISH_MONTHS`) y antes de `_format_date` (línea ~106):

```python
def website_with_utm(url: str) -> str:
    """Append UTM referral parameters so companies can track traffic from contrataenve.com."""
    utm = "utm_source=contrataenve.com&utm_medium=referral"
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{utm}"
```

- [ ] **Step 2: Ejecutar los tests y verificar que pasan**

```bash
RVH_SKIP_JS_BUILD=1 .venv/bin/pytest tests/test_build_site.py::test_website_with_utm_plain_url tests/test_build_site.py::test_website_with_utm_existing_params -v
```

Resultado esperado: `2 passed`

- [ ] **Step 3: Commit**

```bash
git add src/remote_venezuela_hiring/build_site.py tests/test_build_site.py
git commit -m "feat: add website_with_utm helper with unit tests"
```

---

## Task 3: Test para el registro como global de Jinja2 (RED)

**Files:**
- Modify: `tests/test_build_site.py`

- [ ] **Step 1: Añadir el test del global de Jinja2 al final del archivo**

```python
def test_website_with_utm_is_jinja_global() -> None:
    from remote_venezuela_hiring.build_site import TEMPLATES_DIR, _make_env, website_with_utm

    env = _make_env(TEMPLATES_DIR)
    assert "website_with_utm" in env.globals
    assert env.globals["website_with_utm"] is website_with_utm
```

- [ ] **Step 2: Ejecutar el test y verificar que falla**

```bash
RVH_SKIP_JS_BUILD=1 .venv/bin/pytest tests/test_build_site.py::test_website_with_utm_is_jinja_global -v
```

Resultado esperado: `AssertionError: assert 'website_with_utm' in {...}` (la clave no existe aún en los globals).

---

## Task 4: Registrar `website_with_utm` en Jinja2 (GREEN)

**Files:**
- Modify: `src/remote_venezuela_hiring/build_site.py`

- [ ] **Step 1: Registrar la función como global en `_make_env()`**

En `_make_env()` (línea ~124), tras la última línea `env.globals["format_date"] = _format_date`, añadir:

```python
    env.globals["website_with_utm"] = website_with_utm
```

El bloque completo queda así:

```python
def _make_env(templates_dir: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.globals["status_labels"] = STATUS_LABELS
    env.globals["verification_labels"] = VERIFICATION_LABELS
    env.globals["platform_labels"] = PLATFORM_LABELS
    env.globals["format_date"] = _format_date
    env.globals["website_with_utm"] = website_with_utm
    return env
```

- [ ] **Step 2: Ejecutar el test y verificar que pasa**

```bash
RVH_SKIP_JS_BUILD=1 .venv/bin/pytest tests/test_build_site.py::test_website_with_utm_is_jinja_global -v
```

Resultado esperado: `1 passed`

- [ ] **Step 3: Commit**

```bash
git add src/remote_venezuela_hiring/build_site.py tests/test_build_site.py
git commit -m "feat: register website_with_utm as Jinja2 global"
```

---

## Task 5: Tests de integración (RED)

**Files:**
- Modify: `tests/test_build_site.py`

- [ ] **Step 1: Añadir los dos tests de integración al final del archivo**

```python
def test_index_domain_links_have_utm_params(output_dir: Path) -> None:
    build(output_dir=output_dir)
    html = (output_dir / "index.html").read_text(encoding="utf-8")
    # Jinja2 escapa & a &amp; en atributos HTML — eso es correcto y esperado.
    assert "utm_source=contrataenve.com&amp;utm_medium=referral" in html
    assert '<a class="cell-domain"' in html


def test_company_detail_website_link_has_utm(output_dir: Path) -> None:
    build(output_dir=output_dir)
    html = (output_dir / "company" / "proxify.html").read_text(encoding="utf-8")
    assert "utm_source=contrataenve.com&amp;utm_medium=referral" in html
```

- [ ] **Step 2: Ejecutar los tests y verificar que fallan**

```bash
RVH_SKIP_JS_BUILD=1 .venv/bin/pytest tests/test_build_site.py::test_index_domain_links_have_utm_params tests/test_build_site.py::test_company_detail_website_link_has_utm -v
```

Resultado esperado: `2 failed` — los UTM params no están en el HTML aún y `<a class="cell-domain"` no existe.

---

## Task 6: Actualizar templates (GREEN)

**Files:**
- Modify: `templates/index.html`
- Modify: `templates/company.html`

- [ ] **Step 1: Actualizar `templates/index.html`**

Localizar el bloque del dominio (líneas 156-158):

```html
            <div class="cell-domain">
              {{ company.website_str() | replace("https://", "") | replace("http://", "") | trim('/') }}
            </div>
```

Reemplazarlo por:

```html
            <a class="cell-domain"
               href="{{ website_with_utm(company.website_str()) }}"
               target="_blank"
               rel="noopener noreferrer nofollow">
              {{ company.website_str() | replace("https://", "") | replace("http://", "") | trim('/') }}
            </a>
```

- [ ] **Step 2: Actualizar `templates/company.html`**

Localizar la línea 24:

```html
        <a class="company-card-website" href="{{ company.website_str() }}" target="_blank" rel="noopener noreferrer nofollow">
```

Reemplazarla por:

```html
        <a class="company-card-website" href="{{ website_with_utm(company.website_str()) }}" target="_blank" rel="noopener noreferrer nofollow">
```

- [ ] **Step 3: Ejecutar los tests de integración y verificar que pasan**

```bash
RVH_SKIP_JS_BUILD=1 .venv/bin/pytest tests/test_build_site.py::test_index_domain_links_have_utm_params tests/test_build_site.py::test_company_detail_website_link_has_utm -v
```

Resultado esperado: `2 passed`

- [ ] **Step 4: Ejecutar toda la suite para verificar que no hay regresiones**

```bash
RVH_SKIP_JS_BUILD=1 .venv/bin/pytest tests/ -v --ignore=tests/e2e
```

Resultado esperado: todos los tests pasan.

- [ ] **Step 5: Commit**

```bash
git add templates/index.html templates/company.html tests/test_build_site.py
git commit -m "feat: make company domain links clickable with UTM referral params"
```

---

## Task 7: Verificación final

- [ ] **Step 1: Ejecutar la suite completa (incluyendo E2E)**

```bash
.venv/bin/pytest tests/ -v
```

Resultado esperado: todos los tests pasan, incluyendo los E2E de Playwright.

- [ ] **Step 2: Hacer un build manual y revisar visualmente**

```bash
.venv/bin/python -m remote_venezuela_hiring.build_site
```

Abrir `site/index.html` en el navegador, pasar el cursor sobre un dominio de empresa y verificar en la barra de estado que la URL contiene `utm_source=contrataenve.com&utm_medium=referral`. Hacer click y confirmar que la URL de destino tiene los parámetros.
