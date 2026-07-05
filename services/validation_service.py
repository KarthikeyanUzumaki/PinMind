import logging
import re
from typing import List, Dict, Any, Tuple

logger = logging.getLogger("pinmind.validation")

# ═══════════════════════════════════════════════════════════
# HARDWARE KNOWLEDGE DATABASE (Target & Register Reference)
# ═══════════════════════════════════════════════════════════
MCU_HARDWARE_DATABASE = {
    "STM32F401": {
        "architecture": "Cortex-M4",
        "frameworks": ["Bare Metal", "STM32 HAL", "STM32 LL"],
        "compilers": ["GCC ARM", "Clang", "ARMCC"],
        "base_addresses": {
            "RCC_BASE": 0x40023800,
            "GPIOA_BASE": 0x40020000,
            "GPIOB_BASE": 0x40020400,
            "GPIOC_BASE": 0x40020800,
            "SPI1_BASE": 0x40013000,
            "SPI2_BASE": 0x40003800,
            "USART1_BASE": 0x40011000,
            "USART2_BASE": 0x40004400,
            "I2C1_BASE": 0x40005400,
            "I2C2_BASE": 0x40005800,
        },
        "registers": [
            "RCC_CR", "RCC_PLLCFGR", "RCC_CFGR", "RCC_AHB1ENR", "RCC_AHB2ENR",
            "RCC_APB1ENR", "RCC_APB2ENR", "GPIO_MODER", "GPIO_OTYPER", "GPIO_OSPEEDR",
            "GPIO_PUPDR", "GPIO_IDR", "GPIO_ODR", "GPIO_BSRR", "GPIO_LCKR", "GPIO_AFRL",
            "GPIO_AFRH", "SPI_CR1", "SPI_CR2", "SPI_SR", "SPI_DR", "SPI_CRCPR",
            "SPI_RXCRCR", "SPI_TXCRCR", "SPI_I2SCFGR", "SPI_I2SPR", "USART_SR",
            "USART_DR", "USART_BRR", "USART_CR1", "USART_CR2", "USART_CR3", "USART_GTPR",
            "I2C_CR1", "I2C_CR2", "I2C_OAR1", "I2C_OAR2", "I2C_DR", "I2C_SR1", "I2C_SR2",
            "I2C_CCR", "I2C_TRISE", "I2C_FLTR"
        ],
        "clock_limits": {
            "sysclk_max_mhz": 84,
            "apb1_max_mhz": 42,
            "apb2_max_mhz": 84
        }
    },
    "STM32F405": {
        "architecture": "Cortex-M4",
        "frameworks": ["Bare Metal", "STM32 HAL", "STM32 LL"],
        "compilers": ["GCC ARM", "Clang", "ARMCC"],
        "base_addresses": {
            "RCC_BASE": 0x40023800,
            "GPIOA_BASE": 0x40020000,
            "GPIOB_BASE": 0x40020400,
            "GPIOC_BASE": 0x40020800,
            "SPI1_BASE": 0x40013000,
            "SPI2_BASE": 0x40003800,
            "USART1_BASE": 0x40011000,
            "USART2_BASE": 0x40004400,
            "I2C1_BASE": 0x40005400,
            "I2C2_BASE": 0x40005800,
        },
        "registers": [
            "RCC_CR", "RCC_PLLCFGR", "RCC_CFGR", "RCC_AHB1ENR", "RCC_AHB2ENR",
            "RCC_APB1ENR", "RCC_APB2ENR", "GPIO_MODER", "GPIO_OTYPER", "GPIO_OSPEEDR",
            "GPIO_PUPDR", "GPIO_IDR", "GPIO_ODR", "GPIO_BSRR", "GPIO_LCKR", "GPIO_AFRL",
            "GPIO_AFRH", "SPI_CR1", "SPI_CR2", "SPI_SR", "SPI_DR", "SPI_CRCPR",
            "SPI_RXCRCR", "SPI_TXCRCR", "SPI_I2SCFGR", "SPI_I2SPR", "USART_SR",
            "USART_DR", "USART_BRR", "USART_CR1", "USART_CR2", "USART_CR3", "USART_GTPR",
            "I2C_CR1", "I2C_CR2", "I2C_OAR1", "I2C_OAR2", "I2C_DR", "I2C_SR1", "I2C_SR2",
            "I2C_CCR", "I2C_TRISE", "I2C_FLTR"
        ],
        "clock_limits": {
            "sysclk_max_mhz": 168,
            "apb1_max_mhz": 42,
            "apb2_max_mhz": 84
        }
    },
    "STM32G474": {
        "architecture": "Cortex-M4",
        "frameworks": ["Bare Metal", "STM32 HAL", "STM32 LL"],
        "compilers": ["GCC ARM", "Clang", "ARMCC"],
        "base_addresses": {
            "RCC_BASE": 0x40021000,
            "GPIOA_BASE": 0x48000000,
            "GPIOB_BASE": 0x48000400,
            "GPIOC_BASE": 0x48000800,
            "SPI1_BASE": 0x40013000,
            "SPI2_BASE": 0x40003800,
            "USART1_BASE": 0x40013800,
            "USART2_BASE": 0x40004400,
            "I2C1_BASE": 0x40005400,
            "I2C2_BASE": 0x40005800,
        },
        "registers": [
            "RCC_CR", "RCC_CFGR", "RCC_AHB1ENR", "RCC_AHB2ENR", "RCC_APB1ENR1",
            "RCC_APB1ENR2", "RCC_APB2ENR", "GPIO_MODER", "GPIO_OTYPER", "GPIO_OSPEEDR",
            "GPIO_PUPDR", "GPIO_IDR", "GPIO_ODR", "GPIO_BSRR", "GPIO_LCKR", "GPIO_AFRL",
            "GPIO_AFRH", "SPI_CR1", "SPI_CR2", "SPI_SR", "SPI_DR", "USART_SR",
            "USART_DR", "USART_BRR", "USART_CR1", "USART_CR2", "USART_CR3"
        ],
        "clock_limits": {
            "sysclk_max_mhz": 170,
            "apb1_max_mhz": 170,
            "apb2_max_mhz": 170
        }
    },
    "ESP32-WROOM": {
        "architecture": "Tensilica Xtensa LX6",
        "frameworks": ["ESP-IDF", "Arduino", "Bare Metal (Experimental)"],
        "compilers": ["Xtensa GCC", "Clang"],
        "base_addresses": {
            "DR_REG_DPORT_BASE": 0x3FF00000,
            "GPIO_BASE": 0x3FF44000,
            "UART0_BASE": 0x3FF40000,
            "UART1_BASE": 0x3FF50000,
            "UART2_BASE": 0x3FF6E000,
            "I2C0_BASE": 0x3FF53000,
            "I2C1_BASE": 0x3FF67000,
        },
        "registers": [
            "GPIO_OUT_REG", "GPIO_OUT_W1TS_REG", "GPIO_OUT_W1TC_REG",
            "GPIO_ENABLE_REG", "GPIO_ENABLE_W1TS_REG", "GPIO_ENABLE_W1TC_REG",
            "GPIO_IN_REG", "GPIO_PIN_REG", "GPIO_STRAP_REG", "UART_FIFO_REG",
            "UART_INT_RAW_REG", "UART_CLKDIV_REG", "UART_CONF0_REG", "UART_CONF1_REG"
        ],
        "clock_limits": {
            "sysclk_max_mhz": 240
        }
    },
    "RP2040": {
        "architecture": "Dual Cortex-M0+",
        "frameworks": ["Pico SDK", "Bare Metal"],
        "compilers": ["GCC ARM", "Clang"],
        "base_addresses": {
            "SIO_BASE": 0xd0000000,
            "IO_BANK0_BASE": 0x40014000,
            "PADS_BANK0_BASE": 0x4001c000,
            "CLOCKS_BASE": 0x40008000,
            "RESETS_BASE": 0x4000c000,
            "UART0_BASE": 0x40034000,
            "UART1_BASE": 0x40038000,
        },
        "registers": [
            "SIO_GPIO_OUT", "SIO_GPIO_OUT_SET", "SIO_GPIO_OUT_CLR", "SIO_GPIO_OUT_XOR",
            "SIO_GPIO_OE", "SIO_GPIO_OE_SET", "SIO_GPIO_OE_CLR", "SIO_GPIO_IN",
            "IO_BANK0_GPIO0_CTRL", "IO_BANK0_GPIO1_CTRL", "IO_BANK0_GPIO2_CTRL",
            "IO_BANK0_GPIO3_CTRL", "IO_BANK0_GPIO4_CTRL", "IO_BANK0_GPIO5_CTRL",
            "IO_BANK0_GPIO6_CTRL", "IO_BANK0_GPIO7_CTRL", "IO_BANK0_GPIO8_CTRL",
            "IO_BANK0_GPIO9_CTRL", "IO_BANK0_GPIO10_CTRL", "IO_BANK0_GPIO11_CTRL",
            "IO_BANK0_GPIO12_CTRL", "IO_BANK0_GPIO13_CTRL", "IO_BANK0_GPIO14_CTRL",
            "IO_BANK0_GPIO15_CTRL", "IO_BANK0_GPIO16_CTRL", "IO_BANK0_GPIO17_CTRL",
            "IO_BANK0_GPIO18_CTRL", "IO_BANK0_GPIO19_CTRL", "IO_BANK0_GPIO20_CTRL",
            "IO_BANK0_GPIO21_CTRL", "IO_BANK0_GPIO22_CTRL", "IO_BANK0_GPIO23_CTRL",
            "IO_BANK0_GPIO24_CTRL", "IO_BANK0_GPIO25_CTRL", "IO_BANK0_GPIO26_CTRL",
            "IO_BANK0_GPIO27_CTRL", "IO_BANK0_GPIO28_CTRL", "IO_BANK0_GPIO29_CTRL",
            "UART_UARTDR", "UART_UARTRSR", "UART_UARTFR", "UART_UARTIBRD",
            "UART_UARTFBRD", "UART_UARTLCR_H", "UART_UARTCR"
        ],
        "clock_limits": {
            "sysclk_max_mhz": 133
        }
    },
    "AVR-ATmega328P": {
        "architecture": "AVR 8-bit",
        "frameworks": ["AVR-GCC"],
        "compilers": ["AVR-GCC"],
        "base_addresses": {
            "IOPORT_BASE": 0x00,
        },
        "registers": [
            "PINB", "DDRB", "PORTB", "PINC", "DDRC", "PORTC", "PIND", "DDRD", "PORTD",
            "TCCR0A", "TCCR0B", "TCNT0", "OCR0A", "OCR0B", "TIMSK0", "TIFR0",
            "SPCR", "SPSR", "SPDR", "UCSR0A", "UCSR0B", "UCSR0C", "UBRR0H", "UBRR0L", "UDR0"
        ],
        "clock_limits": {
            "sysclk_max_mhz": 20
        }
    },
    "MSP430G2553": {
        "architecture": "MSP430 16-bit",
        "frameworks": ["Bare Metal"],
        "compilers": ["MSP430 GCC"],
        "base_addresses": {
            "PORT1_BASE": 0x20,
            "PORT2_BASE": 0x28,
        },
        "registers": [
            "P1IN", "P1OUT", "P1DIR", "P1IFG", "P1IES", "P1IE", "P1SEL", "P1SEL2",
            "P2IN", "P2OUT", "P2DIR", "P2IFG", "P2IES", "P2IE", "P2SEL", "P2SEL2",
            "WDTCTL", "CALBC1_1MHZ", "CALDCO_1MHZ", "BCSCTL1", "BCSCTL2", "BCSCTL3"
        ],
        "clock_limits": {
            "sysclk_max_mhz": 16
        }
    }
}

