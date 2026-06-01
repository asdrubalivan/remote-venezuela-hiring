# Diseño: Links de empresa con parámetros UTM

**Fecha:** 2026-06-01
**Estado:** Aprobado

## Problema

Los dominios de empresas en la tabla del índice (`index.html`) se muestran como texto plano. Los links del sitio de empresa en la página de detalle (`company.html`) existen pero no incluyen parámetros UTM. Como resultado, las empresas no pueden identificar en sus analytics que el tráfico proviene de contrataenve.com.

## Solución

Añadir una función helper `website_with_utm(url: str) -> str` en `build_site.py`, registrarla como global de Jinja2, y usarla en los dos templates afectados.

## Arquitectura

### Helper function

```python
# src/remote_venezuela_hiring/build_site.py

def website_with_utm(url: str) -> str:
    utm = "utm_source=contrataenve.com&utm_medium=referral"
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{utm}"
```

- Función pura, sin efectos secundarios.
- Detecta si la URL ya tiene query params para usar `&` en vez de `?`.
- No modifica el objeto `Company` ni el modelo de datos.

### Registro como global de Jinja2

En `_make_env()`:

```python
env.globals["website_with_utm"] = website_with_utm
```

Disponible en todos los templates como `{{ website_with_utm(company.website_str()) }}`.

### Cambios en templates

**`templates/index.html`** — líneas 156-158:

El `<div class="cell-domain">` pasa a ser un `<a>` con el mismo estilo visual:

```html
<a class="cell-domain"
   href="{{ website_with_utm(company.website_str()) }}"
   target="_blank"
   rel="noopener noreferrer nofollow">
  {{ company.website_str() | replace("https://", "") | replace("http://", "") | trim('/') }}
</a>
```

**`templates/company.html`** — línea 24:

El link ya existe; solo se actualiza el `href`:

```html
<a class="company-card-website"
   href="{{ website_with_utm(company.website_str()) }}"
   target="_blank"
   rel="noopener noreferrer nofollow">
```

## Nota sobre autoescaping

Jinja2 escapa `&` a `&amp;` en atributos HTML. Esto es HTML válido y correcto — los navegadores decodifican `&amp;` a `&` al navegar. Los tests de integración deben buscar `&amp;` en el HTML renderizado, no `&`.

## Tests (TDD — escritos antes del código)

Todos en `tests/test_build_site.py`.

### Tests unitarios (no requieren build)

| Test | Descripción |
|------|-------------|
| `test_website_with_utm_plain_url` | URL sin query params → usa `?` como separador |
| `test_website_with_utm_existing_params` | URL con params existentes → usa `&` como separador |
| `test_website_with_utm_is_jinja_global` | la función está disponible en el env de Jinja2 |

### Tests de integración (llaman a `build()`)

| Test | Descripción |
|------|-------------|
| `test_index_domain_links_have_utm_params` | `index.html` renderizado contiene `utm_source=contrataenve.com&amp;utm_medium=referral` en un `<a class="cell-domain">` |
| `test_company_detail_website_link_has_utm` | `company/proxify.html` renderizado contiene UTM params en el link del website |

## Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `src/remote_venezuela_hiring/build_site.py` | Nueva función `website_with_utm()` + registro en `_make_env()` |
| `templates/index.html` | `<div class="cell-domain">` → `<a class="cell-domain" ...>` |
| `templates/company.html` | `href` actualizado con `website_with_utm()` |
| `tests/test_build_site.py` | 5 tests nuevos (3 unitarios + 2 integración) |

## Fuera de alcance

- No se añade UTM a los links internos del sitio (links a `company/*.html`).
- No se modifican los datos YAML ni el modelo `Company`.
- No se crean nuevos archivos CSS; el estilo de `.cell-domain` ya existe.
