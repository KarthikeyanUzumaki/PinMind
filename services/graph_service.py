from typing import Dict, Any, List

def build_graph_payload(hardware_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constructs a graph payload (nodes and edges) from the current hardware configurations.
    Used by the frontend to render the Interactive Hardware Knowledge Graph.
    """
    nodes = []
    edges = []
    
    mcu = hardware_context.get("mcu", "STM32F401")
    gpios = hardware_context.get("gpios", [])
    peripherals = hardware_context.get("peripherals", [])
    clocks = hardware_context.get("clocks", {})

    # Add MCU Node (Root)
    nodes.append({
        "id": "mcu",
        "label": mcu,
        "type": "MCU",
        "details": f"Core Clock: {clocks.get('sysclk_mhz', 84)} MHz"
    })

    # Add Clocks Tree Root Node
    if clocks:
        nodes.append({
            "id": "clocks_root",
            "label": "Clock Tree",
            "type": "CLOCK_ROOT",
            "details": f"SYSCLK: {clocks.get('sysclk_mhz', 84)} MHz"
        })
        edges.append({"source": "mcu", "target": "clocks_root", "type": "CLOCK_BUS"})
        
        for k, v in clocks.items():
            clock_node_id = f"clock_{k}"
            nodes.append({
                "id": clock_node_id,
                "label": f"{k.upper()}: {v}MHz",
                "type": "CLOCK_NODE",
                "details": f"Domain frequency constraint"
            })
            edges.append({"source": "clocks_root", "target": clock_node_id, "type": "CLOCK_DOMAIN"})

    # Track ports (e.g. GPIOA, GPIOB) to prevent duplicate port nodes
    ports_added = set()

    # Process GPIOs
    for g in gpios:
        pin = g.get("pin", "")
        label = g.get("label", "")
        mode = g.get("mode", "GPIO_Output")
        
        if not pin:
            continue
            
        # Deduce port grouping (e.g., PA5 -> GPIOA)
        port = "GPIOA"
        if pin.startswith("PA"):
            port = "GPIOA"
        elif pin.startswith("PB"):
            port = "GPIOB"
        elif pin.startswith("PC"):
            port = "GPIOC"
        elif pin.startswith("PD"):
            port = "GPIOD"
        else:
            port = "GPIOPORT"
            
        if port not in ports_added:
            nodes.append({
                "id": port,
                "label": port,
                "type": "PORT",
                "details": f"Memory-mapped port registers"
            })
            edges.append({"source": "mcu", "target": port, "type": "BUS_CONNECTION"})
            ports_added.add(port)
            
        # Add Pin Node
        pin_id = f"pin_{pin}"
        nodes.append({
            "id": pin_id,
            "label": pin,
            "type": "PIN",
            "details": f"Mode: {mode}"
        })
        edges.append({"source": port, "target": pin_id, "type": "PIN_ROUTING"})
        
        # Add Device/Label Node connected to physical Pin
        if label:
            dev_id = f"dev_{label}"
            nodes.append({
                "id": dev_id,
                "label": label,
                "type": "DEVICE",
                "details": f"Assigned function: {mode}"
            })
            edges.append({"source": pin_id, "target": dev_id, "type": "HARDWARE_DEVICE"})

    # Process Peripherals
    for p in peripherals:
        name = p.get("name", "")
        pins = p.get("pins", [])
        dma = p.get("dma_channel", "")
        
        if not name:
            continue
            
        peri_id = f"peri_{name}"
        nodes.append({
            "id": peri_id,
            "label": name,
            "type": "PERIPHERAL",
            "details": f"DMA: {dma if dma else 'None'}"
        })
        
        # Connect Peripheral to MCU
        edges.append({"source": "mcu", "target": peri_id, "type": "PERIPHERAL_BUS"})
        
        # Connect Peripheral to Pins it utilizes
        for pin in pins:
            pin_id = f"pin_{pin}"
            # Add edge to trace peripheral routing
            edges.append({"source": peri_id, "target": pin_id, "type": "PERIPHERAL_PIN"})
            
        # Connect Peripheral to DMA Node if active
        if dma and dma != "None" and dma != "":
            dma_id = f"dma_{dma}"
            nodes.append({
                "id": dma_id,
                "label": f"DMA: {dma}",
                "type": "DMA",
                "details": "Direct Memory Access Channel"
            })
            edges.append({"source": peri_id, "target": dma_id, "type": "DMA_ROUTING"})
            edges.append({"source": "mcu", "target": dma_id, "type": "SYSTEM_BUS"})

    return {"nodes": nodes, "edges": edges}
