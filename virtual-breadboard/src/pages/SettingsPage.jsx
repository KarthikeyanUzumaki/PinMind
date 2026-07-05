import { useState, useEffect } from 'react';
import { logoutUser } from '../firebase';

const BACKEND_URL = 'https://pinmind001.onrender.com';

// ─── Helper Components ──────────────────────────────────────────────────────

const Toggle = ({ value, onChange, label, desc }) => (
  <div
    className="flex justify-between items-center py-3 border-b"
    style={{ borderColor: 'var(--pm-border)' }}
  >
    <div>
      <div className="text-xs font-semibold" style={{ color: 'var(--pm-text)' }}>
        {label}
      </div>
      {desc && (
        <div className="text-[10px] font-mono mt-0.5" style={{ color: 'var(--pm-text-muted)' }}>
          {desc}
        </div>
      )}
    </div>
    <button
      onClick={() => onChange(!value)}
      className="relative rounded-full transition-colors cursor-pointer shrink-0"
      style={{
        width: '40px',
        height: '22px',
        background: value ? 'var(--accent)' : 'var(--pm-surface-2)',
        border: '1px solid var(--pm-border-2)',
        transition: 'background 0.2s',
      }}
      aria-label={label}
      role="switch"
      aria-checked={value}
    >
      <span
        className="absolute rounded-full bg-white shadow"
        style={{
          top: '3px',
          left: '3px',
          width: '14px',
          height: '14px',
          transition: 'transform 0.2s',
          transform: value ? 'translateX(18px)' : 'translateX(0)',
        }}
      />
    </button>
  </div>
);

const Segmented = ({ options, value, onChange }) => (
  <div
    className="flex rounded-lg p-0.5 gap-0.5"
    style={{ background: 'var(--pm-surface-2)', border: '1px solid var(--pm-border)' }}
  >
    {options.map((opt) => (
      <button
        key={opt.value}
        onClick={() => onChange(opt.value)}
        className="flex-1 py-1.5 px-2 text-[10px] font-bold rounded font-mono transition-colors cursor-pointer flex items-center justify-center gap-1"
        style={
          value === opt.value
            ? { background: 'var(--accent)', color: '#f2f2f2' }
            : { color: 'var(--pm-text-muted)', background: 'transparent' }
        }
      >
        {opt.label}
        {opt.badge && (
          <span
            className="text-[7px] px-1 rounded"
            style={{ background: 'var(--warning)', color: '#fff' }}
          >
            {opt.badge}
          </span>
        )}
      </button>
    ))}
  </div>
);

const SectionHeading = ({ title, desc }) => (
  <div className="pb-4 mb-4 border-b" style={{ borderColor: 'var(--pm-border)' }}>
    <h2 className="text-sm font-bold" style={{ color: 'var(--pm-text)' }}>
      {title}
    </h2>
    {desc && (
      <p className="text-xs mt-1 font-mono" style={{ color: 'var(--pm-text-muted)' }}>
        {desc}
      </p>
    )}
  </div>
);

const Field = ({ label, desc, children }) => (
  <div className="py-3 border-b" style={{ borderColor: 'var(--pm-border)' }}>
    <div className="flex justify-between items-start gap-4">
      <div className="min-w-0">
        <div className="text-xs font-semibold mb-0.5" style={{ color: 'var(--pm-text)' }}>
          {label}
        </div>
        {desc && (
          <div className="text-[10px] font-mono" style={{ color: 'var(--pm-text-muted)' }}>
            {desc}
          </div>
        )}
      </div>
      <div className="shrink-0">{children}</div>
    </div>
  </div>
);

// ─── SVG Icons ───────────────────────────────────────────────────────────────

const IconGeneral = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="5" />
    <line x1="12" y1="1" x2="12" y2="3" />
    <line x1="12" y1="21" x2="12" y2="23" />
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
    <line x1="1" y1="12" x2="3" y2="12" />
    <line x1="21" y1="12" x2="23" y2="12" />
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
  </svg>
);

const IconAccount = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);

const IconKey = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4" />
  </svg>
);

const IconEditor = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="16 18 22 12 16 6" />
    <polyline points="8 6 2 12 8 18" />
  </svg>
);

const IconAI = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
  </svg>
);

const IconWorkspace = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
  </svg>
);

const IconPrivacy = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
  </svg>
);

const IconBell = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
    <path d="M13.73 21a2 2 0 0 1-3.46 0" />
  </svg>
);

const IconInfo = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

const IconBack = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="15 18 9 12 15 6" />
  </svg>
);

const IconExternal = () => (
  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
    <polyline points="15 3 21 3 21 9" />
    <line x1="10" y1="14" x2="21" y2="3" />
  </svg>
);

const IconDownload = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="7 10 12 15 17 10" />
    <line x1="12" y1="15" x2="12" y2="3" />
  </svg>
);

