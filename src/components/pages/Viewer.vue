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
        }
    },
    props: [
        'template_path'
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
        let template_name = this.template_path

        // Load data
        // let file_path = get_file_path();
        // if (file_path == null) {
        //     file_path = `data/${template_name}.json`
        // }
        // download_data(file_path).then((data) => {
        //     this.set_data(data)
        // })

        // Load config
        const template = `templates/${template_name}.yml`
        let config = await download_config(template).then((resp) => {
            return jsyaml.load(resp);
        })

        // Load language template
        const lang_code = config.language || 'en'
        const lang_template = `lang/${lang_code}.yml`
        let language_template = await download_config(lang_template).then((language_config) => {
            return jsyaml.load(language_config)
        })
        // TODO: Interweave the language template with custom text, and apply to config
        config.interface_text = language_template

        this.set_config(config)
    },
}
</script>

<template>
    <main v-if="
        consumed_config != null && consumed_config != undefined &&
        data != null && data != undefined">
        <Interface 
            :input_data={data}
            :consumed_config={consumed_config}
        />
    </main>
    <main v-if="
        (consumed_config != null && consumed_config != undefined) &&
        (data == null || data == undefined)">
        <Landing v-bind="$data" />
    </main>
</template>

<style>
  @import '../../assets/css/viewer.css';
</style>