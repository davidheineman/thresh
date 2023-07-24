<script setup>
import Tab from './Tab.vue'
import { toRaw } from 'vue'

import * as monaco from 'monaco-editor'
import loader from "@monaco-editor/loader";
import jsyaml from 'js-yaml';
import { handle_file_download } from "../../assets/js/file-util.js";
</script>

<script>
export default {
    data() {  
        return {
            active_tab: 'serverless',
            packaged_data: '',
            dataEditor: null,
            
            iframe_demo_text: `ADD CODE`
        };
    },
    props: [
        'config',
        'deploy_open',
        'toggle_deploy',
        'input_data'
    ],
    watch: {
        async deploy_open(newVal) {
            if (newVal) {
                this.$nextTick(async () => {
                    this.render_tab_selector();
                    const { dataEditor, getDataValue, setDataValue } = await this.update_data_uploader()
                    this.dataEditor = dataEditor
                    this.getDataValue = getDataValue
                    this.setDataValue = setDataValue
                    this.packaged_data = this.input_data
                    setDataValue(JSON.stringify(this.packaged_data, null, 2))
                });
            }
        }
    },
    methods: {
        selectTab(selectedTab) {
            this.active_tab = selectedTab
            this.update_data_uploader()
            $('.use_editor_data').prop('checked', true);
            $('.data-upload-container').addClass('data-upload-container-disabled')
        },
        render_tab_selector() {
            var tabs = $('.tabs');
            var activeItem = tabs.find('.active');
            var activeWidth = activeItem.innerWidth();
            $(".selector").css({
                "left": activeItem.position.left + "px", 
                "width": activeWidth + "px"
            });
            $(".tabs").on("click","a",function(e){
                e.preventDefault();
                $('.tabs a').removeClass("active");
                $(this).addClass('active');
                var activeWidth = $(this).innerWidth();
                var itemPos = $(this).position();
                $(".selector").css({
                    "left":itemPos.left + "px", 
                    "width": activeWidth + "px"
                });
            });
        },
        async use_editor_data_handler(e) {
            const enabled = e.target.checked
            $('.use_editor_data').prop('checked', enabled);
            this.dataEditor.forEach(function(de) {toRaw(de).updateOptions({ readOnly: enabled })})
            if (enabled) {
                this.setDataValue(JSON.stringify(this.packaged_data, null, 2))
                $('.data-upload-container').addClass('data-upload-container-disabled')
            } else {
                $('.data-upload-container').removeClass('data-upload-container-disabled')
            }
        },
        package_data(e) {
            // TODO: Make sure this data is coming from the right monaco editor
            const data = this.getDataValue()[0]
            const parsed_data = JSON.parse(data)
            const pared_config = jsyaml.dump(this.config)
            parsed_data.push({
                "_nlproc_tools_template": pared_config
            });
            let filename;
            if (this.config.template_name) {
                filename = this.config.template_name
            } else {
                filename = "template"
            }
            filename = filename + "_packaged.json"
            handle_file_download(parsed_data, filename)
        },
        async update_data_uploader() {
            if ($('.data-upload').hasClass('rendered')) { return }
            var dataEditors = []
            var getDataValues = []
            var setDataValues = []
            const createEditor = async function(index, elem) {
                loader.init().then((monaco) => {
                    var dataValue = ""
                    const dataEditor = monaco.editor.create(elem, {
                        value: dataValue,
                        language: 'json',
                        minimap: { enabled: false },
                        automaticLayout: true,
                        theme: "vs-dark",
                        readOnly: true
                    });
                    dataEditor.onDidChangeModelContent((e) => { dataValue = dataEditor.getValue(); });
                    const getDataValue = () => { return dataValue }
                    const setDataValue = (val) => { dataEditor.setValue(val) }
                    getDataValues.push(getDataValue)
                    setDataValues.push(setDataValue)
                    dataEditors.push(dataEditor)
                    $($('.data-upload')[index]).addClass('rendered')
                });
            }
            var promises = []
            await $('.data-upload').each(async function(index, elem) {
                const promise = createEditor(index, elem)
                promises.push(promise)
            });
            await Promise.all(promises)
            var getDataValue = function() {
                return getDataValues.map(function(func) {
                    return func();
                });
            }
            var setDataValue = function(input) {
                setDataValues.forEach(function(func) {
                    func(input);
                });
            }
            const dataEditor = dataEditors
            return new Promise((resolve, reject) => {
                resolve({ 
                    dataEditor, getDataValue, setDataValue 
                }).catch((error) => {
                    reject(error);
                });
            });
        }
    },
    mounted() {
        this.render_tab_selector()
    },
}
</script>