# Pin Alternate function mapping (STM32F401/STM32F405 focus)
VALID_ALTERNATE_FUNCTIONS = {
    "STM32F401": {
        "SPI1": ["PA5", "PA6", "PA7", "PB3", "PB4", "PB5"],
        "SPI2": ["PB12", "PB13", "PB14", "PB15", "PC2", "PC3"],
        "I2C1": ["PB6", "PB7", "PB8", "PB9"],
        "I2C2": ["PB10", "PB3", "PB11", "PB12"],
        "USART1": ["PA9", "PA10", "PB6", "PB7"],
        "USART2": ["PA2", "PA3", "PA0", "PA1"]
    },
    "STM32F405": {
        "SPI1": ["PA5", "PA6", "PA7", "PB3", "PB4", "PB5"],
        "SPI2": ["PB12", "PB13", "PB14", "PB15"],
        "I2C1": ["PB6", "PB7", "PB8", "PB9"],
        "USART1": ["PA9", "PA10"],
        "USART2": ["PA2", "PA3"]
    },
    "ESP32-WROOM": {
        "SPI1": ["GPIO12", "GPIO13", "GPIO14", "GPIO15"],
        "SPI2": ["GPIO19", "GPIO23", "GPIO18", "GPIO5"],
        "I2C1": ["GPIO21", "GPIO22"],
        "USART1": ["GPIO9", "GPIO10"],
        "USART2": ["GPIO16", "GPIO17"]
    }
}

