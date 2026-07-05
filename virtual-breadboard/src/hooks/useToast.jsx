// useToast.js — Global toast notification context + hook
// Usage: const { toast } = useToast();
//        toast.success('Hardware Saved');

import { createContext, useContext, useState, useCallback } from 'react';

const ToastContext = createContext(null);

let _nextId = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const push = useCallback((type, message, duration = 3500) => {
    const id = ++_nextId;
    setToasts(prev => [...prev, { id, type, message, exiting: false }]);
    setTimeout(() => {
      // Mark as exiting to trigger exit animation
      setToasts(prev => prev.map(t => t.id === id ? { ...t, exiting: true } : t));
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id));
      }, 250);
    }, duration);
  }, []);

  const dismiss = useCallback((id) => {
    setToasts(prev => prev.map(t => t.id === id ? { ...t, exiting: true } : t));
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 250);
  }, []);

  const toast = {
    success: (msg, dur) => push('success', msg, dur),
    error:   (msg, dur) => push('error',   msg, dur),
    warning: (msg, dur) => push('warning', msg, dur),
    info:    (msg, dur) => push('info',    msg, dur),
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <ToastContainer toasts={toasts} dismiss={dismiss} />
    </ToastContext.Provider>
  );
}

export const useToast = () => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used inside <ToastProvider>');
  return ctx;
};

// Internal container — rendered once at root level
function ToastContainer({ toasts, dismiss }) {
  if (toasts.length === 0) return null;

  const icons = {
    success: (
      <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
      </svg>
    ),
    error: (
      <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
      </svg>
    ),
    warning: (
      <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    info: (
      <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  };

  const styles = {
    success: { icon: 'text-green-400', bar: 'bg-green-500', bg: 'border-green-500/20' },
    error:   { icon: 'text-red-400',   bar: 'bg-red-500',   bg: 'border-red-500/20'   },
    warning: { icon: 'text-orange-400',bar: 'bg-orange-500',bg: 'border-orange-500/20' },
    info:    { icon: 'text-blue-400',  bar: 'bg-blue-500',  bg: 'border-blue-400/20'  },
  };

  return (
    <div
      className="fixed bottom-5 right-5 z-[9999] flex flex-col gap-2.5 items-end pointer-events-none"
      aria-live="polite"
    >
      {toasts.map(t => {
        const s = styles[t.type] || styles.info;
        return (
          <div
            key={t.id}
            className={`pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl
              border backdrop-blur-lg shadow-2xl min-w-[220px] max-w-[360px]
              bg-[var(--pm-surface)] ${s.bg}
              ${t.exiting ? 'toast-exit' : 'toast-enter'}`}
          >
            {/* Accent bar */}
            <div className={`w-0.5 h-7 rounded-full shrink-0 ${s.bar}`} />

            {/* Icon */}
            <span className={s.icon}>{icons[t.type]}</span>

            {/* Message */}
            <span className="text-[11px] font-medium text-[var(--pm-text)] font-mono-editor flex-1 leading-snug">
              {t.message}
            </span>

            {/* Dismiss */}
            <button
              onClick={() => dismiss(t.id)}
              className="text-[var(--pm-text-muted)] hover:text-[var(--pm-text)] text-xs ml-1 cursor-pointer shrink-0"
            >
              ✕
            </button>
          </div>
        );
      })}
    </div>
  );
}
