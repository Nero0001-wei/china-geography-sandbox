import { fileURLToPath } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import { amapRoutePlugin } from './server/amap-route.js'
import { amapJourneyPlugin } from './server/amap-journey.js'
import { amapLocationPlugin } from './server/amap-location.js'

const landmarkCatalog = fileURLToPath(new URL('./shared/landmark-catalog.json', import.meta.url))
const mapPlaces = fileURLToPath(new URL('./shared/map-places.json', import.meta.url))

export default defineConfig(({ mode }) => {
  const plugins = [react()]
  if (mode !== 'pages') {
    const env = loadEnv(mode, fileURLToPath(new URL('.', import.meta.url)), 'AMAP_WEB_SERVICE_KEY')
    const key = env.AMAP_WEB_SERVICE_KEY
    plugins.push(amapRoutePlugin(key), amapJourneyPlugin(key), amapLocationPlugin(key))
  }
  return {
    base: './',
    plugins,
    build: {
      rollupOptions: {
        output: {
          manualChunks: { three: ['three'], 'landmark-catalog': [landmarkCatalog], 'map-places': [mapPlaces] },
        },
      },
      chunkSizeWarningLimit: 650,
    },
  }
})