REQUIRED_PERIPHERAL_PINS = {
    "SPI1": ["SCK", "MISO", "MOSI"],
    "SPI2": ["SCK", "MISO", "MOSI"],
    "I2C1": ["SCL", "SDA"],
    "I2C2": ["SCL", "SDA"],
    "USART1": ["TX", "RX"],
    "USART2": ["TX", "RX"]
}

# ═══════════════════════════════════════════════════════════
# PRE-GENERATION HARDWARE CONFLICT VALIDATION RULES
# ═══════════════════════════════════════════════════════════
class ConflictRule:
    def validate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        raise NotImplementedError

class TargetAwareValidationRule(ConflictRule):
    """Verifies that the target MCU, framework, and compiler configurations are valid."""
    def validate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        conflicts = []
        mcu = context.get("mcu")
        framework = context.get("framework")
        compiler = context.get("compiler")

        if not mcu:
            conflicts.append({
                "type": "Target Error",
                "resource": "MCU",
                "message": "No MCU architecture selected.",
                "solutions": ["Select a valid MCU architecture in the sidebar dropdown."]
            })
            return conflicts

        db_entry = MCU_HARDWARE_DATABASE.get(mcu)
        if not db_entry:
            conflicts.append({
                "type": "Target Error",
                "resource": f"MCU {mcu}",
                "message": f"Selected MCU '{mcu}' is not supported in the hardware database.",
                "solutions": [f"Select one of the supported MCUs: {', '.join(MCU_HARDWARE_DATABASE.keys())}"]
            })
            return conflicts

        # Validate Framework
        if not framework:
            conflicts.append({
                "type": "Target Error",
                "resource": "Framework",
                "message": "No Target Framework configured for project generation.",
                "solutions": [f"Configure a target framework for {mcu}. Options: {', '.join(db_entry['frameworks'])}"]
            })
        elif framework not in db_entry["frameworks"]:
            conflicts.append({
                "type": "Target Error",
                "resource": f"Framework {framework}",
                "message": f"Framework '{framework}' is incompatible with the selected MCU '{mcu}'.",
                "solutions": [f"Switch framework to one of: {', '.join(db_entry['frameworks'])}"]
            })

        # Validate Compiler
        if not compiler:
            conflicts.append({
                "type": "Target Error",
                "resource": "Compiler",
                "message": "No Target Toolchain compiler configured.",
                "solutions": [f"Select a supported compiler: {', '.join(db_entry['compilers'])}"]
            })
        elif compiler not in db_entry["compilers"]:
            conflicts.append({
                "type": "Target Error",
                "resource": f"Compiler {compiler}",
                "message": f"Compiler '{compiler}' is incompatible with MCU '{mcu}'.",
                "solutions": [f"Switch compiler to one of: {', '.join(db_entry['compilers'])}"]
            })

        # Validate Board
        board = context.get("board")
        if not board:
            conflicts.append({
                "type": "Target Error",
                "resource": "Board",
                "message": "No Development Board configured for project.",
                "solutions": ["Configure a development board in the workspace configurations sidebar."]
            })
            
        # Validate PlatformIO Env
        platformio_env = context.get("platformio_env")
        if not platformio_env:
            conflicts.append({
                "type": "Target Error",
                "resource": "PlatformIO Environment",
                "message": "No PlatformIO Environment configured for compilation verification.",
                "solutions": ["Select a valid PlatformIO environment profile in the sidebar."]
            })

        return conflicts

