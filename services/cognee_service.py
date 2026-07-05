import cognee
import logging

logger = logging.getLogger("pinmind.cognee")

async def save_hardware_context(workspace_id: str, hardware_data: str) -> dict:
    """
    Saves the text/JSON representation of the hardware mappings to Cognee's persistent memory
    and builds the knowledge graph relations.
    """
    try:
        dataset_name = f"workspace_{workspace_id}"
        # 1. Ingest context into the Cognee vector/graph database
        await cognee.remember(data=hardware_data, dataset_name=dataset_name)
        
        # 2. Run graph reasoning and extraction (Memify)
        await cognee.improve(dataset=dataset_name)
        
        return {"status": "success", "message": "Hardware context flashed and graph built!"}
    except Exception as e:
        logger.error(f"Error saving hardware context for {workspace_id}: {e}")
        return {"status": "error", "message": f"Cognee ingestion failed: {str(e)}"}

async def recall_hardware_context(query: str, workspace_id: str) -> str:
    """
    Queries Cognee memory to extract relationship-aware hardware parameters matching the user's query.
    """
    try:
        dataset_name = f"workspace_{workspace_id}"
        recalled_info = await cognee.recall(query_text=query, datasets=[dataset_name])
        # Convert list or object to string representation if needed
        if isinstance(recalled_info, list):
            return "\n".join([str(item) for item in recalled_info])
        return str(recalled_info)
    except Exception as e:
        logger.error(f"Error recalling hardware context for {workspace_id}: {e}")
        return f"Error recalling hardware memory: {str(e)}"

async def delete_workspace_memory(workspace_id: str) -> dict:
    """
    Deletes the dataset graph partition in Cognee memory.
    """
    try:
        dataset_name = f"workspace_{workspace_id}"
        await cognee.forget(dataset=dataset_name)
        return {"status": "success", "message": f"Workspace {workspace_id} memory wiped clean."}
    except Exception as e:
        logger.error(f"Error wiping workspace {workspace_id}: {e}")
        return {"status": "error", "message": f"Wipe failed: {str(e)}"}
