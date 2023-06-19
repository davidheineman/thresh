// import { createApp } from 'vue'
import { createApp } from 'vue/dist/vue.esm-bundler.js';
import App from './App.vue'

// Add global imports
import './assets/js/font-awesome.min.js';
import $ from 'jquery';
window.jQuery = window.$ = $

// Configure Monaco editor
import * as monaco from 'monaco-editor';
import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker';
import jsonWorker from 'monaco-editor/esm/vs/language/json/json.worker?worker';

self.MonacoEnvironment = {
    getWorker(_workerId, label) {
        switch (label) {
            case 'json': return new jsonWorker();
            // case 'yaml': new Worker(new URL('monaco-yaml/yaml.worker', import.meta.url));
            default: return new editorWorker();
        }
    }
};

createApp(App).mount('#app')
