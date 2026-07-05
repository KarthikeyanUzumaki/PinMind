import re
import json
import os
from typing import Dict, Any, List, Optional

PLANNER_VERSION = "v3.2"

class EngineeringTask:
    def __init__(self, name: str, description: str, required_peripheral: str, required_capabilities: List[str]):
        self.name = name
        self.description = description
        self.required_peripheral = required_peripheral
        self.required_capabilities = required_capabilities

class IntentRegistry:
    def __init__(self):
        self.tasks: Dict[str, EngineeringTask] = {}
        
    def register(self, task: EngineeringTask):
        self.tasks[task.name] = task

    def get(self, name: str) -> Optional[EngineeringTask]:
        return self.tasks.get(name)

# Create registry instance and register standard firmware tasks
registry = IntentRegistry()
registry.register(EngineeringTask("LED_BLINK", "Toggle GPIO output periodically", "GPIO", ["GPIO_OUT", "GPIO_TOGGLE", "DELAY"]))
registry.register(EngineeringTask("LED_ON", "Set GPIO output HIGH", "GPIO", ["GPIO_OUT", "SET_HIGH"]))
registry.register(EngineeringTask("LED_OFF", "Set GPIO output LOW", "GPIO", ["GPIO_OUT", "SET_LOW"]))
registry.register(EngineeringTask("PWM_FADE", "Breathing / fading duty cycle using timer PWM", "PWM", ["PWM_CONFIG", "DUTY_CYCLE_CONTROL"]))
registry.register(EngineeringTask("PWM_BRIGHTNESS", "Set PWM duty cycle to fixed brightness", "PWM", ["PWM_CONFIG", "DUTY_CYCLE_WRITE"]))
registry.register(EngineeringTask("SERVO_CONTROL", "PWM servo control angle positioning", "PWM", ["PWM_CONFIG", "PERIOD_20MS", "DUTY_CYCLE_ANGLE"]))
registry.register(EngineeringTask("UART_INIT", "Setup transceiver baudrate and write/read bytes", "UART", ["TX_RX_CONFIG", "BAUDRATE_SELECT", "TRANS_CHAR"]))
registry.register(EngineeringTask("SPI_MASTER", "SPI hardware bus master configuration", "SPI", ["SPI_MASTER_CONFIG", "DATA_TRANSFER"]))
registry.register(EngineeringTask("I2C_MASTER", "I2C master bus address configuration", "I2C", ["I2C_MASTER_INIT", "ADDRESS_SEND"]))
registry.register(EngineeringTask("ADC_READ", "Read analog value converter", "ADC", ["ADC_CHANNEL_SEL", "SAMPLE_HOLD", "READ_VAL"]))

# Prompt Normalization Rules
class NormalizationRule:
    def __init__(self, patterns: List[str], normalized: str):
        self.patterns = patterns
        self.normalized = normalized

NORMALIZATION_RULES = [
    NormalizationRule(["flash", "toggle", "pulse", "heartbeat"], "blink"),
    NormalizationRule(["breathing", "dim", "glow", "gradual"], "fade"),
    NormalizationRule(["intensity", "duty cycle", "dutycycle"], "brightness"),
    NormalizationRule(["transmit", "print", "send", "write", "serial", "usart"], "uart"),
    NormalizationRule(["motor", "angle", "sweep"], "servo"),
    NormalizationRule(["analog read", "read analog", "potentiometer", "sensor value"], "adc"),
]

def normalize_prompt(prompt: str) -> str:
    normalized = prompt.lower()
    for rule in NORMALIZATION_RULES:
        for p in rule.patterns:
            normalized = re.sub(r'\b' + re.escape(p) + r'\b', rule.normalized, normalized)
    return normalized