class TargetFamilyConflictRule(ConflictRule):
    """Ensures that GPIO pin names and clock architectures align with the MCU family selection."""
    def validate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        conflicts = []
        mcu = context.get("mcu", "STM32F401")
        gpios = context.get("gpios", [])
        clocks = context.get("clocks", {})

        # 1. Validate Clock Bus Names for STM32
        if "STM32" in mcu:
            # Check if GPIO pins match PAx, PBx, PCx syntax
            for g in gpios:
                pin = g.get("pin", "")
                if pin and not re.match(r"^P[A-E][0-9]+$", pin):
                    conflicts.append({
                        "type": "Hardware Family Mismatch",
                        "resource": f"GPIO {pin}",
                        "message": f"Pin '{pin}' does not follow STM32 GPIO naming rules (e.g. PA5, PB12).",
                        "solutions": ["Rename the pin using correct Port Letter syntax, e.g. PA0-PA15."]
                    })
        elif "ESP32" in mcu:
            # Check if GPIO pins match GPIOx syntax
            for g in gpios:
                pin = g.get("pin", "")
                if pin and not re.match(r"^GPIO[0-9]+$", pin):
                    conflicts.append({
                        "type": "Hardware Family Mismatch",
                        "resource": f"GPIO {pin}",
                        "message": f"Pin '{pin}' does not follow ESP32 GPIO naming rules (e.g. GPIO32).",
                        "solutions": ["Rename the pin using correct ESP32 syntax, e.g. GPIO4, GPIO21."]
                    })
            # Check if STM32 clock busses apb1/apb2 are set on ESP32
            apb1 = clocks.get("apb1_mhz", 0)
            apb2 = clocks.get("apb2_mhz", 0)
            if apb1 > 0 or apb2 > 0:
                # If they are set to values other than defaults, warning
                if apb1 != 42 or apb2 != 84:
                    conflicts.append({
                        "type": "Hardware Family Mismatch",
                        "resource": "APB Clocks",
                        "message": "APB1 and APB2 clock buses are specific to STM32 architecture and invalid on ESP32.",
                        "solutions": ["Ignore APB clock inputs when working with Tensilica/ESP32 core."]
                    })
        elif "RP2040" in mcu:
            # Check if pins match GPx syntax
            for g in gpios:
                pin = g.get("pin", "")
                if pin and not re.match(r"^GP[0-9]+$", pin):
                    conflicts.append({
                        "type": "Hardware Family Mismatch",
                        "resource": f"GPIO {pin}",
                        "message": f"Pin '{pin}' does not follow RP2040 GPIO naming rules (e.g. GP0).",
                        "solutions": ["Rename the pin using correct RP2040 syntax, e.g. GP12, GP25."]
                    })
        elif "AVR" in mcu:
            # Check if pins match PBx, PCx, PDx syntax
            for g in gpios:
                pin = g.get("pin", "")
                if pin and not re.match(r"^P[B-D][0-7]$", pin):
                    conflicts.append({
                        "type": "Hardware Family Mismatch",
                        "resource": f"GPIO {pin}",
                        "message": f"Pin '{pin}' does not follow AVR Port register naming rules (e.g. PB5, PD2).",
                        "solutions": ["Rename the pin using correct ATmega328P Port mapping, e.g. PB0-PB5, PD0-PD7."]
                    })
        return conflicts

