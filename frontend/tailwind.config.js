/** @type {import('tailwindcss').Config} */
import typography from '@tailwindcss/typography';

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef7ff',
          100: '#d9edff',
          200: '#bce0ff',
          300: '#8ecdff',
          400: '#58b0ff',
          500: '#3890fc',
          600: '#1e70f2',
          700: '#1459e1',
          800: '#1746b6',
          900: '#1a3e8f',
          950: '#142757',
        },
        secondary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#b9e6fe',
          300: '#7cd3fd',
          400: '#36bffa',
          500: '#0ca6eb',
          600: '#0085c5',
          700: '#0369a0',
          800: '#075784',
          900: '#0c496c',
          950: '#082f49',
        },
        dark: {
          50: '#f6f6f7',
          100: '#e1e3e7',
          200: '#c2c7cf',
          300: '#9da3b0',
          400: '#7a7f8e',
          500: '#616674',
          600: '#4d515e',
          700: '#40424c',
          800: '#363840',
          900: '#212230',
          950: '#191a25',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            color: theme('colors.gray.900'),
            a: {
              color: theme('colors.primary.600'),
              '&:hover': {
                color: theme('colors.primary.800'),
              },
            },
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
          },
        },
        dark: {
          css: {
            color: theme('colors.gray.100'),
            a: {
              color: theme('colors.primary.400'),
              '&:hover': {
                color: theme('colors.primary.300'),
              },
            },
          },
        },
      }),
    },
  },
  plugins: [
    typography,
  ],
} 