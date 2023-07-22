<script setup>
import EditList from "./EditList.vue";
</script>

<script>
export default {
    props: [
        'hits_data',
        'set_hits_data',
        'current_hit',
        'edits_dict',
        'set_edits_dict',
        'editor_open',
        'set_editor_state',
        'refresh_interface_edit',
        'annotating_edit_span_category_id',
        'set_annotating_edit_span_category_id',
        'annotating_edit_span',
        'set_annotating_edit_span',
        'lines',
        'set_lines',
        'config'
    ],
    data() {
        return {}
    },
    methods: {
        add_an_edit() {
            if (this.editor_open) {
                $('#add_an_edit').slideUp(300);
                $(".add_button .icon-default").removeClass("open")
            } else {
                $('#add_an_edit').slideDown(300);
                $(".add_button .icon-default").addClass("open")
            }
            this.set_editor_state(!this.editor_open)
        },
    },
    computed: {
        annotated_edits () {
            if (this.hits_data == null) { return 0 }
            let edit_data = this.hits_data[this.current_hit - 1]['edits']
            if (edit_data == null) { return 0 } 
            var count = 0
            edit_data.forEach(function(e) {
                if (e.hasOwnProperty('annotation') && e.annotation !== null) {
                    count++;
                }
            });
            return count
        },
        total_edits () {
            if (this.hits_data == null) { return 0 }
            let edit_data = this.hits_data[this.current_hit - 1]['edits']
            if (edit_data == null) { return 0 } 
            return edit_data.length
        },
    }
}
</script>

<template>
    <section>
        <div class="mt1 cf">
            <div class="fl w-80">
                <p class="f3 annotation-label ttu">{{ config.interface_text.annotation_viewer.header }} (<span v-if="!config.disable || !Object.values(config.disable).includes('annotation')">{{ annotated_edits }}/{{ total_edits }}</span><span v-if="config.disable && Object.values(config.disable).includes('annotation')">{{ total_edits }}</span>)</p>
            </div>
            <div class="fl w-20 tr">
                <p @click="add_an_edit" class="add_button pa2 br-pill-ns ba bw1 grow" :class="{'disabled': config.disable && Object.values(config.disable).includes('selection')}">
                    <i class="fa-solid fa-plus fa-1-5x icon-default pointer mr2"></i>
                    <span class="f4">{{ config.interface_text.buttons.add_edit_label }}</span>
                </p>
            </div>
        </div>
        <div>
            <EditList v-bind="$props" :config="config" />
        </div>
        <div id="hits-data" class="mt1 dn">{{ hits_data }}</div>
    </section>
</template>