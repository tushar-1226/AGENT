'use client';

import { useEffect, useState } from 'react';

interface Toast {
  id: number;
  message: string;
  title?: string;
  type: 'success' | 'error';
  duration: number; // ms
  actionLabel?: string;
  actionPayload?: any;
}

function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: (id: number) => void }) {
  const [remaining, setRemaining] = useState<number>(toast.duration);

  useEffect(() => {
    let start = Date.now();
    let raf: number | null = null;
    const tick = () => {
      const elapsed = Date.now() - start;
      const left = Math.max(0, toast.duration - elapsed);
      setRemaining(left);
      if (left <= 0) {
        onRemove(toast.id);
      } else {
        raf = requestAnimationFrame(tick);
      }
    };
    raf = requestAnimationFrame(tick);
    return () => {
      if (raf) cancelAnimationFrame(raf);
    };
  }, [toast.id, toast.duration, onRemove]);

  const handleMouseEnter = () => {
    // Pause by setting remaining to current and cancelling animations by setting a flag
    // We'll stop updates by setting a data attribute used by tick; simpler approach: do nothing—tick reads Date.now() and will continue.
    // For a simple pause, we remove by clearing removal timeout via a custom event; to keep implementation focused, provide click-to-dismiss and progress bar only.
  };

  const progress = Math.round(((toast.duration - remaining) / toast.duration) * 100);

  return (
    <div className={`flex flex-col w-full max-w-sm glass-card p-3 border ${toast.type === 'success' ? 'border-green-400/40' : 'border-red-400/40'} animate-slide-in`} onMouseEnter={handleMouseEnter}>
      <div className="flex items-start gap-3">
        <div className={`flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center ${toast.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}`}>
          {toast.type === 'success' ? (
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          )}
        </div>

        <div className="flex-1">
          <div className="flex items-center justify-between">
            <div>
              {toast.title && <div className="text-sm font-semibold">{toast.title}</div>}
              <div className="text-sm text-white/90">{toast.message}</div>
            </div>
            <div className="flex items-center gap-2">
              {toast.actionLabel && (
                <button
                  onClick={() => {
                    window.dispatchEvent(new CustomEvent('toastAction', { detail: { payload: toast.actionPayload } }));
                    onRemove(toast.id);
                  }}
                  className="px-3 py-1 bg-white/10 rounded text-sm"
                >
                  {toast.actionLabel}
                </button>
              )}
              <button onClick={() => onRemove(toast.id)} className="text-sm text-gray-300 hover:text-white ml-2">✕</button>
            </div>
          </div>

          <div className="mt-2 h-1 w-full bg-white/5 rounded overflow-hidden">
            <div className="h-full bg-white/60" style={{ width: `${progress}%`, transition: 'width 120ms linear' }} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    const handleToast = (event: any) => {
      const { message, type = 'success', title, duration = 3000, actionLabel, actionPayload } = event.detail;
      const id = Date.now() + Math.floor(Math.random() * 1000);

      const toast: Toast = { id, message, title, type, duration, actionLabel, actionPayload };

      setToasts((prev) => [...prev, toast]);
    };

    window.addEventListener('showToast', handleToast);
    return () => window.removeEventListener('showToast', handleToast);
  }, []);

  const remove = (id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <div className="fixed top-4 right-4 z-[200] flex flex-col gap-3">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} onRemove={remove} />
      ))}
    </div>
  );
}
