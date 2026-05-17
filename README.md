# Remote Venezuela Hiring

[![Validate](https://github.com/asdrubalivan/remote-venezuela-hiring/actions/workflows/validate.yml/badge.svg)](https://github.com/asdrubalivan/remote-venezuela-hiring/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.12-blue)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/asdrubalivan/remote-venezuela-hiring)

Base de datos pública, mantenida por la comunidad, sobre empresas que podrían admitir candidatos remotos basados en Venezuela.

> **Este proyecto no constituye asesoría legal y no es una declaración oficial de ninguna empresa. La compatibilidad puede cambiar con el tiempo. Verifica siempre directamente con la empresa.**

---

## Qué es esto

Una lista neutral, factual y mantenida por la comunidad que registra si las empresas parecen aceptar o rechazar postulaciones de candidatos basados en Venezuela. Los datos provienen de reportes comunitarios, ofertas de empleo y experiencias al postular — no de declaraciones oficiales de las empresas.

## Qué NO es

- No es un sitio de reseñas de empresas
- No es un espacio para calificar balance vida-trabajo, cultura, salarios o gestión
- No es una fuente de asesoría legal
- No es un respaldo o rechazo oficial de ninguna empresa
- No está afiliado con ninguna empresa listada

---

## Definiciones de estado

| Estado | Significado |
|---|---|
| `accepts` | La empresa parece permitir postulaciones desde Venezuela, o un candidato logró postularse sin bloqueos visibles |
| `rejects` | La empresa o el flujo de postulación indica que Venezuela no está soportado actualmente |
| `unknown` | Aún no hay información clara disponible |

El sitio web los muestra como:
- **Probablemente acepta Venezuela** (accepts)
- **Reportado como no aceptando Venezuela** (rejects)
- **Desconocido / requiere verificación** (unknown)

## Definiciones del método de verificación

| Método | Significado |
|---|---|
| `application_form` | Observado directamente a través del formulario de postulación |
| `recruiter` | Información obtenida de una interacción con un reclutador |
| `public_job_post` | Inferido a partir de una oferta de empleo pública |
| `community_report` | Reportado por un miembro de la comunidad |
| `unknown` | Método no especificado |

---

## Directorio de empresas

<!-- COMPANIES_TABLE_START -->
| Empresa | Estado | Plataforma | Método | Tags | Verificada |
|:--------|:------:|:----------:|:------:|:----:|:----------:|
| [BairesDev](https://www.bairesdev.com/) | ✅ Acepta | Greenhouse | Formulario de solicitud | backend, frontend | 17 may 2026 |
| [Interfell](https://interfell.com/) | ✅ Acepta | LinkedIn | Reporte comunitario | backend, frontend, remote | 16 may 2026 |
| [Oberstaff](https://www.oberstaff.com/) | ✅ Acepta | Desconocido | Reporte comunitario | digital-marketing, marketing, recruitment, seo | 16 may 2026 |
| [Proxify](https://proxify.io/) | ✅ Acepta | LinkedIn | Formulario de solicitud | backend, contractor, python | 15 may 2026 |
| [Remote.com](https://remote.com/) | ✅ Acepta | Sitio de la empresa | Oferta pública | hr, remote, worldwide | 15 may 2026 |
| [Team International](https://www.teaminternational.com/) | ✅ Acepta | Desconocido | Formulario de solicitud | backend, frontend | 15 may 2026 |
| [Workana](https://www.workana.com/) | ✅ Acepta | Sitio de la empresa | Formulario de solicitud | freelance, latam, remote | 15 may 2026 |
| [Devlane](https://www.devlane.com/) | ❌ No acepta | Desconocido | Formulario de solicitud | backend, staff-augmentation | 15 may 2026 |
| [Hostinger](https://www.hostinger.com/) | ❌ No acepta | TeamTailor | Formulario de solicitud | hosting, remote, tech | 17 may 2026 |
| [Strider](https://www.onstrider.com/) | ❌ No acepta | LinkedIn | Reporte comunitario | — | 16 may 2026 |
| [Virtasant](https://virtasant.com/) | ❌ No acepta | Sitio de la empresa | Reporte comunitario | cloud, consulting, remote | 15 may 2026 |
| [X-Team](https://www.xteam.com/) | ❌ No acepta | Sitio de la empresa | Formulario de solicitud | remote | 16 may 2026 |
| [Customer.io](https://customer.io/) | ❓ Desconocido | Greenhouse | Oferta pública | backend, remote, saas | 15 may 2026 |
| [Tesorio](https://www.tesorio.com/) | ❓ Desconocido | Greenhouse | Oferta pública | fintech, remote, saas | 15 may 2026 |
| [Xebia](https://xebia.com/) | ❓ Desconocido | Lever | Oferta pública | consulting, remote | 15 may 2026 |
<!-- COMPANIES_TABLE_END -->

> Tabla actualizada automáticamente en cada push a `main`. Ver el [sitio interactivo](https://asdrubalivan.github.io/remote-venezuela-hiring/) para filtros avanzados y detalle completo.

---

## Cómo usar el sitio

Visita el sitio en GitHub Pages para navegar y filtrar empresas por estado, plataforma, etiquetas y más. Haz clic en el nombre de cualquier empresa para ver los detalles completos.

---

## Cómo agregar una empresa a través de GitHub Issues

1. Abre un nuevo issue usando el formulario **Add Company**
2. Completa los campos — sé factual y neutral
3. Un maintainer revisará y fusionará un PR generado
4. No pegues mensajes privados, nombres de reclutadores ni capturas de pantalla

## Cómo agregar una empresa a través de un PR de YAML

1. Copia un archivo existente de `data/companies/`
2. Nómbralo `{company-id}.yaml` (kebab-case en minúsculas que coincida con el campo `id`)
3. Completa los campos
4. Ejecuta `python -m remote_venezuela_hiring.validate_data` localmente
5. Abre un PR — una empresa por PR

---

## Desarrollo local

```bash
git clone https://github.com/asdrubalivan/remote-venezuela-hiring.git
cd remote-venezuela-hiring
make setup
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

`make setup` crea el entorno virtual, instala dependencias Python y Node, e instala los pre-commit hooks automáticamente.

### Comandos disponibles

| Comando | Descripción |
|---|---|
| `make setup` | Setup completo del entorno (primera vez) |
| `make test` | Corre pytest |
| `make lint` | Ruff + Mypy |
| `make validate` | Valida los YAML de empresas |
| `make build` | Genera el bundle JS y el sitio estático en `./site/` |
| `make serve` | Build + servidor local en http://localhost:8080 |

## Despliegue

El sitio se despliega automáticamente en GitHub Pages en cada push a `main` mediante `.github/workflows/deploy-pages.yml`. Habilita GitHub Pages en la configuración del repositorio apuntando a **GitHub Actions** como fuente.

---

## Reglas de privacidad y seguridad

- No incluyas nombres de reclutadores
- No incluyas direcciones de correo electrónico ni mensajes privados
- No incluyas capturas de pantalla
- No incluyas información salarial
- No incluyas comentarios sobre cultura o balance vida-trabajo
- Las notas deben ser factuales y de menos de 500 caracteres
- Las notas se revisan antes de fusionarse

---

## Contribuir

Consulta [CONTRIBUTING.md](CONTRIBUTING.md).