const IconSun = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="5" />
    <line x1="12" y1="1" x2="12" y2="3" />
    <line x1="12" y1="21" x2="12" y2="23" />
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
    <line x1="1" y1="12" x2="3" y2="12" />
    <line x1="21" y1="12" x2="23" y2="12" />
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
  </svg>
);

const IconMoon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
  </svg>
);

const IconMonitor = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
    <line x1="8" y1="21" x2="16" y2="21" />
    <line x1="12" y1="17" x2="12" y2="21" />
  </svg>
);

// ─── Sidebar Navigation ───────────────────────────────────────────────────────

const NAV_ITEMS = [
  { id: 'general',       label: 'General',       Icon: IconGeneral },
  { id: 'account',      label: 'Account',        Icon: IconAccount },
  { id: 'gemini',       label: 'Gemini API',     Icon: IconKey },
  { id: 'editor',       label: 'Editor',         Icon: IconEditor },
  { id: 'about',        label: 'About',          Icon: IconInfo },
];

// ─── Main SettingsPage ────────────────────────────────────────────────────────

export default function SettingsPage({
  currentUser,
  authToken,
  settings,
  updateSettings,
  themeMode,
  setTheme,
  accentColor,
  setAccent,
  onBack,
  toast,
}) {
  const [activeSection, setActiveSection] = useState('general');

  // Gemini API state
  const [apiStatus, setApiStatus]           = useState(null); // null | { has_key, name, email, avatar_url }
  const [apiKeyInput, setApiKeyInput]       = useState('');
  const [apiLoading, setApiLoading]         = useState(false);
  const [apiTestResult, setApiTestResult]   = useState(null); // null | { ok: bool, msg: string }
  const [apiTestLoading, setApiTestLoading] = useState(false);

  // Fetch API status on mount / when section changes
  useEffect(() => {
    if (activeSection === 'gemini') {
      fetchApiStatus();
    }
  }, [activeSection]);

  const authHeaders = () => ({
    'Content-Type': 'application/json',
    Authorization: `Bearer ${authToken}`,
  });

  const fetchApiStatus = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/user/settings`, { headers: authHeaders() });
      if (!res.ok) throw new Error('Failed to fetch');
      const data = await res.json();
      setApiStatus(data);
    } catch {
      setApiStatus({ has_key: false });
    }
  };

  const handleSaveKey = async () => {
    if (!apiKeyInput.trim()) return;
    setApiLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/user/key/save`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ api_key: apiKeyInput.trim() }),
      });
      if (!res.ok) throw new Error('Save failed');
      setApiKeyInput('');
      await fetchApiStatus();
      toast.success('API Key saved securely');
    } catch {
      toast.error('Failed to save API key');
    } finally {
      setApiLoading(false);
    }
  };

  const handleTestKey = async (keyToTest) => {
    setApiTestLoading(true);
    setApiTestResult(null);
    try {
      const res = await fetch(`${BACKEND_URL}/api/user/key/test`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ api_key: keyToTest || apiKeyInput.trim() }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Test failed');
      setApiTestResult({ ok: true, msg: 'Connection successful! Key is valid.' });
    } catch (e) {
      setApiTestResult({ ok: false, msg: e.message || 'Key test failed.' });
    } finally {
      setApiTestLoading(false);
    }
  };

  const handleRemoveKey = async () => {
    const confirmed = window.confirm(
      'Remove your Gemini API key? You will need to re-enter it to use AI features.'
    );
    if (!confirmed) return;
    setApiLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/user/key/remove`, {
        method: 'POST',
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error('Remove failed');
      await fetchApiStatus();
      setApiTestResult(null);
      toast.info('API Key removed');
    } catch {
      toast.error('Failed to remove API key');
    } finally {
      setApiLoading(false);
    }
  };

  const handleSignOut = async () => {
    try {
      await logoutUser();
    } catch {
      toast.error('Failed to sign out');
    }
  };

  const formatCreationDate = (ts) => {
    if (!ts) return 'Unknown';
    return new Date(ts).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  // ─── Section Renderers ─────────────────────────────────────────────────────

  const renderGeneral = () => (
    <div>
      <SectionHeading
        title="General"
        desc="Customize the look and feel of PinMind."
      />

      {/* Theme Selector */}
      <div className="py-3 border-b" style={{ borderColor: 'var(--pm-border)' }}>
        <div className="text-xs font-semibold mb-3" style={{ color: 'var(--pm-text)' }}>
          Theme
        </div>
        <div className="flex gap-3">
          {[
            { mode: 'light', label: 'Light', Icon: IconSun },
            { mode: 'dark',  label: 'Dark',  Icon: IconMoon },
            { mode: 'system',label: 'System',Icon: IconMonitor },
          ].map(({ mode, label, Icon }) => {
            const active = themeMode === mode;
            return (
              <button
                key={mode}
                onClick={() => setTheme(mode)}
                className="flex-1 flex flex-col items-center gap-2 py-4 px-3 rounded-xl transition-all cursor-pointer"
                style={{
                  background: active ? 'var(--accent-dim)' : 'var(--pm-surface-2)',
                  border: active ? '1.5px solid var(--accent-border)' : '1.5px solid var(--pm-border)',
                  color: active ? 'var(--accent)' : 'var(--pm-text-muted)',
                }}
              >
                <Icon />
                <span className="text-[11px] font-semibold">{label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Accent Color */}
      <div className="py-3 border-b" style={{ borderColor: 'var(--pm-border)' }}>
        <div className="text-xs font-semibold mb-3" style={{ color: 'var(--pm-text)' }}>
          Accent Color
        </div>
        <div className="flex gap-3">
          {[
            { key: 'blue',   hex: '#3b82f6' },
            { key: 'purple', hex: '#a855f7' },
            { key: 'green',  hex: '#22c55e' },
            { key: 'orange', hex: '#f97316' },
          ].map(({ key, hex }) => {
            const active = accentColor === key;
            return (
              <button
                key={key}
                onClick={() => setAccent(key)}
                title={key.charAt(0).toUpperCase() + key.slice(1)}
                className="rounded-full cursor-pointer transition-all"
                style={{
                  width: '26px',
                  height: '26px',
                  background: hex,
                  outline: active ? `3px solid ${hex}` : '3px solid transparent',
                  outlineOffset: '2px',
                  boxShadow: active ? `0 0 10px ${hex}66` : 'none',
                }}
              />
            );
          })}
        </div>
      </div>

      <Toggle
        value={settings?.appearance?.animations ?? true}
        onChange={(v) => updateSettings('appearance', 'animations', v)}
        label="Animations"
        desc="Enable motion and transition effects throughout the UI."
      />
      <Toggle
        value={settings?.appearance?.glass ?? true}
        onChange={(v) => updateSettings('appearance', 'glass', v)}
        label="Glass Effects"
        desc="Enable frosted glass / backdrop-blur on panels and modals."
      />
    </div>
  );

  const renderAccount = () => (
    <div>
      <SectionHeading
        title="Account"
        desc="Manage your PinMind account and profile."
      />

      {/* Profile Card */}
      <div
        className="rounded-xl p-5 mb-5 flex items-center gap-4"
        style={{ background: 'var(--pm-surface-2)', border: '1px solid var(--pm-border)' }}
      >
        {currentUser?.photoURL ? (
          <img
            src={currentUser.photoURL}
            alt="avatar"
            className="rounded-full object-cover shrink-0"
            style={{ width: '56px', height: '56px' }}
          />
        ) : (
          <div
            className="rounded-full flex items-center justify-center shrink-0 text-lg font-bold"
            style={{
              width: '56px',
              height: '56px',
              background: 'var(--accent-dim)',
              color: 'var(--accent)',
            }}
          >
            {(currentUser?.displayName?.[0] || currentUser?.email?.[0] || '?').toUpperCase()}
          </div>
        )}
        <div className="min-w-0">
          <div className="text-sm font-bold truncate" style={{ color: 'var(--pm-text)' }}>
            {currentUser?.displayName || 'Anonymous'}
          </div>
          <div className="text-xs truncate mt-0.5" style={{ color: 'var(--pm-text-muted)' }}>
            {currentUser?.email}
          </div>
          <div className="text-[10px] mt-1 font-mono" style={{ color: 'var(--pm-text-muted)' }}>
            Member since {formatCreationDate(currentUser?.metadata?.creationTime)}
          </div>
        </div>
      </div>

      {/* Manage Account Button */}
      <div className="flex flex-col gap-2 mb-4">
        <button
          className="text-xs font-semibold px-4 py-2.5 rounded-lg transition-all cursor-pointer"
          style={{
            background: 'transparent',
            border: '1px solid var(--pm-border-2)',
            color: 'var(--pm-text)',
          }}
          onClick={() => toast.info('Account management coming soon.')}
        >
          Manage Account
        </button>
        <button
          className="text-xs font-semibold px-4 py-2.5 rounded-lg transition-all cursor-pointer"
          style={{
            background: 'transparent',
            border: '1px solid var(--error)',
            color: 'var(--error)',
          }}
          onClick={handleSignOut}
        >
          Sign Out
        </button>
      </div>
    </div>
  );

  const renderGemini = () => {
    const connected = apiStatus?.has_key;
    return (
      <div>
        <SectionHeading
          title="Gemini API"
          desc="Connect your Google Gemini API key to enable AI-powered firmware generation."
        />

        {/* Status Badge */}
        <div className="flex items-center gap-2 mb-5">
          <span className="text-xs font-semibold" style={{ color: 'var(--pm-text-muted)' }}>
            Status:
          </span>
          <span
            className="text-[10px] font-bold px-2.5 py-1 rounded-full font-mono"
            style={
              connected
                ? { background: 'rgba(34,197,94,0.12)', color: 'var(--success)' }
                : { background: 'rgba(249,115,22,0.12)', color: 'var(--warning)' }
            }
          >
            {connected ? '● CONNECTED' : '○ NOT CONNECTED'}
          </span>
        </div>

        {connected ? (
          /* Connected state */
          <div>
            <div
              className="rounded-xl p-4 mb-4 flex items-center justify-between gap-4"
              style={{ background: 'var(--pm-surface-2)', border: '1px solid var(--pm-border)' }}
            >
              <div>
                <div className="text-[10px] font-mono mb-1" style={{ color: 'var(--pm-text-muted)' }}>
                  Saved API Key
                </div>
                <div className="text-sm font-mono tracking-widest" style={{ color: 'var(--pm-text)' }}>
                  ●●●●●●●●●●●●●●●●
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleTestKey('')}
                  disabled={apiTestLoading}
                  className="text-[10px] font-bold px-3 py-1.5 rounded-lg cursor-pointer transition-all"
                  style={{
                    background: 'var(--accent-dim)',
                    color: 'var(--accent)',
                    border: '1px solid var(--accent-border)',
                    opacity: apiTestLoading ? 0.6 : 1,
                  }}
                >
                  {apiTestLoading ? 'Testing…' : 'Test'}
                </button>
                <button
                  onClick={handleRemoveKey}
                  disabled={apiLoading}
                  className="text-[10px] font-bold px-3 py-1.5 rounded-lg cursor-pointer transition-all"
                  style={{
                    background: 'transparent',
                    color: 'var(--error)',
                    border: '1px solid var(--error)',
                    opacity: apiLoading ? 0.6 : 1,
                  }}
                >
                  Remove
                </button>
              </div>
            </div>

            {/* Update key */}
            <div className="text-xs font-semibold mb-2" style={{ color: 'var(--pm-text)' }}>
              Update API Key
            </div>
            <div className="flex gap-2 mb-3">
              <input
                type="password"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                placeholder="Enter new API key…"
                className="flex-1 text-xs px-3 py-2.5 rounded-lg font-mono outline-none"
                style={{
                  background: 'var(--pm-surface-2)',
                  border: '1px solid var(--pm-border)',
                  color: 'var(--pm-text)',
                }}
              />
              <button
                onClick={handleSaveKey}
                disabled={apiLoading || !apiKeyInput.trim()}
                className="text-[10px] font-bold px-4 py-2.5 rounded-lg cursor-pointer transition-all"
                style={{
                  background: 'var(--accent)',
                  color: '#fff',
                  opacity: apiLoading || !apiKeyInput.trim() ? 0.5 : 1,
                }}
              >
                {apiLoading ? 'Saving…' : 'Update'}
              </button>
            </div>
          </div>
        ) : (
          /* Not connected state */
          <div>
            <div className="text-xs font-semibold mb-2" style={{ color: 'var(--pm-text)' }}>
              Enter your Gemini API Key
            </div>
            <div className="flex gap-2 mb-3">
              <input
                type="password"
                value={apiKeyInput}
                onChange={(e) => { setApiKeyInput(e.target.value); setApiTestResult(null); }}
                placeholder="AIza…"
                className="flex-1 text-xs px-3 py-2.5 rounded-lg font-mono outline-none"
                style={{
                  background: 'var(--pm-surface-2)',
                  border: '1px solid var(--pm-border)',
                  color: 'var(--pm-text)',
                }}
              />
              <button
                onClick={() => handleTestKey(apiKeyInput)}
                disabled={apiTestLoading || !apiKeyInput.trim()}
                className="text-[10px] font-bold px-3 py-2.5 rounded-lg cursor-pointer transition-all shrink-0"
                style={{
                  background: 'var(--accent-dim)',
                  color: 'var(--accent)',
                  border: '1px solid var(--accent-border)',
                  opacity: apiTestLoading || !apiKeyInput.trim() ? 0.5 : 1,
                }}
              >
                {apiTestLoading ? 'Testing…' : 'Test'}
              </button>
              <button
                onClick={handleSaveKey}
                disabled={apiLoading || !apiKeyInput.trim()}
                className="text-[10px] font-bold px-4 py-2.5 rounded-lg cursor-pointer transition-all shrink-0"
                style={{
                  background: 'var(--accent)',
                  color: '#fff',
                  opacity: apiLoading || !apiKeyInput.trim() ? 0.5 : 1,
                }}
              >
                {apiLoading ? 'Saving…' : 'Save'}
              </button>
            </div>
          </div>
        )}

        {/* Test Result */}
        {apiTestResult && (
          <div
            className="mt-3 text-xs px-4 py-2.5 rounded-lg font-mono"
            style={{
              background: apiTestResult.ok ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)',
              color: apiTestResult.ok ? 'var(--success)' : 'var(--error)',
              border: `1px solid ${apiTestResult.ok ? 'var(--success)' : 'var(--error)'}`,
            }}
          >
            {apiTestResult.ok ? '✓ ' : '✗ '}{apiTestResult.msg}
          </div>
        )}

        <div className="mt-4 text-[10px] font-mono" style={{ color: 'var(--pm-text-muted)' }}>
          Get a free API key at{' '}
          <a
            href="https://aistudio.google.com/app/apikey"
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: 'var(--accent)' }}
          >
            aistudio.google.com
          </a>
          . Your key is encrypted and stored securely.
        </div>
      </div>
    );
  };

  const renderEditor = () => (
    <div>
      <SectionHeading
        title="Editor"
        desc="Configure the code editor appearance and behavior."
      />
      <Field label="Font Family" desc="Monospace font used in the code editor.">
        <Segmented
          value={settings?.editor?.fontFamily ?? 'jetbrains'}
          onChange={(v) => updateSettings('editor', 'fontFamily', v)}
          options={[
            { value: 'jetbrains', label: 'JetBrains' },
            { value: 'fira',     label: 'Fira Code' },
            { value: 'cascadia', label: 'Cascadia' },
          ]}
        />
      </Field>
      <Field label="Font Size" desc="Base font size for the code editor.">
        <Segmented
          value={settings?.editor?.fontSize ?? 'medium'}
          onChange={(v) => updateSettings('editor', 'fontSize', v)}
          options={[
            { value: 'small',  label: 'Small' },
            { value: 'medium', label: 'Medium' },
            { value: 'large',  label: 'Large' },
          ]}
        />
      </Field>
      <Field label="Tab Size" desc="Number of spaces per tab indent.">
        <Segmented
          value={String(settings?.editor?.tabSize ?? '4')}
          onChange={(v) => updateSettings('editor', 'tabSize', v)}
          options={[
            { value: '2', label: '2' },
            { value: '4', label: '4' },
            { value: '8', label: '8' },
          ]}
        />
      </Field>
      <Toggle
        value={settings?.editor?.wordWrap ?? false}
        onChange={(v) => updateSettings('editor', 'wordWrap', v)}
        label="Word Wrap"
        desc="Wrap long lines to avoid horizontal scrolling."
      />
      <Toggle
        value={settings?.editor?.lineNumbers ?? true}
        onChange={(v) => updateSettings('editor', 'lineNumbers', v)}
        label="Line Numbers"
        desc="Show line numbers in the gutter."
      />
      <Toggle
        value={settings?.editor?.minimap ?? true}
        onChange={(v) => updateSettings('editor', 'minimap', v)}
        label="Minimap"
        desc="Show a scaled-down overview of the entire file on the right."
      />
      <Toggle
        value={settings?.editor?.autoCopy ?? false}
        onChange={(v) => updateSettings('editor', 'autoCopy', v)}
        label="Auto Copy Generated Code"
        desc="Automatically copy AI-generated code to clipboard."
      />
      <Toggle
        value={settings?.editor?.autoSave ?? true}
        onChange={(v) => updateSettings('editor', 'autoSave', v)}
        label="Auto Save Chat"
        desc="Automatically persist chat sessions to your workspace."
      />
    </div>
  );

  const renderAI = () => (
    <div>
      <SectionHeading
        title="AI Settings"
        desc="Configure how PinMind's AI generates and presents firmware code."
      />
      <Field label="Preferred Model" desc="Gemini model used for all AI generation tasks.">
        <Segmented
          value={settings?.ai?.model ?? 'flash'}
          onChange={(v) => updateSettings('ai', 'model', v)}
          options={[
            { value: 'flash', label: 'Flash 2.5' },
            { value: 'pro',   label: 'Pro 2.5', badge: 'BETA' },
          ]}
        />
      </Field>
      <Field label="Generation Style" desc="Controls verbosity and detail of AI responses.">
        <Segmented
          value={settings?.ai?.generationStyle ?? 'standard'}
          onChange={(v) => updateSettings('ai', 'generationStyle', v)}
          options={[
            { value: 'minimal',  label: 'Minimal' },
            { value: 'standard', label: 'Standard' },
            { value: 'detailed', label: 'Detailed' },
          ]}
        />
      </Field>
      <Field label="Code Style" desc="Target firmware framework for generated code.">
        <Segmented
          value={settings?.ai?.codeStyle ?? 'hal'}
          onChange={(v) => updateSettings('ai', 'codeStyle', v)}
          options={[
            { value: 'baremetal', label: 'Bare Metal' },
            { value: 'hal',       label: 'HAL' },
            { value: 'espidf',    label: 'ESP-IDF' },
            { value: 'arduino',   label: 'Arduino' },
          ]}
        />
      </Field>
      <Field label="Comment Style" desc="How much inline documentation to include in generated code.">
        <Segmented
          value={settings?.ai?.commentStyle ?? 'standard'}
          onChange={(v) => updateSettings('ai', 'commentStyle', v)}
          options={[
            { value: 'minimal',  label: 'Minimal' },
            { value: 'standard', label: 'Standard' },
            { value: 'detailed', label: 'Detailed' },
          ]}
        />
      </Field>
    </div>
  );

  const MCU_OPTIONS = [
    { value: 'stm32f401', label: 'STM32F401' },
    { value: 'stm32f103', label: 'STM32F103 (Blue Pill)' },
    { value: 'esp32',     label: 'ESP32' },
    { value: 'esp8266',   label: 'ESP8266' },
    { value: 'rp2040',    label: 'RP2040 (Raspberry Pi Pico)' },
    { value: 'attiny85',  label: 'ATtiny85' },
    { value: 'atmega328', label: 'ATmega328P (Arduino Uno)' },
  ];

  const TEMPLATE_OPTIONS = [
    { value: 'blank',    label: 'Blank Project' },
    { value: 'stm32f401',label: 'STM32F401 Starter' },
    { value: 'esp32',    label: 'ESP32 Starter' },
    { value: 'rp2040',   label: 'RP2040 Starter' },
    { value: 'avr',      label: 'AVR Starter' },
    { value: 'arduino',  label: 'Arduino Starter' },
  ];

  const selectStyle = {
    background: 'var(--pm-surface-2)',
    border: '1px solid var(--pm-border)',
    color: 'var(--pm-text)',
    borderRadius: '8px',
    padding: '6px 10px',
    fontSize: '11px',
    fontFamily: 'inherit',
    cursor: 'pointer',
    outline: 'none',
    minWidth: '180px',
  };

  const renderWorkspace = () => (
    <div>
      <SectionHeading
        title="Workspace"
        desc="Default configuration applied when creating new workspaces."
      />
      <Field label="Default MCU" desc="Microcontroller pre-selected for new workspaces.">
        <select
          value={settings?.hardware?.defaultMcu ?? 'stm32f401'}
          onChange={(e) => updateSettings('hardware', 'defaultMcu', e.target.value)}
          style={selectStyle}
        >
          {MCU_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </Field>
      <Field label="Default Template" desc="Project template applied when creating a new workspace.">
        <select
          value={settings?.hardware?.defaultTemplate ?? 'blank'}
          onChange={(e) => updateSettings('hardware', 'defaultTemplate', e.target.value)}
          style={selectStyle}
        >
          {TEMPLATE_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </Field>
      <Toggle
        value={settings?.hardware?.autoValidation ?? true}
        onChange={(v) => updateSettings('hardware', 'autoValidation', v)}
        label="Auto Validation"
        desc="Automatically validate pin assignments whenever the hardware graph changes."
      />
      <Toggle
        value={settings?.hardware?.autoBuildGraph ?? true}
        onChange={(v) => updateSettings('hardware', 'autoBuildGraph', v)}
        label="Auto Build Hardware Graph"
        desc="Rebuild the hardware graph automatically after each AI generation."
      />
    </div>
  );

  const renderPrivacy = () => (
    <div>
      <SectionHeading
        title="Privacy & Security"
        desc="Manage your data and account security."
      />

      {/* Data exports */}
      <div className="mb-6">
        <div className="text-xs font-semibold mb-3" style={{ color: 'var(--pm-text)' }}>
          Data Export
        </div>
        <div className="flex flex-col gap-2">
          <button
            className="flex items-center gap-2 text-xs font-semibold px-4 py-2.5 rounded-lg transition-all cursor-pointer w-fit"
            style={{
              background: 'var(--pm-surface-2)',
              border: '1px solid var(--pm-border-2)',
              color: 'var(--pm-text)',
            }}
            onClick={() => toast.info('Workspace export coming soon.')}
          >
            <IconDownload />
            Export Workspace
          </button>
          <button
            className="flex items-center gap-2 text-xs font-semibold px-4 py-2.5 rounded-lg transition-all cursor-pointer w-fit"
            style={{
              background: 'var(--pm-surface-2)',
              border: '1px solid var(--pm-border-2)',
              color: 'var(--pm-text)',
            }}
            onClick={() => toast.info('Chat history export coming soon.')}
          >
            <IconDownload />
            Download Chat History
          </button>
        </div>
      </div>

      {/* Danger Zone */}
      <div
        className="rounded-xl p-5"
        style={{ borderLeft: '3px solid var(--error)', background: 'rgba(239,68,68,0.04)' }}
      >
        <div className="text-xs font-bold mb-4 uppercase tracking-wider" style={{ color: 'var(--error)' }}>
          Danger Zone
        </div>

        <div className="flex flex-col gap-3">
          {/* Delete Chat History */}
          <div className="flex items-center justify-between gap-4">
            <div>
              <div className="text-xs font-semibold" style={{ color: 'var(--pm-text)' }}>
                Delete Chat History
              </div>
              <div className="text-[10px] font-mono mt-0.5" style={{ color: 'var(--pm-text-muted)' }}>
                Permanently delete all AI conversation history.
              </div>
            </div>
            <button
              className="text-[10px] font-bold px-3 py-1.5 rounded-lg cursor-pointer shrink-0 transition-all"
              style={{ background: 'transparent', border: '1px solid var(--error)', color: 'var(--error)' }}
              onClick={() => {
                if (window.confirm('Delete all chat history? This cannot be undone.')) {
                  toast.warning('Chat history deletion coming soon.');
                }
              }}
            >
              Delete History
            </button>
          </div>

          {/* Delete All Workspaces */}
          <div className="flex items-center justify-between gap-4">
            <div>
              <div className="text-xs font-semibold" style={{ color: 'var(--pm-text)' }}>
                Delete All Workspaces
              </div>
              <div className="text-[10px] font-mono mt-0.5" style={{ color: 'var(--pm-text-muted)' }}>
                Remove every workspace, project, and generated file.
              </div>
            </div>
            <button
              className="text-[10px] font-bold px-3 py-1.5 rounded-lg cursor-pointer shrink-0 transition-all"
              style={{ background: 'transparent', border: '1px solid var(--error)', color: 'var(--error)' }}
              onClick={() => {
                if (window.confirm('Delete ALL workspaces? This cannot be undone.')) {
                  toast.warning('Workspace deletion coming soon.');
                }
              }}
            >
              Delete All
            </button>
          </div>

          {/* Delete Account */}
          <div
            className="flex items-center justify-between gap-4 pt-3 mt-2 border-t"
            style={{ borderColor: 'rgba(239,68,68,0.25)' }}
          >
            <div>
              <div className="text-xs font-bold" style={{ color: 'var(--error)' }}>
                Delete Account
              </div>
              <div className="text-[10px] font-mono mt-0.5" style={{ color: 'var(--pm-text-muted)' }}>
                Permanently delete your account and all associated data. This action is irreversible.
              </div>
            </div>
            <button
              className="text-[10px] font-bold px-4 py-2 rounded-lg cursor-pointer shrink-0 transition-all"
              style={{ background: 'var(--error)', color: '#fff' }}
              onClick={() => {
                const first = window.confirm(
                  'Are you sure you want to delete your account? All data will be permanently removed.'
                );
                if (!first) return;
                const second = window.confirm(
                  'This is your final confirmation. Your account CANNOT be recovered. Continue?'
                );
                if (second) {
                  toast.warning('Account deletion coming soon. Contact support@pinmind.dev.');
                }
              }}
            >
              Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderNotifications = () => (
    <div>
      <SectionHeading
        title="Notifications"
        desc="Choose which events trigger notifications."
      />
      <Toggle
        value={settings?.notifications?.firmwareComplete ?? true}
        onChange={(v) => updateSettings('notifications', 'firmwareComplete', v)}
        label="Firmware Generation Complete"
        desc="Notify when AI finishes generating firmware code."
      />
      <Toggle
        value={settings?.notifications?.validationErrors ?? true}
        onChange={(v) => updateSettings('notifications', 'validationErrors', v)}
        label="Validation Errors"
        desc="Notify when pin assignment or hardware validation finds issues."
      />
      <Toggle
        value={settings?.notifications?.workspaceUpdates ?? false}
        onChange={(v) => updateSettings('notifications', 'workspaceUpdates', v)}
        label="Workspace Updates"
        desc="Notify when collaborators make changes to shared workspaces."
      />
      <Toggle
        value={settings?.notifications?.productUpdates ?? true}
        onChange={(v) => updateSettings('notifications', 'productUpdates', v)}
        label="Product Updates"
        desc="Receive announcements about new PinMind features and releases."
      />
    </div>
  );

  const AboutLink = ({ href, label }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-1.5 text-xs transition-all"
      style={{ color: 'var(--accent)' }}
    >
      {label}
      <IconExternal />
    </a>
  );

  const renderAbout = () => (
    <div>
      <SectionHeading title="About PinMind" desc="Version and legal information." />

      {/* Version info */}
      <div
        className="rounded-xl p-4 mb-5"
        style={{ background: 'var(--pm-surface-2)', border: '1px solid var(--pm-border)' }}
      >
        {[
          { label: 'Version', value: 'v1.0.0' },
          { label: 'Build',   value: '2026.06' },
          { label: 'License', value: 'MIT' },
        ].map(({ label, value }) => (
          <div
            key={label}
            className="flex justify-between items-center py-2.5 border-b last:border-0"
            style={{ borderColor: 'var(--pm-border)' }}
          >
            <span className="text-xs font-semibold" style={{ color: 'var(--pm-text)' }}>{label}</span>
            <span className="text-xs font-mono" style={{ color: 'var(--pm-text-muted)' }}>{value}</span>
          </div>
        ))}
      </div>

      {/* Links */}
      <div className="flex flex-col gap-3">
        <AboutLink href="https://github.com/KarthikeyanUzumaki/PinMind_model" label="GitHub Repository" />
        <AboutLink href="https://github.com/KarthikeyanUzumaki/PinMind_model/wiki" label="Documentation" />
        <AboutLink href="https://github.com/KarthikeyanUzumaki/PinMind_model/blob/main/PRIVACY.md" label="Privacy Policy" />
        <AboutLink href="https://github.com/KarthikeyanUzumaki/PinMind_model/blob/main/TERMS.md" label="Terms of Service" />
        <AboutLink href="https://github.com/KarthikeyanUzumaki/PinMind_model/issues/new" label="Report a Bug" />
      </div>

      {/* Footer credit */}
      <div
        className="mt-8 text-center text-[10px] font-mono"
        style={{ color: 'var(--pm-text-muted)' }}
      >
        Built with ❤️ by Karthikeyan · PinMind © 2026
      </div>
    </div>
  );

  const SECTION_RENDERERS = {
    general:       renderGeneral,
    account:       renderAccount,
    gemini:        renderGemini,
    editor:        renderEditor,
    about:         renderAbout,
  };

  // ─── Layout ─────────────────────────────────────────────────────────────────

  return (
    <div
      className="flex"
      style={{ height: '100vh', background: 'var(--pm-bg)', overflow: 'hidden' }}
    >
      {/* ── Sidebar ─────────────────────────────────────────────────────────── */}
      <aside
        className="flex flex-col"
        style={{
          width: '240px',
          minWidth: '240px',
          height: '100vh',
          background: 'var(--pm-surface)',
          borderRight: '1px solid var(--pm-border)',
          overflowY: 'auto',
        }}
      >
        {/* Sidebar Header */}
        <div
          className="px-4 pt-5 pb-4 border-b"
          style={{ borderColor: 'var(--pm-border)' }}
        >
          {/* Back Button */}
          <button
            onClick={onBack}
            className="flex items-center gap-1.5 text-xs font-medium mb-4 transition-all cursor-pointer"
            style={{ color: 'var(--pm-text-muted)' }}
            onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--pm-text)')}
            onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--pm-text-muted)')}
          >
            <IconBack />
            Back to Workspace
          </button>

          {/* Logo + Title */}
          <div className="flex items-center gap-2.5">
            <div
              className="flex items-center justify-center rounded-lg"
              style={{
                width: '28px',
                height: '28px',
                background: 'var(--accent)',
                boxShadow: 'var(--accent-glow)',
                flexShrink: 0,
              }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="3" />
                <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" />
              </svg>
            </div>
            <div>
              <div className="text-xs font-bold" style={{ color: 'var(--pm-text)' }}>
                PinMind
              </div>
              <div className="text-[10px] font-mono" style={{ color: 'var(--pm-text-muted)' }}>
                Settings
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex flex-col gap-0.5 p-3 flex-1">
          {NAV_ITEMS.map(({ id, label, Icon }) => {
            const active = activeSection === id;
            return (
              <button
                key={id}
                onClick={() => setActiveSection(id)}
                className="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-xs font-medium transition-all cursor-pointer text-left"
                style={{
                  background: active ? 'var(--accent-dim)' : 'transparent',
                  color: active ? 'var(--accent)' : 'var(--pm-text-muted)',
                  border: 'none',
                }}
                onMouseEnter={(e) => {
                  if (!active) {
                    e.currentTarget.style.background = 'var(--pm-surface-2)';
                    e.currentTarget.style.color = 'var(--pm-text)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!active) {
                    e.currentTarget.style.background = 'transparent';
                    e.currentTarget.style.color = 'var(--pm-text-muted)';
                  }
                }}
              >
                <Icon />
                {label}
              </button>
            );
          })}
        </nav>
      </aside>

      {/* ── Content Panel ────────────────────────────────────────────────────── */}
      <main
        className="flex-1"
        style={{ overflowY: 'auto', height: '100vh' }}
      >
        <div style={{ maxWidth: '672px', margin: '0 auto', padding: '32px 24px 80px' }}>
          {(SECTION_RENDERERS[activeSection] ?? renderGeneral)()}
        </div>
      </main>
    </div>
  );
}
