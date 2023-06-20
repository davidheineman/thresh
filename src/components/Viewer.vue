<script setup>
    import Interface from "./Interface.vue";

    import { download_data, download_config, get_file_path } from "../assets/js/file-util.js";
    import jsyaml from 'js-yaml';
</script>

<script>
export default {
    data() {
        return {
            data: null,
            config: null,
        }
    },
    methods: {
        set_data(data) {
            this.data = data
        },
        set_config(config) {
            this.config = config
        },
    },
    created: async function() {
        // Load data
        let file_path = get_file_path();
        if (file_path == null) {
            file_path = '/data/salsa.json'
        }
        download_data(file_path).then((data) => {
            this.set_data(data)
        })

        // Load config
        let template = '/templates/salsa.yml'
        download_config(template).then((config) => {
            const parsedYaml = jsyaml.load(config);
            this.set_config(parsedYaml)
        })
    },
}
</script>

<template>
    <main v-if="
        config != null && 
        config != undefined &&
        data != null &&
        data != undefined">
        <Interface 
            :input_data={data}
            :config={config}
        />
    </main>
</template>