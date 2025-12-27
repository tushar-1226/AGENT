'use client';

import { useEffect, useState } from 'react';

interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error';
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    const handleToast = (event: any) => {
      const { message, type } = event.detail;
      const id = Date.now();

      setToasts((prev) => [...prev, { id, message, type }]);

      // Auto remove after 3 seconds
      setTimeout(() => {
        setToasts((prev) => prev.filter((toast) => toast.id !== id));
      }, 3000);
    };

    window.addEventListener('showToast', handleToast);
    return () => window.removeEventListener('showToast', handleToast);
  }, []);

  return (
    <div className="fixed top-4 right-4 z-[200] space-y-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`flex items-center gap-3 px-6 py-4 rounded-lg shadow-lg backdrop-blur-sm border animate-slide-in ${
            toast.type === 'success'
              ? 'bg-green-500/90 border-green-400 text-white'
              : 'bg-red-500/90 border-red-400 text-white'
          }`}
        >
          {toast.type === 'success' ? (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          )}
          <span className="font-medium">{toast.message}</span>
        </div>
      ))}
    </div>
  );
}
