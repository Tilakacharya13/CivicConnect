/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: { 50: '#eef2ff', 100: '#e0e7ff', 500: '#6366f1', 600: '#4f46e5', 700: '#4338ca', 900: '#25205d' },
        ink: '#172033',
      },
      borderRadius: { '4xl': '2rem' },
      fontFamily: { sans: ['Inter', 'sans-serif'] },
      boxShadow: {
        soft: '0 8px 30px rgba(30, 41, 59, 0.06)',
        lift: '0 16px 42px rgba(30, 41, 59, 0.12)',
        glow: '0 18px 60px -30px rgba(99, 102, 241, 0.38)',
      },
      keyframes: {
        'fade-in-up': { '0%': { opacity: '0', transform: 'translateY(18px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
      },
      animation: { 'fade-in-up': 'fade-in-up .65s cubic-bezier(.2,.8,.2,1) both' },
    },
  },
  plugins: [],
}
