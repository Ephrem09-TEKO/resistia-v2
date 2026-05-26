/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        night: {
          DEFAULT: '#0A0F1E',
          800: '#0D1528',
          700: '#111D35',
        },
        cyan: {
          DEFAULT: '#00D4FF',
          dark: '#00A8CC',
        },
        violet: {
          DEFAULT: '#7B2FFF',
          dark: '#5A1FCC',
        },
        bio: {
          DEFAULT: '#00E676',
          dark: '#00B85A',
        },
        amr: {
          DEFAULT: '#FF6B35',
          dark: '#CC5020',
        },
        danger: {
          DEFAULT: '#FF1744',
          dark: '#CC1035',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px #00D4FF' },
          '100%': { boxShadow: '0 0 20px #00D4FF, 0 0 40px #00D4FF' },
        },
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
        glow: 'glow 2s ease-in-out infinite alternate',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}