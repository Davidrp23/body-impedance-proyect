/*!
 *****************************************************************************
 @file:    AD5940Main.h
 @author:  Firmware Team
 @brief:   Header file for AD5940 main functions
 @version: 3.0 (Zephyr port)
 -----------------------------------------------------------------------------

Copyright (c) 2017-2025 Analog Devices, Inc. All Rights Reserved.

*****************************************************************************/

#ifndef AD5940MAIN_H
#define AD5940MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stdbool.h>
#include "debug_config.h"

/* Measurement point structure */
typedef struct {
    float frequency;
    float magnitude;
    float phase;
} MeasurementPoint;

/* Global measurement buffer */
extern MeasurementPoint g_measurement_buffer[DEFAULT_SWEEP_POINTS];
extern uint8_t g_measurement_count;

/**
 * @brief Main AD5940 measurement function
 * @details Performs a complete bioimpedance sweep according to configured parameters
 */
void AD5940_Main(void);

#ifdef __cplusplus
}
#endif

#endif /* AD5940MAIN_H */
