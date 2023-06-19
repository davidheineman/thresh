<script setup>
  import Interface from "./Interface.vue";

  import { download_data, get_file_path } from "../assets/js/file-util.js";
  import { CONFIG } from "../assets/js/constants.js";

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
        },
        set_config(config) {
            this.config = config
            if (config != this.configInput) {
                this.configInput = jsyaml.dump(config)
            }
        },
        async update_config() {
            // console.log(Object.freeze(this.dataEditor).getValue())
            // this.config = jsyaml.load(Object.freeze(this.dataEditor).get())
            // this.data = JSON.parse(this.configEditor.getValue())
        },
        async update_editors() {
            return new Promise((resolve, reject) => {
                loader.init().then((monaco) => {
                    const dataEditor = monaco.editor.create(document.getElementById('data-editor'), {
                        value: `${this.data}`,
                        language: 'json',
                        minimap: { enabled: false },
                        automaticLayout: true,
                        theme: "vs-dark",
                    });

                    const configEditor = monaco.editor.create(document.getElementById('config-editor'), {
                        value: `${jsyaml.dump(this.config)}`,
                        language: 'yaml',
                        minimap: { enabled: false },
                        automaticLayout: true,
                        theme: "vs-dark",
                    });

                    resolve({ dataEditor, configEditor });
                }).catch((error) => {
                    reject(error);
                });
            });
        }
    },
    created: function() {
        let file_path = get_file_path();
        download_data(file_path).then((data) => {
          this.set_data(data)
        })
        this.set_config(CONFIG)

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
            const { dataEditor, configEditor } = await this.update_editors();
            this.dataEditor = dataEditor;
            this.configEditor = configEditor;
        },
    }
</script>

<template>
    <main>
        <div class="builder">
            <div class="editor" id="editor">
                <div class='editor-container config-editor-container'>
                    <div id='config-editor' />
                </div>
                <div class='editor-container data-editor-container'>
                    <div id='data-editor' />
                </div>
                <div class='submit-container'>
                    <button class='submit-button btn-blue' @click="update_config">Deploy</button>
                    <button class='submit-button btn-green' @click="update_config">Compile →</button>
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
