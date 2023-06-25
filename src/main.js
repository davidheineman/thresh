import { createApp, h } from "vue/dist/vue.esm-bundler.js"
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

// Add global imports
import './assets/js/font-awesome.min.js';
import $ from 'jquery';
window.jQuery = window.$ = $

const routes = [
    { path: '/salsa', component: () => import("./components/pages/Viewer.vue") },
    { path: '/', component: () => import("./components/pages/Builder.vue") },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const app = createApp({
    render: () => (
        h(App)
    ),
})
app.use(router)
app.mount('#app')
