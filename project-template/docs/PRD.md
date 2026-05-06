# Product Requirements Document (PRD)

## Objetivo del proyecto

<!--
Describir en 2-3 párrafos:
- ¿Qué problema resuelve este proyecto?
- ¿Qué va a hacer el sistema?
- ¿Para quién es? (usuario final, caso de uso)

Ejemplo: "Este proyecto implementa un sistema de monitoreo de bioimpedancia
usando el AFE AD5940 conectado al nRF5340 DK. El sistema mide impedancia
corporal y transmite los datos por BLE a una aplicación móvil."
-->

[Escribir aquí el objetivo del proyecto]

## Requisitos Funcionales

| ID     | Requisito                                              | Prioridad | Capa               |
|--------|--------------------------------------------------------|-----------|---------------------|
| RF-001 | Leer sensor por SPI usando Zephyr SPI API              | Alta      | Driver / Port Layer |
| RF-002 | Exponer BLE GATT Service con característica de datos   | Alta      | Communication       |
| RF-003 | [Descripción del requisito]                            | Media     | [Capa]              |
| RF-004 | [Descripción del requisito]                            | Baja      | [Capa]              |

<!--
Capas válidas: Hardware Setup, Driver / Port Layer, Application Logic, Communication, System Integration.
Prioridades: Alta (debe funcionar para la demo), Media (mejora significativa), Baja (nice-to-have).
Usar verbos concretos: leer, escribir, transmitir, calcular, configurar, mostrar.
-->

## Requisitos No Funcionales

| ID      | Requisito                                                  | Categoría     |
|---------|------------------------------------------------------------|---------------|
| RNF-001 | El sistema debe responder a una lectura en menos de 500 ms | Rendimiento   |
| RNF-002 | El consumo en idle no debe superar X mA                    | Energía       |
| RNF-003 | [Descripción del requisito]                                | [Categoría]   |

<!--
Categorías comunes: Rendimiento, Energía, Fiabilidad, Mantenibilidad, Seguridad.
-->

## Restricciones

- Hardware: nRF5340 DK, [sensor/periférico externo]
- SDK: nRF Connect SDK v2.x / Zephyr RTOS
- Comunicación: BLE 5.x (si aplica)
- [Otras restricciones de hardware, protocolo, o normativa]

## Criterios de aceptación

<!-- ¿Cómo sabemos que el proyecto está "terminado"? Listar condiciones verificables. -->

- [ ] El sistema lee datos del sensor correctamente (verificado con logs)
- [ ] Los datos se transmiten por BLE y se reciben en el dispositivo receptor
- [ ] El sistema funciona de forma continua durante al menos 10 minutos sin errores
- [ ] [Criterio adicional]

## Fuera de alcance

<!-- ¿Qué NO va a hacer este proyecto? Esto evita scope creep. -->

- [Funcionalidad que no se implementará]
- [Funcionalidad que queda para trabajo futuro]
