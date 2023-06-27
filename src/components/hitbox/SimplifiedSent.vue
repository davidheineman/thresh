<script setup>
import _ from 'lodash';
</script>

<script>
export default {
    data() {
        return {
            simplified_html: ""
        }
    },
    props: [
        'hits_data',
        'current_hit',
        'edits_dict',
        'selected_edits_html',
        'selected_edits',
        'set_selected_edits',
        'selected_state',
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
            this.process_simplified_html();
        },
        hits_data() {
            this.process_simplified_html();
        },
        set_span_text() {
            this.process_simplified_html();
        },
        selected_state() {
            this.process_simplified_html_with_selected_span(this.selected_state.simplified_category);
        }
    },
    methods: {
        process_simplified_html() {
            const sent_type = 'output_idx'
            const span_class = 'simplified_span'
            const sent = this.hits_data[this.current_hit - 1].simplified

            this.simplified_html = this.render_sentence(sent, sent_type, span_class, null);
        },
        process_simplified_html_with_selected_span(category) {
            const sent_type = 'output_idx'
            const span_class = 'simplified_span'
            const sent = this.hits_data[this.current_hit - 1].simplified

            this.simplified_html = this.render_sentence(sent, sent_type, span_class, category);
        },
        // TOOD: I removed the hover span code, but there were some edge cases in there for split edits
        select_simplified_html(e) {
            if (!this.hit_box_config.enable_select_simplified_sentence) {
                return
            }
            let selected_category = $("input[name=edit_cotegory]:checked").val();
            let selection = window.getSelection();
            if (selection.anchorNode != selection.focusNode || selection.anchorNode == null) {
                this.process_simplified_html_with_selected_span(selected_category)
                return;
            }

            $('#simplified-sentence').addClass(`select-color-${selected_category}`)

            let range = selection.getRangeAt(0);
            let [start, end] = [range.startOffset, range.endOffset];
            
            if (start == end) {
                return;
            }
            end -= 1; 
            let txt = this.hits_data[this.current_hit - 1].simplified
            while (txt.charAt(start) == ' ') {
                start += 1; 
            }
            while (start - 1 >= 0 && txt.charAt(start - 1) != ' ') {
                start -= 1; 
            }
            while (txt.charAt(end) == ' ') {
                end -= 1; 
            }
            while (end + 1 <= txt.length - 1 && txt.charAt(end + 1) != ' ') {
                end += 1; 
            }
            end += 1;
            if (start >= end) {
                this.process_simplified_html_with_selected_span(selected_category)
                return;
            }

            let new_span_text = `<span class="bg-${selected_category}-light">\xa0${txt.substring(start, end)}\xa0</span>`
            this.set_span_text(new_span_text, 'simplified');

            if (this.hit_box_config.enable_multi_select_simplified_sentence) {
                let new_indices = this.selected_state.simplified_idx
                if (new_indices == null || new_indices.length == 0) {
                    new_indices = []
                }
                new_indices.push([start, end]);
                this.set_span_indices(new_indices, 'simplified');
                let new_span_text = "";
                // iterate through this.selected_span_in_simplified_indexs
                for (let i = 0; i < new_indices.length; i++) {
                    let [start, end] = new_indices[i];
                    new_span_text += `<span class="bg-${selected_category}-light">\xa0
                        <span @click="remove_selected('${selected_category}',${start},${end})" class="hover-white black br-pill mr1 pointer">✘</span>
                            ${txt.substring(start, end)}\xa0</span>&nbsp&nbsp`;
                }
                this.set_span_text(new_span_text, 'simplified');
            } else {
                this.set_span_indices([start, end], 'simplified');
            }
            this.set_span_category(selected_category, 'simplified');
            this.process_simplified_html_with_selected_span(selected_category);
        },
        deselect_simplified_html(e) {
            if (!this.hit_box_config.enable_select_simplified_sentence) {
                return
            }
            $("#simplified-sentence").html(this.hits_data[this.current_hit - 1].simplified);
            this.simplified_html = this.hits_data[this.current_hit - 1].simplified
        }
    },
    computed: {
        get_simplified_html() {
            return {
                template: ` <div @mousedown='deselect_simplified_html' @mouseup='select_simplified_html' id="simplified-sentence" class="f4 lh-paras"> ${ this.simplified_html } </div> `,
                methods: {
                        select_simplified_html: this.select_simplified_html,
                        deselect_simplified_html: this.deselect_simplified_html,
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
    <component :is="get_simplified_html"></component>
</template>