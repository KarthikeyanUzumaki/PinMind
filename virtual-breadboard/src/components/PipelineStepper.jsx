import React from 'react';
import { motion } from 'framer-motion';

const steps = [
  { id: 'remember', label: 'remember()', type: 'Saving', desc: 'Hardware stored in Cognee' },
  { id: 'recall', label: 'recall()', type: 'Generating', desc: 'Hardware context retrieved' },
  { id: 'improve', label: 'improve()', type: 'Editing', desc: 'Knowledge graph updated' },
  { id: 'forget', label: 'forget()', type: 'Deleting', desc: 'Memory removed' }
];

export default function PipelineStepper({ activeStep }) {
  // activeStep: 'remember', 'recall', 'improve', 'forget' or null/empty
  return (
    <div className="w-full flex items-center justify-between gap-2 p-3 rounded-xl border border-[var(--pm-border-2)] bg-[var(--pm-surface)]">
      {steps.map((step, idx) => {
        const isActive = activeStep === step.id;
        return (
          <React.Fragment key={step.id}>
            {idx > 0 && (
              <div 
                className="flex-1 h-0.5 transition-colors duration-300"
                style={{ background: isActive ? 'var(--accent)' : 'var(--pm-border)' }}
              />
            )}
            <motion.div 
              className="flex flex-col items-center text-center p-2 rounded-lg min-w-[76px] transition-all duration-300 border"
              style={{
                background: isActive ? 'var(--accent-dim)' : 'var(--pm-surface-2)',
                borderColor: isActive ? 'var(--accent)' : 'var(--pm-border)',
              }}
              whileHover={{ scale: 1.02 }}
            >
              <span 
                className="text-[9px] font-bold font-mono-editor"
                style={{ color: isActive ? 'var(--accent)' : 'var(--pm-text-muted)' }}
              >
                {step.label}
              </span>
              <span 
                className="text-[8px] mt-0.5 font-sans"
                style={{ color: isActive ? 'var(--pm-text)' : 'var(--pm-text-dim)' }}
              >
                {step.type}
              </span>
            </motion.div>
          </React.Fragment>
        );
      })}
    </div>
  );
}