def extract_engineering_parameters(prompt: str) -> Dict[str, Any]:
    """
    Parses user prompt using regex rules to extract engineering attributes.
    """
    params = {}
    prompt_low = prompt.lower()

    # 1. Baud rate
    baud_match = re.search(r'\b(9600|19200|38400|57600|115200|921600)\b', prompt_low)
    if baud_match:
        params["baud_rate"] = int(baud_match.group(1))
    else:
        baud_match_2 = re.search(r'(\d+)\s*(?:baud|bps)', prompt_low)
        if baud_match_2:
            params["baud_rate"] = int(baud_match_2.group(1))

    # 2. Interval / Delay (Normalize to milliseconds)
    delay_match = re.search(r'(\d+(?:\.\d+)?)\s*(seconds?|sec?s?|milliseconds?|ms|minutes?|min?s?|m)\b', prompt_low)
    if delay_match:
        value = float(delay_match.group(1))
        unit = delay_match.group(2).lower()
        if unit.startswith("second") or unit.startswith("sec") or unit == "s":
            params["interval_ms"] = int(value * 1000)
        elif unit.startswith("minute") or unit.startswith("min") or unit == "m":
            params["interval_ms"] = int(value * 60000)
        else:
            params["interval_ms"] = int(value)

    # 3. Duty cycle / Brightness
    duty_match = re.search(r'(\d+)\s*(?:%|percent)', prompt_low)
    if duty_match:
        params["duty_cycle_pct"] = int(duty_match.group(1))
    else:
        brightness_match = re.search(r'brightness\s*(?:of|at)?\s*(\d+)', prompt_low)
        if brightness_match:
            params["brightness_pct"] = int(brightness_match.group(1))

    # 4. Frequency
    freq_match = re.search(r'(\d+(?:\.\d+)?)\s*(khz|hz|mhz)', prompt_low)
    if freq_match:
        val = float(freq_match.group(1))
        unit = freq_match.group(2)
        if unit == "khz":
            params["frequency_hz"] = int(val * 1000)
        elif unit == "mhz":
            params["frequency_hz"] = int(val * 1000000)
        else:
            params["frequency_hz"] = int(val)

    # 5. ADC/DAC Resolution
    res_match = re.search(r'(\d+)\s*(?:-| )?bit', prompt_low)
    if res_match:
        params["resolution_bits"] = int(res_match.group(1))

    # 6. Hardware Timer ID
    timer_match = re.search(r'\b(?:timer|tim)\s*([0-9]+)\b', prompt_low)
    if timer_match:
        params["timer_id"] = int(timer_match.group(1))

    # 7. Interrupt / DMA attributes
    if any(w in prompt_low for w in ["interrupt", "isr", "callback"]):
        params["use_interrupt"] = True
    if "dma" in prompt_low:
        params["use_dma"] = True

    return params

class EngineeringPlan:
    def __init__(
        self,
        raw_prompt: str,
        normalized_prompt: str,
        intents: List[str],
        parameters: Dict[str, Any],
        complexity: str,
        generation_strategy: str,
        confidence: float,
        planner_version: str,
        required_peripheral: str,
        required_capabilities: List[str]
    ):
        self.raw_prompt = raw_prompt
        self.normalized_prompt = normalized_prompt
        self.intents = intents
        self.parameters = parameters
        self.complexity = complexity
        self.generation_strategy = generation_strategy
        self.confidence = confidence
        self.planner_version = planner_version
        self.required_peripheral = required_peripheral
        self.required_capabilities = required_capabilities

def plan_engineering_task(prompt: str, framework: str = "Bare Metal") -> EngineeringPlan:
    """
    Core Task Planner: normalizes prompt, extracts parameters, detects multiple intents,
    checks complexity level, and assigns generation strategies.
    """
    normalized = normalize_prompt(prompt)
    params = extract_engineering_parameters(prompt)
    
    # Match registry intents
    intents = []
    if "blink" in normalized:
        intents.append("LED_BLINK")
    if "led" in normalized and "on" in normalized and "blink" not in normalized:
        intents.append("LED_ON")
    if "led" in normalized and "off" in normalized and "blink" not in normalized:
        intents.append("LED_OFF")
    if "fade" in normalized:
        intents.append("PWM_FADE")
    if "brightness" in normalized and "fade" not in normalized:
        intents.append("PWM_BRIGHTNESS")
    if "servo" in normalized:
        intents.append("SERVO_CONTROL")
    if "uart" in normalized or "serial" in normalized:
        intents.append("UART_INIT")
    if "spi" in normalized:
        intents.append("SPI_MASTER")
    if "i2c" in normalized:
        intents.append("I2C_MASTER")
    if "adc" in normalized:
        intents.append("ADC_READ")

    if not intents:
        intents = ["CUSTOM_DRIVER"]

    # Retrieve required peripheral capability constraints
    primary_intent = intents[0]
    task_def = registry.get(primary_intent)
    if task_def:
        req_peripheral = task_def.required_peripheral
        req_capabilities = task_def.required_capabilities
        confidence = 0.95
    else:
        req_peripheral = "GPIO"
        req_capabilities = []
        confidence = 0.50

    # Complexity mapping
    if len(intents) >= 3 or params.get("use_dma") or params.get("use_interrupt"):
        complexity = "Complex"
    elif len(intents) == 2 or len(params) >= 3:
        complexity = "Medium"
    else:
        complexity = "Simple"

    # Generation strategy resolver (Framework Aware)
    # Always route standard simple/medium intents to Parameterized Templates to minimize LLM reliance
    standard_intents = ["LED_BLINK", "LED_ON", "LED_OFF", "PWM_FADE", "PWM_BRIGHTNESS", "SERVO_CONTROL", "UART_INIT", "SPI_MASTER", "I2C_MASTER", "ADC_READ"]
    if primary_intent in standard_intents and complexity != "Complex":
        strategy = "PARAMETERIZED_TEMPLATE"
    elif complexity == "Complex":
        strategy = "LLM"
    else:
        strategy = "HYBRID"

    return EngineeringPlan(
        raw_prompt=prompt,
        normalized_prompt=normalized,
        intents=intents,
        parameters=params,
        complexity=complexity,
        generation_strategy=strategy,
        confidence=confidence,
        planner_version=PLANNER_VERSION,
        required_peripheral=req_peripheral,
        required_capabilities=req_capabilities
    )

