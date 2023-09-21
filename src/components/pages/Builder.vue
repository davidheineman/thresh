<script setup>
    import Interface from "./Interface.vue";
    import Deploy from "../builder/Deploy.vue";
    import Cite from "../builder/Cite.vue";

    import { download_data, download_config, get_file_path, joinPaths } from "../../assets/js/file-util.js";

    import jsyaml from 'js-yaml';
    import * as monaco from 'monaco-editor'
    import loader from "@monaco-editor/loader";

    // Configure Monaco editor
    loader.config({ paths: { vs: 'https://unpkg.com/monaco-editor@0.33.0/min/vs' } }) // or local
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
    }
</script>

<script>


export default {
    data() {
        return {
            data: null,
            config: null,

            dataEditor: null,
            configEditor: null,

            deploy_open: false,
            cite_open: false,
            selectedTemplate: '',

            dragging: {
                vertical: false,
                horizontal: false,
            },

            getDataValue: null,
            getConfigValue: null,
            setDataValue: null,
            setConfigValue: null,
        }
    },
    watch: {
        selectedTemplate(newValue) {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('t', newValue);
            window.history.replaceState(null, '', `${window.location.pathname}?${urlParams}`);
            this.load_builder(newValue);
        }
    },
    methods: {
        set_data(data) {
            this.data = data
            if (data != this.dataInput) {
                this.dataInput = JSON.stringify(data, null, 2)
            }
            this.setDataValue(this.dataInput)
        },
        async set_config(config) {
            let parsedYaml = jsyaml.load(config);
            await this.push_config(parsedYaml)
            if (parsedYaml != this.configInput) {
                this.configInput = jsyaml.dump(parsedYaml)
            }
            this.setConfigValue(config)
        },
        async push_config(config) {
            // Load language template
            const lang_code = config.language || 'en'
            const lang_template = `lang/${lang_code}.yml`
            let language_template = await download_config(lang_template).then((language_config) => {
                return jsyaml.load(language_config)
            })
            config.interface_text = Object.assign({}, language_template, config.interface_text);
            this.config = config
        },
        async compile() {
            let new_config = jsyaml.load(this.getConfigValue())
            await this.push_config(new_config)
            this.data = JSON.parse(this.getDataValue())
        },
        async update_editors() {
            var monaco_compile = this.compile
            return new Promise((resolve, reject) => {
                loader.init().then((monaco) => {
                    var dataValue = ""
                    const dataEditor = monaco.editor.create(document.getElementById('data-editor'), {
                        value: dataValue,
                        language: 'json',
                        minimap: { enabled: false },
                        automaticLayout: true,
                        theme: "vs-dark"
                    });
                    dataEditor.onDidChangeModelContent((e) => { dataValue = dataEditor.getValue(); });
                    const getDataValue = () => { return dataValue }
                    const setDataValue = (val) => { dataEditor.setValue(val) }

                    var configValue = ""
                    const configEditor = monaco.editor.create(document.getElementById('config-editor'), {
                        value: `${configValue}`,
                        language: 'yaml',
                        minimap: { enabled: false },
                        automaticLayout: true,
                        theme: "vs-dark"
                    });
                    configEditor.onDidChangeModelContent((e) => { configValue = configEditor.getValue(); });
                    const getConfigValue = () => { return configValue }
                    const setConfigValue = (val) => { configEditor.setValue(val) }

                    dataEditor.addAction({
                        id: "data-save", label: "",
                        keybindings: [ monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS ],
                        run: function () { monaco_compile() },
                    })
                    configEditor.addAction({
                        id: "config-save", label: "",
                        keybindings: [ monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS ],
                        run: function () { monaco_compile() },
                    })

                    resolve({ dataEditor, configEditor, getDataValue, getConfigValue, setDataValue, setConfigValue });
                }).catch((error) => {
                    reject(error);
                });
            });
        },
        toggle_deploy() {
            this.deploy_open = !this.deploy_open
        },
        toggle_cite() {
            this.cite_open = !this.cite_open
        },
        start_drag(type) {
            if (type == 'vertical') {
                this.dragging.vertical = true;
                $("#builder")[0].style.cursor = "ew-resize";
            } else if (type == 'horizontal') {
                this.dragging.horizontal = true;
                $("#editor")[0].style.cursor = "ev-resize";
            }
        },
        reset_col_sizes() {
            $("#builder")[0].style.gridTemplateColumns = '1fr 0fr 1fr'
            $("#editor")[0].style.gridAutoRows = '2fr 0fr 1fr'
        },
        end_drag() {
            this.dragging.vertical = false;
            this.dragging.horizontal = false;
            $("#builder")[0].style.cursor = "auto";
        },
        on_drag(e) {
            if (this.dragging.vertical) {
                const page = $("#builder")[0];
                const editor = $("#editor")[0];
                const editor_width = this.dragging.vertical ? e.clientX : editor.clientWidth;
                const dragbar_width = 5;

                let new_col_definition = [
                    editor_width,
                    dragbar_width,
                    window.innerWidth - dragbar_width - editor_width
                ].map(c => c.toString() + "px").join(" ");
                page.style.gridTemplateColumns = new_col_definition;
                e.preventDefault()
            } else if (this.dragging.horizontal) {
                const page = $("#editor")[0];
                const editor = $("#config-editor-container")[0];
                const submit_height = $('.submit-container')[0].clientHeight;
                const header_height = $('.header')[0].clientHeight;
                
                const editor_height = this.dragging.horizontal ? e.clientY - submit_height - header_height : editor.clientHeight;
                const dragbar_height = 5;

                let new_col_definition = [
                    editor_height,
                    dragbar_height,
                    window.innerHeight - dragbar_height - editor_height - submit_height - header_height
                ].map(c => c.toString() + "px").join(" "); 
                page.style.gridAutoRows = new_col_definition;
                e.preventDefault()
            }
        },
        templatesByTask(task) {
            return this.$templates.filter(d => d.task === task);
        },
        async load_builder(template_arg) {
            if (template_arg == null) {
                template_arg = 'demo_start'
            } 

            template_arg = template_arg.replace('demo_', 'demo/')
            
            const basePath = import.meta.env.BASE_URL;
            let template, file_path
            if (!template_arg.includes('http')) {
                template = joinPaths(basePath, `/templates/${template_arg}.yml`)
                file_path = joinPaths(basePath, `/data/${template_arg}.json`)
            } else {
                template = template_arg
                file_path = joinPaths(basePath, `/data/demo/start.json`)
            }
            
            this.selectedOption = template

            this.data = null
            this.config = null

            // Load config
            var local_config;
            await download_config(template).then((config) => {
                local_config = jsyaml.load(config)
                this.set_config(config)
            })

            if (local_config.default_data_link) {
                file_path = local_config.default_data_link
            }

            // Load data
            download_data(file_path).then((data) => {
                this.data = data
                this.set_data(this.data)
            })
        },
        highlight_container(i) {
            if (this.config.highlight_first_interface && i == 1) {
                return "adjudication-container-highlight"
            }
        }
    },
    created: async function() {
        // Initialize monaco editors
        const { dataEditor, configEditor, getDataValue, getConfigValue, setDataValue, setConfigValue } = await this.update_editors();
        this.dataEditor = dataEditor
        this.configEditor = configEditor
        this.getDataValue = getDataValue
        this.getConfigValue = getConfigValue
        this.setDataValue = setDataValue
        this.setConfigValue = setConfigValue

        const urlParams = new URLSearchParams(window.location.search);
        let template_arg = urlParams.get('t');
        // let file_path = get_file_path();
        
        this.load_builder(template_arg)

        window.addEventListener('resize', this.reset_col_sizes);
    },
    computed: {
        isViewable() {
            return this.$templates.some(d => d.path === this.config.template_name && d.hosted);
        },
        uniqueTasks() {
            return [...new Set(this.$templates.map(d => d.task))].sort();
        }
    }
}
</script>

