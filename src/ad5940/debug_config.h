#ifndef DEBUG_CONFIG_H
#define DEBUG_CONFIG_H

#include <zephyr/sys/printk.h>

#define DEBUG_PRINT(fmt, ...) printk(fmt, ##__VA_ARGS__)
#define DEBUG_LOG_INFO(...)

#define DEFAULT_SWEEP_POINTS    48
#define DEFAULT_NUM_REPETITIONS 1

#endif
