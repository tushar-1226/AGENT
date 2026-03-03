/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './pages/**/*.{js,ts,jsx,tsx,mdx}',
        './components/**/*.{js,ts,jsx,tsx,mdx}',
        './app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                border: 'hsl(var(--border))',
                background: 'hsl(var(--bg-primary))',
                foreground: 'hsl(var(--text-primary))',
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-out',
                'slide-in': 'slideIn 0.3s ease-out',
                'pop': 'pop 0.42s cubic-bezier(.2,.9,.25,1)',
                'spin-slow': 'spin 3s linear infinite',
                'spin-reverse-slow': 'spin-reverse 4s linear infinite',
                'scan': 'scan 2s ease-in-out infinite',
                'wave': 'wave 1s ease-in-out infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                slideIn: {
                    '0%': { transform: 'translateX(100%)', opacity: '0' },
                    '100%': { transform: 'translateX(0)', opacity: '1' },
                },
                pop: {
                    '0%': { transform: 'scale(0.92)', opacity: '0' },
                    '50%': { transform: 'scale(1.06)', opacity: '1' },
                    '100%': { transform: 'scale(1)', opacity: '1' },
                },
                'spin-reverse': {
                    '0%': { transform: 'rotate(360deg)' },
                    '100%': { transform: 'rotate(0deg)' },
                },
                scan: {
                    '0%, 100%': { transform: 'translateY(-100%)' },
                    '50%': { transform: 'translateY(100%)' },
                },
                wave: {
                    '0%, 100%': { height: '20%' },
                    '50%': { height: '100%' },
                },
            },
        },
    },
    plugins: [],
}
