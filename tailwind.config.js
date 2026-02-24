/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './app_accounts/**/*.py',
    './app_projects/**/*.py',
    './app_teams/**/*.py',
    './app_tickets/**/*.py',
    './helpdesk/**/*.py',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
