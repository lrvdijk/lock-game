#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>

#include "lcd.h"
#include "shell.h"
#include "lock.h"
#include "jtag.h"

// Function definitions
void open_lock();
void close_lock();

// Check status of lock only once per second
ISR(TIMER1_OVF_vect)
{
	TCNT1 = 49910;
	
    lock_check_status();
}

int main()
{
	cli();

	// Setup timers
	// Timer1 for temp meassure
	TCCR1A = 0; // Normal operation
	TCCR1B = (1 << CS12) | (1 << CS10);
	TCNT1 = 49910;

	// Enable interrupts
	TIMSK1 = (1 << TOIE1);
	
    DDRD = 0xFF;
    PORTD = 0;
	DDRB = 0;

	// Setup LCD
	lcd_init();
	lcd_cursor(false, false);

	// Run rest of the program
	while(1)
	{
        if(jtag_status & JTAG_INIT)
        {
            if(PORTB & 0x6C) 
            {
                shell_init(USER_ROOT);
            }
            else
            {
                shell_init(USER_NORMAL);
            }
        }

        if(lock_current_code() == lock_stored_code())
        {
            open_lock();
        }
        else
        {
            close_lock();
        }

	}
}

void open_lock()
{
	// Disable heating and enable cooling
	PORTD |= (1 << 7);

	// Output to LCD
	lcd_cls();
	lcd_puts("Slot open");
}

void close_lock()
{
	PORTD &= ~(1 << 7);

	// Output to LCD
	lcd_cls();
	lcd_puts("Slot dicht");
}