<template>
  <main class="deploy-overlay overlay-container">
    <div class="overlay" v-if="deploy_open" @click="toggle_deploy"></div>
    <section v-if="deploy_open" class="modal br-pill-ns">
        <div class="wrapper">
            <nav class="tabs">
                <div class="selector"></div>
                <!-- :class="{'is-active': active_tab == 'mturk'} -->
                <a @click="selectTab('serverless')" class="active">Serverless</a>
                <a @click="selectTab('hosted')">Hosted</a>
                <a @click="selectTab('python')">Python</a>
                <a @click="selectTab('mturk')">MTurk</a>
            </nav>
        </div>

        <div id="tab-contents">
            <Tab name="serverless" :selected="active_tab == 'serverless'">
                <h2>Package with data and annotate on <code>nlproc.tools</code></h2>
                <p>This will package your data alongside the template, and you can send this directly to annotators to annotate at <code>nlproc.tools/annotate</code>. This is recommended for sharing data quickly (e.g. among co-authors), or small-scale annotation projects.</p>
                <h3>Data</h3>
                <div class="flex items-center mb2">
                    <input class="mr2 use_editor_data" type="checkbox" id="use_editor_data" value="use_editor_data" checked @change="use_editor_data_handler">
                    <label for="use_editor_data" class="lh-copy">Use data from editor</label>
                </div>
                <div class='upload-container data-upload-container data-upload-container-disabled' id="data-upload-container">
                    <div class='data-upload' />
                </div>
                <button @click="package_data" class="pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn mr2">Package Data</button>
                <a href="/annotate" target="_blank">
                    <button class="pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn">Visit <code>nlproc.tools/annotate</code></button>
                </a>
            </Tab>
            <Tab name="hosted" :selected="active_tab == 'hosted'">
                <h2>Host template and annotate on <code>nlproc.tools</code></h2>
                <p>Host the template at your own domain and link it to <code>nlproc.tools</code>. This is recommended for sharing your template alongside your work, in-house annotation projects or ablation studies.</p>
                <h3>Linking Templates</h3>
                <p>You can link to any template using the format:</p>
                <pre>nlproc.tools/<b>?i=[link to your interface]</b></pre>
                <p>For example:</p>
                <pre><a href='http://nlproc.tools/?i=https://salsa-eval.com/interface.yml' target="_blank">nlproc.tools/?i=https://salsa-eval.com/interface.yml</a></pre>
                <p>You can host the template on your own domain, or using existing free online repositories</p>
                <hr />
                <h3>Host with Gihub</h3>
                <p>Create a GitHub repo and add your template.</p>
                <pre>https://github.com/davidheineman/salsa/blob/main/interface.yml</pre>
                <p>And distribute using the <code>gh</code> parameter:</p>
                <pre>nlproc.tools/<b>?gh=[link to your github template]</b></pre>
                <pre><a href="http://nlproc.tools/?gh=davidheineman/salsa/main/interface.yml" target="_blank">nlproc.tools/?gh=davidheineman/salsa/main/interface.yml</a></pre>
                <h3>Host with HuggingFace</h3>
                <p>Create a HuggingFace dataset and add your template (e.g., alongside your published data).</p>
                <pre>https://huggingface.co/datasets/davidheineman/salsa/resolve/main/interface.yml</pre>
                <p>And distribute using the <code>hf</code> parameter:</p>
                <pre>nlproc.tools/<b>?hf=[link to your huggingface template]</b></pre>
                <pre><a href="http://nlproc.tools/?hf=davidheineman/salsa/main/interface.yml" target="_blank">nlproc.tools/?hf=davidheineman/salsa/main/interface.yml</a></pre>
                <hr />
                <h3>(Optional) Host Data</h3>
                <p>You can host data as well (e.g., to create individual links for annotators) using the following format:</p>
                <pre>nlproc.tools/?i=[link to your interface]<b>&amp;d=[link to your data]</b></pre>
                <p>For example:</p>
                <pre><a href='http://nlproc.tools/?gh=davidheineman/salsa/main/interface.yml&amp;d=davidheineman/salsa/main/demo_interface_data.json' target="_blank">nlproc.tools/?gh=davidheineman/salsa/main/interface.yml&amp;d=davidheineman/salsa/main/demo_interface_data.json</a></pre>
                <p>You can follow the above instructions for hosting your data on GitHub or HuggingFace.</p>
                <h3>(Optional) Deployment with an iFrame</h3>
                <p>Want to host your interface using a custom link? Use the following code to host your template within any HTML document:</p>
                <pre>{{ iframe_demo_text }}</pre>
                <p>See an example here (<i>Note: no additional setup is required! Just the iframe</i>):</p>
                <pre><a href="http://salsa-eval.com/interface" target="_blank">salsa-eval.com/interface</a></pre>
                <h3>(Optional) Host Default Data</h3>
                <p>If you are sharing your template, you can specify a link within your config to include example data. This adds a "View Example Data" button to the landing page, and provides example data when editing the template.</p>
                <pre>default_data_link: [link to your data]</pre>
            </Tab>
            <Tab name="python" :selected="active_tab == 'python'">
                <h2>Deploy your template using <code>nlproc_tools</code> + Python</h2>
                <p>Plug your interface generation directly into your code using the <code>nlproc_tools</code> pip library. This is recommended for orchestrating large-scale annotation projects, using multiple interfaces simultaneously (e.g., a multi-lingual project) or for creating a pipeline between generation and annotation (e.g., a RLHF training setup).</p>
                <h3>Setup</h3>
                <pre>pip install nlproc_tools</pre>
                <pre>TODO ADD CODE</pre>
                <p>Then you can send directly to annotators, or upload to your own server (see Hosted).</p>
                <hr />
                <h3>(Optional) Deploy to MTurk</h3>
                <p>To allow direct access to the AWS API, we have not created wrapper functions. Instead, check out our <a href='/'>example notebook →</a> which uses <code>nlproc_tools</code> and <code>boto3</code> to deploy a large-scale annotation project.</p>
                <h3>(Optional) Integrate with HuggingFace Transformers</h3>
                <p>If you want to create a RLHF pipeline with your data, feel free to take a look at <a href='/'>our example notebook</a> on the topic!</p>
            </Tab>
            <Tab name="mturk" :selected="active_tab == 'mturk'">
                <h2>Deploy to MTurk</h2>
                <p>This will directly create an MTurk job for your dataset in this browser. This is recommended for small scale annotation or debugging, NOT for a large project. In that case, we recommend deploying with Python.</p>
                <h3>Data</h3>
                <div class="flex items-center mb2">
                    <input class="mr2 use_editor_data" type="checkbox" id="use_editor_data" value="use_editor_data" checked @change="use_editor_data_handler">
                    <label for="use_editor_data" class="lh-copy">Use data from editor</label>
                </div>
                <div class='upload-container data-upload-container' id="data-upload-container">
                    <div class='data-upload' />
                </div>
                <h3>Job Configuration</h3>
                <div class="flex items-center mb2">
                    <input class="mr2" type="checkbox" id="mturk_test_env" value="mturk_test_env" checked>
                    <label for="mturk_test_env" class="lh-copy">Deploy to MTurk test environment (at <code>requester.mturk.com/developer/sandbox</code>)</label>
                </div>
                <div class="flex items-center mb2">
                    <input class="mr2" type="checkbox" id="enable_files" value="enable_files" checked>
                    <label for="enable_files" class="lh-copy">Add the <code>disable_upload_download=True</code> flag to disable annotators from using the file upload/download buttons</label>
                </div>
                <h3>Security Credentials</h3>
                <p><i>Note: We do NOT see your credentials, as the MTurk API calls are done exclusively in your browser (<a href='/'>see source code</a>).</i></p>
                <div class="aws-creds mb2">
                    <div class="w-100">
                        <label for="name" class="f6 b db mb2">Access Key ID</label>
                        <input id="name" class="input-reset ba b--black-20 pa2 mb2 db" type="text" aria-describedby="name-desc">
                    </div>
                    <div class="w-100">
                        <label for="name" class="f6 b db mb2">Secret Key</label>
                        <input id="name" class="input-reset ba b--black-20 pa2 mb2 db" type="text" aria-describedby="name-desc">
                    </div>
                    <div class="w-100">
                        <label for="name" class="f6 b db mb2">Temporary Secret Key</label>
                        <input id="name" class="input-reset ba b--black-20 pa2 mb2 db" type="text" aria-describedby="name-desc">
                    </div>
                </div>
                <button class="pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn mr2">Deploy</button>
            </Tab>
        </div>
    </section>
  </main>
</template>