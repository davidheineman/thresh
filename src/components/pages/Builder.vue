<script setup>
    import Interface from "./Interface.vue";

    import { download_data, download_config, get_file_path } from "../../assets/js/file-util.js";

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

            getDataValue: null,
            getConfigValue: null,
            setDataValue: null,
            setConfigValue: null,
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
        set_config(config) {
            this.config = config
            if (config != this.configInput) {
                this.configInput = jsyaml.dump(config)
            }
            this.setConfigValue(this.configInput)
        },
        async compile() {
            this.config = jsyaml.load(this.getConfigValue())
            this.data = JSON.parse(this.getDataValue())
        },
        async update_editors() {
            return new Promise((resolve, reject) => {
                loader.init().then((monaco) => {
                    var dataValue = "" // `${this.data}`
                    const dataEditor = monaco.editor.create(document.getElementById('data-editor'), {
                        value: dataValue,
                        language: 'json',
                        minimap: { enabled: false },
                        automaticLayout: true,
                        theme: "vs-dark",
                    });
                    dataEditor.onDidChangeModelContent((e) => { dataValue = dataEditor.getValue(); });
                    const getDataValue = () => { return dataValue }
                    const setDataValue = (val) => { dataEditor.setValue(val) }

                    var configValue = "" // jsyaml.dump(this.config)
                    const configEditor = monaco.editor.create(document.getElementById('config-editor'), {
                        value: `${configValue}`,
                        language: 'yaml',
                        minimap: { enabled: false },
                        automaticLayout: true,
                        theme: "vs-dark",
                    });
                    configEditor.onDidChangeModelContent((e) => { configValue = configEditor.getValue(); });
                    const getConfigValue = () => { return configValue }
                    const setConfigValue = (val) => { configEditor.setValue(val) }

                    resolve({ dataEditor, configEditor, getDataValue, getConfigValue, setDataValue, setConfigValue });
                }).catch((error) => {
                    reject(error);
                });
            });
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

        // Load data
        let file_path = get_file_path();
        if (file_path == null) {
            file_path = '/data/salsa.json'
        }
        download_data(file_path).then((data) => {
            this.data = data
            this.set_data(this.data)
        })

        // Load config
        let template = '/templates/salsa.yml'
        download_config(template).then((config) => {
            let parsedYaml = jsyaml.load(config);
            // console.log(parsedYaml)
            // parsedYaml = {config: parsedYaml}
            // Essentially in prod it doesn't add the unnecessary .config key...
            this.set_config(parsedYaml)
        })

        // Resize handle
        // const resizeHandle = document.querySelector('.resize-handle');
        // const container = document.querySelector('.builder');
        // let isResizing = false;
        // let containerWidth = container.offsetWidth;
        // resizeHandle.addEventListener('mousedown', () => {
        // isResizing = true;
        // });
        // document.addEventListener('mousemove', (event) => {
        // if (!isResizing) return;
        // const containerRect = container.getBoundingClientRect();
        // const containerWidthDelta = event.clientX - containerRect.left;
        // container.style.flex = `0 0 ${containerWidthDelta}px`;
        // });
        // document.addEventListener('mouseup', () => {
        // isResizing = false;
        // containerWidth = container.offsetWidth;
        // });
        },
    }
</script>

<template>
    <main>
        <div class="builder">
            <div class="editor" id="editor">
                <div class='submit-container'>
                    <button class='submit-button btn-blue'>Deploy</button>
                    <button class='submit-button btn-green' @click="compile">Compile →</button>
                </div>
                <div class='editor-container config-editor-container'>
                    <div id='config-editor' />
                </div>
                <div class='editor-container data-editor-container'>
                    <div id='data-editor' />
                </div>
            </div>
            <div class="resize-handle" />
            <div class="sandbox">
                <div v-if="
                    config != null && 
                    config != undefined &&
                    data != null &&
                    data != undefined
                ">
                    <Interface 
                        :input_data={data}
                        :consumed_config={config}
                    />
                </div>
            </div>
        </div>
    </main>
</template>

<style>
  @import '../../assets/css/editor.css';
</style>
