# PROTOTIPO — rediseño de la portada (descartable)

Cinco direcciones visuales para la portada, con los mismos textos y datos reales.
No es código de producción: sirve para decidir, por votación pública, hacia dónde
va el rediseño. La decisión validada se lleva luego a `templates/` y `static/`.

| # | Variante | Idea |
|---|----------|------|
| 1 | Clasificados | La página de Empleos del periódico; se encierra en rojo lo que sí acepta |
| 2 | Piso de Maiquetía | Las franjas cromáticas del aeropuerto; la banda cambia de color con el filtro |
| 3 | Boleto | Cada empresa es un cupón de pasaje; el estado va sellado |
| 4 | Metro | Señalética del Metro de Caracas; la lista es una línea con estaciones |
| 5 | Guía amarilla | La guía telefónica de CANTV; índice A–Z y puntos guía |

## Correr

```sh
make proto          # construye y sirve en http://127.0.0.1:8090/?v=1
```

Cambia de variante con la barra flotante, las flechas ← → o las teclas 1–5.
Parámetros: `?v=N`, `?status=accepts|rejects|unknown`, `?q=texto`, `?bar=0` (oculta la barra).

Capturas: `.venv/bin/python prototypes/rediseno-portada/shoot.py [--only N]` → `shots/`.

## Estructura

- `build.py` renderiza `variants/vN-*/markup.html` con los datos reales y verifica que
  estén todos los textos de la portada actual.
- `proto.js` tiene el comportamiento compartido (búsqueda, pestañas, filtros, orden) y
  la barra; cada variante lo engancha con atributos `data-rvh-*` (contrato en el archivo).
- `_reference.html` es el markup sin estilo con todos los textos y ganchos.
