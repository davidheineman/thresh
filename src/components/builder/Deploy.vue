<script setup>
import Tab from './Tab.vue'
import { toRaw } from 'vue'

import * as monaco from 'monaco-editor'
import loader from "@monaco-editor/loader";
import jsyaml from 'js-yaml';
import { handle_file_download, handle_interface_download } from "../../assets/js/file-util.js";
</script>

<script>
export default {
    data() {  
        return {
            active_tab: 'serverless',
            packaged_data: '',
            dataEditor: null
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
            const parsed_config = jsyaml.dump(this.config)
            parsed_data.push({
                "_thresh_template": parsed_config
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
        },
        download_interface() {
            const parsed_config = jsyaml.dump(this.config)
            handle_interface_download(
                parsed_config,
                this.config.template_name,
                null,
                false
            )
        },
        download_interface_packaged() {
            const parsed_config = jsyaml.dump(this.config)
            handle_interface_download(
                parsed_config,
                this.config.template_name,
                this.input_data,
                true
            )
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
                <!-- :class="{'is-active': active_tab == 'crowdsource'} -->
                <a @click="selectTab('serverless')" class="active">Serverless</a>
                <a @click="selectTab('hosted')">Hosted</a>
                <a @click="selectTab('python')">Python</a>
                <a @click="selectTab('crowdsource')">Crowdsource</a>
            </nav>
        </div>

        <div id="tab-contents">
            <Tab name="serverless" :selected="active_tab == 'serverless'">
                <h2>Package template + annotate on <code>thresh.tools</code></h2>
                <p>This will package your data and template in a single JSON file, and you can send this directly to annotators to annotate at <code>thresh.tools/annotate</code>. This is recommended for sharing data quickly (e.g. among co-authors), or small-scale annotation projects.</p>
                <h3>Export Data</h3>
                <div class="flex items-center mb2">
                    <input class="mr2 use_editor_data" type="checkbox" id="use_editor_data" value="use_editor_data" checked @change="use_editor_data_handler">
                    <label for="use_editor_data" class="lh-copy">Use data from editor</label>
                </div>
                <div class='upload-container data-upload-container data-upload-container-disabled' id="data-upload-container">
                    <div class='data-upload' />
                </div>
                <button @click="package_data" class="pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn mr2">Package Data + Interface</button>
                <a href="/annotate" target="_blank">
                    <button class="pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn">Visit <code>thresh.tools/annotate</code></button>
                </a>
            </Tab>
            <Tab name="hosted" :selected="active_tab == 'hosted'">
                <h2>Host template + connect to <code>thresh.tools</code></h2>
                <p>Host the template at your own domain and link it to <code>thresh.tools</code>. This is recommended for sharing your template alongside your work, in-house annotation projects or ablation studies.</p>
                <button @click="download_interface" class="pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn mr2">Download Interface</button>
                <h3>Linking a Template</h3>
                <p>You can link to any template using the format:</p>
                <pre>thresh.tools/<b>?i=[link to your interface]</b></pre>
                <p>For example:</p>
                <pre><a href='https://thresh.tools/?i=https://salsa-eval.com/interface.yml' target="_blank">thresh.tools/?i=https://salsa-eval.com/interface.yml</a></pre>
                <p>You can host the template on your own domain, or using existing free online repositories</p>
                <hr />
                <h3>Host with Gihub</h3>
                <p>Create a GitHub repo and add your template.</p>
                <pre>https://github.com/davidheineman/salsa/blob/main/interface.yml</pre>
                <p>And distribute using the <code>gh</code> parameter:</p>
                <pre>thresh.tools/<b>?gh=[link to your github template]</b></pre>
                <pre><a href="https://thresh.tools/?gh=davidheineman/salsa/main/interface.yml" target="_blank">thresh.tools/?gh=davidheineman/salsa/main/interface.yml</a></pre>
                <hr />
                <h3>Host with HuggingFace</h3>
                <p>Create a HuggingFace dataset and add your template (e.g., alongside your published data).</p>
                <pre>https://huggingface.co/datasets/davidheineman/salsa/resolve/main/interface.yml</pre>
                <p>And distribute using the <code>hf</code> parameter:</p>
                <pre>thresh.tools/<b>?hf=[link to your huggingface template]</b></pre>
                <pre><a href="https://thresh.tools/?hf=davidheineman/salsa/main/interface.yml" target="_blank">thresh.tools/?hf=davidheineman/salsa/main/interface.yml</a></pre>
                <hr />
                <h3>(Optional) Host Data</h3>
                <p>You can host data as well (e.g., to create individual links for annotators) using the following format:</p>
                <pre>thresh.tools/?i=[link to your interface]<b>&amp;d=[link to your data]</b></pre>
                <p>For example:</p>
                <pre><a href='https://thresh.tools/?gh=davidheineman/salsa/main/interface.yml&amp;d=davidheineman/salsa/main/demo_interface_data.json' target="_blank">thresh.tools/?gh=davidheineman/salsa/main/interface.yml&amp;d=davidheineman/salsa/main/demo_interface_data.json</a></pre>
                <p>You can follow the above instructions for hosting your data on GitHub or HuggingFace.</p>
                <hr />
                <h3>(Optional) Deployment with an iFrame</h3>
                <p>Want to host your interface using a custom link? Use the following code to host your template within any HTML document. The following will package your interface into an HTML file for distribution:</p>
                <button @click="download_interface_packaged" class="pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn mr2">Download Interface as HTML</button>
                <p>See an example here (<i>Note: no additional setup is required! Just the iframe</i>):</p>
                <pre><a href="http://salsa-eval.com/interface" target="_blank">salsa-eval.com/interface</a></pre>
                <hr />
                <h3>(Optional) Host Default Data</h3>
                <p>If you are sharing your template, you can specify a link within your config to include example data. This adds a "View Example Data" button to the landing page, and provides example data when editing the template.</p>
                <pre>default_data_link: [link to your data]</pre>
            </Tab>
            <Tab name="python" :selected="active_tab == 'python'">
                <h2>Manage data collection using <code>thresh</code> + Python</h2>
                <p>Plug your interface generation directly into your code using the <code>thresh</code> pip library. This is recommended for orchestrating large-scale annotation projects, deploying multiple interfaces simultaneously or for creating a pipeline between generation and annotation (e.g., a RLHF training setup).</p>
                <button @click="download_interface" class="pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn mr2">Download Interface</button>
                <h3>Setup</h3>
                <pre>pip install thresh</pre>
                <p>With the <code>thresh</code> library, your interface template is used to serialize your data into a Python object. Simply call <code>load_interface()</code>:</p>
                <pre>
from thresh import load_interface

# Load SALSA data using the SALSA typology
YourInterface = load_interface("your_interface.yml")

# Load existing annotations
thresh_data = YourInterface.load_annotations("your_data.json")</pre>
                <p>When you are finished preparing your data, you can export your data object to JSON using <code>export_data</code>:</p>
                <pre>
# Export data to [file_name].json for annotation
YourInterface.export_data(
    data=thresh_data,
    filename="[file_name].json"
)
</pre>
                <p>Then you can send directly to annotators, or upload to your own server.</p>
                <hr />
                <h3>Learn more</h3>
                <p>Check out our <a href='https://github.com/davidheineman/thresh.tools/blob/main/notebook_tutorials/load_data.ipynb'>example notebook →</a> which details each feature of the <code>thresh</code>, including using the custom <code>thresh</code> data classes.</p>
                <!-- <h3>(Optional) Integrate with HuggingFace Transformers</h3>
                <p>If you want to create a RLHF pipeline with your data, feel free to take a look at <a href='/'>our example notebook</a> on the topic!</p> -->
            </Tab>
            <Tab name="crowdsource" :selected="active_tab == 'crowdsource'">
                <h2>Deploy to crowdsource platforms</h2>
                <p>For large-scale crowdsource annotation projects, we reccomend using <code>thresh</code> and Python to deploy. Just add this line to configure crowdsourcing:</p>
                <pre>crowdsource: "[platform]"</pre>
                <button @click="download_interface" class="pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn mr2">Download Interface</button>
                <p>View our <a href='https://github.com/davidheineman/thresh.tools/blob/main/notebook_tutorials/deploy_to_prolific.ipynb'>example notebook →</a> which uses <code>thresh</code> and <code>dallinger</code> to deploy a large-scale annotation project to Prolific programatically.</p>
                <div style="text-align: center">
                    <img src="/img/prolific.png" width="500">
                    <img src="/img/prolific-deployed.png" width="500">
                </div>
                <!-- <p>This will directly create an Crowdsource job for your dataset in this browser. This is recommended for small scale annotation or debugging, NOT for a large project. In that case, we recommend deploying with Python.</p>
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
                    <input class="mr2" type="checkbox" id="crowdsource_test_env" value="crowdsource_test_env" checked>
                    <label for="crowdsource_test_env" class="lh-copy">Deploy to Crowdsource test environment (at <code>requester.crowdsource.com/developer/sandbox</code>)</label>
                </div>
                <div class="flex items-center mb2">
                    <input class="mr2" type="checkbox" id="enable_files" value="enable_files" checked>
                    <label for="enable_files" class="lh-copy">Add the <code>disable_upload_download=True</code> flag to disable annotators from using the file upload/download buttons</label>
                </div>
                <h3>Security Credentials</h3>
                <p><i>Note: We do NOT see your credentials, as the Crowdsource API calls are done exclusively in your browser (<a href='/'>see source code</a>).</i></p>
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
                <button class="pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn mr2">Deploy</button> -->
            </Tab>
        </div>
    </section>
  </main>
</template>