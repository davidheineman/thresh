<script setup>
import _ from 'lodash';
</script>

<script>
export default {
    data() {
        return {
            source_html: "",
        }
    },
    props: [
        'hits_data',
        'current_hit',
        'edits_dict',
        'selected_state',
        'selected_edits_html',
        'selected_edits',
        'set_selected_edits',
        'set_span_text',
        'set_span_indices',
        'set_span_category',
        'remove_selected',
        'lines',
        'set_lines',

        'process_edit_list',
        'hasAnnotations',
        'is_selected',
        'get_selected_index',
        'multi_select_enabled',
        'render_sentence',
        'click_span',
        'hover_span',
        'un_hover_span',
        'hit_box_config'
    ],
    watch: {
        current_hit() {
            this.process_source_html();
        },
        hits_data() {
            this.process_source_html();
        },
        set_span_text() {
            this.process_source_html();
        },
        selected_state() {
            this.process_source_html_with_selected_span(this.selected_state.source_category);
        }
    },
    methods: {
        process_source_html() {
            this.process_source_html_with_selected_span(null);
        },
        process_source_html_with_selected_span(category) {
            const sent_type = 'input_idx'
            const span_class = 'source_span'
            const sent = this.hits_data[this.current_hit - 1].source

            this.source_html = this.render_sentence(sent, sent_type, span_class, category);
        },
        select_source_html() {
            if (!this.hit_box_config.enable_select_source_sentence) {
                return
            }

            let selected_category = $("input[name=edit_cotegory]:checked").val();
            let selection = window.getSelection();
            if (selection.anchorNode != selection.focusNode || selection.anchorNode == null) {
                this.process_source_html_with_selected_span(selected_category)
                return;
            }

            $('#source-sentence').addClass(`select-color-${selected_category}`)

            let range = selection.getRangeAt(0)
            let [start, end] = [range.startOffset, range.endOffset]
            
            if (start == end) {
                return
            } 

            end -= 1
            let txt = this.hits_data[this.current_hit - 1].source
            while (txt.charAt(start) == ' ') {
                start += 1
            }
            while (start - 1 >= 0 && txt.charAt(start - 1) != ' ') {
                start -= 1
            }
            while (txt.charAt(end) == ' ') {
                end -= 1
            }
            while (end + 1 <= txt.length - 1 && txt.charAt(end + 1) != ' ') {
                end += 1
            }
            end += 1
            if (start >= end) {
                this.process_source_html_with_selected_span(selected_category)
                return
            }

            let new_span_text = `<span class="bg-${selected_category}-light">\xa0${txt.substring(start, end)}\xa0</span>`
            this.set_span_text(new_span_text, 'source')

            if (this.hit_box_config.enable_multi_select_source_sentence) {
                let new_indices = this.selected_state.source_idx
                if (new_indices == null || new_indices.length == 0) {
                    new_indices = []
                }
                new_indices.push([start, end])
                this.set_span_indices(new_indices, 'source')
                let new_span_text = ""
                // iterate through this.selected_span_in_source_indexs
                for (let i = 0; i < new_indices.length; i++) {
                    let [start, end] = new_indices[i]
                    new_span_text += `
                    <span class="bg-${selected_category}-light">\xa0
                        <span @click="remove_selected('${selected_category}', ${start}, ${end})" class="hover-white black br-pill mr1 pointer">✘</span>
                            ${txt.substring(start, end)}\xa0</span>&nbsp&nbsp`
                }
                this.set_span_text(new_span_text, 'source')
            } else {
                this.set_span_indices([start, end], 'source')
            }
            this.set_span_category(selected_category, 'source')
            this.process_source_html_with_selected_span(selected_category)
        },
        deselect_source_html() {
            if (!this.hit_box_config.enable_select_source_sentence) {
                return
            }
            $("#source-sentence").html(this.hits_data[this.current_hit - 1].source)
            this.source_html = this.hits_data[this.current_hit - 1].source
        }
    },
    computed: {
        get_source_html() {
            return {
                template: `<span @mousedown='deselect_source_html' @mouseup='select_source_html' id="source-sentence" class="f4 lh-paras">${this.source_html}</span>`,
                methods: {
                    select_source_html: this.select_source_html,
                    deselect_source_html: this.deselect_source_html,
                    remove_selected: this.remove_selected,
                    hover_span: this.hover_span,
                    un_hover_span: this.un_hover_span,
                    click_span: this.click_span
                }
            }
        }
    }
}
</script>

<template>
    <component :is="get_source_html"></component>
</template>