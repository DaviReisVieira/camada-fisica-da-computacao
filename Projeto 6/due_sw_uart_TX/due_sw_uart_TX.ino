#include "sw_uart.h"

due_sw_uart uart;

void setup() { 
  sw_uart_setup(&uart, 4, 1, 8, SW_UART_EVEN_PARITY);
}

void loop() {
  test_write();
  delay(5000);
}

void test_write() {
  sw_uart_write_byte(&uart, 'a');
}
