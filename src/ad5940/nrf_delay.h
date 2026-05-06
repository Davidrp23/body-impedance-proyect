#ifndef NRF_DELAY_H_COMPAT
#define NRF_DELAY_H_COMPAT

#include <zephyr/kernel.h>

static inline void nrf_delay_us(uint32_t us) { k_busy_wait(us); }
static inline void nrf_delay_ms(uint32_t ms) { k_msleep(ms); }

#endif