class GPIOCollisionRule(ConflictRule):
    """Checks if the same physical GPIO pin is assigned to multiple resources."""
    def validate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        conflicts = []
        gpios = context.get("gpios", [])
        peripherals = context.get("peripherals", [])
        
        pin_mappings: Dict[str, List[str]] = {}
        for gpio in gpios:
            pin = gpio.get("pin")
            label = gpio.get("label")
            if pin and label:
                if pin not in pin_mappings:
                    pin_mappings[pin] = []
                pin_mappings[pin].append(f"GPIO ({label})")
                
        for peri in peripherals:
            name = peri.get("name", "Unknown")
            pins = peri.get("pins", [])
            for pin in pins:
                if pin:
                    if pin not in pin_mappings:
                        pin_mappings[pin] = []
                    pin_mappings[pin].append(f"Peripheral {name}")

        for pin, owners in pin_mappings.items():
            if len(owners) > 1:
                conflicts.append({
                    "type": "GPIO Conflict",
                    "resource": pin,
                    "message": f"Pin {pin} is requested by multiple components: {', '.join(owners)}.",
                    "solutions": [
                        "Move the GPIO to another free pin.",
                        f"Reconfigure the peripheral {owners[1]} pin layout to avoid collision.",
                        "Use alternate pin multiplexing mode."
                    ]
                })
        return conflicts

class AlternateFunctionRule(ConflictRule):
    """Checks if a pin supports the alternate function (AF) of the assigned peripheral."""
    def validate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        conflicts = []
        mcu = context.get("mcu", "STM32F401")
        peripherals = context.get("peripherals", [])
        
        mcu_af_db = VALID_ALTERNATE_FUNCTIONS.get(mcu, {})
        if not mcu_af_db:
            return conflicts

        for peri in peripherals:
            name = peri.get("name", "")
            pins = peri.get("pins", [])
            base_name = name.split("_")[0]
            valid_pins = mcu_af_db.get(base_name)
            
            if valid_pins:
                for pin in pins:
                    if pin and pin not in valid_pins:
                        conflicts.append({
                            "type": "Alternate Function Conflict",
                            "resource": f"{name} -> {pin}",
                            "message": f"Pin {pin} does not support Alternate Function routing for peripheral {name} on {mcu}.",
                            "solutions": [
                                f"Route {name} to one of the hardware-routed pins: {', '.join(valid_pins)}.",
                                "Switch to software bit-banged driver mode if speed is not critical."
                            ]
                        })
        return conflicts

class ClockDomainRule(ConflictRule):
    """Validates system clock configuration against maximum speed limits in MCU DB."""
    def validate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        conflicts = []
        mcu = context.get("mcu", "STM32F401")
        clocks = context.get("clocks", {})
        
        sysclk = clocks.get("sysclk_mhz", 0)
        apb1 = clocks.get("apb1_mhz", 0)
        apb2 = clocks.get("apb2_mhz", 0)
        
        db_entry = MCU_HARDWARE_DATABASE.get(mcu)
        if not db_entry or "clock_limits" not in db_entry or not sysclk:
            return conflicts

        limits = db_entry["clock_limits"]
        max_sysclk = limits.get("sysclk_max_mhz", 0)
        max_apb1 = limits.get("apb1_max_mhz", 0)
        max_apb2 = limits.get("apb2_max_mhz", 0)

        if max_sysclk and sysclk > max_sysclk:
            conflicts.append({
                "type": "Clock Frequency Conflict",
                "resource": "SYSCLK",
                "message": f"System clock of {sysclk}MHz exceeds the {mcu} maximum limit of {max_sysclk}MHz.",
                "solutions": ["Reduce PLL multiplier frequency.", "Configure clock prescalers."]
            })
        if max_apb1 and apb1 > max_apb1:
            conflicts.append({
                "type": "Clock Warning",
                "resource": "APB1",
                "message": f"APB1 bus speed ({apb1}MHz) exceeds the max limit of {max_apb1}MHz.",
                "solutions": ["Adjust APB1 prescaler division factor to fit within limits."]
            })
        if max_apb2 and apb2 > max_apb2:
            conflicts.append({
                "type": "Clock Warning",
                "resource": "APB2",
                "message": f"APB2 bus speed ({apb2}MHz) exceeds the max limit of {max_apb2}MHz.",
                "solutions": ["Adjust APB2 prescaler division factor to fit within limits."]
            })
        return conflicts

class DMACollisionRule(ConflictRule):
    """Checks for DMA Stream/Channel sharing collisions between peripherals."""
    def validate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        conflicts = []
        peripherals = context.get("peripherals", [])
        
        dma_map: Dict[str, List[str]] = {}
        for p in peripherals:
            name = p.get("name")
            dma = p.get("dma_channel")
            if name and dma and dma != "None" and dma != "":
                if dma not in dma_map:
                    dma_map[dma] = []
                dma_map[dma].append(name)
                
        for dma, owners in dma_map.items():
            if len(owners) > 1:
                conflicts.append({
                    "type": "DMA Stream Conflict",
                    "resource": dma,
                    "message": f"DMA allocation {dma} is shared between active peripherals: {', '.join(owners)}.",
                    "solutions": [
                        "Reconfigure one peripheral to use a different DMA channel/stream.",
                        "Switch to polling or interrupt-driven transfers."
                    ]
                })
        return conflicts

