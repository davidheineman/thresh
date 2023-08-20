<script setup>
    import Interface from "./Interface.vue";
    import Landing from "./Landing.vue";

    import { download_data, download_config, get_file_path } from "../../assets/js/file-util.js";
    import jsyaml from 'js-yaml';
</script>

<script>
export default {
    data() {
        return {
            data: null,
            consumed_config: null,
            
            set_data: this.set_data,
            set_config: this.set_config,
            customize_template_link: null,
            is_fetching: true,
            configInjection: null
        }
    },
    props: [
        'template_path',
        'serverless',
        'injection'
    ],
    methods: {
        set_data(data) {
            this.data = data
        },
        set_config(config) {
            this.consumed_config = config
        },
        highlight_container(i) {
            if (this.consumed_config.highlight_first_interface && i == 1) {
                return "adjudication-container-highlight"
            }
        },
        async load_language(config) {
            // Load language template
            const lang_code = config.language || 'en'
            const lang_template = `lang/${lang_code}.yml`
            let language_template = await download_config(lang_template).then((language_config) => {
                return jsyaml.load(language_config)
            })
            config.interface_text = Object.assign({}, language_template, config.interface_text);
            return config
        },
        async load_config(config_raw) {
            let config = jsyaml.load(config_raw);
            config = await this.load_language(config)
            
            // Enable crowdsource mode
            const params = new URLSearchParams(window.location.search);
            var prolificPID = params.get("PROLIFIC_PID");
            if (prolificPID) {
                config['crowdsource'] = "prolific"
            }

            this.set_config(config)
        },
        async load_data(data=null) {
            // Load data
            const params = new URLSearchParams(window.location.search);

            var dParam = params.get("d");
            var prolificPID = params.get("PROLIFIC_PID");
            var prolificStudyId = params.get("STUDY_ID");
            var prolificSessionId = params.get("SESSION_ID");
            
            if (dParam) {
                let datapath = dParam
                if (ghParam) {
                    datapath = `https://raw.githubusercontent.com/${dParam}`
                } else if (hfParam) {
                    datapath = `https://huggingface.co/datasets/${dParam.replace('main', 'resolve/main')}`
                }
                await download_data(datapath).then((data) => {
                    // Inject crowdsource parameters
                    if (prolificPID) {
                        for (let sent of data) {
                            if (!sent['metadata']) {
                                sent['metadata'] = {}
                            }
                            sent['metadata']['PROLIFIC_PID'] = prolificPID
                            sent['metadata']['STUDY_ID'] = prolificStudyId
                            sent['metadata']['SESSION_ID'] = prolificSessionId
                        }
                    }

                    if (this.consumed_config.adjudication) {
                        data = Array(this.consumed_config.adjudication).fill(data)
                    }

                    this.set_data(data)
                })
            } else if (this.consumed_config.adjudication) {
                let data = Array(this.consumed_config.adjudication).fill(null)
                for (let idx = 1; idx < this.consumed_config.adjudication + 1; idx++) {
                    var ajudicationDParam = params.get(`d${idx}`);
                    if (ajudicationDParam) {
                        data[idx-1] = {
                            "data": await download_data(ajudicationDParam)
                        }
                    }
                }
                this.set_data(data)
            } else {
                this.set_data(data)
            }
        }
    },
    created: async function() {
        let template_name;

        // Template paramters
        const params = new URLSearchParams(window.location.search);
        var iParam = params.get("i");
        var ghParam = params.get("gh");
        var hfParam = params.get("hf");

        if (iParam) {
            template_name = iParam
            this.customize_template_link = template_name
        } else if (ghParam) {
            template_name = `https://raw.githubusercontent.com/${ghParam}`
            this.customize_template_link = template_name
        } else if (hfParam) {
            template_name = `https://huggingface.co/datasets/${hfParam.replace('main', 'resolve/main')}`
            this.customize_template_link = template_name
        } else {
            template_name = `templates/${this.template_path}.yml`
            this.customize_template_link = this.template_path
        }

        if (this.serverless) {
            template_name = `templates/serverless.yml`
        }

        // Allow for config in custom HTML
        if (this.injection) {
            window.addEventListener('message', async (e) => {
                await this.load_config(e.data.template)
                const data_raw = await JSON.parse(e.data.data)
                await this.load_data(data_raw)
                this.customize_template_link = null
                this.is_fetching = false
            });
            return
        }

        // Load config
        const template = template_name
        const config_raw = await download_config(template)

        await this.load_config(config_raw)
        await this.load_data()

        this.is_fetching = false
    }
}
</script>

<template>
    <main v-if="
        (consumed_config != null && consumed_config != undefined) &&
        (data != null && data != undefined) &&
        is_fetching == false">
        <div v-if="consumed_config.adjudication" class="adjudication-container mh4">
            <Interface 
                v-for="idx in consumed_config.adjudication"
                v-bind:key="idx"
                :class="highlight_container(idx)"
                :highlight="consumed_config.highlight_first_interface && idx == 1"
                :input_data="data[idx-1]"
                :consumed_config={consumed_config}
            />
        </div>
        <div v-else class="mh4">
            <Interface 
                :input_data={data}
                :consumed_config={consumed_config}
            />
        </div>
    </main>
    <main v-else-if="
        (consumed_config != null && consumed_config != undefined) &&
        (data == null || data == undefined) &&
        is_fetching == false">
        <Landing v-bind="$data" />
    </main>
    <main v-else>
        <div class="spinner-container">
            <div class="spinner"></div>
        </div>
    </main>
</template>

<style>
  @import '../../assets/css/viewer.css';
</style>