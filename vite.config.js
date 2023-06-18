import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Load YML config
const fs = require('fs');
const yaml = require('js-yaml');
const template_path = 'src/assets/template.yml';
const parsedYaml = yaml.load(fs.readFileSync(template_path, 'utf8'));

export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      vue$: 'vue/dist/vue.esm-bundler.js',
    }
  },
  define: {
    globalTemplate: JSON.stringify(parsedYaml)
  }
})
