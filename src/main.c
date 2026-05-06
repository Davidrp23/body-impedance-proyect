#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <stdio.h>
#include <string.h>
#include "ad5940.h"
#include "AD5940Main.h"

LOG_MODULE_REGISTER(main, LOG_LEVEL_INF);

int main(void)
{
	if (AD5940_MCUResourceInit() != 0) {
		return -1;
	}

	char cmd_buf[16];
	int cmd_idx = 0;

	while (1) {
		int c = getchar();
		
		if (c == EOF || c == 0) {
			k_sleep(K_MSEC(10));
			continue;
		}

		/* Esperar el comando "send" seguido de un terminador */
		if (c == '\n' || c == '\r') {
			cmd_buf[cmd_idx] = '\0';
			if (strcmp(cmd_buf, "send") == 0) {
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
