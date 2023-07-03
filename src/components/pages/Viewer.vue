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
        }
    },
    props: [
        'template_path',
        'serverless'
    ],
    methods: {
        set_data(data) {
            this.data = data
        },
        set_config(config) {
            this.consumed_config = config
        },
    },
    created: async function() {
        let template_name;

        const params = new URLSearchParams(window.location.search)
        var iParam = params.get("i");
        var ghParam = params.get("gh");
        var hfParam = params.get("hf");

        if (iParam) {
            template_name = iParam
            this.customize_template_link = template_name
        } else if (ghParam) {
            // https://raw.githubusercontent.com/davidheineman/salsa/main/interface.yml
            template_name = `https://raw.githubusercontent.com/${ghParam}`
            this.customize_template_link = template_name
        } else if (hfParam) {
            // https://huggingface.co/datasets/davidheineman/salsa/resolve/main/interface.yml
            template_name = `https://huggingface.co/datasets/${hfParam.replace('main', 'resolve/main')}`
            this.customize_template_link = template_name
        } else {
            this.customize_template_link = this.template_path
            template_name = `templates/${this.template_path}.yml`
        }

        if (this.serverless) {
            template_name = `templates/serverless.yml`
        }

        // Load config
        const template = template_name
        let config = await download_config(template).then((resp) => {
            return jsyaml.load(resp);
        })

        // Load language template
        const lang_code = config.language || 'en'
        const lang_template = `lang/${lang_code}.yml`
        let language_template = await download_config(lang_template).then((language_config) => {
            return jsyaml.load(language_config)
        })
        config.interface_text = Object.assign({}, language_template, config.interface_text);
        this.set_config(config)

        // Load data
        var dParam = params.get("d");
        if (dParam) {
            let datapath = dParam
            if (ghParam) {
                datapath = `https://raw.githubusercontent.com/${dParam}`
            } else if (hfParam) {
                datapath = `https://huggingface.co/datasets/${dParam.replace('main', 'resolve/main')}`
            }
            await download_data(datapath).then((data) => {
                this.set_data(data)
            })
        }

        this.is_fetching = false
    },
}
</script>

<template>
    <main v-if="
        consumed_config != null && consumed_config != undefined &&
        data != null && data != undefined &&
        is_fetching == false">
        <Interface 
            :input_data={data}
            :consumed_config={consumed_config}
        />
    </main>
    <main v-if="
        (consumed_config != null && consumed_config != undefined) &&
        (data == null || data == undefined) &&
        is_fetching == false">
        <Landing v-bind="$data" />
    </main>
</template>

<style>
  @import '../../assets/css/viewer.css';
</style>