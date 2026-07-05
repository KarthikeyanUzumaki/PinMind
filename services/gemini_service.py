import logging
import os
import re
from typing import Dict, Any

logger = logging.getLogger("pinmind.gemini")

def generate_simulated_firmware(prompt: str, context: Dict[str, Any]) -> str:
    """
    Template engine: renders parameterized source code based on MCU, framework, and classified intent.
    Injects extracted engineering parameters dynamically (e.g. custom intervals, baudrates).
    """
    mcu = context.get("mcu", "STM32F401")
    framework = context.get("framework", "Bare Metal")
    gpios = context.get("gpios", [])
    peripherals = context.get("peripherals", [])
    clocks = context.get("clocks", {})
    sysclk = clocks.get("sysclk_mhz", 84)

    # Classify intent to select the correct template
    from services.task_planner import plan_engineering_task
    plan = plan_engineering_task(prompt)
    intent = plan.intents[0] if plan.intents else "CUSTOM_DRIVER"
    params = plan.parameters
    
    # Resolve pins
    led_pins = [g for g in gpios if "led" in g.get("label", "").lower() or "status" in g.get("label", "").lower()]
    if not led_pins and gpios:
        led_pins = [gpios[0]]
    led_pin = led_pins[0].get("pin", "PA5") if led_pins else "PA5"
    led_label = led_pins[0].get("label", "STATUS_LED") if led_pins else "STATUS_LED"

    port_letter = "A"
    pin_num = "5"
    if "STM32" in mcu or "AVR" in mcu:
        m = re.match(r"^P([A-G])([0-9]+)$", led_pin)
        if m:
            port_letter = m.group(1)
            pin_num = m.group(2)
    elif "ESP32" in mcu:
        m = re.match(r"^GPIO([0-9]+)$", led_pin)
        if m:
            pin_num = m.group(1)
    elif "RP2040" in mcu:
        m = re.match(r"^GP([0-9]+)$", led_pin)
        if m:
            pin_num = m.group(1)

    # Extract engineering variables
    interval_ms = params.get("interval_ms", 500)
    baud_rate = params.get("baud_rate", 115200)
    res_bits = params.get("resolution_bits", 12)
    duty_pct = params.get("duty_cycle_pct") or params.get("brightness_pct") or 100
    duty_val = int((duty_pct / 100) * 255)

    out = f"/*\n * ==========================================================================\n"
    out += f" * PINMIND GENERATION ENGINE - PARAMETERIZED LOCAL TEMPLATE\n"
    out += f" * MCU: {mcu} | Framework: {framework} | Intent: {intent}\n"
    out += f" * Mapped Pin: {led_label} on {led_pin}\n"
    out += f" * Extracted Params: interval_ms={interval_ms}, baud_rate={baud_rate}, resolution={res_bits}-bit, duty={duty_pct}%\n"
    out += f" * ==========================================================================\n */\n\n"

    # Match intent templates
    if intent == "LED_BLINK":
        if "Arduino" in framework:
            out += f"""void setup() {{
  pinMode({pin_num}, OUTPUT);
}}

void loop() {{
  digitalWrite({pin_num}, HIGH);
  delay({interval_ms});
  digitalWrite({pin_num}, LOW);
  delay({interval_ms});
}}"""
        elif "ESP-IDF" in framework:
            out += f"""#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define BLINK_GPIO {pin_num}

void app_main(void) {{
    gpio_reset_pin(BLINK_GPIO);
    gpio_set_direction(BLINK_GPIO, GPIO_MODE_OUTPUT);
    while(1) {{
        gpio_set_level(BLINK_GPIO, 1);
        vTaskDelay({interval_ms} / portTICK_PERIOD_MS);
        gpio_set_level(BLINK_GPIO, 0);
        vTaskDelay({interval_ms} / portTICK_PERIOD_MS);
    }}
}}"""
        else: # HAL / STM32
            out += f"""#include "stm32f4xx_hal.h"

void SystemClock_Config(void);
static void MX_GPIO_Init(void);

int main(void) {{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    
    while (1) {{
        HAL_GPIO_TogglePin(GPIO{port_letter}, GPIO_PIN_{pin_num});
        HAL_Delay({interval_ms});
    }}
}}

static void MX_GPIO_Init(void) {{
    GPIO_InitTypeDef GPIO_InitStruct = {{0}};
    if (GPIO{port_letter} == GPIOA) __HAL_RCC_GPIOA_CLK_ENABLE();
    else if (GPIO{port_letter} == GPIOB) __HAL_RCC_GPIOB_CLK_ENABLE();
    
    HAL_GPIO_WritePin(GPIO{port_letter}, GPIO_PIN_{pin_num}, GPIO_PIN_RESET);
    GPIO_InitStruct.Pin = GPIO_PIN_{pin_num};
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIO{port_letter}, &GPIO_InitStruct);
}}"""

    elif intent == "LED_ON":
        if "Arduino" in framework:
            out += f"""void setup() {{
  pinMode({pin_num}, OUTPUT);
}}

void loop() {{
  digitalWrite({pin_num}, HIGH);
}}"""
        else:
            out += f"""#include "stm32f4xx_hal.h"
int main(void) {{
    HAL_Init();
    __HAL_RCC_GPIO{port_letter}_CLK_ENABLE();
    GPIO_InitTypeDef GPIO_InitStruct = {{0}};
    GPIO_InitStruct.Pin = GPIO_PIN_{pin_num};
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    HAL_GPIO_Init(GPIO{port_letter}, &GPIO_InitStruct);
    HAL_GPIO_WritePin(GPIO{port_letter}, GPIO_PIN_{pin_num}, GPIO_PIN_SET);
    while(1);
}}"""

    elif intent == "LED_OFF":
        if "Arduino" in framework:
            out += f"""void setup() {{
  pinMode({pin_num}, OUTPUT);
}}

void loop() {{
  digitalWrite({pin_num}, LOW);
}}"""
        else:
            out += f"""#include "stm32f4xx_hal.h"
int main(void) {{
    HAL_Init();
    __HAL_RCC_GPIO{port_letter}_CLK_ENABLE();
    GPIO_InitTypeDef GPIO_InitStruct = {{0}};
    GPIO_InitStruct.Pin = GPIO_PIN_{pin_num};
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    HAL_GPIO_Init(GPIO{port_letter}, &GPIO_InitStruct);
    HAL_GPIO_WritePin(GPIO{port_letter}, GPIO_PIN_{pin_num}, GPIO_PIN_RESET);
    while(1);
}}"""

    elif intent in ["PWM_FADE", "PWM_BRIGHTNESS"]:
        if "Arduino" in framework:
            if "esp32" in mcu.lower():
                out += f"""const int LED_PIN = {pin_num};
const int PWM_CHANNEL = 0;
const int PWM_FREQ = 5000;
const int PWM_RESOLUTION = 8;

void setup() {{
  ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(LED_PIN, PWM_CHANNEL);
  ledcWrite(PWM_CHANNEL, {duty_val}); // Set duty cycle
}}

void loop() {{
  // Parameterized fading / static brightness
  for (int duty = 0; duty <= {duty_val}; duty++) {{
    ledcWrite(PWM_CHANNEL, duty);
    delay(10);
  }}
  for (int duty = {duty_val}; duty >= 0; duty--) {{
    ledcWrite(PWM_CHANNEL, duty);
    delay(10);
  }}
}}"""
            else:
                out += f"""const int LED_PIN = {pin_num};

void setup() {{
  pinMode(LED_PIN, OUTPUT);
  analogWrite(LED_PIN, {duty_val});
}}

void loop() {{
  for (int val = 0; val <= {duty_val}; val++) {{
    analogWrite(LED_PIN, val);
    delay(10);
  }}
  for (int val = {duty_val}; val >= 0; val--) {{
    analogWrite(LED_PIN, val);
    delay(10);
  }}
}}"""
        else: # HAL PWM
            out += f"""#include "stm32f4xx_hal.h"
TIM_HandleTypeDef htim1;

void MX_TIM1_Init(void) {{
    __HAL_RCC_TIM1_CLK_ENABLE();
    TIM_OC_InitTypeDef sConfigOC = {{0}};
    htim1.Instance = TIM1;
    htim1.Init.Prescaler = 84 - 1;
    htim1.Init.Period = 255 - 1;
    HAL_TIM_PWM_Init(&htim1);
    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = {duty_val};
    HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_1);
}}

int main(void) {{
    HAL_Init();
    MX_TIM1_Init();
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
    uint32_t duty = 0;
    int dir = 1;
    while(1) {{
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, duty);
        duty += dir;
        if (duty >= {duty_val}) dir = -1;
        if (duty <= 0) dir = 1;
        HAL_Delay(10);
    }}
}}"""

    elif intent == "SERVO_CONTROL":
        if "Arduino" in framework:
            out += f"""#include <Servo.h>
Servo myservo;
const int SERVO_PIN = {pin_num};

void setup() {{
  myservo.attach(SERVO_PIN);
}}

void loop() {{
  for (int pos = 0; pos <= 180; pos += 1) {{
    myservo.write(pos);
    delay(15);
  }}
  for (int pos = 180; pos >= 0; pos -= 1) {{
    myservo.write(pos);
    delay(15);
  }}
}}"""
        else:
            out += f"""#include "stm32f4xx_hal.h"
TIM_HandleTypeDef htim2;

void MX_TIM2_Init(void) {{
    __HAL_RCC_TIM2_CLK_ENABLE();
    TIM_OC_InitTypeDef sConfigOC = {{0}};
    htim2.Instance = TIM2;
    htim2.Init.Prescaler = 1680 - 1; // 50Hz clock
    htim2.Init.Period = 1000 - 1;
    HAL_TIM_PWM_Init(&htim2);
    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = 50; // Neutral 1.5ms pulse
    HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_1);
}}

int main(void) {{
    HAL_Init();
    MX_TIM2_Init();
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
    while(1) {{
        __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, 50); // 0 degrees
        HAL_Delay(1000);
        __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, 100); // 180 degrees
        HAL_Delay(1000);
    }}
}}"""

    elif intent == "UART_INIT":
        out += f"""#include "stm32f4xx_hal.h"
UART_HandleTypeDef huart2;

void MX_USART2_UART_Init(void) {{
    __HAL_RCC_USART2_CLK_ENABLE();
    huart2.Instance = USART2;
    huart2.Init.BaudRate = {baud_rate};
    huart2.Init.WordLength = UART_WORDLENGTH_8B;
    huart2.Init.StopBits = UART_STOPBITS_1;
    huart2.Init.Parity = UART_PARITY_NONE;
    huart2.Init.Mode = UART_MODE_TX_RX;
    HAL_UART_Init(&huart2);
}}

int main(void) {{
    HAL_Init();
    MX_USART2_UART_Init();
    char msg[] = "UART Initialized @ {baud_rate}\\r\\n";
    while(1) {{
        HAL_UART_Transmit(&huart2, (uint8_t*)msg, sizeof(msg)-1, 100);
        HAL_Delay(1000);
    }}
}}"""

    elif intent == "SPI_MASTER":
        out += f"""#include "stm32f4xx_hal.h"
SPI_HandleTypeDef hspi1;

void MX_SPI1_Init(void) {{
    __HAL_RCC_SPI1_CLK_ENABLE();
    hspi1.Instance = SPI1;
    hspi1.Init.Mode = SPI_MODE_MASTER;
    hspi1.Init.Direction = SPI_DIRECTION_2LINES;
    hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
    hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
    hspi1.Init.NSS = SPI_NSS_SOFT;
    HAL_SPI_Init(&hspi1);
}}

int main(void) {{
    HAL_Init();
    MX_SPI1_Init();
    uint8_t tx_data = 0xAA;
    uint8_t rx_data = 0x00;
    while(1) {{
        HAL_SPI_TransmitReceive(&hspi1, &tx_data, &rx_data, 1, 100);
        HAL_Delay(500);
    }}
}}"""

    elif intent == "I2C_MASTER":
        out += f"""#include "stm32f4xx_hal.h"
I2C_HandleTypeDef hi2c1;

void MX_I2C1_Init(void) {{
    __HAL_RCC_I2C1_CLK_ENABLE();
    hi2c1.Instance = I2C1;
    hi2c1.Init.ClockSpeed = 100000;
    hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
    hi2c1.Init.OwnAddress1 = 0;
    hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
    HAL_I2C_Init(&hi2c1);
}}

int main(void) {{
    HAL_Init();
    MX_I2C1_Init();
    uint8_t buf[2] = {{0x01, 0x02}};
    while(1) {{
        HAL_I2C_Master_Transmit(&hi2c1, 0x50 << 1, buf, 2, 100);
        HAL_Delay(500);
    }}
}}"""

    elif intent == "ADC_READ":
        if "Arduino" in framework:
            out += f"""const int POT_PIN = {pin_num};
int val = 0;

void setup() {{
  Serial.begin(115200);
  pinMode(POT_PIN, INPUT);
  analogReadResolution({res_bits}); // Set extracted resolution
}}

void loop() {{
  val = analogRead(POT_PIN);
  Serial.println(val);
  delay(100);
}}"""
        else:
            out += f"""#include "stm32f4xx_hal.h"
ADC_HandleTypeDef hadc1;

void MX_ADC1_Init(void) {{
    __HAL_RCC_ADC1_CLK_ENABLE();
    ADC_ChannelConfTypeDef sConfig = {{0}};
    hadc1.Instance = ADC1;
    HAL_ADC_Init(&hadc1);
    sConfig.Channel = ADC_CHANNEL_1;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_3CYCLES;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);
}}

int main(void) {{
    HAL_Init();
    MX_ADC1_Init();
    uint32_t adc_val = 0;
    while(1) {{
        HAL_ADC_Start(&hadc1);
        if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {{
            adc_val = HAL_ADC_GetValue(&hadc1);
        }}
        HAL_ADC_Stop(&hadc1);
        HAL_Delay(100);
    }}
}}"""
    else:
        out += f"""// Stub code for Custom Engineering Driver
void setup() {{
    // Custom logic
}}
void loop() {{
    // Custom loop
}}"""

    return out

async def generate_firmware_code(prompt: str, system_instruction: str, hardware_context: Dict[str, Any], user_api_key: str = None) -> str:
    """
    Calls the Google Gemini API to generate the code block,
    or falls back to Simulation Mode if no API key is present.
    """
    api_key = user_api_key or os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        logger.info("No Gemini API key resolved. Running in Simulation Mode.")
        return generate_simulated_firmware(prompt, hardware_context)
        
    try:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=system_instruction
            )
            response = await model.generate_content_async(prompt)
            return response.text
        except ImportError:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            return response.text
    except Exception as e:
        logger.error(f"Gemini API execution failed: {e}. Falling back to simulation.")
        return f"// [Warning] Gemini API call failed: {str(e)}\n// Falling back to Simulation Mode.\n\n" + generate_simulated_firmware(prompt, hardware_context)
