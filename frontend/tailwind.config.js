/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // NotebookLM dark theme colors
        'nb-bg': '#1a1a1a',
        'nb-bg-secondary': '#2a2a2a',
        'nb-bg-tertiary': '#333333',
        'nb-border': '#404040',
        'nb-text': '#ffffff',
        'nb-text-secondary': '#b3b3b3',
        'nb-text-muted': '#808080',
        'nb-accent': '#4285f4',
        'nb-accent-hover': '#5294f5',
        'nb-success': '#34a853',
        'nb-warning': '#fbbc04',
        'nb-error': '#ea4335',
        'nb-purple': '#9c27b0',
        'nb-card': '#262626',
        'nb-hover': '#3c3c3c'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'pulse-gentle': 'pulseGentle 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseGentle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
      },
    },
  },
  plugins: [],
} 