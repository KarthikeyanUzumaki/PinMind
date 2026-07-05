// useTheme.js — Dark / Light / System theme manager
// Reads from localStorage, falls back to OS preference
// Applies data-theme and data-accent attributes to <html>

import { useState, useEffect } from 'react';

const STORAGE_KEY = 'pm-theme-v2';

const getSystemTheme = () =>
  window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

const getInitialTheme = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return JSON.parse(stored);
  } catch (_) {}
  return { mode: 'system', accent: 'blue' };
};

const resolveMode = (mode) =>
  mode === 'system' ? getSystemTheme() : mode;

export function useTheme() {
  const [prefs, setPrefs] = useState(getInitialTheme);

  // Apply data-theme and data-accent to <html> whenever prefs change
  useEffect(() => {
    const html = document.documentElement;
    html.setAttribute('data-theme', resolveMode(prefs.mode));
    html.setAttribute('data-accent', prefs.accent || 'blue');
  }, [prefs]);

  // Listen for OS preference changes (when mode === 'system')
  useEffect(() => {
    if (prefs.mode !== 'system') return;
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = () => {
      document.documentElement.setAttribute('data-theme', getSystemTheme());
    };
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [prefs.mode]);

  const setTheme = (mode) => {
    setPrefs(prev => {
      const next = { ...prev, mode };
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(next)); } catch (_) {}
      return next;
    });
  };

  const setAccent = (accent) => {
    setPrefs(prev => {
      const next = { ...prev, accent };
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(next)); } catch (_) {}
      return next;
    });
  };

  return {
    themeMode: prefs.mode,            // 'dark' | 'light' | 'system'
    accentColor: prefs.accent,        // 'blue' | 'purple' | 'green' | 'orange'
    resolvedTheme: resolveMode(prefs.mode), // actual 'dark' or 'light'
    setTheme,
    setAccent,
  };
}
