# Design: [Nombre del bloque]

**Autor:** [nombre] | **Fecha:** [fecha] | **Issue:** #XX

## Objetivo

Qué hace este bloque en 2-3 frases.

## Interfaz

Funciones públicas, parámetros, valores de retorno.

```c
/* Example:
int sensor_init(void);
int sensor_read(float *value);
*/
```

## Diseño

Cómo funciona internamente. Diagrama si aplica.

## Dependencias

- Nodos del Devicetree necesarios (ej: `&spi2` con status `okay`)
- CONFIG_ necesarios en prj.conf (ej: `CONFIG_SPI=y`)
- Otros bloques del proyecto que deben funcionar antes

## Criterios de verificación

- [ ] Criterio 1: "Al ejecutar X, el log muestra Y"
- [ ] Criterio 2: "El valor leído está en el rango [A, B]"
- [ ] Criterio 3: "El sistema responde en menos de X ms"
