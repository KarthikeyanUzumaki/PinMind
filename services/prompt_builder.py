from typing import Dict, Any

def build_copilot_prompt(user_prompt: str, recalled_memory: str, hardware_context: Dict[str, Any]) -> str:
    """
    Constructs a highly structured system prompt for Gemini based on user intent,
    recalled memory graph, and selected target Board / PlatformIO environment.
    """
    mcu = hardware_context.get("mcu", "STM32F401")
    framework = hardware_context.get("framework", "Bare Metal")
    compiler = hardware_context.get("compiler", "GCC ARM")
    board = hardware_context.get("board", "STM32F401 Nucleo")
    platformio_env = hardware_context.get("platformio_env", "nucleo_f401re")
    gpios = hardware_context.get("gpios", [])
    peripherals = hardware_context.get("peripherals", [])
    clocks = hardware_context.get("clocks", {})

    gpio_lines = []
    for g in gpios:
        gpio_lines.append(f"  - Pin {g.get('pin')}: {g.get('label')} ({g.get('mode', 'GPIO_Output')})")
    gpio_str = "\n".join(gpio_lines) if gpio_lines else "  - None configured"

    peri_lines = []
    for p in peripherals:
        dma_info = f", DMA Channel: {p.get('dma_channel')}" if p.get('dma_channel') else ""
        pins_info = f", Pins: {', '.join(p.get('pins', []))}" if p.get('pins') else ""
        peri_lines.append(f"  - {p.get('name')}{pins_info}{dma_info}")
    peri_str = "\n".join(peri_lines) if peri_lines else "  - None configured"

    clock_lines = []
    for k, v in clocks.items():
        clock_lines.append(f"  - {k}: {v} MHz")
    clock_str = "\n".join(clock_lines) if clock_lines else "  - None configured"

    # Define target-specific headers and requirements
    entry_point = "main(void)"
    if "Arduino" in framework:
        entry_point = "setup() and loop()"
    elif "ESP-IDF" in framework:
        entry_point = "app_main(void)"

    headers = []
    if "STM32" in mcu:
        if "HAL" in framework:
            headers = ["#include \"stm32f4xx_hal.h\"" if "G4" not in mcu else "#include \"stm32g4xx_hal.h\""]
        elif "LL" in framework:
            headers = ["#include \"stm32f4xx_ll_gpio.h\"", "#include \"stm32f4xx_ll_rcc.h\""]
        else:
            headers = ["#include \"stm32f4xx.h\"", "#include <stdint.h>"]
    elif "ESP32" in mcu:
        if "Arduino" in framework:
            headers = ["#include <Arduino.h>"]
        else:
            headers = ["#include <stdio.h>", "#include \"driver/gpio.h\"", "#include \"freertos/FreeRTOS.h\"", "#include \"freertos/task.h\""]
    elif "RP2040" in mcu:
        if "Pico SDK" in framework:
            headers = ["#include \"pico/stdlib.h\"", "#include \"hardware/gpio.h\""]
        else:
            headers = ["#include \"pico.h\"", "#include <stdint.h>"]
    elif "AVR" in mcu:
        headers = ["#include <avr/io.h>", "#include <util/delay.h>"]
    else:
        headers = ["#include <stdint.h>"]

    headers_str = "\n".join(headers)

    system_instruction = f"""You are a senior low-level firmware engineer. Write compilable C/C++ code for the {mcu} microcontroller.
Generate driver code according to the hardware description below.

=== TARGET HARDWARE ENVIRONMENT ===
MCU Model: {mcu}
Development Board: {board}
PlatformIO Env: {platformio_env}
Target Framework: {framework}
Compiler Toolchain: {compiler}

Clock Speed Configuration:
{clock_str}

GPIO Assignments:
{gpio_str}

Peripheral Attachments:
{peri_str}

=== COGNEE GRAPH RECALL MEMORY ===
{recalled_memory}

=== MANDATORY GENERATION RULES ===
1. STRICT FRAMEWORK COMPLIANCE:
   - For 'Arduino' framework: Generate ONLY `setup()` and `loop()`. Do NOT define `main()` or `app_main()`. Do NOT output any explanations regarding `main()`.
   - For 'ESP-IDF' framework: Generate `app_main(void)`. Do NOT define `main()`.
   - For 'Bare Metal' or other standard CMSIS frameworks: Generate `main(void)`.
2. NO CONVERSATIONAL FLUFF:
   - Do NOT provide tutorial-style explanations, instructions, or discussions outside the code block.
   - Return ONLY the clean, compilable code block.
   - Use concise inline engineering comments to explain registers or hardware configurations. No conversational introduction or conclusion.
3. REGISTER & PIN INTEGRITY:
   - Target compiler is {compiler}. Include precisely these headers at the top:
{headers_str}
   - Use symbolic CMSIS or framework macros (e.g., `GPIOA->MODER`, `PORTB`, `GPIO_PIN_5`) instead of magic register numbers or hardcoded hexadecimal offsets where possible.
   - Never mix framework conventions. Do NOT generate Arduino APIs inside ESP-IDF or Bare Metal projects.
4. NO MARKDOWN OR AI BANNERS:
   - Do NOT wrap the generated code inside markdown code blocks (do NOT use ```c or ```cpp backticks).
   - Do NOT include any markdown banners, title headers, or explanations.
   - Output only raw compilable source code lines directly.
"""
    return system_instruction