<template>
    <Deploy :deploy_open="deploy_open" :toggle_deploy="toggle_deploy" :config="config" :input_data="data" />
    <Cite :cite_open="cite_open" :toggle_cite="toggle_cite" :config="config" />
    <main class="builder-container">
        <div class="header">
            <div class="template-label-name">
                <img src="/favicon.ico" width=40 alt="Icon">
                <!-- <h3>Annotation Builder</h3> -->
            </div>
            <div class="template-label-header">
                <h2 v-if="config != null && config != undefined">Editing: {{ config.template_label }}</h2>
            </div>
            <div>
                <a href="https://github.com/davidheineman/thresh.tools" class="github-corner" aria-label="View source on GitHub">
                <svg width="45" height="45" viewBox="0 0 250 250" style="fill:#727272; color:#151513; position: absolute; top: 0; border: 0; right: 0;" aria-hidden="true">
                    <path d="M0,0 L115,115 L130,115 L142,142 L250,250 L250,0 Z"></path>
                    <path d="M128.3,109.0 C113.8,99.7 119.0,89.6 119.0,89.6 C122.0,82.7 120.5,78.6 120.5,78.6 C119.2,72.0 123.4,76.3 123.4,76.3 C127.3,80.9 125.5,87.3 125.5,87.3 C122.9,97.6 130.6,101.9 134.4,103.2" fill="currentColor" style="transform-origin: 130px 106px;" class="octo-arm"></path>
                    <path d="M115.0,115.0 C114.9,115.1 118.7,116.5 119.8,115.4 L133.7,101.6 C136.9,99.2 139.9,98.4 142.2,98.6 C133.8,88.0 127.5,74.4 143.8,58.0 C148.5,53.4 154.0,51.2 159.7,51.0 C160.3,49.4 163.2,43.6 171.4,40.1 C171.4,40.1 176.1,42.5 178.8,56.2 C183.1,58.6 187.2,61.8 190.9,65.4 C194.5,69.0 197.7,73.2 200.1,77.6 C213.8,80.2 216.3,84.9 216.3,84.9 C212.7,93.1 206.9,96.0 205.4,96.6 C205.1,102.4 203.0,107.8 198.3,112.5 C181.9,128.9 168.3,122.5 157.7,114.1 C157.9,116.9 156.7,120.9 152.7,124.9 L141.0,136.5 C139.8,137.7 141.6,141.9 141.8,141.8 Z" fill="currentColor" class="octo-body"></path>
                </svg>
                </a>
            </div>
        </div>
        <div id="builder" class="builder" @mouseup="end_drag" @mousemove="on_drag">
            <div class="editor" id="editor">
                <div class='submit-container'>
                    <select id="types" v-model="selectedTemplate" class="template-selector h-100 db h2 f6 bg-near-white ba b--sliver" name="">
                        <option value="">Explore templates...</option>
                        <optgroup v-for="task in uniqueTasks" :label="task" :key="task">
                            <option v-for="(template, index) in templatesByTask(task)" :value="template.path" :key="index">{{ template.name }}</option>
                        </optgroup>
                    </select>
                    <button class='pa2 ba bw1 pointer btn-gold' @click="toggle_cite" v-if="config != null && config != undefined && config.citation">
                        <span class="f5 b">Cite this Typology</span>
                        <i class="fa-solid fa-crown fa-1-3x icon-default ml2"></i>
                    </button>
                    <a v-if="config != null && config != undefined && isViewable" :href="config.template_name" target="_blank">
                        <button class='pa2 ba bw1 pointer btn-green'>
                            <span class="f5 b">View</span>
                            <i class="fa-solid fa-up-right-from-square fa-1-3x icon-default ml2"></i>
                        </button>
                    </a> 
                    <button class='pa2 ba bw1 pointer deploy-btn' @click="toggle_deploy">
                        <span class="f5 b">Deploy</span>
                        <i class="fa-solid fa-angles-up fa-1-3x icon-default ml2"></i>
                    </button>
                    <button class='pa2 ba bw1 pointer btn-blue' @click="compile">
                        <span class="f5 b">Compile</span>
                        <i class="fa-solid fa-repeat fa-1-3x icon-default ml2"></i>
                    </button>
                </div>
                <div class='editor-container config-editor-container' id="config-editor-container">
                    <div id='config-editor' />
                </div>
                <div class="h-resize-handle" id="h-resize-handle" @mousedown="start_drag('horizontal')"><div class='h-resize-dots'></div></div>
                <div class='editor-container data-editor-container' id="data-editor-container">
                    <div id='data-editor' />
                </div>
            </div>
            <div class="resize-handle" id="resize-handle" @mousedown="start_drag('vertical')"><div class='resize-dots'></div></div>
            <div class="sandbox" id="sandbox">
                <div v-if="
                    config != null && config != undefined &&
                    data != null && data != undefined
                ">
                    <div v-if="config.adjudication" class="adjudication-container">
                        <Interface 
                            v-for="idx in config.adjudication"
                            v-bind:key="idx"
                            :class="highlight_container(idx)"
                            :highlight="config.highlight_first_interface && idx == 1"
                            :input_data={data}
                            :consumed_config={config}
                        />
                    </div>
                    <div v-else class="mt4">
                        <Interface 
                            :input_data={data}
                            :consumed_config={config}
                        />
                    </div>
                </div>
                <div v-else>
                    <div class="spinner-container">
                        <div class="spinner"></div>
                    </div>
                </div>
            </div>
        </div>
    </main>
</template>

<style>
  @import '../../assets/css/editor.css';
</style>
