<script setup>
import _ from 'lodash';
</script>

<script>
export default {
    data() {
        return {
            simplified_html: "",
            enable_select_simplified_sentence: true,
        }
    },
    props: [
        'hits_data',
        'current_hit',
        'edits_dict',
        'selected_span_in_simplified',
        'selected_span_in_simplified_indexs',
        'selected_span_in_simplified_category',
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
            this.process_simplified_html();
        },
        hits_data() {
            this.process_simplified_html();
        },
        set_span_text() {
            this.process_simplified_html();
        },
        selected_span_in_simplified(e) {
            this.process_simplified_html_with_selected_span(this.selected_span_in_simplified_category);
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
        click_span(e) {
            let edits_dict = this.edits_dict
            let category = e.target.dataset.category
            let id = e.target.dataset.id
            let real_id = id.split("-")[1]
            if ($(".quality-selection").is(":visible")) {
                if ($("input[name=edit_cotegory]:checked").val() == 'split') {
                    let normal_id = parseInt(real_id) + 1
                    if (e.target.classList.contains(`split-sign`)) {
                        if (normal_id == 1) {
                            this.selected_split = `the 1st split`
                        } else if (normal_id == 2) {
                            this.selected_split = `the 2nd split`
                        } else if (normal_id == 3) {
                            this.selected_split = `the 3rd split`
                        } else {
                            this.selected_split = `the ${normal_id}th split`
                        }
                        this.selected_split_id = parseInt(real_id)
                    } else {
                        let new_selected_edits = _.cloneDeep(this.selected_edits);
                        if (real_id in new_selected_edits[category]) {
                            delete new_selected_edits[category][real_id]
                        } else {
                            new_selected_edits[category][real_id] = edits_dict[category][real_id]
                        }
                        this.set_selected_edits(new_selected_edits)
                    }
                }
                if ($("input[name=edit_cotegory]:checked").val() == 'structure') {
                    let new_selected_edits = _.cloneDeep(this.selected_edits);
                    if (real_id in new_selected_edits[category]) {
                        delete new_selected_edits[category][real_id]
                    } else {
                        new_selected_edits[category][real_id] = edits_dict[category][real_id]
                    }
                    this.set_selected_edits(new_selected_edits)
                }
                
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
            let category = e.target.dataset.category
            let spans = $(`.${category}[data-id=${e.target.dataset.id}]`)
            spans.addClass("white")

            let split_signs = $(`.split-sign[data-id=${e.target.dataset.id}]`)

            let below_spans= $(`.${category}_below[data-id=${e.target.dataset.id}]`)
            below_spans.addClass("white")
            below_spans.removeClass(`txt-${category}`)
            below_spans.removeClass(`txt-${category}-light`)

            let id = e.target.dataset.id
            let real_id = id.split("-")[1]
            if (e.target.classList.contains(`split-sign`)) {
                if (e.target.classList.contains(`txt-${category}-light`)) {
                    spans.addClass(`bg-${category}-light`)
                    spans.addClass(`white`)
                    spans.removeClass(`txt-${category}-light`)
                    below_spans.addClass(`bg-${category}-light`)
                    return
                } else {
                    spans.addClass(`bg-${category}`)
                    spans.addClass(`white`)
                    spans.removeClass(`txt-${category}`)
                    below_spans.addClass(`bg-${category}`)
                    return
                }
            }
            
            let new_lines = _.cloneDeep(this.lines);

            // check if bd-{category}-light is already in the class list
            if (e.target.classList.contains(`border-${category}-light`)) {
                spans.addClass(`bg-${category}-light`)
                if (category == 'split') {
                    split_signs.removeClass(`txt-${category}-light`)
                }
                below_spans.addClass(`bg-${category}-light`)
                try {
                    if (category == 'substitution') {
                        new_lines[category][real_id].color = "rgba(173, 197, 250, 1.0)"
                    }
                } catch (e) {
                    console.log(e)
                }
                
            } else {
                spans.addClass(`bg-${category}`)
                if (category == 'split') {
                    split_signs.removeClass(`txt-${category}`)
                }
                below_spans.addClass(`bg-${category}`)
                try {
                    if (category == 'substitution') {
                        new_lines[category][real_id].color = "rgba(33, 134, 235, 1.0)"
                    }
                } catch (e) {
                    console.log(e)
                }
            }

            this.set_lines(new_lines)
        },
        un_hover_span(e) {
            if ($(".quality-selection").is(":visible")) {
                return
            }
            let category = e.target.dataset.category
            let spans = $(`.${category}[data-id=${e.target.dataset.id}]`)
            spans.removeClass("white")

            let split_signs = $(`.split-sign[data-id=${e.target.dataset.id}]`)

            let below_spans= $(`.${category}_below[data-id=${e.target.dataset.id}]`)
            below_spans.removeClass("white")

            let id = e.target.dataset.id
            let real_id = id.split("-")[1]

            let below_spans_class_list = below_spans.attr('class').split(/\s+/)
            if (e.target.classList.contains(`split-sign`)) {
                if (below_spans_class_list.includes(`bg-${category}-light`)) {
                    spans.removeClass(`bg-${category}-light`)
                    spans.removeClass(`white`)
                    split_signs.addClass(`txt-${category}-light`)
                    below_spans.removeClass(`bg-${category}-light`)
                    below_spans.addClass(`txt-${category}-light`)
                    return
                } else {
                    spans.removeClass(`bg-${category}`)
                    spans.removeClass(`white`)
                    split_signs.addClass(`txt-${category}`)
                    below_spans.removeClass(`bg-${category}`)
                    below_spans.addClass(`txt-${category}`)
                    return
                }
            }


            let new_lines = _.cloneDeep(this.lines);

            if (e.target.classList.contains(`border-${category}-light`)) {
                below_spans.addClass(`txt-${category}-light`)
                if (category == 'split') {
                    split_signs.addClass(`txt-${category}-light`)
                }
                try {
                    if (category == 'substitution') {
                        new_lines[category][real_id].color = "rgba(173, 197, 250, 0.4)"
                    }
                } catch (e) {
                    console.log(e)
                }
            } else {
                below_spans.addClass(`txt-${category}`)
                if (category == 'split') {
                    split_signs.addClass(`txt-${category}`)
                }
                try {
                    if (category == 'substitution') {
                        console.log(new_lines[category])
                        new_lines[category][real_id].color = "rgba(33, 134, 235, 0.46)"
                    }
                } catch (e) {
                    console.log(e)
                }
            }

            this.set_lines(new_lines)

            spans.removeClass(`bg-${category}`)
            spans.removeClass(`bg-${category}-light`)
            below_spans.removeClass(`bg-${category}`)
            below_spans.removeClass(`bg-${category}-light`)
        },
        select_simplified_html(e) {
            if (!this.enable_select_simplified_sentence) {
                return
            }
            let selected_category = $("input[name=edit_cotegory]:checked").val();
            let selection = window.getSelection();
            if (selection.anchorNode != selection.focusNode || selection.anchorNode == null) {
                this.process_simplified_html_with_selected_span(selected_category)
                return;
            }
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
            this.set_span_text('\xa0' + txt.substring(start, end) + '\xa0', 'simplified');

            if (this.enable_multi_select_simplified_sentence) {
                let new_indices = this.selected_span_in_simplified_indexs
                new_indices.push([start, end]);
                this.set_span_indices(new_indices, 'simplified');
                let new_span_text = "";
                // iterate through this.selected_span_in_simplified_indexs
                for (let i = 0; i < new_indices.length; i++) {
                    let [start, end] = new_indices[i];
                    new_span_text += `<span class="bg-substitution-light">\xa0
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
            if (!this.enable_select_simplified_sentence) {
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
                        remove_selected: this.remove_selected,
                        select_simplified_html: this.select_simplified_html,
                        deselect_simplified_html: this.deselect_simplified_html,
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