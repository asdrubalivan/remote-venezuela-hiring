---
name: add-company-interview
description: Agrega una empresa al directorio data/companies/ mediante una entrevista rápida de 6 preguntas. Usa este skill cuando el usuario quiera añadir una empresa nueva al proyecto, registrar si una empresa acepta o rechaza candidatos de Venezuela, o agregar información de una compañía sin editar YAML manualmente. Triggerear también ante frases como "agregar empresa", "añadir compañía", "registrar empresa", "nueva empresa en el directorio".
model: claude-haiku-4-5-20251001
---

# add-company-interview

Conduce una entrevista breve para recopilar los datos de una empresa y crea el archivo YAML correspondiente en `data/companies/`.

## Flujo de ejecución

### Paso 1 — Nombre y sitio web

Usa `AskUserQuestion` para pedir el nombre oficial y el sitio web de la empresa:

```
question: "¿Cuál es el nombre y el sitio web de la empresa?"
header: "Empresa"
options: (no usar dropdown aquí — dejar campo "Other" libre)
```

Si el usuario escribe ambos en un solo mensaje (ej: "Acme Corp, https://acme.com"), extrae los dos valores sin volver a preguntar.

Validaciones:
- El nombre no puede estar vacío.
- El website debe comenzar con `https://`. Si el usuario da una URL sin `https://`, prefijarla automáticamente y avisarle.

### Paso 2 — Estado (`status`)

```
question: "¿Esta empresa acepta candidatos basados en Venezuela?"
header: "Estado"
options:
  - accepts: Sí, acepta candidatos de Venezuela
  - rejects: No, rechaza candidatos de Venezuela
  - unknown: No se sabe con certeza
```

### Paso 3 — Método de verificación (`verification_method`)

Presenta las opciones según el `status` elegido:

Si `status` es `accepts` o `rejects`:
```
question: "¿Cómo se verificó esta información?"
header: "Verificación"
options:
  - public_job_post: Anuncio de trabajo público
  - recruiter: Confirmado por reclutador
  - application_form: Formulario de aplicación
  - community_report: Reporte de la comunidad
```
(No mostrar `unknown` cuando status es definitivo — sería inválido según el modelo de datos.)

Si `status` es `unknown`:
```
options: (las 4 de arriba + unknown: No se sabe)
```

### Paso 4 — Plataforma de contratación (opcional)

```
question: "¿En qué plataforma publican sus vacantes? (opcional)"
header: "Plataforma"
options:
  - greenhouse / ashby / lever / workable / teamtailor / linkedin / company_site / other / unknown
  - omit: No especificar (omite este campo del YAML)
```

### Paso 5 — Tags (opcional)

```
question: "¿Qué tags describen a esta empresa? Ej: backend, remote, saas (opcional, separados por coma)"
header: "Tags"
options:
  - (campo libre — "Other")
  - skip: Sin tags
```

Normalización: convertir cada tag a kebab-case lowercase, ordenar alfabéticamente.

### Paso 6 — Notas (opcional)

```
question: "¿Alguna nota adicional sobre esta empresa? (opcional, máx 500 caracteres)"
header: "Notas"
options:
  - (campo libre — "Other")
  - skip: Sin notas
```

Si supera 500 caracteres, truncar en 497 y agregar `...`, avisando al usuario.

---

## Generación automática de campos

- `id`: slug kebab-case del nombre. Regla: lowercase, reemplazar espacios y puntos por `-`, eliminar caracteres especiales. Ejemplos: `Customer.io` → `customer-io`, `Acme Corp` → `acme-corp`.
- `last_checked`: fecha de hoy en formato `YYYY-MM-DD`.
- `archived`: `false`.

---

## Escritura del YAML

Antes de escribir, verificar si ya existe `data/companies/{id}.yaml`. Si existe, informar al usuario y preguntar si desea sobreescribir.

Orden canónico de campos:

```yaml
id: {id}
name: {name}
website: {website}
status: {status}
last_checked: {YYYY-MM-DD}
verification_method: {verification_method}
hiring_platform: {hiring_platform}   # omitir si fue "No especificar"
tags:                                 # omitir si no hay tags
  - {tag1}
  - {tag2}
notes: >                              # omitir si no hay notas
  {notes}
archived: false
```

Al terminar, mostrar el contenido del YAML generado en un bloque de código y la ruta donde se guardó.

---

## Restricciones importantes

- Si `status` es `accepts` o `rejects`, nunca asignar `verification_method: unknown`.
- Tags: kebab-case, ordenados alfabéticamente.
- Notes: sin las palabras `scam`, `toxic`, `illegal`, `sanctions violation`, `burnout`. Si el usuario las incluye, pedirle que reformule en términos neutrales y factuales.
- Website: siempre con `https://`.
