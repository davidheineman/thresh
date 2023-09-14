<script setup>
import _ from 'lodash';
</script>

<script>
export default {
    data() {
        return {
            target_html: ""
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
        'handle_tokenization_rendering',

        'process_edit_list',
        'hasAnnotations',
        'is_selected',
        'get_selected_index',
        'multi_select_enabled',
        'render_sentence',
        'click_span',
        'hover_span',
        'un_hover_span',

        'hit_box_config',
        'config'
    ],
    watch: {
        current_hit() {
            this.process_target_html();
        },
        hits_data() {
            this.process_target_html();
        },
        set_span_text() {
            this.process_target_html();
        },
        selected_state() {
            this.process_target_html_with_selected_span(this.selected_state.target_category);
        }
    },
    methods: {
        process_target_html() {
            const sent_type = 'output_idx'
            const span_class = 'target_span'
            const sent = this.hits_data[this.current_hit - 1].target

            try {
                this.target_html = this.render_sentence(sent, sent_type, span_class, null);
            } catch (e) {
                this.target_html = ''
                console.warn(e)
            }
        },
        process_target_html_with_selected_span(category) {
            const sent_type = 'output_idx'
            const span_class = 'target_span'
            const sent = this.hits_data[this.current_hit - 1].target

            try {
                this.target_html = this.render_sentence(sent, sent_type, span_class, category);
            } catch (e) {
                this.target_html = ''
                console.warn(e)
            }
        },
        // TOOD: I removed the hover span code, but there were some edge cases in there for split edits
        select_target_html(e) {
            if (!this.hit_box_config.enable_select_target_sentence) {
                return
            }
            let selected_category = $("input[name=edit_cotegory]:checked").val();
            let selection = window.getSelection();
            if (selection.anchorNode != selection.focusNode || selection.anchorNode == null) {
                this.process_target_html_with_selected_span(selected_category)
                return;
            }

            $('#target-sentence').addClass(`select-color-${selected_category}`)

            let split_chars = [' ']
            if (this.config.tokenization && this.config.tokenization == 'tokenized') {
                split_chars = ['Ġ', ' ']
            }
            let txt = this.hits_data[this.current_hit - 1].target

            let range = selection.getRangeAt(0);
            let [start, end] = [range.startOffset, range.endOffset];
            
            if (start == end) {
                return;
            }
            
            if (!this.config.tokenization || this.config.tokenization != 'char') {
                end -= 1; 
                while (split_chars.includes(txt.charAt(start))) {
                    start += 1; 
                }
                while (start - 1 >= 0 && !split_chars.includes(txt.charAt(start - 1))) {
                    start -= 1; 
                }
                while (split_chars.includes(txt.charAt(end))) {
                    end -= 1; 
                }
                while (end + 1 <= txt.length - 1 && !split_chars.includes(txt.charAt(end + 1))) {
                    end += 1; 
                }
                end += 1;
            }

            if (start >= end) {
                this.process_target_html_with_selected_span(selected_category)
                return;
            }

            let new_span_text = `<span class="selected-span-text bg-${selected_category}-light">\xa0${txt.substring(start, end)}\xa0</span>`
            this.set_span_text(new_span_text, 'target');

            if (this.hit_box_config.enable_multi_select_target_sentence) {
                let new_indices = this.selected_state.target_idx
                if (new_indices == null || new_indices.length == 0) {
                    new_indices = []
                }
                new_indices.push([start, end]);
                this.set_span_indices(new_indices, 'target');
                let new_span_text = "";
                // iterate through this.selected_span_in_target_indexs
                for (let i = 0; i < new_indices.length; i++) {
                    let [start, end] = new_indices[i];
                    new_span_text += `<span class="selected-span-text bg-${selected_category}-light">\xa0
                        <span @click="remove_selected('${selected_category}',${start},${end})" class="hover-white black br-pill mr1 pointer">✘</span>
                            ${txt.substring(start, end)}\xa0</span>&nbsp&nbsp`;
                }
                this.set_span_text(new_span_text, 'target');
            } else {
                this.set_span_indices([start, end], 'target');
            }
            this.set_span_category(selected_category, 'target');
            this.process_target_html_with_selected_span(selected_category);
        },
        deselect_target_html(e) {
            if (!this.hit_box_config.enable_select_target_sentence) {
                return
            }
            $("#target-sentence").html(this.hits_data[this.current_hit - 1].target);
            this.target_html = this.hits_data[this.current_hit - 1].target
        }
    },
    computed: {
        get_target_html() {
            return {
                template: ` <pre @mousedown='deselect_target_html' @mouseup='select_target_html' id="target-sentence" class="f4 lh-paras sans-serif" style="white-space: pre-line;"> ${ this.target_html } </pre> `,
                methods: {
                        select_target_html: this.select_target_html,
                        deselect_target_html: this.deselect_target_html,
                        remove_selected: this.remove_selected,
                        hover_span: this.hover_span,
                        un_hover_span: this.un_hover_span,
                        click_span: this.click_span,
                        handle_tokenization_rendering: this.handle_tokenization_rendering
                },
                mounted() {
                    this.handle_tokenization_rendering()
                }
            }
        }
    }
}
</script>

<template>
    <component :is="get_target_html"></component>
</template>
