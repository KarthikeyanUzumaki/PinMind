import React from 'react';
import { motion } from 'framer-motion';
import { loginWithGoogle } from '../firebase';

export default function LandingPage({ onGetStarted }) {
  const triggerGetStarted = onGetStarted || loginWithGoogle;

  return (
    <div className="h-screen w-screen overflow-hidden flex flex-col items-center justify-center relative select-none"
      style={{ background: 'var(--pm-bg)', color: 'var(--pm-text)' }}>

      {/* Background radial glow */}
      <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute top-[30%] left-[50%] -translate-x-1/2 w-[500px] h-[500px] rounded-full
          bg-blue-600/[0.08] blur-[120px]" />
        <div className="absolute inset-0 opacity-[0.25]"
          style={{
            backgroundImage: `radial-gradient(var(--pm-border-2) 1.2px, transparent 1.2px)`,
            backgroundSize: '26px 26px',
          }}
        />
      </div>

      {/* Clean Center Panel */}
      <motion.main 
        className="relative z-10 flex flex-col items-center text-center space-y-8 max-w-lg px-6"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        {/* Chip Icon */}
        <div className="p-4 rounded-3xl border relative bg-[var(--pm-surface)] shadow-2xl"
          style={{ borderColor: 'var(--pm-border-2)' }}>
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="var(--accent)" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round"
              d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 5h10a2 2 0 012 2v10a2 2 0 01-2 2H7a2 2 0 01-2-2V7a2 2 0 012-2z" />
          </svg>
        </div>

        {/* Brand Header */}
        <div className="space-y-2">
          <h1 className="text-5xl font-extrabold tracking-tight" style={{ letterSpacing: '-0.03em' }}>
            PinMind
          </h1>
          <p className="text-[10px] font-bold tracking-[0.25em] uppercase font-mono-editor" style={{ color: 'var(--accent)' }}>
            Firmware Intelligence Workspace
          </p>
        </div>

        {/* Tagline */}
        <div className="space-y-1">
          <h2 className="text-xl font-bold tracking-tight text-[var(--pm-text)]">
            Configure Once. Remember Forever.
          </h2>
          <p className="text-[10px] font-bold font-mono-editor text-[var(--pm-text-muted)] tracking-wider">
            Powered by Cognee
          </p>
        </div>

        {/* Simple CTA */}
        <div className="pt-2">
          <motion.button
            onClick={triggerGetStarted}
            whileHover={{ scale: 1.03, boxShadow: '0 8px 30px var(--accent-glow)' }}
            whileTap={{ scale: 0.98 }}
            className="flex items-center gap-2.5 px-8 py-3.5 rounded-xl text-sm font-bold text-white cursor-pointer transition-all border border-[var(--accent-border)]"
            style={{
              background: 'var(--accent)',
              boxShadow: '0 4px 20px var(--accent-glow)',
            }}
          >
            Get Started
          </motion.button>
        </div>
      </motion.main>
    </div>
  );
}