class PeripheralCompatibilityRule(ConflictRule):
    """Ensures peripherals have the minimum required pins configured to operate."""
    def validate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        conflicts = []
        peripherals = context.get("peripherals", [])
        
        for p in peripherals:
            name = p.get("name", "")
            pins = p.get("pins", [])
            base_name = name.split("_")[0]
            
            req_signals = REQUIRED_PERIPHERAL_PINS.get(base_name)
            if req_signals:
                non_empty_pins = [pin for pin in pins if pin]
                if len(non_empty_pins) < len(req_signals):
                    conflicts.append({
                        "type": "Peripheral Pin Mismatch",
                        "resource": name,
                        "message": f"Peripheral {name} requires at least {len(req_signals)} pins ({', '.join(req_signals)}), but only {len(non_empty_pins)} are assigned.",
                        "solutions": [
                            f"Add pin assignments to peripheral {name} until all signals are mapped."
                        ]
                    })
        return conflicts


# ═══════════════════════════════════════════════════════════
# POST-GENERATION FIRMWARE / REGISTER VALIDATION
# ═══════════════════════════════════════════════════════════
def post_validate_registers(code: str, mcu: str) -> List[str]:
    """
    Parses generated C code to extract hexadecimal base addresses and register names
    and cross-checks them against the selected MCU's register database record.
    Returns a list of failed validation reports.
    """
    errors = []
    db_entry = MCU_HARDWARE_DATABASE.get(mcu)
    if not db_entry:
        return errors

    # 1. Parse hex numbers (e.g. 0x40023800)
    hex_addresses = re.findall(r"0[xX][0-9a-fA-F]{4,8}", code)
    valid_bases = db_entry.get("base_addresses", {})
    
    for addr_str in hex_addresses:
        addr_val = int(addr_str, 16)
        if 0x40000000 <= addr_val <= 0x60000000 or 0x3FF00000 <= addr_val <= 0x3FF70000:
            matched = False
            for base_name, base_val in valid_bases.items():
                if abs(addr_val - base_val) < 0x00100000:
                    matched = True
                    break
            
            if not matched:
                belonging_mcus = []
                for other_mcu, other_entry in MCU_HARDWARE_DATABASE.items():
                    if other_mcu == mcu:
                        continue
                    for base_name, base_val in other_entry.get("base_addresses", {}).items():
                        if abs(addr_val - base_val) < 0x00100000:
                            belonging_mcus.append(other_mcu)
                            break
                if belonging_mcus:
                    errors.append(
                        f"Address overlap: Address '{addr_str}' belongs to {', '.join(belonging_mcus)} "
                        f"base addresses, but is being used in code generated for {mcu}."
                    )

    # 2. Parse register macro names
    words = re.findall(r"\b[A-Z][A-Z0-9_]{3,24}\b", code)
    valid_regs = db_entry.get("registers", [])
    
    for w in set(words):
        is_reg_like = any(p in w for p in ["RCC_", "GPIO", "SPI", "USART", "I2C", "DMA", "PORT", "DDR", "PIN", "UART"])
        if is_reg_like and w not in valid_bases:
            stripped_name = w
            for prefix in ["GPIOA_", "GPIOB_", "GPIOC_", "GPIOD_", "GPIOE_", "GPIO_", "SPI1_", "SPI2_", "USART1_", "USART2_", "I2C1_", "I2C2_", "UART0_", "UART1_", "UART2_"]:
                if w.startswith(prefix):
                    stripped_name = "GPIO_" + w[len(prefix):] if prefix.startswith("GPIO") else prefix[:-1] + "_" + w[len(prefix):]
                    if stripped_name not in valid_regs:
                        suffix = w[len(prefix):]
                        matched_suffix = any(vr.endswith(suffix) for vr in valid_regs)
                        if matched_suffix:
                            stripped_name = next(vr for vr in valid_regs if vr.endswith(suffix))
                    break
            
            if stripped_name not in valid_regs and not any(vr in w for vr in valid_regs):
                if w not in ["NULL", "CMSIS", "CORTEX", "STM32", "ESP32", "XTENSA", "PICO", "AVR", "INPUT", "OUTPUT", "HIGH", "LOW"]:
                    other_mcus = []
                    for other_mcu, other_entry in MCU_HARDWARE_DATABASE.items():
                        if other_mcu == mcu:
                            continue
                        if w in other_entry.get("registers", []) or any(vr in w for vr in other_entry.get("registers", [])):
                            other_mcus.append(other_mcu)
                    
                    if other_mcus:
                        errors.append(
                            f"Register mismatch: Register symbol '{w}' belongs to register configurations for "
                            f"{', '.join(other_mcus)}, but was generated in driver code for {mcu}."
                        )
                    else:
                        errors.append(
                            f"Hallucinated register: Register symbol '{w}' does not exist in the {mcu} hardware specification map."
                        )

    return errors


