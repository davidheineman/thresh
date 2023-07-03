import { createApp, h } from "vue/dist/vue.esm-bundler.js"
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

// Add global imports
import './assets/js/font-awesome.min.js';
import $ from 'jquery';
window.jQuery = window.$ = $

const templates = [
    { name: "SALSA", path: "salsa", task: "Simplification", hosted: true },
    { name: "Scarecrow", path: "scarecrow", task: "Long-form Generation", hosted: true },
    { name: "FRANK", path: "frank", task: "Summarization", hosted: true },
    { name: "MQM", path: "mqm", task: "Translation", hosted: true },
]

const demo_templates = [
    { name: "Start Here", path: "demo", task: "Examples" },
    { name: "Custom Instructions", path: "demo_instructions", task: "Examples" },
    { name: "Advanced Edit Types", path: "demo_edit_types", task: "Examples" },
    { name: "Advanced Question Trees", path: "demo_question_trees", task: "Examples" },
    { name: "Paragraph-level Annoation", path: "demo_paragraph", task: "Examples" },
    { name: "Limited Functionality", path: "demo_disable", task: "Examples" },
    { name: "Multi-language Deployment", path: "demo_multilingual", task: "Examples" }
]

// Change route for custom template links
const params = new URLSearchParams(window.location.search)
var iParam = params.get("i");
var ghParam = params.get("gh");
var hfParam = params.get("hf");

const routes = [
    { path: '/annotate', props: () => ({ serverless: true }), component: () => import("./components/pages/Viewer.vue") },
    { path: '/', component: (iParam || ghParam || hfParam) ? () => import("./components/pages/Viewer.vue") : () => import("./components/pages/Builder.vue") }
]

for (const template of templates) {
    const template_path = template.path
    routes.push({ path: `/${template.path}`, props: () => ({ template_path: template_path }), component: () => import("./components/pages/Viewer.vue") })
}

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const app = createApp({
    render: () => (
        h(App)
    ),
})
app.config.globalProperties.$templates = [...templates, ...demo_templates]
app.use(router)
app.mount('#app')
