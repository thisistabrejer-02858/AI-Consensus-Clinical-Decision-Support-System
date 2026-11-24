/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#202a29',
        sage: '#385b55',
        canvas: '#f5f6f4',
      },
    },
  },
  plugins: [],
}
