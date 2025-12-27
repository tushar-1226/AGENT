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
        'electric-blue': {
          DEFAULT: 'hsl(210, 100%, 60%)',
          hover: 'hsl(210, 100%, 65%)',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      borderRadius: {
        'xl': '12px',
        '2xl': '14px',
      },
      boxShadow: {
        'glass': '0 8px 32px rgba(0, 0, 0, 0.6), inset 0 1px 1px rgba(255, 255, 255, 0.05)',
        'glass-hover': '0 12px 48px rgba(0, 0, 0, 0.7), 0 0 24px rgba(59, 130, 246, 0.1)',
        'glow-blue': '0 0 20px rgba(59, 130, 246, 0.15)',
      },
      backdropBlur: {
        'xs': '2px',
      },
    },
  },
  plugins: [],
}
