import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
<<<<<<< HEAD
  optimizeDeps: {
    include: ['chart.js', 'chart.js/auto', 'react-chartjs-2'],
  },
=======
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881
})
