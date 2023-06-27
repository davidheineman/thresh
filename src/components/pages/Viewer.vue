<script setup>
    import Interface from "./Interface.vue";

    import { download_data, download_config, get_file_path } from "../../assets/js/file-util.js";
    import jsyaml from 'js-yaml';
</script>

<script>
export default {
    data() {
        return {
            data: null,
            consumed_config: null,
        }
    },
    props: [
        'template'
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
        let template_name = this.template

        // Load data
        let file_path = get_file_path();
        if (file_path == null) {
            file_path = `data/${template_name}.json`
        }
        download_data(file_path).then((data) => {
            this.set_data(data)
        })

        // Load config
        let template = `templates/${template_name}.yml`
        download_config(template).then((config) => {
            const parsedYaml = jsyaml.load(config);
            this.set_config(parsedYaml)
        })
    },
}
</script>

<template>
    <main v-if="
        consumed_config != null && 
        consumed_config != undefined &&
        data != null &&
        data != undefined">
        <Interface 
            :input_data={data}
            :consumed_config={consumed_config}
        />
    </main>
</template>

<style>
  @import '../../assets/css/viewer.css';
</style>