/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'gray-850': '#1f2937',
        'gray-750': '#374151',
        'gray-650': '#4b5563',
      },
      fontFamily: {
        'google-sans': ['Google Sans', 'sans-serif'],
      },
    },
  },
  plugins: [],
} 