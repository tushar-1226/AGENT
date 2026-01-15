// Toast notification utility
export function showToast(message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info', options?: { duration?: number; payload?: any }) {
    if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('showToast', {
            detail: {
                message,
                type,
                duration: options?.duration || 3000,
                payload: options?.payload
            }
        }));
    }
}
