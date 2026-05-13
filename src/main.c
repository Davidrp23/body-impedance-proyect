#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <stdio.h>
#include <string.h>
#include <zephyr/drivers/uart.h>
#include "ad5940.h"
#include "AD5940Main.h"

LOG_MODULE_REGISTER(main, LOG_LEVEL_INF);

int main(void)
{
	/* Obtener el dispositivo UART asociado a la consola */
	const struct device *uart_dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_console));
	if (!device_is_ready(uart_dev)) {
		LOG_ERR("El dispositivo UART no esta listo");
		return -1;
	}

	if (AD5940_MCUResourceInit() != 0) {
		return -1;
	}



	char cmd_buf[16];
	int cmd_idx = 0;

	while (1) {
		unsigned char c;
		
		/* uart_poll_in lee 1 byte físico. Devuelve 0 si leyó algo, o un error (como -1) si no hay datos */
		if (uart_poll_in(uart_dev, &c) != 0) {
			k_sleep(K_MSEC(10));
			continue;
		}

		/* Esperar el comando "send" seguido de un terminador */
		if (c == '\n' || c == '\r') {
			cmd_buf[cmd_idx] = '\0';
			if (strstr(cmd_buf, "send") != NULL) {
				AD5940_Main();
			}
			cmd_idx = 0; /* Reset para el siguiente comando */
		} else {
			if (cmd_idx < sizeof(cmd_buf) - 1) {
				cmd_buf[cmd_idx++] = (char)c;
			}
		}
	}

	return 0;
}