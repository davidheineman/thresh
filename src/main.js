// import { createApp } from 'vue'
import { createApp } from 'vue/dist/vue.esm-bundler.js';
import App from './App.vue'

// Add global imports
import './assets/js/font-awesome.min.js';
import $ from 'jquery';
window.jQuery = window.$ = $

createApp(App).mount('#app')
