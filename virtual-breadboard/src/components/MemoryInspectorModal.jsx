import React from 'react';
import { motion } from 'framer-motion';

// Placeholder MemoryInspectorModal component
export default function MemoryInspectorModal({ node, onClose }) {
  if (!node) return null;
  return (
    <motion.div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="bg-[var(--pm-surface)] border border-[var(--pm-border-2)] rounded-2xl p-6 w-full max-w-md"
        onClick={e => e.stopPropagation()}
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
      >
        <h2 className="text-lg font-bold mb-4" style={{ color: 'var(--pm-text)' }}>Node Details</h2>
        <pre className="text-sm" style={{ color: 'var(--pm-text-muted)' }}>
{JSON.stringify(node, null, 2)}
        </pre>
        <button
          className="mt-4 px-4 py-2 bg-[var(--accent)] text-white rounded"
          onClick={onClose}
        >Close</button>
      </motion.div>
    </motion.div>
  );
}
