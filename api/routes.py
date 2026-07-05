import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

# Import schemas and database session connection
from models import schemas
from database import models
from database.connection import get_db

# Import Firebase ID Token dependency
from services.auth_service import get_current_user

# Import services
from services.cognee_service import save_hardware_context, recall_hardware_context, delete_workspace_memory
from services.validation_service import check_hardware_conflicts, post_validate_registers, analyze_static_code, calculate_hardware_hash, classify_template_request
from services.prompt_builder import build_copilot_prompt
from services.graph_service import build_graph_payload
from services.gemini_service import generate_firmware_code

logger = logging.getLogger("pinmind.api")

router = APIRouter()

def ensure_db_user_exists(db: Session, current_user: dict) -> models.User:
    """Helper to upsert users into db upon first connection."""
    user = db.query(models.User).filter_by(uid=current_user["uid"]).first()
    if not user:
        user = models.User(
            uid=current_user["uid"],
            email=current_user["email"],
            name=current_user["name"],
            avatar_url=current_user["avatar_url"]
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.get("/api/workspaces")
async def get_user_workspaces(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    """
    Returns only the workspaces owned by the authenticated user.
    """
    ensure_db_user_exists(db, current_user)
    workspaces = db.query(models.Workspace).filter_by(user_id=current_user["uid"]).order_by(models.Workspace.created_at.desc()).all()
    
    # Return mapping lists
    return [{"id": w.id, "name": w.name} for w in workspaces]

@router.get("/api/hardware")
async def get_hardware_context(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns the persisted hardware context for a workspace.
    """
    ensure_db_user_exists(db, current_user)
    workspace = db.query(models.Workspace).filter_by(id=workspace_id, user_id=current_user["uid"]).first()
    if not workspace:
        raise HTTPException(status_code=403, detail="Workspace access forbidden.")
        
    hc = db.query(models.HardwareContext).filter_by(workspace_id=workspace_id).first()
    if not hc:
        return {
            "mcu": "STM32F401",
            "framework": "Bare Metal",
            "compiler": "GCC ARM",
            "board": "STM32F401 Nucleo",
            "platformio_env": "nucleo_f401re",
            "clocks": {"sysclk_mhz": 84, "apb1_mhz": 42, "apb2_mhz": 84},
            "gpios": [],
            "peripherals": []
        }
    return {
        "mcu": hc.mcu,
        "framework": hc.framework,
        "compiler": hc.compiler,
        "board": hc.board,
        "platformio_env": hc.platformio_env,
        "clocks": hc.clocks,
        "gpios": hc.gpios,
        "peripherals": hc.peripherals
    }

@router.post("/api/hardware/save")
async def save_hardware(
    data: schemas.HardwareContext,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Persists configuration data in Supabase PostgreSQL and updates the Cognee Graph.
    """
    try:
        ensure_db_user_exists(db, current_user)
        
        # 1. Verify or create workspace ownership
        workspace = db.query(models.Workspace).filter_by(id=data.workspace_id, user_id=current_user["uid"]).first()
        if not workspace:
            workspace = models.Workspace(
                id=data.workspace_id,
                user_id=current_user["uid"],
                name=data.workspace_id.replace("_", " ").title()
            )
            db.add(workspace)
            db.commit()
            db.refresh(workspace)
            
        # 2. Upsert Hardware Context
        hc = db.query(models.HardwareContext).filter_by(workspace_id=workspace.id).first()
        clocks_dict = data.clocks.dict()
        gpios_list = [g.dict() for g in data.gpios]
        peris_list = [p.dict() for p in data.peripherals]
        
        if not hc:
            hc = models.HardwareContext(
                workspace_id=workspace.id,
                mcu=data.mcu,
                framework=data.framework,
                compiler=data.compiler,
                board=data.board,
                platformio_env=data.platformio_env,
                clocks=clocks_dict,
                gpios=gpios_list,
                peripherals=peris_list
            )
            db.add(hc)
        else:
            hc.mcu = data.mcu
            hc.framework = data.framework
            hc.compiler = data.compiler
            hc.board = data.board
            hc.platformio_env = data.platformio_env
            hc.clocks = clocks_dict
            hc.gpios = gpios_list
            hc.peripherals = peris_list
        db.commit()
        
        # 3. Format context string to save to Cognee
        gpios_summary = ", ".join([f"{g['pin']}={g['label']}({g['mode']})" for g in gpios_list])
        peris_summary = ", ".join([f"{p['name']} on pins {p['pins']}" for p in peris_list])
        clocks_summary = f"SYSCLK={clocks_dict['sysclk_mhz']}MHz, APB1={clocks_dict['apb1_mhz']}MHz, APB2={clocks_dict['apb2_mhz']}MHz"
        
        raw_hardware_text = (
            f"MCU Model: {data.mcu}\n"
            f"GPIO Assignments: {gpios_summary}\n"
            f"Peripherals: {peris_summary}\n"
            f"Clocks: {clocks_summary}"
        )
        
        # Synchronize Cognee graph engine
        cognee_res = await save_hardware_context(workspace.id, raw_hardware_text)
        cognee_status = "success" if cognee_res["status"] == "success" else "offline_mode"
        
        return {
            "status": "success",
            "message": "Hardware context saved and memorized.",
            "cognee_status": cognee_status
        }
    except Exception as e:
        logger.error(f"Failed to synchronize database state: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Write Failure: {str(e)}")

@router.get("/api/memory")
async def get_memory(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieves the memory graph built from database configs.
    """
    ensure_db_user_exists(db, current_user)
    
    # Verify workspace ownership
    workspace = db.query(models.Workspace).filter_by(id=workspace_id, user_id=current_user["uid"]).first()
    if not workspace:
        return {"nodes": [], "edges": []}
        
    hc = db.query(models.HardwareContext).filter_by(workspace_id=workspace_id).first()
    if not hc:
        return {"nodes": [], "edges": []}
        
    # Build graph visualization model
    context_dict = {
        "mcu": hc.mcu,
        "clocks": hc.clocks,
        "gpios": hc.gpios,
        "peripherals": hc.peripherals
    }
    return build_graph_payload(context_dict)

@router.get("/api/chats")
async def get_chat_history(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns historical chat sessions log.
    """
    ensure_db_user_exists(db, current_user)
    
    # Verify ownership
    workspace = db.query(models.Workspace).filter_by(id=workspace_id, user_id=current_user["uid"]).first()
    if not workspace:
        raise HTTPException(status_code=403, detail="Workspace access forbidden.")
        
    chats = db.query(models.ChatHistory).filter_by(workspace_id=workspace_id).order_by(models.ChatHistory.created_at.asc()).all()
    return [{"role": c.role, "content": c.content, "metadata": c.metadata_json} for c in chats]

@router.post("/api/chat")
async def chat_assistant(
    request: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Verifies rules, recall context from Cognee memory, invokes Gemini, and logs conversations.
    """
    ensure_db_user_exists(db, current_user)
    
    workspace = db.query(models.Workspace).filter_by(id=request.workspace_id, user_id=current_user["uid"]).first()
    if not workspace:
        raise HTTPException(status_code=403, detail="Workspace access forbidden.")
        
    hc = db.query(models.HardwareContext).filter_by(workspace_id=workspace.id).first()
    if not hc:
        raise HTTPException(status_code=404, detail="Please sync hardware configuration before chatting.")
        
    logs = ["Loaded configuration details from Supabase."]
    
    # 1. Direct Constraint Validations
    context_dict = {
        "mcu": hc.mcu,
        "framework": hc.framework,
        "compiler": hc.compiler,
        "board": hc.board,
        "platformio_env": hc.platformio_env,
        "clocks": hc.clocks,
        "gpios": hc.gpios,
        "peripherals": hc.peripherals
    }
    validation_res = check_hardware_conflicts(context_dict)
    
    # Log User Prompt to chat history database
    user_chat = models.ChatHistory(workspace_id=workspace.id, role="user", content=request.prompt)
    db.add(user_chat)
    db.commit()

    if not validation_res["is_valid"]:
        logs.append("Physical conflict detected by local validation rules engine.")
        
        # Build conflict message block
        conflict_msg = "/*\n * CONFLICT DETECTED - PIPELINE HALTED\n"
        conflict_msg += " * The validation engine detected hardware allocation overlaps.\n"
        conflict_msg += " * ==========================================================\n"
        for conf in validation_res["conflicts"]:
            conflict_msg += f" * [{conf['type']}] On Resource: {conf['resource']}\n"
            conflict_msg += f" * Message: {conf['message']}\n"
            conflict_msg += " * Possible Solutions:\n"
            for sol in conf["solutions"]:
                conflict_msg += f" *   - {sol}\n"
                conflict_msg += " * ----------------------------------------------------------\n"
        conflict_msg += " */"
        
        # Save conflict block to database
        system_chat = models.ChatHistory(workspace_id=workspace.id, role="system", content=conflict_msg)
        db.add(system_chat)
        db.commit()
        
        return {
            "response": conflict_msg,
            "logs": logs,
            "has_conflict": True,
            "conflicts": validation_res["conflicts"]
        }
        
    logs.append("No hardware assignment conflicts found. Initializing Engineering Task Planner...")

    # 1. Engineering Task Planner & Peripheral Context Checks
    from services.task_planner import plan_engineering_task, verify_peripheral_requirements
    from services.validation_service import verify_functional_behavior
    
    # Run the V3.2 Task Planner (incorporating framework awareness)
    plan = plan_engineering_task(request.prompt, framework=context_dict["framework"])
    logs.append(f"Task Planner ({plan.planner_version}): Classified intents as {plan.intents} requiring peripheral '{plan.required_peripheral}' with capabilities: {plan.required_capabilities}. Complexity: {plan.complexity}. Strategy: {plan.generation_strategy}. Confidence: {plan.confidence}")
    
    # Run prompt context validation (includes input-only pin checking)
    context_error = verify_peripheral_requirements(plan, context_dict)
    if context_error:
        logs.append(f"Prompt Context Validation Failed: {context_error}")
        
        error_msg = "/*\n * HARDWARE REQUIREMENT MISMATCH - PIPELINE HALTED\n"
        error_msg += f" * Intent(s): {', '.join(plan.intents)}\n"
        error_msg += f" * Required Peripheral: {plan.required_peripheral}\n"
        error_msg += f" * Error: {context_error}\n"
        error_msg += " * Suggested Fix: Please configure the required pin assignments in the configuration panel first.\n"
        error_msg += " */"
        
        system_chat = models.ChatHistory(workspace_id=workspace.id, role="system", content=error_msg)
        db.add(system_chat)
        db.commit()
        
        return {
            "response": error_msg,
            "logs": logs,
            "has_conflict": True,
            "conflicts": [{"type": "Peripheral Mismatch", "resource": plan.required_peripheral, "message": context_error, "solutions": ["Configure Pin/Peripheral"]}]
        }

    # Calculate Hardware Context Hash
    current_hash = calculate_hardware_hash(context_dict)

    # Compile structured "Why This Code?" explanations
    why_explanations = [
        f"Microcontroller target {context_dict['mcu']} ({context_dict['board']}) configured.",
        f"Framework '{context_dict['framework']}' with PlatformIO Environment '{context_dict['platformio_env']}' is active.",
    ]
    if context_dict["gpios"]:
        why_explanations.append("Active GPIO Maps: " + ", ".join([f"{g['pin']} mapped to {g['label']} ({g['mode']})" for g in context_dict["gpios"]]))
    else:
        why_explanations.append("No active GPIO mappings were defined in the configuration panel.")
        
    if "Arduino" in context_dict["framework"]:
        why_explanations.append("Only setup() and loop() functions are generated because Arduino manages the main() entry point internally.")
    elif "ESP-IDF" in context_dict["framework"]:
        why_explanations.append("app_main() is generated as the primary FreeRTOS task entry point for ESP-IDF.")
    else:
        why_explanations.append("Standard main() entry loop is generated for CMSIS bare-metal register interaction.")

    # A. Routing to Template Generation (if strategy matches)
    if plan.generation_strategy == "PARAMETERIZED_TEMPLATE":
        logs.append(f"Task Planner: Routing to local Parameterized Template Engine.")
        from services.gemini_service import generate_simulated_firmware
        response_text = generate_simulated_firmware(request.prompt, context_dict)
        
        # Multi-level validation checks
        framework_errors = analyze_static_code(response_text, context_dict)
        register_errors = post_validate_registers(response_text, context_dict["mcu"])
        behavior_errors = verify_functional_behavior(response_text, plan.intents[0] if plan.intents else "")
        
        # Run compilation check
        from services.compiler_service import verify_compilation
        comp_status, comp_errors = verify_compilation(workspace.id, response_text, context_dict)
        all_errors = framework_errors + register_errors + behavior_errors + comp_errors
        
        validation_report = {
            "quality_report": {
                "hardware_context": "Passed" if not any("GPIO" in e or "Pin" in e for e in all_errors) else "Failed",
                "framework": "Passed" if not framework_errors else "Failed",
                "behavior": "Passed" if not behavior_errors else "Failed",
                "registers": "Passed" if not register_errors else "Failed",
                "compilation": comp_status,
                "source": "Template"
            },
            "errors": all_errors,
            "retries": 0,
            "why_explanations": why_explanations,
            "metadata": {
                "planner_version": plan.planner_version,
                "raw_prompt": plan.raw_prompt,
                "normalized_prompt": plan.normalized_prompt,
                "intents": plan.intents,
                "parameters": plan.parameters,
                "complexity": plan.complexity,
                "strategy": plan.generation_strategy
            }
        }
        
        # Write to DB
        ai_chat = models.ChatHistory(
            workspace_id=workspace.id,
            role="ai",
            content=response_text,
            metadata_json={"validation_report": validation_report, "hardware_hash": current_hash, "template_version": "v4.0"}
        )
        db.add(ai_chat)
        db.commit()
        
        return {
            "response": response_text,
            "logs": logs,
            "has_conflict": False,
            "conflicts": [],
            "validation_report": validation_report
        }

    # B. Cache lookup using Workspace ID + Context Hash + Prompt + Framework + Version
    last_user_msg = db.query(models.ChatHistory).filter_by(
        workspace_id=workspace.id,
        role="user",
        content=request.prompt
    ).order_by(models.ChatHistory.created_at.desc()).first()
    
    if last_user_msg:
        cached_ai_msg = db.query(models.ChatHistory).filter(
            models.ChatHistory.workspace_id == workspace.id,
            models.ChatHistory.role == "ai",
            models.ChatHistory.created_at > last_user_msg.created_at
        ).order_by(models.ChatHistory.created_at.asc()).first()
        
        if cached_ai_msg and cached_ai_msg.metadata_json:
            cached_hash = cached_ai_msg.metadata_json.get("hardware_hash")
            cached_ver = cached_ai_msg.metadata_json.get("template_version")
            if cached_hash == current_hash and cached_ver == "v4.0":
                logs.append("Cache Hit: Found matching prompt, template version, and hardware context hash. Reusing cached driver.")
                validation_report = cached_ai_msg.metadata_json.get("validation_report", {})
                if "quality_report" in validation_report:
                    validation_report["quality_report"]["source"] = "Cache"
                validation_report["why_explanations"] = why_explanations
                
                return {
                    "response": cached_ai_msg.content,
                    "logs": logs,
                    "has_conflict": False,
                    "conflicts": [],
                    "validation_report": validation_report
                }

    # C. LLM/Hybrid pathway (if cache misses)
    # 2. Inquire Cognee graph memories
    logs.append(f"Querying Cognee semantic memory graph partitions for context...")
    try:
        recalled_context = await recall_hardware_context(request.prompt, workspace.id)
        logs.append("Cognee retrieved semantic memory node links.")
    except Exception as e:
        logger.warning(f"Cognee recall failure: {e}")
        recalled_context = "Graph Memory Offline. Falling back to local cached DB tables."
        logs.append("Cognee partition unavailable. Fallback to SQL mapping tables.")
        
    # Retrieve user's custom API key if configured (BYOK)
    user_api_key = None
    user_key_rec = db.query(models.UserKeys).filter_by(user_id=current_user["uid"]).first()
    if user_key_rec:
        try:
            from utils.helpers import decrypt_api_key
            user_api_key = decrypt_api_key(user_key_rec.encrypted_gemini_key)
            logs.append("Routing request via custom user Gemini API key.")
        except Exception as e:
            logger.error(f"Error decrypting user API key: {e}")
            logs.append("Failed to decrypt user API key. Falling back to server key.")

    # 3. Assemble prompt with symbolic register macros rules
    system_instruction = build_copilot_prompt(request.prompt, recalled_context, context_dict)
    
    # 4. Generate using Gemini with Self-Healing Verification Loop
    logs.append(f"Sending system instructions downstream to Google Gemini API (Strategy: {plan.generation_strategy})...")
    
    max_retries = 3
    retry_count = 0
    response_text = await generate_firmware_code(request.prompt, system_instruction, context_dict, user_api_key=user_api_key)
    
    # Run initial multi-level analysis
    syntax_errors = []
    if not response_text.startswith("/*") and not response_text.startswith("#include") and not response_text.startswith("void") and not response_text.startswith("const"):
        syntax_errors.append("Syntax Error: Generated C code block appears truncated or incorrect.")
    
    framework_errors = analyze_static_code(response_text, context_dict)
    register_errors = post_validate_registers(response_text, context_dict["mcu"])
    behavior_errors = verify_functional_behavior(response_text, plan.intents[0] if plan.intents else "")
    
    # Run compilation check
    from services.compiler_service import verify_compilation
    comp_status, comp_errors = verify_compilation(workspace.id, response_text, context_dict)
    all_errors = syntax_errors + framework_errors + register_errors + behavior_errors + comp_errors
    
    while all_errors and retry_count < max_retries:
        retry_count += 1
        logs.append(f"Validation failed with {len(all_errors)} errors. Constructing Compiler Repair Report and regenerating...")
        
        # Build self-healing repair instructions
        repair_report = "--- HARDWARE REPAIR REPORT ---\n"
        repair_report += f"Requested Intent(s): {plan.intents}\n"
        repair_report += f"Required Peripheral Capabilities: {plan.required_capabilities}\n"
        repair_report += f"Extracted Parameters: {plan.parameters}\n\n"
        repair_report += "Violations & Compilation Errors Found:\n"
        for err in all_errors:
            repair_report += f"- {err}\n"
        repair_report += "\nPlease regenerate the code correcting all violations. Output ONLY valid compilable C/C++ code."
        
        # Request corrected output
        response_text = await generate_firmware_code(repair_report, system_instruction, context_dict, user_api_key=user_api_key)
        
        # Re-analyze
        syntax_errors = []
        if not response_text.startswith("/*") and not response_text.startswith("#include") and not response_text.startswith("void") and not response_text.startswith("const"):
            syntax_errors.append("Syntax Error: Generated C code block appears truncated or incorrect.")
        framework_errors = analyze_static_code(response_text, context_dict)
        register_errors = post_validate_registers(response_text, context_dict["mcu"])
        behavior_errors = verify_functional_behavior(response_text, plan.intents[0] if plan.intents else "")
        
        # Re-verify compilation
        comp_status, comp_errors = verify_compilation(workspace.id, response_text, context_dict)
        all_errors = syntax_errors + framework_errors + register_errors + behavior_errors + comp_errors

    logs.append(f"Firmware verification pipeline completed after {retry_count} repairs.")

    validation_report = {
        "quality_report": {
            "hardware_context": "Passed" if not any("GPIO" in e or "Pin" in e for e in all_errors) else "Failed",
            "framework": "Passed" if not framework_errors else "Failed",
            "behavior": "Passed" if not behavior_errors else "Failed",
            "registers": "Passed" if not register_errors else "Failed",
            "compilation": comp_status,
            "source": "Gemini"
        },
        "errors": all_errors,
        "retries": retry_count,
        "why_explanations": why_explanations,
        "metadata": {
            "planner_version": plan.planner_version,
            "raw_prompt": plan.raw_prompt,
            "normalized_prompt": plan.normalized_prompt,
            "intents": plan.intents,
            "parameters": plan.parameters,
            "complexity": plan.complexity,
            "strategy": plan.generation_strategy
        }
    }

    # 5. Persist final AI response
    ai_chat = models.ChatHistory(
        workspace_id=workspace.id,
        role="ai",
        content=response_text,
        metadata_json={"validation_report": validation_report, "hardware_hash": current_hash, "template_version": "v4.0"}
    )
    db.add(ai_chat)
    db.commit()
    
    return {
        "response": response_text,
        "logs": logs,
        "has_conflict": False,
        "conflicts": [],
        "validation_report": validation_report
    }

@router.delete("/api/workspace/{id}")
async def delete_workspace(
    id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Deletes user-owned workspace details from PostgreSQL and purges Cognee semantic records.
    """
    ensure_db_user_exists(db, current_user)
    
    # Verify ownership
    workspace = db.query(models.Workspace).filter_by(id=id, user_id=current_user["uid"]).first()
    if not workspace:
        raise HTTPException(status_code=403, detail="Workspace access forbidden.")
        
    try:
        db.delete(workspace)
        db.commit()
        
        # Wipe Cognee graph references
        await delete_workspace_memory(id)
        
        return {"status": "success", "message": f"Workspace {id} purged successfully."}
    except Exception as e:
        db.rollback()
        logger.error(f"Error purging workspace database node: {e}")
        raise HTTPException(status_code=500, detail=f"Database Delete Failure: {str(e)}")

@router.get("/api/user/settings")
async def get_user_settings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns user settings state, including whether they have a saved Gemini key.
    """
    ensure_db_user_exists(db, current_user)
    rec = db.query(models.UserKeys).filter_by(user_id=current_user["uid"]).first()
    return {
        "has_key": rec is not None,
        "name": current_user["name"],
        "email": current_user["email"],
        "avatar_url": current_user["avatar_url"]
    }

@router.post("/api/user/key/save")
async def save_user_key(
    payload: schemas.ApiKeyPayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Encrypts and saves the user's custom Gemini API key.
    """
    ensure_db_user_exists(db, current_user)
    key = payload.api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="API key cannot be empty.")
        
    try:
        from utils.helpers import encrypt_api_key
        encrypted = encrypt_api_key(key)
        
        rec = db.query(models.UserKeys).filter_by(user_id=current_user["uid"]).first()
        if not rec:
            rec = models.UserKeys(
                user_id=current_user["uid"],
                encrypted_gemini_key=encrypted,
                salt="none"
            )
            db.add(rec)
        else:
            rec.encrypted_gemini_key = encrypted
        db.commit()
        return {"status": "success", "message": "Gemini API key saved securely."}
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving user API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/user/key/test")
async def test_user_key(
    payload: schemas.ApiKeyPayload,
    current_user: dict = Depends(get_current_user)
):
    """
    Verifies a Gemini API key by making a test completion call.
    """
    key = payload.api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="API key is required.")
        
    try:
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": "Hello"}]}]}
        
        async with httpx.AsyncClient() as client:
            res = await client.post(url, json=data, headers=headers, timeout=5.0)
            if res.status_code == 200:
                return {"valid": True}
            else:
                error_detail = res.json().get("error", {}).get("message", "API verification failed.")
                return {"valid": False, "error": error_detail}
    except Exception as e:
        return {"valid": False, "error": str(e)}

@router.post("/api/user/key/remove")
async def remove_user_key(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Deletes the saved Gemini API key for the user.
    """
    ensure_db_user_exists(db, current_user)
    rec = db.query(models.UserKeys).filter_by(user_id=current_user["uid"]).first()
    if rec:
        db.delete(rec)
        db.commit()
    return {"status": "success", "message": "Gemini API key removed."}

@router.get("/api/user/preferences")
async def get_user_preferences(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieves user preferences and UI state from PostgreSQL/SQLite.
    """
    ensure_db_user_exists(db, current_user)
    pref = db.query(models.UserPreferences).filter_by(user_id=current_user["uid"]).first()
    if not pref:
        return {"preferences": {}}
    return {"preferences": pref.preferences}

@router.post("/api/user/preferences")
async def save_user_preferences(
    payload: schemas.UserPreferencesPayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Persists user preferences and UI settings in PostgreSQL/SQLite.
    """
    ensure_db_user_exists(db, current_user)
    pref = db.query(models.UserPreferences).filter_by(user_id=current_user["uid"]).first()
    if not pref:
        pref = models.UserPreferences(
            user_id=current_user["uid"],
            preferences=payload.preferences
        )
        db.add(pref)
    else:
        pref.preferences = payload.preferences
    db.commit()
    return {"status": "success", "message": "User preferences synchronized successfully."}
