// App.jsx — Root router and theme provider
// Manages auth, currentView, theme, settings, command palette

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { auth, loginWithGoogle } from './firebase';
import { onAuthStateChanged } from 'firebase/auth';

import { useTheme } from './hooks/useTheme';
import { useSettings, applySettingsToDOM } from './hooks/useSettings';
import { ToastProvider, useToast } from './hooks/useToast.jsx';

import LandingPage      from './pages/LandingPage';
import OnboardingPage   from './pages/OnboardingPage';
import WorkspacePage    from './pages/WorkspacePage';
import SettingsPage     from './pages/SettingsPage';
import CommandPalette   from './components/CommandPalette';

const BACKEND_URL = 'http://localhost:8000';

// ─── Spinner shown during Firebase session restoration ───────────────────────
const SessionSpinner = () => (
  <div
    className="h-screen w-screen flex items-center justify-center"
    style={{ background: 'var(--pm-bg)' }}
  >
    <div className="flex items-center gap-3">
      <div
        className="w-5 h-5 border-2 rounded-full animate-spin"
        style={{ borderColor: 'var(--accent)', borderTopColor: 'transparent' }}
      />
      <span className="text-xs font-mono-editor uppercase tracking-widest" style={{ color: 'var(--pm-text-muted)' }}>
        Restoring Session…
      </span>
    </div>
  </div>
);

// ─── Screen shown if backend connection fails ────────────────────────────────
const ConnectionErrorScreen = ({ onRetry }) => (
  <div
    className="h-screen w-screen flex flex-col items-center justify-center p-6 text-center"
    style={{ background: 'var(--pm-bg)' }}
  >
    <div className="max-w-sm space-y-4 font-mono-editor">
      <div className="text-[var(--error)] text-lg font-bold">⚠️ CONNECTION ERROR</div>
      <p className="text-xs text-[var(--pm-text-muted)] leading-relaxed">
        Unable to connect to the PinMind Firmware Intelligence API. Please verify that the backend server is running and accessible.
      </p>
      <button
        onClick={onRetry}
        className="px-6 py-2.5 bg-[var(--accent)] text-white text-xs font-bold rounded-xl cursor-pointer hover:brightness-110 transition-all"
        style={{ boxShadow: '0 4px 12px var(--accent-glow)' }}
      >
        Retry Connection
      </button>
    </div>
  </div>
);