def load_hardware_rules(mcu: str) -> Dict[str, Any]:
    """
    Loads JSON specifications from hardware_db matching active MCU target.
    """
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "hardware_db")
    filename = "stm32f401.json"
    mcu_low = mcu.lower()
    if "esp32" in mcu_low:
        filename = "esp32.json"
    elif "stm32f411" in mcu_low:
        filename = "stm32f411.json"
    elif "stm32f407" in mcu_low:
        filename = "stm32f407.json"
        
    path = os.path.join(db_dir, filename)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def load_framework_rules(framework: str) -> Dict[str, Any]:
    """
    Loads framework specifications from framework_db matching active framework target.
    """
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "framework_db")
    filename = "cmsis.json"
    fw_low = framework.lower()
    if "arduino" in fw_low:
        filename = "arduino.json"
    elif "esp-idf" in fw_low:
        filename = "espidf.json"
    elif "hal" in fw_low or "stm32" in fw_low:
        filename = "stm32hal.json"
        
    path = os.path.join(db_dir, filename)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def verify_peripheral_requirements(plan: EngineeringPlan, context: Dict[str, Any]) -> Optional[str]:
    """
    Pre-validates that active hardware context can satisfy requested engineering plan features.
    Enforces hardware restrictions (e.g. ESP32 input-only pins).
    """
    mcu = context.get("mcu", "STM32F401")
    gpios = context.get("gpios", [])
    peripherals = context.get("peripherals", [])
    rules = load_hardware_rules(mcu)

    # 1. Reject input-only pins for output tasks (e.g. GPIO34, 35, 36, 39 on ESP32)
    output_intents = ["LED_BLINK", "LED_ON", "LED_OFF", "PWM_FADE", "PWM_BRIGHTNESS", "SERVO_CONTROL"]
    if any(intent in output_intents for intent in plan.intents):
        for g in gpios:
            pin_name = g.get("pin", "")
            # Check ESP32 input-only constraints
            if "esp32" in mcu.lower() and pin_name in ["GPIO34", "GPIO35", "GPIO36", "GPIO39"]:
                return f"GPIO Pin {pin_name} is input-only on {mcu} (lacks output driver registers) and cannot be used for output task '{plan.intents[0]}'. Please re-assign to an output-capable pin."

    # 2. GPIO Requirements
    if plan.required_peripheral == "GPIO":
        output_gpios = [g for g in gpios if g.get("mode") == "GPIO_Output" or "led" in g.get("label", "").lower()]
        if not output_gpios:
            return "No GPIO Output pin configured in this workspace. Please add a GPIO pin with mode 'GPIO_Output' or label 'LED' in the configuration panel first."

    # 3. PWM Requirements
    elif plan.required_peripheral == "PWM":
        pwm_gpios = [g for g in gpios if g.get("mode") in ["GPIO_Output", "PWM"] or "led" in g.get("label", "").lower()]
        if not pwm_gpios:
            return "No PWM / Output GPIO configured in this workspace. Fading or motor controls require at least one output pin."
        
        # Check specific pin compatibility from Rules Engine
        supported_pwm = rules.get("supported_pwm_pins")
        if supported_pwm:
            active_pin = pwm_gpios[0].get("pin")
            clean_pin = active_pin
            if "esp32" in mcu.lower() and active_pin.startswith("GPIO"):
                try:
                    clean_pin = int(active_pin.replace("GPIO", ""))
                except ValueError:
                    pass
            
            if clean_pin not in supported_pwm:
                return f"Selected pin {active_pin} is not wired to a hardware Timer channel on {mcu}. Supported PWM pins are: {supported_pwm}"

    # 4. ADC Requirements
    elif plan.required_peripheral == "ADC":
        adc_gpios = [g for g in gpios if g.get("mode") == "Analog" or "adc" in g.get("label", "").lower()]
        if not adc_gpios:
            return "No Analog input pin configured in this workspace. ADC operations require a GPIO pin with mode 'Analog'."
        
        # Check rule compatibility
        supported_adc = rules.get("supported_adc_pins")
        if supported_adc:
            active_pin = adc_gpios[0].get("pin")
            clean_pin = active_pin
            if "esp32" in mcu.lower() and active_pin.startswith("GPIO"):
                try:
                    clean_pin = int(active_pin.replace("GPIO", ""))
                except ValueError:
                    pass
            if clean_pin not in supported_adc:
                return f"Selected pin {active_pin} does not support ADC conversion on {mcu}. Supported ADC pins are: {supported_adc}"

    # 5. Bus Peripherals (UART, SPI, I2C)
    elif plan.required_peripheral in ["UART", "SPI", "I2C"]:
        matching_periphs = [p for p in peripherals if plan.required_peripheral in p.get("name", "").upper()]
        if not matching_periphs:
            return f"Required hardware peripheral '{plan.required_peripheral}' is not configured. Please add the {plan.required_peripheral} peripheral block under peripherals first."

    return None
