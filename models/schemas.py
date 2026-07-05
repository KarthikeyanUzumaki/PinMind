from typing import List, Optional
from pydantic import BaseModel

class GPIOAssignment(BaseModel):
    pin: str
    label: str
    mode: str

class PeripheralMapping(BaseModel):
    name: str
    pins: List[str]
    dma_channel: Optional[str] = None

class ClockConfig(BaseModel):
    sysclk_mhz: int
    apb1_mhz: int
    apb2_mhz: int

class HardwareContext(BaseModel):
    workspace_id: str
    mcu: str
    framework: Optional[str] = None
    compiler: Optional[str] = None
    board: Optional[str] = None
    platformio_env: Optional[str] = None
    gpios: List[GPIOAssignment]
    peripherals: List[PeripheralMapping]
    clocks: ClockConfig

class ChatRequest(BaseModel):
    workspace_id: str
    prompt: str

class ApiKeyPayload(BaseModel):
    api_key: str

class UserPreferencesPayload(BaseModel):
    preferences: dict

class WorkspaceRenamePayload(BaseModel):
    name: str

class WorkspaceCreatePayload(BaseModel):
    name: str
