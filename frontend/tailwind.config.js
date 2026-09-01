/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0F2B5B',
        accent: '#00C896',
        'accent-warn': '#F5A623',
        'bg-dark': '#0A1628',
        'bg-card': '#111E36',
        surface: '#1A2E4A',
        'text-primary': '#E8F0FE',
        'text-muted': '#8899BB',
        success: '#22C55E',
        danger: '#EF4444',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-green': 'pulse-green 2s ease-in-out infinite',
        'step-in': 'step-in 0.4s ease-out forwards',
        'border-glow': 'border-glow 2s ease-in-out infinite',
        'spin-slow': 'spin 2s linear infinite',
        'fade-in': 'fade-in 0.3s ease-out forwards',
        'slide-up': 'slide-up 0.4s ease-out forwards',
        'blink': 'blink 1s step-end infinite',
      },
      keyframes: {
        'pulse-green': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 0 0 rgba(0,200,150,0.4)' },
          '50%': { opacity: '0.8', boxShadow: '0 0 0 8px rgba(0,200,150,0)' },
        },
        'step-in': {
          from: { opacity: '0', transform: 'translateX(-12px)' },
          to: { opacity: '1', transform: 'translateX(0)' },
        },
        'border-glow': {
          '0%, 100%': { borderColor: 'rgba(0,200,150,0.3)' },
          '50%': { borderColor: 'rgba(0,200,150,0.9)' },
        },
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        'slide-up': {
          from: { opacity: '0', transform: 'translateY(16px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'blink': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
      },
      boxShadow: {
        'card': '0 0 0 1px rgba(0,200,150,0.15), 0 4px 24px rgba(0,0,0,0.4)',
        'glow': '0 0 20px rgba(0,200,150,0.3)',
        'glow-sm': '0 0 8px rgba(0,200,150,0.2)',
      },
    },
  },
  plugins: [],
}
