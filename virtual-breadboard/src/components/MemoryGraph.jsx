import React, { useState, useEffect } from 'react';

export default function MemoryGraph({
  workspaceId = 'default',
  mcu = 'ESP32-WROOM',
  framework = 'Arduino',
  gpios = [],
  peripherals = [],
  isGenerating = false,
  hasFirmware = false,
  presentMode = false,
  isLoading = false
}) {
  const [selectedNode, setSelectedNode] = useState(null);
  const [hoveredNode, setHoveredNode] = useState(null);

  if (isLoading) {
    return (
      <div className="w-full flex flex-col rounded-2xl border border-[var(--pm-border)] bg-[var(--pm-surface-2)] overflow-hidden shadow-2xl animate-pulse">
        <div className="flex justify-between items-center px-4 py-3 bg-[var(--pm-surface)] border-b border-[var(--pm-border)]">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded bg-[var(--accent)] animate-pulse" />
            <span className="text-[10px] font-bold uppercase tracking-wider font-mono-editor text-[var(--pm-text-muted)]">
              Recalling Graph Memory...
            </span>
          </div>
        </div>
        <div className="relative w-full overflow-hidden bg-[#07080c] flex flex-col items-center justify-center gap-4" style={{ height: '220px' }}>
          {/* Skeleton representation of graph nodes */}
          <div className="flex justify-around w-full px-8 items-center h-full">
            <div className="w-24 h-9 rounded-lg bg-slate-800/40 border border-slate-700/20" />
            <div className="w-1.5 h-1.5 rounded-full bg-slate-800" />
            <div className="w-1.5 h-1.5 rounded-full bg-slate-800" />
            <div className="w-1.5 h-1.5 rounded-full bg-slate-800" />
            <div className="w-28 h-9 rounded-lg bg-slate-800/40 border border-slate-700/20" />
            <div className="w-1.5 h-1.5 rounded-full bg-slate-800" />
            <div className="w-1.5 h-1.5 rounded-full bg-slate-800" />
            <div className="w-1.5 h-1.5 rounded-full bg-slate-800" />
            <div className="w-32 h-9 rounded-lg bg-slate-800/40 border border-slate-700/20" />
          </div>
          <div className="text-[9px] font-mono-editor text-slate-500 uppercase tracking-widest absolute bottom-4">Constructing relation vectors...</div>
        </div>
      </div>
    );
  }

  // Dynamic nodes array mapping exactly what is configured
  const items = [];
  peripherals.forEach((p, idx) => {
    items.push({
      id: `periph-${p.name}`,
      name: p.name,
      label: `${p.name} (${p.pins.join(', ')})`,
      type: 'Peripheral',
      index: idx
    });
  });
  gpios.forEach((g, idx) => {
    if (g.pin) {
      items.push({
        id: `gpio-${g.pin}`,
        name: g.pin,
        label: `${g.label || 'Pin'} (${g.pin})`,
        type: 'GPIO Assignment',
        index: idx + peripherals.length
      });
    }
  });

  // Calculate dynamic dimensions for centered 3-column layout
  const spacingY = 50;
  const listHeight = items.length * spacingY;
  const svgHeight = Math.max(220, listHeight + 70);
  const centerY = svgHeight / 2;

  // Node centers shifted to the right to prevent left-side clipping
  const col1X = 100; // Workspace
  const col2X = 270; // MCU
  const col3X = 470; // Peripherals/Pins

  // Compute selection highlight states
  const getHighlightState = () => {
    if (!selectedNode) {
      return {
        isNodeActive: () => true,
        isPathActive: () => true
      };
    }

    const activeNodes = new Set();
    const activePaths = new Set();

    if (selectedNode === 'workspace') {
      activeNodes.add('workspace');
      activeNodes.add('mcu');
      activePaths.add('ws-to-mcu');
    } else if (selectedNode === 'mcu') {
      activeNodes.add('workspace');
      activeNodes.add('mcu');
      activePaths.add('ws-to-mcu');
      items.forEach(item => {
        activeNodes.add(item.id);
        activePaths.add(`mcu-to-${item.id}`);
      });
    } else {
      // It is one of the peripheral/GPIO items
      const selectedItem = items.find(item => item.id === selectedNode);
      if (selectedItem) {
        activeNodes.add('mcu');
        activeNodes.add(selectedItem.id);
        activePaths.add(`mcu-to-${selectedItem.id}`);
      }
    }

    return {
      isNodeActive: (id) => activeNodes.has(id),
      isPathActive: (id) => activePaths.has(id)
    };
  };

  const highlightState = getHighlightState();

  const renderNode = (id, cx, cy, label, sublabel, color, width) => {
    const isSel = selectedNode === id;
    const isGov = hoveredNode === id;
    const isAct = highlightState.isNodeActive(id);

    return (
      <g 
        transform={`translate(${cx}, ${cy})`}
        className="cursor-pointer select-none"
        onClick={() => setSelectedNode(selectedNode === id ? null : id)}
        onMouseEnter={() => setHoveredNode(id)}
        onMouseLeave={() => setHoveredNode(null)}
        style={{ opacity: isAct ? 1 : 0.22, transition: 'all 0.25s ease' }}
      >
        {/* Node Box */}
        <rect 
          x={-width / 2} 
          y="-18" 
          width={width} 
          height="36" 
          rx="6" 
          fill="#0f1115" 
          stroke={isSel ? 'var(--accent)' : isGov ? 'rgba(255, 255, 255, 0.25)' : 'rgba(255, 255, 255, 0.08)'} 
          strokeWidth="1.2" 
          style={{ transition: 'all 0.25s ease' }}
        />
        
        {/* Connection Ports */}
        <circle cx={-width / 2} cy="0" r="2.5" fill={color} opacity="0.8" />
        <circle cx={width / 2} cy="0" r="2.5" fill={color} opacity="0.8" />

        {/* Text details */}
        <text x={-width / 2 + 10} y="-4" className="text-[7.5px] font-bold fill-slate-400 font-mono-editor uppercase tracking-wider">{sublabel}</text>
        <text x={-width / 2 + 10} y="8" className="text-[9.5px] font-bold fill-white font-mono-editor truncate" style={{ maxWidth: `${width - 20}px` }}>
          {label}
        </text>
      </g>
    );
  };

  const renderPath = (id, d) => {
    const isAct = highlightState.isPathActive(id);

    return (
      <path
        d={d}
        fill="none"
        stroke={isAct ? 'var(--accent)' : 'rgba(255, 255, 255, 0.08)'}
        strokeWidth={isAct ? '2' : '1.2'}
        opacity={isAct ? 1 : 0.1}
        style={{ transition: 'all 0.25s ease' }}
      />
    );
  };

  return (
    <div className="w-full flex flex-col rounded-2xl border border-[var(--pm-border)] bg-[var(--pm-surface-2)] overflow-hidden shadow-2xl">
      {/* Header bar */}
      <div className="flex justify-between items-center px-4 py-3 bg-[var(--pm-surface)] border-b border-[var(--pm-border)]">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded bg-[var(--accent)] animate-pulse" />
          <span className="text-[10px] font-bold uppercase tracking-wider font-mono-editor text-[var(--pm-text)]">
            Hardware Memory Graph
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-[9px] font-mono-editor">
          {selectedNode && (
            <button 
              onClick={() => setSelectedNode(null)} 
              className="px-2 py-0.5 rounded border border-[var(--pm-border)] hover:border-[var(--accent)] hover:text-[var(--accent)] bg-[var(--pm-surface-3)] text-[8px] font-bold tracking-wide transition-colors cursor-pointer text-[var(--pm-text)]"
            >
              RESET VIEW
            </button>
          )}
          <span className="text-[var(--pm-text-muted)] font-bold">CLICK NODE TO ISOLATE</span>
        </div>
      </div>

      {/* Grid Canvas container */}
      <div className="relative w-full overflow-hidden bg-[#07080c]" style={{ height: `${svgHeight}px`, transition: 'height 0.3s ease-out' }}>
        <svg viewBox={`0 0 600 ${svgHeight}`} className="w-full h-full">
          <defs>
            <pattern id="pcb-grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <circle cx="10" cy="10" r="1.2" fill="rgba(255, 255, 255, 0.04)" />
            </pattern>
          </defs>

          {/* Grid Background */}
          <rect width="100%" height="100%" fill="url(#pcb-grid)" />

          {/* CONNECTIONS PATHS */}
          
          {/* Workspace -> MCU */}
          {renderPath('ws-to-mcu', `M ${col1X + 55} ${centerY} L ${col2X - 60} ${centerY}`)}

          {/* MCU -> Items */}
          {items.map((item) => {
            const blockY = (centerY - listHeight / 2) + item.index * spacingY + 8;
            const pathIdMcu = `mcu-to-${item.id}`;

            return (
              <g key={`paths-${item.id}`}>
                {renderPath(pathIdMcu, `M ${col2X + 60} ${centerY} C ${col2X + 85} ${centerY}, ${col3X - 85} ${blockY + 18}, ${col3X - 70} ${blockY + 18}`)}
              </g>
            );
          })}


          {/* NODES CARDS */}
          
          {/* Column 1: Workspace */}
          {renderNode('workspace', col1X, centerY, workspaceId, 'Workspace', 'var(--accent)', 110)}

          {/* Column 2: MCU (Dynamic representation) */}
          {renderNode('mcu', col2X, centerY, mcu, 'MCU target', '#3b82f6', 120)}

          {/* Column 3: Configured Peripherals / Pins */}
          {items.map((item) => {
            const blockY = (centerY - listHeight / 2) + item.index * spacingY + 8;
            return (
              <g key={item.id}>
                {renderNode(item.id, col3X, blockY + 18, item.label, item.type, '#eab308', 140)}
              </g>
            );
          })}
          {items.length === 0 && renderNode('no-config', col3X, centerY, 'No pins set up', 'Hardware Config', '#94a3b8', 140)}

        </svg>
      </div>
    </div>
  );
}
