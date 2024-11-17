/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#cf0058',
        secondary: '#931c74',
        accent: '#ff6c96',
      },
    },
  },
  plugins: [],
};