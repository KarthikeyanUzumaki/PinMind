// OnboardingPage.jsx — First-time Gemini API key setup
// Shown after first Google Sign-In if user has no saved key

import { useState } from 'react';
import { motion } from 'framer-motion';

const BACKEND_URL = 'http://localhost:8000';

export default function OnboardingPage({ authToken, onComplete }) {
  const [apiKey, setApiKey]       = useState('');
  const [testing, setTesting]     = useState(false);
  const [saving, setSaving]       = useState(false);
  const [testResult, setTestResult] = useState(null);

  const handleTest = async () => {
    if (!apiKey.trim()) return;
    setTesting(true);
    setTestResult(null);
    try {
      const res = await fetch(`${BACKEND_URL}/api/user/key/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authToken}` },
        body: JSON.stringify({ api_key: apiKey }),
      });
      const data = await res.json();
      setTestResult(data);
    } catch (e) {
      setTestResult({ valid: false, error: e.message });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    if (!apiKey.trim()) return;
    setSaving(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/user/key/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authToken}` },
        body: JSON.stringify({ api_key: apiKey }),
      });
      if (res.ok) onComplete();
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      className="h-screen w-screen flex flex-col items-center justify-center overflow-hidden relative"
      style={{ background: 'var(--pm-bg)' }}
    >
      {/* Background glow */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full
          bg-blue-600/[0.06] blur-[120px]" />
        <div className="absolute inset-0 opacity-[0.2]"
          style={{
            backgroundImage: `radial-gradient(var(--pm-border) 1px, transparent 1px)`,
            backgroundSize: '24px 24px',
          }}
        />
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="relative z-10 w-full max-w-md mx-4 rounded-2xl p-8 space-y-6 shadow-2xl"
        style={{
          background: 'var(--pm-surface)',
          border: '1px solid var(--pm-border-2)',
          boxShadow: '0 0 40px var(--accent-glow), 0 16px 48px rgba(0,0,0,0.4)',
        }}
      >
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex justify-center mb-4">
            <div className="p-3 rounded-2xl" style={{ background: 'var(--accent-dim)', border: '1px solid var(--accent-border)' }}>
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="var(--accent)" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
            </div>
          </div>
          <h1 className="text-lg font-bold" style={{ color: 'var(--pm-text)' }}>
            Connect Your Gemini API
          </h1>
          <p className="text-xs font-mono-editor leading-relaxed" style={{ color: 'var(--pm-text-muted)' }}>
            PinMind uses your personal Gemini API key to generate register-level firmware. Your key is encrypted and stored securely.
          </p>
        </div>

        {/* Input */}
        <div className="space-y-2">
          <label className="block text-[10px] font-bold uppercase tracking-wider font-mono-editor"
            style={{ color: 'var(--pm-text-muted)' }}>
            Google Gemini API Key
          </label>
          <input
            type="password"
            placeholder="AIzaSy..."
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSave()}
            className="w-full rounded-lg px-3 py-2.5 text-xs font-mono-editor outline-none transition-colors"
            style={{
              background: 'var(--pm-surface-2)',
              border: '1px solid var(--pm-border-2)',
              color: 'var(--pm-text)',
            }}
          />
          <a
            href="https://aistudio.google.com/app/apikey"
            target="_blank"
            rel="noreferrer"
            className="text-[10px] font-mono-editor hover:underline"
            style={{ color: 'var(--accent)' }}
          >
            Get a free API key from Google AI Studio →
          </a>
        </div>

        {/* Test result */}
        {testResult && (
          <div
            className="p-2.5 rounded-lg text-xs font-mono-editor"
            style={{
              background: testResult.valid ? 'var(--success-dim)' : 'var(--error-dim)',
              border: `1px solid ${testResult.valid ? 'var(--success)' : 'var(--error)'}33`,
              color: testResult.valid ? 'var(--success)' : 'var(--error)',
            }}
          >
            {testResult.valid
              ? '✓ API connection verified successfully!'
              : `✗ Connection failed: ${testResult.error}`}
          </div>
        )}

        {/* Buttons */}
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={handleTest}
            disabled={testing || !apiKey.trim()}
            className="py-2.5 rounded-lg text-xs font-bold font-mono-editor disabled:opacity-50 cursor-pointer transition-colors"
            style={{
              background: 'var(--pm-surface-2)',
              border: '1px solid var(--pm-border-2)',
              color: 'var(--pm-text)',
            }}
          >
            {testing ? 'Testing...' : 'Test Connection'}
          </button>
          <button
            onClick={handleSave}
            disabled={saving || !apiKey.trim()}
            className="py-2.5 rounded-lg text-xs font-bold text-white font-mono-editor disabled:opacity-50 cursor-pointer transition-all"
            style={{
              background: 'var(--accent)',
              boxShadow: '0 4px 16px var(--accent-glow)',
            }}
          >
            {saving ? 'Saving...' : 'Continue →'}
          </button>
        </div>

        {/* Skip */}
        <div className="text-center pt-1">
          <button
            onClick={onComplete}
            className="text-[10px] font-mono-editor hover:underline transition-opacity opacity-60 hover:opacity-100 cursor-pointer"
            style={{ color: 'var(--pm-text-muted)' }}
          >
            Skip — use server shared key (limited)
          </button>
        </div>
      </motion.div>
    </div>
  );
}
