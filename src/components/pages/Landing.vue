<script setup>
import _ from 'lodash';
import jsyaml from 'js-yaml';
import { handle_file_upload, download_data, get_file_path } from "../../assets/js/file-util.js";
</script>

<script>
export default {
    data() {
        return { 
            filelist: [],
            config: {}
        }
    },
    props: [
        'consumed_config',
        'set_data',
        'set_config',
        'customize_template_link'
    ],
    watch: {
      consumed_config() {
        this.consume_config()
      }
    },
    methods: {
        consume_config() {
          if (this.consumed_config.hasOwnProperty('consumed_config')) {
            this.config = _.cloneDeep(this.consumed_config.consumed_config)
          } else if (this.consumed_config.hasOwnProperty('config')) { 
            this.config = _.cloneDeep(this.consumed_config.config)
          } else {
            this.config = _.cloneDeep(this.consumed_config)
          }
          
          if (this.config.template_label) {
            $('title').text(this.config.template_label);
            // TODO: Add - tagline
          }
        },
        async handle_drag_drop(e) {
            let new_hits_data = await handle_file_upload(e)
            if (this.config.template_name == 'serverless') {
                let yml_template = new_hits_data.find(i => i.hasOwnProperty('_thresh_template'))?._thresh_template;
                yml_template = jsyaml.load(yml_template)
                this.set_config(yml_template)
                new_hits_data = new_hits_data.filter(i => !("_thresh_template" in i));
            }
            this.set_data(new_hits_data)
            // this.filelist = [...this.$refs.file.files];
        },
        remove(i) {
            this.filelist.splice(i, 1);
        },
        dragover(e) {
            e.preDefault();
            // Add some visual fluff to show the user can drop its files
            if (!e.currentTarget.classList.contains('bg-green-300')) {
                e.currentTarget.classList.remove('bg-gray-100');
                e.currentTarget.classList.add('bg-green-300');
            }
        },
        dragleave(e) {
            // Clean up
            e.currentTarget.classList.add('bg-gray-100');
            e.currentTarget.classList.remove('bg-green-300');
        },
        async drop(e) {
            e.preDefault();
            await handle_drag_drop(e)
            e.currentTarget.classList.add('bg-gray-100');
            e.currentTarget.classList.remove('bg-green-300');
        },
        get_example_data() {
            let file_path
            if (this.customize_template_link.includes('http')) {
                if (this.config.default_data_link) {
                    file_path = this.config.default_data_link
                } else {
                    file_path = `data/demo/start.json`
                }
            } else {
                let tmp_name = this.config.template_name
                tmp_name = tmp_name.replace('demo_', 'demo/')
                file_path = `data/${tmp_name}.json`
            }
            download_data(file_path).then((data) => {
                this.set_data(data)
            })
        }
    },
    created() {
      this.consume_config()
    },
    computed: {
        template_link() {
            return `/?t=${this.customize_template_link}`;
        }
    }
}
</script>

<template>
    <main class="landing-box">
        <div class="container landing-container">
            <h4>Annotating with</h4>
            <h2>{{ config.template_label }}</h2>
            <h3>{{ config.template_description }}</h3>
            <div class="flex justify-center"> <!-- flex w-full h-screen items-center justify-center text-center -->
                <div class="ba b--dashed bw2 file-box" @dragover="dragover" @dragleave="dragleave" @drop="drop"> <!-- p-12 bg-gray-100 border border-gray-300  --> 
                    <input type="file" multiple name="fields[assetsFieldHandle][]" id="assetsFieldHandle" 
                        class="file-input-field" @change="handle_drag_drop" ref="file" accept=".json" /> <!-- w-px h-px opacity-0 overflow-hidden absolute -->
                
                    <label for="assetsFieldHandle" class="block cursor-pointer">
                        <div>
                            Drag &amp; drop, or <span class="underline">click here</span> to add an annotation file
                        </div>
                    </label>
                    <!-- <ul class="mt-4" v-if="filelist.length" v-cloak>
                        <li class="text-sm p-1" v-bind:key="file" v-for="file in filelist">
                            {{ file.name }}<button class="ml-2" type="button" @click="remove(filelist.indexOf(file))" title="Remove file">remove</button>
                        </li>
                    </ul> -->
                </div>
            </div>
            <div class="separator" v-if="config.template_name != 'serverless'">
                <span>or</span>
            </div>
            <div class="option-buttons" v-if="config.template_name != 'serverless'">
                <a v-if="config.tutorial_link" :href="config.tutorial_link">
                    <button class="pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn">See Tutorial</button>
                </a>
                <a @click="get_example_data">
                    <button class="pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn">View Example Data</button>
                </a>
                <a :href="template_link" v-if="this.customize_template_link">
                    <button class="pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn">Customize this Template</button>
                </a>
                <a v-if="config.paper_link" :href="config.paper_link" target="_blank">
                    <button class="pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn">View Paper</button>
                </a>

            </div>
        </div>
    </main>
</template>

<style>
  @import '../../assets/css/landing.css';
  @import '../../assets/css/index.css';
  @import '../../assets/css/button.css';
  @import 'https://unpkg.com/tachyons@4.10.0/css/tachyons.min.css';
</style>
