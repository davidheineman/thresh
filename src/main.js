import { createApp, h } from "vue/dist/vue.esm-bundler.js"
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import { joinPaths  } from "./assets/js/file-util";

// Add global imports
import './assets/js/font-awesome.min.js';
import $ from 'jquery';
window.jQuery = window.$ = $

const templates = [
    { name: "SALSA", path: "salsa", task: "Simplification", hosted: true },
    { name: "Scarecrow", path: "scarecrow", task: "Open-ended Generation", hosted: true },
    { name: "FRANK", path: "frank", task: "Summarization", hosted: true },
    { name: "MQM", path: "mqm", task: "Translation", hosted: true },
    { name: "CWZCC", path: "cwzcc", task: "Grammar Error Correction", hosted: true },
    { name: "MultiPIT", path: "multipit", task: "Paraphrase Generation", hosted: true },
    { name: "SNaC", path: "snac", task: "Summarization", hosted: true },
    { name: "ERRANT", path: "errant", task: "Grammar Error Correction", hosted: true },
    { name: "arXivEdits", path: "arxivedits", task: "Text Revision", hosted: true },
    { name: "Da San Martino et al., 2019", path: "propaganda", task: "Propaganda Analysis", hosted: true },
    { name: "Wu et al., 2023", path: "fg-rlhf", task: "Fine-Grained RLHF", hosted: true },
    // { name: "AttrEval", path: "attreval", task: "Attribution", hosted: true },
    // { name: "FLASK", path: "flask", task: "Open-ended Generation", hosted: true },
    // { name: "Gorman et al., 2019", path: "gorman-etal-2019", task: "Morphological Error Detection", hosted: true },
    // { name: "Wan et al., 2019", path: "wan-etal-2019", task: "Spoiler Detection", hosted: true },
]

const demo_templates = [
    { name: "Start Here", path: "demo_start", task: "Examples" },
    { name: "Advanced Edit Types", path: "demo_edit_types", task: "Examples" },
    { name: "Advanced Question Trees", path: "demo_question_trees", task: "Examples" },
    { name: "Custom Instructions", path: "demo_instructions", task: "Examples" },
    { name: "Paragraph-level Annoation", path: "demo_paragraph", task: "Examples" },
    { name: "Adjudication", path: "demo_adjudication", task: "Examples" },
    { name: "Limited Functionality", path: "demo_disable", task: "Examples" },
    { name: "Word-level Selection", path: "demo_tokenization", task: "Examples" },
    { name: "Multi-language Deployment", path: "demo_multilingual", task: "Examples" },
    { name: "Crowdsource Deployment", path: "demo_crowdsource", task: "Examples" }
]

// Change route for custom template links
const params = new URLSearchParams(window.location.search)
var iParam = params.get("i");
var ghParam = params.get("gh");
var hfParam = params.get("hf");

const basePath = import.meta.env.BASE_URL;
const routes = [
    { path: joinPaths(basePath, '/'), component: (iParam || ghParam || hfParam) ? () => import("./components/pages/Viewer.vue") : () => import("./components/pages/Builder.vue") },
    { path: joinPaths(basePath, '/demo'), component: () => import("./components/pages/Builder.vue") },
    { path: joinPaths(basePath, '/custom'), props: () => ({ injection: true }), component: () => import("./components/pages/Viewer.vue") },
    { path: joinPaths(basePath, '/annotate'), props: () => ({ serverless: true }), component: () => import("./components/pages/Viewer.vue") }
]

for (const template of templates) {
    const template_path = template.path
    routes.push({ path: joinPaths(basePath, `/${template.path}`), props: () => ({ template_path: template_path }), component: () => import("./components/pages/Viewer.vue") })
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
