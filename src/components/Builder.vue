<script setup>
  import Interface from "./Interface.vue";

  import { download_data, get_file_path } from "../assets/js/file-util.js";

  import jsyaml from 'js-yaml';
  import MonacoEditor from 'monaco-editor-vue';

  import loader from "@monaco-editor/loader";

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
    components: {
        MonacoEditor
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
                    var dataValue = `${this.data}`
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

                    var configValue = jsyaml.dump(this.config)
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
    created: function() {
        // Load data
        // let file_path = get_file_path();
        // download_data(file_path).then((data) => {
        //   this.data = data
        // })

        // Load YML config
        // const fs = require('fs');
        // const yaml = require('js-yaml');
        // const template_path = 'src/assets/template.yml';
        // const parsedYaml = yaml.load(fs.readFileSync(template_path, 'utf8'));
        // this.config = CONFIG 

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
        async mounted() {
            const { dataEditor, configEditor, getDataValue, getConfigValue, setDataValue, setConfigValue } = await this.update_editors();
            this.dataEditor = dataEditor
            this.configEditor = configEditor
            this.getDataValue = getDataValue
            this.getConfigValue = getConfigValue
            this.setDataValue = setDataValue
            this.setConfigValue = setConfigValue
            this.set_data(this.data)
            this.set_config(this.config)
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
                <Interface 
                    :input_data={data}
                    :config={config}
                />
            </div>
        </div>
    </main>
</template>

<style>
  @import '../assets/css/editor.css';
</style>
