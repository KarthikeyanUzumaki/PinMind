// CommandPalette.jsx — Ctrl+K global command palette
// Cursor/Linear style: centered modal, search, keyboard navigation

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const SearchIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
);

export default function CommandPalette({ isOpen, onClose, commands }) {
  const [query, setQuery] = useState('');
  const [activeIdx, setActiveIdx] = useState(0);
  const inputRef = useRef(null);
  const listRef = useRef(null);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setActiveIdx(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  // Filter commands by query
  const filtered = query.trim()
    ? commands.filter(c =>
        c.label.toLowerCase().includes(query.toLowerCase()) ||
        (c.category && c.category.toLowerCase().includes(query.toLowerCase()))
      )
    : commands;

  // Reset active index when filter changes
  useEffect(() => setActiveIdx(0), [query]);

  const runCommand = (cmd) => {
    onClose();
    setTimeout(() => cmd.action(), 50); // slight delay so modal closes first
  };

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIdx(i => Math.min(i + 1, filtered.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIdx(i => Math.max(i - 1, 0));
    } else if (e.key === 'Enter') {
      if (filtered[activeIdx]) runCommand(filtered[activeIdx]);
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  // Scroll active item into view
  useEffect(() => {
    const el = listRef.current?.children[activeIdx];
    el?.scrollIntoView({ block: 'nearest' });
  }, [activeIdx]);

  const categoryIcons = {
    workspace:  '◈',
    settings:   '⚙',
    navigation: '→',
    action:     '⚡',
    account:    '◉',
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[9998] flex items-start justify-center pt-[15vh]">
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Palette box */}
          <motion.div
            className="relative z-10 w-full max-w-xl mx-4"
            initial={{ opacity: 0, y: -16, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.97 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
          >
            <div className="bg-[var(--pm-surface)] border border-[var(--pm-border-2)] rounded-2xl shadow-2xl overflow-hidden">
              
              {/* Search row */}
              <div className="flex items-center gap-3 px-4 py-3.5 border-b border-[var(--pm-border)]">
                <span className="text-[var(--pm-text-muted)]">
                  <SearchIcon />
                </span>
                <input
                  ref={inputRef}
                  type="text"
                  placeholder="Search commands, workspaces, settings..."
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="flex-1 bg-transparent text-sm text-[var(--pm-text)] placeholder-[var(--pm-text-muted)] outline-none font-sans"
                />
                <kbd className="text-[10px] bg-[var(--pm-surface-2)] border border-[var(--pm-border)] text-[var(--pm-text-muted)] px-1.5 py-0.5 rounded font-mono-editor">
                  Esc
                </kbd>
              </div>

              {/* Results list */}
              <div
                ref={listRef}
                className="max-h-80 overflow-y-auto py-1.5"
              >
                {filtered.length === 0 ? (
                  <div className="py-8 text-center text-xs text-[var(--pm-text-muted)] font-mono-editor">
                    No commands found for "{query}"
                  </div>
                ) : (
                  filtered.map((cmd, idx) => (
                    <button
                      key={cmd.id}
                      className={`w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors cursor-pointer
                        ${idx === activeIdx
                          ? 'bg-[var(--accent-dim)] text-[var(--accent)]'
                          : 'text-[var(--pm-text)] hover:bg-[var(--pm-surface-2)]'
                        }`}
                      onClick={() => runCommand(cmd)}
                      onMouseEnter={() => setActiveIdx(idx)}
                    >
                      {/* Category icon */}
                      <span className={`text-sm w-5 text-center font-mono-editor shrink-0
                        ${idx === activeIdx ? 'text-[var(--accent)]' : 'text-[var(--pm-text-muted)]'}`}>
                        {categoryIcons[cmd.category] || '▸'}
                      </span>

                      {/* Label + description */}
                      <div className="flex-1 min-w-0">
                        <div className="text-xs font-semibold truncate">{cmd.label}</div>
                        {cmd.desc && (
                          <div className={`text-[10px] truncate mt-0.5 font-mono-editor
                            ${idx === activeIdx ? 'text-[var(--accent)]/70' : 'text-[var(--pm-text-muted)]'}`}>
                            {cmd.desc}
                          </div>
                        )}
                      </div>

                      {/* Shortcut */}
                      {cmd.shortcut && (
                        <kbd className={`text-[9px] shrink-0 px-1.5 py-0.5 rounded border font-mono-editor
                          ${idx === activeIdx
                            ? 'bg-[var(--accent-dim)] border-[var(--accent-border)] text-[var(--accent)]'
                            : 'bg-[var(--pm-surface-2)] border-[var(--pm-border)] text-[var(--pm-text-muted)]'
                          }`}>
                          {cmd.shortcut}
                        </kbd>
                      )}
                    </button>
                  ))
                )}
              </div>

              {/* Footer hint */}
              <div className="px-4 py-2 border-t border-[var(--pm-border)] flex items-center gap-3 text-[9px] text-[var(--pm-text-muted)] font-mono-editor">
                <span><kbd className="bg-[var(--pm-surface-2)] px-1 py-0.5 rounded border border-[var(--pm-border)]">↑↓</kbd> navigate</span>
                <span><kbd className="bg-[var(--pm-surface-2)] px-1 py-0.5 rounded border border-[var(--pm-border)]">↵</kbd> run</span>
                <span><kbd className="bg-[var(--pm-surface-2)] px-1 py-0.5 rounded border border-[var(--pm-border)]">Esc</kbd> close</span>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