// ─── Inner app — has access to ToastContext ───────────────────────────────────
function AppInner() {
  const { toast } = useToast();

  // Theme & settings
  const { themeMode, accentColor, resolvedTheme, setTheme, setAccent } = useTheme();
  const [currentUser, setCurrentUser] = useState(null);
  const [authToken,   setAuthToken]   = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [connectionError, setConnectionError] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  const { settings, updateSettings } = useSettings(authToken);

  // Apply settings DOM attributes on mount
  useEffect(() => { applySettingsToDOM(settings); }, []);

  // User settings from backend (e.g. has_key)
  const [userSettings, setUserSettings] = useState({ has_key: false });

  // View routing
  // Views: 'landing' | 'onboarding' | 'workspace' | 'settings'
  const [currentView, setCurrentView] = useState('landing');

  // Command palette
  const [paletteOpen, setPaletteOpen] = useState(false);

  // ── Backend user settings ─────────────────────────────────────────────────
  const fetchUserSettings = useCallback(async (token) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/user/settings`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUserSettings(data);
        setConnectionError(false);
        return data;
      }
    } catch (_) {
      setConnectionError(true);
    }
    return null;
  }, []);

  const handleRetryConnection = () => {
    setConnectionError(false);
    setRetryCount(prev => prev + 1);
  };

  // ── Firebase auth listener ────────────────────────────────────────────────
  useEffect(() => {
    const unsub = onAuthStateChanged(auth, async (user) => {
      setAuthLoading(true);
      setConnectionError(false);
      if (user) {
        setCurrentUser(user);
        try {
          const token = await user.getIdToken();
          setAuthToken(token);
          const data = await fetchUserSettings(token);
          if (data) {
            if (!data.has_key) {
              setCurrentView('onboarding');
            } else {
              setCurrentView('workspace');
            }
          }
        } catch (e) {
          console.error(e);
          setConnectionError(true);
        }
      } else {
        setCurrentUser(null);
        setAuthToken(null);
        setCurrentView('landing');
      }
      setAuthLoading(false);
    });
    return () => unsub();
  }, [retryCount]);

  // ── Global keyboard shortcuts ─────────────────────────────────────────────
  useEffect(() => {
    const handler = (e) => {
      const ctrl = e.ctrlKey || e.metaKey;
      if (ctrl && e.key === 'k') { e.preventDefault(); setPaletteOpen(p => !p); }
      if (ctrl && e.key === ',') { e.preventDefault(); if (currentUser) setCurrentView('settings'); }
      if (e.key === 'Escape')    { setPaletteOpen(false); }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [currentUser]);

  // ── Command palette commands ──────────────────────────────────────────────
  const paletteCommands = [
    {
      id: 'settings',
      label: 'Open Settings',
      desc: 'Appearance, API, Editor, AI preferences',
      category: 'navigation',
      shortcut: 'Ctrl+,',
      action: () => setCurrentView('settings'),
    },
    {
      id: 'workspace',
      label: 'Go to Workspace',
      desc: 'Firmware Intelligence Workspace',
      category: 'navigation',
      action: () => setCurrentView('workspace'),
    },
    {
      id: 'theme-toggle',
      label: 'Toggle Theme',
      desc: `Current: ${themeMode} → switch to ${themeMode === 'dark' ? 'light' : 'dark'}`,
      category: 'action',
      action: () => setTheme(themeMode === 'dark' ? 'light' : 'dark'),
    },
    {
      id: 'theme-dark',
      label: 'Switch to Dark Mode',
      category: 'action',
      action: () => setTheme('dark'),
    },
    {
      id: 'theme-light',
      label: 'Switch to Light Mode',
      category: 'action',
      action: () => setTheme('light'),
    },
    {
      id: 'accent-blue',
      label: 'Set Accent: Blue',
      category: 'action',
      action: () => setAccent('blue'),
    },
    {
      id: 'accent-purple',
      label: 'Set Accent: Purple',
      category: 'action',
      action: () => setAccent('purple'),
    },
    {
      id: 'accent-green',
      label: 'Set Accent: Green',
      category: 'action',
      action: () => setAccent('green'),
    },
    {
      id: 'accent-orange',
      label: 'Set Accent: Orange',
      category: 'action',
      action: () => setAccent('orange'),
    },
    {
      id: 'signout',
      label: 'Sign Out',
      desc: 'Return to the landing page',
      category: 'account',
      action: async () => {
        const { logoutUser } = await import('./firebase');
        await logoutUser();
        setCurrentView('landing');
      },
    },
  ];

  // ── Page transitions ──────────────────────────────────────────────────────
  const pageVariants = {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { duration: 0.18 } },
    exit:    { opacity: 0, transition: { duration: 0.12 } },
  };

  // ── Render ────────────────────────────────────────────────────────────────
  if (authLoading) return <SessionSpinner />;
  if (connectionError) return <ConnectionErrorScreen onRetry={handleRetryConnection} />;

  return (
    <>
      <AnimatePresence mode="wait">
        {currentView === 'landing' && (
          <motion.div key="landing" {...pageVariants}>
            <LandingPage onGetStarted={loginWithGoogle} />
          </motion.div>
        )}

        {currentView === 'onboarding' && (
          <motion.div key="onboarding" {...pageVariants}>
            <OnboardingPage
              authToken={authToken}
              onComplete={() => {
                fetchUserSettings(authToken).then(d => {
                  setUserSettings(d || { has_key: true });
                  setCurrentView('workspace');
                  toast.success('Gemini API connected! Welcome to PinMind.');
                });
              }}
            />
          </motion.div>
        )}

        {currentView === 'workspace' && (
          <motion.div key="workspace" {...pageVariants} style={{ height: '100vh', overflow: 'hidden' }}>
            <WorkspacePage
              currentUser={currentUser}
              authToken={authToken}
              userSettings={userSettings}
              setUserSettings={setUserSettings}
              onNavigateToSettings={() => setCurrentView('settings')}
              onOpenCommandPalette={() => setPaletteOpen(true)}
              toast={toast}
            />
          </motion.div>
        )}

        {currentView === 'settings' && (
          <motion.div key="settings" {...pageVariants} style={{ height: '100vh', overflow: 'hidden' }}>
            <SettingsPage
              currentUser={currentUser}
              authToken={authToken}
              settings={settings}
              updateSettings={updateSettings}
              themeMode={themeMode}
              setTheme={setTheme}
              accentColor={accentColor}
              setAccent={setAccent}
              onBack={() => setCurrentView('workspace')}
              toast={toast}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Command Palette — rendered above everything */}
      <CommandPalette
        isOpen={paletteOpen}
        onClose={() => setPaletteOpen(false)}
        commands={paletteCommands}
      />
    </>
  );
}

// ─── Root — wraps AppInner in ToastProvider ───────────────────────────────────
export default function App() {
  return (
    <ToastProvider>
      <AppInner />
    </ToastProvider>
  );
}