# ═══════════════════════════════════════════════════════════
# STATIC CODE ANALYSIS (Framework & Code Structure Checks)
# ═══════════════════════════════════════════════════════════
def analyze_static_code(code: str, context: Dict[str, Any]) -> List[str]:
    """
    Runs static code verification on the generated firmware code.
    Checks for:
    - Missing target framework entry point (main/app_main/setup-loop)
    - Missing framework headers
    - Hardcoded magic register pointer writes (e.g. *(uint32_t*)0x40023830 = 1)
    - Invalid GPIO references in code (checking mismatch with assigned pins)
    """
    errors = []
    mcu = context.get("mcu", "STM32F401")
    framework = context.get("framework", "Bare Metal")
    gpios = context.get("gpios", [])

    # 1. Entry point check
    if "ESP-IDF" in framework:
        if "app_main" not in code:
            errors.append("Missing entry point: ESP-IDF firmware must define 'app_main(void)'.")
        if "main(" in code:
            errors.append("Framework mismatch: ESP-IDF firmware should use 'app_main', NOT standard 'main()'.")
    elif "Arduino" in framework:
        if "setup" not in code or "loop" not in code:
            errors.append("Missing entry point: Arduino sketch must define 'setup()' and 'loop()' functions.")
        if "main(" in code or "app_main" in code:
            errors.append("Framework mismatch: Arduino sketch must define ONLY 'setup()' and 'loop()'. standard 'main()' or 'app_main()' functions are forbidden.")
    else:
        if "main" not in code:
            errors.append(f"Missing entry point: standard {framework} program must define 'main()'.")
        if "setup()" in code or "loop()" in code:
            errors.append(f"Framework mismatch: {framework} program should define 'main()', NOT 'setup()' or 'loop()'.")

    # 2. Check required includes
    if "STM32" in mcu:
        if "HAL" in framework:
            if "stm32f4xx_hal.h" not in code and "stm32g4xx_hal.h" not in code:
                errors.append("Missing header: HAL project must include stm32f4xx_hal.h / stm32g4xx_hal.h.")
        elif "LL" in framework:
            if "ll_gpio.h" not in code and "ll_rcc.h" not in code:
                errors.append("Missing header: Low-Layer driver must include LL headers (e.g. stm32f4xx_ll_gpio.h).")
    elif "ESP32" in mcu:
        if "Arduino" in framework:
            if "Arduino.h" not in code:
                errors.append("Missing header: Arduino sketch must include <Arduino.h>.")
        else:
            if "driver/gpio.h" not in code:
                errors.append("Missing header: ESP-IDF driver must include <driver/gpio.h>.")

    # 3. Check for hardcoded register writes (magic pointer assignments)
    # Match constructs like *(volatile uint32_t*)0x40023830 = ...
    magic_writes = re.findall(r"\*\(\s*(?:volatile\s+)?uint32_t\s*\*\s*\)\s*0[xX][0-9a-fA-F]+", code)
    if magic_writes:
        errors.append(
            f"Style warning: Detected {len(magic_writes)} hardcoded pointer writes (magic numbers). "
            "Prefer CMSIS symbolic defines (e.g. GPIOA->MODER) over raw hexadecimal registers."
        )

    # 4. Check for invalid GPIO references
    # Ensure generated code uses at least one of the active user-assigned GPIO pins
    # e.g., if user mapped PA5 but code writes to PA7
    assigned_pins = [g.get("pin") for g in gpios if g.get("pin")]
    if assigned_pins:
        referenced_assigned = False
        for pin in assigned_pins:
            if pin in code:
                referenced_assigned = True
                break
        
        # If code references other pins of same family but not the assigned one
        if not referenced_assigned:
            # Check if there are other pins referenced (e.g. PA or GPIO)
            other_pin_refs = []
            if "STM32" in mcu:
                other_pin_refs = re.findall(r"\bGPIO_PIN_[0-9]+\b|\bPA[0-9]+\b|\bPB[0-9]+\b", code)
            elif "ESP32" in mcu:
                other_pin_refs = re.findall(r"\bGPIO_NUM_[0-9]+\b|\bGPIO_[0-9]+\b", code)
            elif "RP2040" in mcu:
                other_pin_refs = re.findall(r"\bGP[0-9]+\b", code)

            if other_pin_refs:
                errors.append(
                    f"GPIO Reference Warning: The generated code references pins {', '.join(set(other_pin_refs))}, "
                    f"but your hardware configuration assigns {', '.join(assigned_pins)}."
                )

    return errors


