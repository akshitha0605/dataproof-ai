/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f7ff',
          100: '#e0effe',
          500: '#0284c7',
          600: '#0265d2',
          700: '#034ea2',
          900: '#0c2240',
        },
        slateDark: '#0b0f19',
        panelDark: '#111827',
        borderDark: '#1f293d',
      },
    },
  },
  plugins: [],
}
