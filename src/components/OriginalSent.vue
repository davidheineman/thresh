<script setup>
import _ from 'lodash';
</script>

<script>
export default {
    data() {
        return {
            original_html: "",
            enable_select_original_sentence: true,
        }
    },
    props: [
        'hits_data',
        'current_hit',
        'edits_dict',
        'selected_span_in_original',
        'selected_span_in_original_indexs',
        'selected_span_in_original_category',
        'selected_edits_html',
        'selected_edits',
        'set_selected_edits',
        'selected_split',
        'selected_split_id',
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
    ],
    watch: {
        current_hit() {
            this.process_original_html();
        },
        hits_data() {
            this.process_original_html();
        },
        set_span_text() {
            this.process_original_html();
        },
        selected_span_in_original() {
            this.process_original_html_with_selected_span(this.selected_span_in_original_category);
        }
    },
    methods: {
        process_original_html() {
            this.process_original_html_with_selected_span(null);
        },
        process_original_html_with_selected_span(category) {
            const sent_type = 'input_idx'
            const span_class = 'original_span'
            const sent = this.hits_data[this.current_hit - 1].original

            this.original_html = this.render_sentence(sent, sent_type, span_class, category);
        },
        click_span(e) {
            const edits_dict = this.edits_dict
            const category = e.target.dataset.category
            const id = e.target.dataset.id
            const real_id = id.split("-")[1]

            if ($(".quality-selection").is(":visible")) {
                let new_selected_edits = _.cloneDeep(this.selected_edits);
                const selected_cateogry_name = $("input[name=edit_cotegory]:checked").val()
                if (selected_cateogry_name == 'split' || selected_cateogry_name == 'structure') {
                    if (real_id in new_selected_edits[category]) {
                        delete new_selected_edits[category][real_id]
                    } else {
                        new_selected_edits[category][real_id] = edits_dict[category][real_id]
                    }
                }
                this.set_selected_edits(new_selected_edits)
                
                // call annotate_edit code within EditList
                // this.set_edit_html(new_edit_html)
            } else {
                $(`.annotation-icon[data-id=${id}]`).click()
            }
        },
        hover_span(e) {
            if ($(".quality-selection").is(":visible")) {
                return
            }

            const category = e.target.dataset.category
            const id = e.target.dataset.id
            const real_id = id.split("-")[1]

            let color_code, color_class;
            if (e.target.classList.contains(`border-${category}-light`)) {
                color_code = `bg-${category}-light`
                color_class = "rgba(173, 197, 250, 1.0)"
            } else {
                color_code = `bg-${category}`
                color_class = "rgba(33, 134, 235, 1.0)"
            }

            let spans = $(`.${category}[data-id=${e.target.dataset.id}]`)
            let below_spans= $(`.${category}_below[data-id=${e.target.dataset.id}]`)
            spans.addClass(`white ${color_code}`)
            below_spans.addClass(`white ${color_code}`)
            below_spans.removeClass(`txt-${category} txt-${category}-light`)

            let new_lines = _.cloneDeep(this.lines)
            try {
                if (category == 'substitution') {
                    new_lines[category][real_id].color = color_class
                }
            } catch (e) { console.log(e) }
            this.set_lines(new_lines)
        },
        un_hover_span(e) {
            if ($(".quality-selection").is(":visible")) {
                return
            }

            const category = e.target.dataset.category
            const id = e.target.dataset.id
            const real_id = id.split("-")[1]

            let color_code, color_class;
            if (e.target.classList.contains(`border-${category}-light`)) {
                color_code = "rgba(173, 197, 250, 0.4)"
                color_class = `txt-${category}-light`
            } else {
                color_code = "rgba(33, 134, 235, 0.46)"
                color_class = `txt-${category}`
            }

            let spans = $(`.${category}[data-id=${e.target.dataset.id}]`)
            let below_spans= $(`.${category}_below[data-id=${e.target.dataset.id}]`)
            below_spans.addClass(color_class)
            spans.removeClass(`white bg-${category} bg-${category}-light`)
            below_spans.removeClass(`white bg-${category} bg-${category}-light`)

            let new_lines = _.cloneDeep(this.lines);
            try {
                if (category == 'substitution') {
                    new_lines[category][real_id].color = color_code
                }
            } catch (e) { console.log(e) }
            this.set_lines(new_lines)
        },
        select_original_html() {
            if (!this.enable_select_original_sentence) {
                return
            }

            let selected_category = $("input[name=edit_cotegory]:checked").val();
            let selection = window.getSelection();
            if (selection.anchorNode != selection.focusNode || selection.anchorNode == null) {
                this.process_original_html_with_selected_span(selected_category)
                return;
            }

            let range = selection.getRangeAt(0)
            let [start, end] = [range.startOffset, range.endOffset]
            
            if (start == end) {
                return
            } 

            end -= 1
            let txt = this.hits_data[this.current_hit - 1].original
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
                this.process_original_html_with_selected_span(selected_category)
                return
            }
            this.set_span_text('\xa0' + txt.substring(start, end) + '\xa0', 'original')

            if (this.enable_multi_select_original_sentence) {
                let new_indices = this.selected_span_in_original_indexs
                new_indices.push([start, end])
                set_span_indices(new_indices, 'original')
                let new_span_text = ""
                // iterate through this.selected_span_in_original_indexs
                for (let i = 0; i < new_indices.length; i++) {
                    let [start, end] = new_indices[i]
                    new_span_text += `
                    <span class="bg-substitution-light">\xa0
                        <span @click="remove_selected('${selected_category}', ${start}, ${end})" class="hover-white black br-pill mr1 pointer">✘</span>
                            ${txt.substring(start, end)}\xa0
                        </span>
                    &nbsp&nbsp`
                }
                this.set_span_text(new_span_text, 'original')
            } else {
                this.set_span_indices([start, end], 'original')
            }
            this.set_span_category(selected_category, 'original')
            this.process_original_html_with_selected_span(selected_category)
        },
        deselect_original_html() {
            if (!this.enable_select_original_sentence) {
                return
            }
            $("#original-sentence").html(this.hits_data[this.current_hit - 1].original)
            this.original_html = this.hits_data[this.current_hit - 1].original
        }
    },
    computed: {
        get_original_html() {
            return {
                template: `<div @mousedown='deselect_original_html' @mouseup='select_original_html' id="original-sentence" class="f4 lh-paras">${this.original_html}</div>`,
                methods: {
                    remove_selected: this.remove_selected,
                    select_original_html: this.select_original_html,
                    deselect_original_html: this.deselect_original_html,
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
    <component :is="get_original_html"></component>
</template>