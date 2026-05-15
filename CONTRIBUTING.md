# Contribuir a Remote Venezuela Hiring

Gracias por ayudar a mantener esta base de datos precisa y útil.

## Reglas principales

- **Mantén los reportes factuales.** Reporta solo lo que observaste o experimentaste directamente.
- **No pegues correspondencia privada.** Nada de fragmentos de correos, mensajes de reclutadores, registros de chat o DMs.
- **No incluyas nombres de reclutadores.** No nombres a personas individuales de ninguna empresa.
- **No incluyas capturas de pantalla.** Ninguna imagen de formularios de postulación, rechazos o conversaciones.
- **No agregues reseñas de empresas.** Este no es un espacio para comentarios sobre cultura, gestión o balance vida-trabajo.
- **No agregues información salarial o de compensación.**
- **Usa `unknown` cuando no estés seguro.** Siempre es mejor reportar `unknown` que adivinar.
- **Una empresa por PR.**
- **El YAML debe pasar la validación.** Ejecuta `python -m remote_venezuela_hiring.validate_data` antes de abrir un PR.

## Agregar una empresa

### Vía GitHub Issue (recomendado para contribuidores no técnicos)

1. Abre un nuevo issue usando el formulario **Add Company**
2. Completa todos los campos con precisión
3. Un bot generará un PR a partir de tu issue — un maintainer lo revisará

### Vía pull request de YAML

1. Haz fork del repositorio
2. Copia `data/companies/unknown-example.yaml` como plantilla
3. Nombra el archivo `{company-id}.yaml` — el campo `id` debe coincidir exactamente
4. Completa los campos siguiendo el esquema de abajo
5. Ejecuta `python -m remote_venezuela_hiring.validate_data`
6. Abre un PR con el título `Add company: {Company Name}`

## Referencia de campos del YAML

```yaml
id: company-id          # lowercase kebab-case, must match filename
name: Company Name      # official company name
website: https://...    # company website URL
status: unknown         # accepts | rejects | unknown
last_checked: 2026-05-15  # ISO date, cannot be in the future
verification_method: unknown  # application_form | recruiter | public_job_post | community_report | unknown
hiring_platform: unknown      # optional: greenhouse | ashby | lever | workable | teamtailor | linkedin | company_site | other | unknown
tags:                   # optional list of lowercase kebab-case tags
  - backend
  - remote
notes: >                # optional, max 500 chars, factual only
  Short factual note.
archived: false         # set to true only for companies no longer relevant
```

## Lineamientos para las notas

- Máximo 500 caracteres
- Solo factual y neutral
- Sin juicios subjetivos
- Palabras prohibidas: scam, toxic, illegal, sanctions violation, 996, burnout, bad work-life balance, screenshot, recruiter name, email thread

## Actualizar una empresa

Usa el formulario de issue **Update Company** o abre un PR que modifique el archivo YAML existente. Actualiza `last_checked` con la fecha de hoy.

## Archivar una empresa

Establece `archived: true` en el YAML. Los registros archivados quedan ocultos por defecto en el sitio pero permanecen en la base de datos como historial.
