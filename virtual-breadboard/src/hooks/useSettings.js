// useSettings.js — All user preferences stored in localStorage & synced with cloud backend
// Covers: appearance, editor, AI, hardware, notifications

import { useState, useEffect } from 'react';

const STORAGE_KEY = 'pm-settings-v2';

const DEFAULT_SETTINGS = {
  appearance: {
    fontFamily:  'jetbrains',  // 'jetbrains' | 'fira' | 'cascadia'
    fontSize:    'medium',     // 'small' | 'medium' | 'large'
    density:     'comfortable',// 'compact' | 'comfortable'
    animations:  true,
    glass:       true,
  },
  editor: {
    wordWrap:    false,
    lineNumbers: true,
    minimap:     false,
    autoCopy:    false,
    language:    'c',          // 'c' | 'cpp' | 'rust'
    tabSize:     4,            // 2 | 4 | 8
    autoSave:    true,
  },
  ai: {
    model:           'gemini-2.5-flash',  // 'gemini-2.5-flash' | 'gemini-2.5-pro'
    generationStyle: 'standard',          // 'minimal' | 'standard' | 'detailed'
    codeStyle:       'bare-metal',        // 'bare-metal' | 'hal' | 'esp-idf' | 'arduino'
    commentStyle:    'standard',          // 'minimal' | 'standard' | 'detailed'
  },
  hardware: {
    defaultMcu:       'STM32F401',
    autoValidation:   true,
    autoBuildGraph:   true,
    defaultTemplate:  'blank',   // 'stm32' | 'esp32' | 'rp2040' | 'avr' | 'arduino' | 'blank'
    codingStandard:   'cmsis',   // 'cmsis' | 'hal' | 'bare'
  },
  notifications: {
    firmwareComplete:  true,
    validationErrors:  true,
    workspaceUpdates:  false,
    productUpdates:    false,
  },
};

const loadSettings = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      // Deep merge with defaults (so new keys always appear)
      return deepMerge(DEFAULT_SETTINGS, parsed);
    }
  } catch (_) {}
  return DEFAULT_SETTINGS;
};

const deepMerge = (defaults, overrides) => {
  const result = { ...defaults };
  for (const key in overrides) {
    if (
      overrides[key] !== null &&
      typeof overrides[key] === 'object' &&
      !Array.isArray(overrides[key])
    ) {
      result[key] = deepMerge(defaults[key] || {}, overrides[key]);
    } else {
      result[key] = overrides[key];
    }
  }
  return result;
};

export function useSettings(authToken) {
  const [settings, setSettings] = useState(loadSettings);

  // Sync settings FROM backend whenever token is resolved
  useEffect(() => {
    if (!authToken) return;
    const fetchRemoteSettings = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/user/preferences', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (res.ok) {
          const data = await res.json();
          if (data.preferences && Object.keys(data.preferences).length > 0) {
            setSettings(prev => {
              const next = deepMerge(prev, data.preferences);
              applySettingsToDOM(next);
              try { localStorage.setItem(STORAGE_KEY, JSON.stringify(next)); } catch (_) {}
              return next;
            });
          }
        }
      } catch (e) {
        console.error("Failed to sync settings from cloud:", e);
      }
    };
    fetchRemoteSettings();
  }, [authToken]);

  const updateSettings = (section, key, value) => {
    setSettings(prev => {
      const next = {
        ...prev,
        [section]: {
          ...prev[section],
          [key]: value,
        },
      };
      // Apply relevant data-* attributes immediately
      applySettingsToDOM(next);
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(next)); } catch (_) {}
      
      // Save TO backend in the background
      if (authToken) {
        fetch('http://localhost:8000/api/user/preferences', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}` 
          },
          body: JSON.stringify({ preferences: next }),
        }).catch(err => console.error("Failed to sync settings to cloud:", err));
      }
      return next;
    });
  };

  return { settings, updateSettings };
}

export const applySettingsToDOM = (settings) => {
  if (!settings || !settings.appearance) return;
  const html = document.documentElement;
  html.setAttribute('data-fontsize',   settings.appearance.fontSize);
  html.setAttribute('data-fontfamily', settings.appearance.fontFamily);
  html.setAttribute('data-density',    settings.appearance.density);
  html.setAttribute('data-animations', settings.appearance.animations ? 'true' : 'false');
  html.setAttribute('data-glass',      settings.appearance.glass      ? 'true' : 'false');
};