# ═══════════════════════════════════════════════════════════
# ENGINE CORE RUNNER
# ═══════════════════════════════════════════════════════════
class ValidationEngine:
    def __init__(self):
        self.rules: List[ConflictRule] = [
            TargetAwareValidationRule(),
            TargetFamilyConflictRule(),
            GPIOCollisionRule(),
            AlternateFunctionRule(),
            ClockDomainRule(),
            DMACollisionRule(),
            PeripheralCompatibilityRule()
        ]

    def validate_hardware(self, context: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        all_conflicts = []
        for rule in self.rules:
            try:
                res = rule.validate(context)
                all_conflicts.extend(res)
            except Exception as e:
                logger.error(f"Validator rule failed: {e}")
        return len(all_conflicts) == 0, all_conflicts

# Global Engine
engine = ValidationEngine()

def check_hardware_conflicts(context: Dict[str, Any]) -> Dict[str, Any]:
    is_valid, conflicts = engine.validate_hardware(context)
    return {
        "is_valid": is_valid,
        "conflicts": conflicts
    }

def classify_template_request(prompt: str) -> str:
    """
    Classifies a user prompt to determine if it is a basic driver setup request.
    Returns: LED_BLINK, UART_INIT, SPI_MASTER, I2C_MASTER, PWM_INIT, ADC_READ, TIMER_INIT, or None
    """
    prompt_low = prompt.lower()
    
    # 1. LED Blink / GPIO Toggle
    if "blink" in prompt_low or "toggle" in prompt_low:
        if any(w in prompt_low for w in ["led", "gpio", "pin"]):
            return "LED_BLINK"
            
    # 2. UART Init
    if "uart" in prompt_low or "usart" in prompt_low:
        if any(w in prompt_low for w in ["init", "setup", "configure", "hello", "write", "transmit"]):
            return "UART_INIT"
            
    # 3. SPI Master
    if "spi" in prompt_low:
        if any(w in prompt_low for w in ["init", "setup", "configure", "master", "transmit", "send"]):
            return "SPI_MASTER"
            
    # 4. I2C Master
    if "i2c" in prompt_low or "twi" in prompt_low:
        if any(w in prompt_low for w in ["init", "setup", "configure", "master"]):
            return "I2C_MASTER"
            
    # 5. PWM Configuration
    if "pwm" in prompt_low or "pulse width" in prompt_low:
        if any(w in prompt_low for w in ["init", "setup", "configure", "duty"]):
            return "PWM_INIT"
            
    # 6. ADC Read
    if "adc" in prompt_low or "analog read" in prompt_low:
        if any(w in prompt_low for w in ["init", "read", "sample"]):
            return "ADC_READ"
            
    # 7. Timer Init
    if "timer" in prompt_low:
        if any(w in prompt_low for w in ["init", "setup", "configure", "delay", "interrupt"]):
            return "TIMER_INIT"
            
    return None

import hashlib
import json

def calculate_hardware_hash(hc: Dict[str, Any]) -> str:
    """
    Computes a deterministic SHA-256 hash of the active hardware configurations.
    """
    gpios = sorted(hc.get("gpios", []), key=lambda x: x.get("pin", ""))
    peripherals = sorted(hc.get("peripherals", []), key=lambda x: x.get("name", ""))
    
    data = {
        "mcu": hc.get("mcu", "STM32F401"),
        "board": hc.get("board", "STM32F401 Nucleo-64"),
        "framework": hc.get("framework", "Bare Metal"),
        "compiler": hc.get("compiler", "GCC ARM"),
        "platformio_env": hc.get("platformio_env", "nucleo_f401re"),
        "clocks": hc.get("clocks", {}),
        "gpios": gpios,
        "peripherals": peripherals
    }
    
    serialized = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

def verify_functional_behavior(code: str, intent: str) -> List[str]:
    """
    Scans the generated firmware C code for capability-level hardware signatures.
    Returns list of validation failure descriptions, empty if compliant.
    """
    failures = []
    
    # 1. PWM Capability check
    if intent in ["PWM_FADE", "PWM_BRIGHTNESS", "SERVO_CONTROL"]:
        pwm_sigs = ["analogWrite", "ledcWrite", "ledcSetup", "HAL_TIM_PWM_Start", "TIM_OC", "OCR1A", "OCR1B", "OCR2A", "OCR2B", "TIM_HandleTypeDef"]
        if not any(sig in code for sig in pwm_sigs):
            failures.append(
                "Behavior Validation Error: Prompt requested PWM capability (fading/servo), but code only uses binary output. "
                "The C implementation must configure a Hardware Timer or PWM peripheral controller."
            )
            
    # 2. Toggle/Delay Capability check
    elif intent == "LED_BLINK":
        blink_sigs = ["delay", "HAL_Delay", "vTaskDelay", "sleep", "TogglePin", "Toggle", "toggle", "^="]
        if not any(sig in code for sig in blink_sigs):
            failures.append(
                "Behavior Validation Error: Blinking requested, but delay loops or toggling functions are missing."
            )
            
    # 3. Transceiver Serial Communication check
    elif intent == "UART_INIT":
        uart_sigs = ["Serial.begin", "HAL_UART_Init", "USART", "UBRR0", "uart_config", "uart_driver_install"]
        if not any(sig in code for sig in uart_sigs):
            failures.append(
                "Behavior Validation Error: UART transmission requested, but no transceiver setup signatures were found."
            )
            
    # 4. SPI bus controller check
    elif intent == "SPI_MASTER":
        spi_sigs = ["SPI.begin", "HAL_SPI_Init", "SPCR", "spi_bus_initialize", "SPI"]
        if not any(sig in code for sig in spi_sigs):
            failures.append(
                "Behavior Validation Error: SPI bus controller initialization or transaction functions are missing."
            )

    # 5. I2C controller check
    elif intent == "I2C_MASTER":
        i2c_sigs = ["Wire.begin", "HAL_I2C_Init", "TWCR", "i2c_driver_install", "I2C"]
        if not any(sig in code for sig in i2c_sigs):
            failures.append(
                "Behavior Validation Error: I2C interface initialization or transmission functions are missing."
            )

    # 6. Analog ADC check
    elif intent == "ADC_READ":
        adc_sigs = ["analogRead", "HAL_ADC_Start", "ADMUX", "adc1_get_raw", "ADC"]
        if not any(sig in code for sig in adc_sigs):
            failures.append(
                "Behavior Validation Error: ADC analog read conversion start or value sampling is missing."
            )

    return failures
