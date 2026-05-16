# CLAUDE.md

## Reglas de trabajo

- **Nunca hacer commits directamente a `main`.** Todos los cambios van en una rama y se proponen mediante Pull Request.
- Al ejecutar tareas con agentes, usar siempre `isolation: "worktree"` para que los cambios queden en una rama aislada.

## Arquitectura

### Descripción general

Sitio estático de información sobre empresas que contratan desde Venezuela, construido con Python y desplegado en GitHub Pages. El contenido lo aportan contribuidores mediante issues de GitHub; un workflow lo convierte automáticamente en PRs.

### Estructura de directorios

```
data/companies/          # Un archivo YAML por empresa (fuente de verdad)
src/remote_venezuela_hiring/
  build_site.py          # Genera el HTML estático en site/
  validate_data.py       # Valida el esquema de los YAML
  issue_to_yaml.py       # Convierte el body de un issue en YAML
scripts/
  build-js.mjs           # Bundler TypeScript → static/*.js (esbuild)
static/                  # TypeScript del frontend
tests/e2e/               # Tests Playwright (test_index.py, test_stats.py)
.github/workflows/
  validate.yml           # CI: lint, tipos, pytest+E2E, validación de datos, smoke build
  issue-to-pr.yml        # Convierte issues etiquetados en PRs automáticos
  deploy-pages.yml       # Build + deploy a GitHub Pages (solo en push a main)
```

### Stack técnico

| Capa | Tecnología |
|------|-----------|
| Python | 3.12, pyproject.toml, Ruff, Mypy (strict) |
| Node | 24, pnpm 11, esbuild |
| Tests | pytest + Playwright (Chromium) |
| CI | GitHub Actions |
| Deploy | GitHub Pages |

### Flujo de contribución de datos

1. Contribuidor abre un issue con label `add-company` o `update-status`.
2. `issue-to-pr.yml` parsea el body, genera el YAML y abre un PR usando `PAT_TOKEN` (fine-grained PAT con permisos mínimos: Contents R/W + Pull requests R/W + Issues R).
3. `validate.yml` corre automáticamente en el PR: lint → tipos → validación YAML → pytest E2E → smoke build.
4. El mantenedor revisa y mergea. `deploy-pages.yml` despliega el sitio actualizado.

### CI en detalle (`validate.yml`)

Corre en `push` a `main` y en `pull_request` contra `main`. Pasos en orden:

1. TypeScript type-check (`tsc --noEmit`)
2. Build del bundle JS (`scripts/build-js.mjs`)
3. Ruff lint + format check
4. Mypy strict
5. Validación de YAML (`validate_data`)
6. Playwright install + pytest (unit + E2E)
7. Build del sitio completo (smoke test)
