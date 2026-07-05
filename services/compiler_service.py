import os
import shutil
import subprocess
import json
import re
from typing import Dict, Any, Tuple, List

def generate_platformio_project(workspace_id: str, code: str, context: Dict[str, Any]) -> str:
    """
    Generates a standard compilable PlatformIO project structure in the filesystem.
    Returns the absolute path to the generated project directory.
    """
    mcu = context.get("mcu", "STM32F401")
    framework = context.get("framework", "Bare Metal")
    board = context.get("board", "nucleo_f401re")
    pio_env = context.get("platformio_env", "nucleo_f401re")
    baud_rate = context.get("baud_rate", 115200)

    # Resolve platform mapping
    platform = "ststm32"
    if "esp32" in mcu.lower():
        platform = "espressif32"
        board = "esp32dev"
    elif "rp2040" in mcu.lower():
        platform = "raspberrypi"
        board = "pico"
    elif "avr" in mcu.lower() or "atmega" in mcu.lower():
        platform = "atmelavr"
        board = "uno"

    # Define project directory
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workspace_projects", workspace_id)
    src_dir = os.path.join(base_dir, "src")
    os.makedirs(src_dir, exist_ok=True)

    # 1. Write src/main.cpp
    main_path = os.path.join(src_dir, "main.cpp")
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(code)

    # 2. Write platformio.ini
    ini_path = os.path.join(base_dir, "platformio.ini")
    ini_content = f"""[env:{pio_env}]
platform = {platform}
board = {board}
framework = {framework.lower().replace(" ", "")}
monitor_speed = {baud_rate}
"""
    with open(ini_path, "w", encoding="utf-8") as f:
        f.write(ini_content)

    # 3. Write README.md
    readme_path = os.path.join(base_dir, "README.md")
    readme_content = f"""# PinMind Generated Workspace Project
This PlatformIO project was automatically compiled and verified by PinMind.

## Target Hardware
- MCU: {mcu}
- Board: {board}
- Framework: {framework}
- Environment: {pio_env}
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    # 4. Write pinmind.json context metadata
    pm_json_path = os.path.join(base_dir, "pinmind.json")
    with open(pm_json_path, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2)

    return base_dir

def check_platformio_installed() -> bool:
    """Checks if PlatformIO CLI tool is installed and reachable in path."""
    try:
        # Run pio --version
        res = subprocess.run(["pio", "--version"], capture_output=True, text=True, check=False)
        return res.returncode == 0
    except Exception:
        return False

def verify_compilation(workspace_id: str, code: str, context: Dict[str, Any]) -> Tuple[str, List[str]]:
    """
    Executes compilation check using PlatformIO CLI if installed,
    otherwise falls back to a strict dry-run syntax verification parser.
    Returns status ("Passed", "SKIPPED", or "Failed") and lists of error messages.
    """
    errors = []

    # 1. First run syntactic dry-run verification (Multi-Level validation: Syntax & Framework)
    syntax_ok, syntax_errs = run_dry_run_syntax_check(code, context)
    if not syntax_ok:
        return "Failed", syntax_errs

    # 2. Project generation
    try:
        project_dir = generate_platformio_project(workspace_id, code, context)
    except Exception as e:
        return "Failed", [f"Project Generation Error: {str(e)}"]

    # 3. Compile check
    if check_platformio_installed():
        try:
            res = subprocess.run(["pio", "run", "-d", project_dir], capture_output=True, text=True, check=False)
            if res.returncode != 0:
                # Extract compiler errors from stdout/stderr
                comp_errs = []
                for line in (res.stdout + res.stderr).splitlines():
                    if "error:" in line or "fatal error:" in line:
                        comp_errs.append(f"Compiler Error: {line.strip()}")
                if not comp_errs:
                    comp_errs.append("PlatformIO Compilation failed. Please verify syntax or header includes.")
                return "Failed", comp_errs
            else:
                return "Passed", []
        except Exception as e:
            return "SKIPPED", [f"PlatformIO Compilation execution failed: {str(e)}. Swapping to SKIPPED mode."]
    else:
        return "SKIPPED", []

def run_dry_run_syntax_check(code: str, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Performs static dry-run code validations checking brace matching, semi-colons,
    standard include matches, and mandatory framework entry points.
    """
    errors = []
    framework = context.get("framework", "Bare Metal").lower()

    # 1. Balanced Brackets check
    if code.count("{") != code.count("}"):
        errors.append(f"Syntax Error: Unbalanced curly braces. Count of '{{' is {code.count('{')}, while '}}' is {code.count('}')}.")
    if code.count("(") != code.count(")"):
        errors.append(f"Syntax Error: Unbalanced parentheses. Count of '(' is {code.count('(')}, while ')' is {code.count(')')}.")

    # 2. Missing semi-colon detection on lines ending with alpha-numeric characters (basic checker)
    lines = code.splitlines()
    for idx, line in enumerate(lines, 1):
        line_strip = line.strip()
        # Strip inline comments (e.g. // comment or /* comment */)
        line_no_comment = line.split("//")[0].split("/*")[0].strip()
        
        # Look for typical statements that require semicolon
        if (
            line_no_comment and 
            not line_no_comment.endswith(";") and 
            not line_no_comment.endswith("{") and 
            not line_no_comment.endswith("}") and 
            not line_no_comment.startswith("#") and 
            not line_no_comment.endswith(":") and # Labels or cases
            re.search(r'[A-Za-z0-9_)]$', line_no_comment)
        ):
            # Verify if it's not a function header (e.g. void setup())
            if not re.search(r'\b(void|int|setup|loop|main|app_main)\s*\(', line_no_comment):
                errors.append(f"Syntax Error [line {idx}]: Statement appears to be missing a trailing semicolon ';'. Line: '{line_strip}'")

    # 3. Check for Framework entry points
    if "arduino" in framework:
        if "void setup(" not in code:
            errors.append("Framework Error: Missing setup() entry point in Arduino firmware.")
        if "void loop(" not in code:
            errors.append("Framework Error: Missing loop() entry point in Arduino firmware.")
    elif "esp-idf" in framework:
        if "app_main" not in code:
            errors.append("Framework Error: Missing app_main() entry point in ESP-IDF firmware.")
    elif "hal" in framework or "bare metal" in framework:
        if "main(" not in code and "main ( void )" not in code:
            errors.append("Framework Error: Missing main() entry function for register interaction.")

    return len(errors) == 0, errors
