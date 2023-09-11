<script setup>
import VRuntimeTemplate from "vue3-runtime-template";
import _ from 'lodash';
import LeaderLine from 'leader-line-vue';
import tinycolor from 'tinycolor2';
import { COLORS, LIKERT_COLOR_MAP } from '../../assets/js/constants.js';
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
        return {
            edits_html: "",
            line_locked: false
        }
    },
    watch: {
        current_hit() {
            $(`#circle-${this.current_hit}`).addClass('circle-active');
            this.process_edits_html();
            this.draw_lines();
        },
        hits_data() {
            this.process_edits_html();
            this.draw_lines();
        },
        edits_dict() {
            this.draw_lines();
        },
    },
    methods: {
        annotate_edit(e) {
            const source_sentence = this.hits_data[this.current_hit - 1].source
            const target_sentence = this.hits_data[this.current_hit - 1].target
            const edit_dict = this.edits_dict

            const category = e.target.dataset.category
            const id = e.target.dataset.id
            const real_id = parseInt(e.target.dataset.id.split("-")[1])

            $(".child-question").hide();
            if (this.editor_open) {
                $(`.quality-selection[data-category=${category}]`).hide(300);
                this.refresh_interface_edit();
                return;
            } else {
                $(`.quality-selection`).hide(300)
                $(`.quality-selection[data-category=${category}]`).slideDown(300);
                $(e.target).addClass(`txt-${category}`)
                this.set_editor_state(!this.editor_open)
            }
            $(`.${category}[data-id=${id}]`).removeClass(`border-${category}-light`).addClass(`white border-${category} bg-${category}`)

            let annotating_span = edit_dict.find(function(entry) {
                return entry['category'] === category && entry['id'] === real_id;
            });

            if (this.getEditConfig(category)['multi_span']) {
                let source_spans = annotating_span['input_idx']
                let new_edit_span = ""
                for (let i = 0; i < source_spans.length; i++) {
                    if (i != 0) {
                        new_edit_span += `<span class="edit-type txt-${category} f3"> and </span>`
                    }
                    new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${category} border-${category}-all ${category}_below">
                        &nbsp${source_sentence.substring(source_spans[i][0], source_spans[i][1])}&nbsp</span>`
                }
                this.set_annotating_edit_span(new_edit_span, 'source')

                let target_spans = annotating_span['output_idx']
                new_edit_span = ""
                for (let i = 0; i < target_spans.length; i++) {
                    if (i != 0) {
                        new_edit_span += `<span class="edit-type txt-${category} f3"> and </span>`
                    }
                    new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${category} border-${category}-all ${category}_below">
                        &nbsp${target_sentence.substring(target_spans[i][0], target_spans[i][1])}&nbsp</span>`
                }
                this.set_annotating_edit_span(new_edit_span, 'target')
            } else if (this.getEditConfig(category)['type'] == 'composite') {
                let new_edit_span = ""
                let light = ""

                new_edit_span += `<span class="edit-type txt-${category}${light} f3"> (</span>`;
                for (let j = 0; j < annotating_span['constituent_edits'].length; j++) {
                    const constituent_edit = annotating_span['constituent_edits'][j];
                    const constituent_key = constituent_edit['category'];

                    new_edit_span += this.render_edit_text(constituent_edit, real_id, constituent_key, light)
                    if (j == annotating_span['constituent_edits'].length - 1) {
                        new_edit_span += `<span class="edit-type txt-${category}${light} f3"> )</span>`;
                    } else {
                        new_edit_span += `<span class="edit-type txt-${category}${light} f3"> , </span>`;
                    }
                }
                this.set_annotating_edit_span(new_edit_span, 'composite')
            } else {
                if (annotating_span.hasOwnProperty('input_idx')) {
                    let span_idx = annotating_span['input_idx'][0]
                    let new_edit_span = ""
                    new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${category} border-${category}-all ${category}_below">
                        &nbsp${source_sentence.substring(span_idx[0], span_idx[1])}&nbsp</span>`
                    this.set_annotating_edit_span(new_edit_span, 'source')
                }

                if (annotating_span.hasOwnProperty('output_idx')) {
                    let span_idx = annotating_span['output_idx'][0]
                    let new_edit_span = ""
                    new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${category} border-${category}-all ${category}_below">
                        &nbsp${target_sentence.substring(span_idx[0], span_idx[1])}&nbsp</span>`
                    this.set_annotating_edit_span(new_edit_span, 'target')
                }
            }

            this.set_annotating_edit_span_category_id(real_id)
        },
        trash_edit(e) {
            const real_id = parseInt(e.target.dataset.id.split("-")[1])
            const category = e.target.dataset.category
            const old_edits_list = this.hits_data[this.current_hit - 1]["edits"]

            let new_edits_list = []
            for (const old_edit of old_edits_list) {
                if (old_edit["id"] == real_id && old_edit["category"] == category) {
                    continue
                }
                new_edits_list.push(old_edit)
            }

            let new_hits_data = _.cloneDeep(this.hits_data);
            new_hits_data[this.current_hit - 1]["edits"] = new_edits_list
            this.set_hits_data(new_hits_data);
        },
        hasAnnotation(edit) {
            return edit['annotation'] != null || (this.config.disable && Object.values(this.config.disable).includes('annotation'))
        },
        getEditConfig(category) {
            if (!this.config.hasOwnProperty('edits')) { return {}; }
            return this.config['edits'].find(function(entry) {
                return entry['name'] === category;
            });
        },
        linesDisabled() {
          return this.config.hasOwnProperty('display') && Object.values(this.config.display).includes('disable-lines')
        },
        getAnnotationHtml(ann_config, ann) {
            if (ann == null) {
                return '';
            }

            let ann_html = ''
            for (let edit_ann_type of ann_config) {
                let ann_type_name = edit_ann_type['name']
                let ann_type_label = edit_ann_type.label ? edit_ann_type.label : ann_type_name

                ann_type_label = ann_type_label.replace('grammar_error', 'G') // TODO: Get rid of manual override

                if (!edit_ann_type.hasOwnProperty('options')) {
                    continue
                }

                if (edit_ann_type['options'] == 'binary') {
                    if (ann[ann_type_name] == "yes") {
                        // ann_html += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                        // ann_html += ` <span class="brown ba bw1 pa1 br-pills">Coref error</span>`;
                        ann_html += ` <span class="brown ba bw1 pa1 br-pills mr2">${ann_type_label}</span>`;
                    }
                } else if (edit_ann_type['options'] == 'likert-3') {
                    if (ann[ann_type_name] != null) {
                        let ann_color = LIKERT_COLOR_MAP[ann[ann_type_name]] ? LIKERT_COLOR_MAP[ann[ann_type_name]] : 'black'
                        ann_html += `<span class="${ann_color} br-pills ba bw1 pa1">${ann_type_label}: ${ann[ann_type_name]}</span>`;
                    }
                } else if (edit_ann_type['options'] == 'textarea' || edit_ann_type['options'] == 'textbox') {
                    if (ann[ann_type_name] != null) {
                        let ann_color = 'green'
                        ann_html += `<span class="${ann_color} br-pills ba bw1 pa1 mr2">${ann_type_label}: ${ann[ann_type_name]}</span>`;
                    }
                } else {
                    // custom edit types
                    if (!ann[ann_type_name]) { continue }
                    let selected = ann[ann_type_name]["val"]
                    if (selected != null && selected != "") {
                        ann_html += ''

                        let custom_label = edit_ann_type['options'].find(d => d.name === selected)
                        custom_label = custom_label.label ? custom_label.label : selected
                        ann_html += `<span class="light-purple ba bw1 pa1 mr2">${custom_label}</span>`

                        if (edit_ann_type.hasOwnProperty('options')) {
                            ann_html += this.getAnnotationHtml(edit_ann_type['options'], ann[ann_type_name])
                        }
                    }
                }
            }
            return ann_html
        },
        render_edit_text(edit, i, key, light) {
            const edit_config = this.getEditConfig(key)
            const edit_label = edit_config.label ? edit_config.label : key

            let new_html = ''
            new_html += `
                <span data-id="${key}-${i}" data-category="${key}" class="default_cursor" @mouseover="hover_span" @mouseout="un_hover_span">
                    <span class="edit-type txt-${key}${light} f3">${edit_label} </span>`;

            if (!edit.hasOwnProperty('input_idx') && !edit.hasOwnProperty('output_idx')) { return new_html }

            if (edit_config['type'] == 'multi_span') {
                if (edit.hasOwnProperty('input_idx')) {
                    let source_spans_for_subs = edit['input_idx']
                    for (let j = 0; j < source_spans_for_subs.length; j++) {
                        let source_span = source_spans_for_subs[j];
                        if (j != 0) {
                            new_html += `<span class="edit-type txt-${key}${light} f3"> and </span>`;
                        }
                        new_html += `
                            <span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">
                                &nbsp${this.hits_data[this.current_hit - 1].source.substring(source_span[0], source_span[1])}&nbsp</span>`;
                    }
                }
                if (edit.hasOwnProperty('input_idx') && edit.hasOwnProperty('output_idx')) {
                    new_html += `<span class="edit-type txt-${key}${light} f3"> with </span>`;
                }
                if (edit.hasOwnProperty('output_idx')) {
                    let target_spans_for_subs = edit['output_idx']
                    for (let j = 0; j < target_spans_for_subs.length; j++) {
                        let target_span = target_spans_for_subs[j];
                        if (j != 0) {
                            new_html += `<span class="edit-type txt-${key}${light} f3"> and </span>`;
                        }
                        new_html += `
                            <span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">
                                &nbsp${this.hits_data[this.current_hit - 1].target.substring(target_span[0], target_span[1])}&nbsp</span>`;
                    }
                }
            } else {
                new_html += `
                <span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                if (edit.hasOwnProperty('input_idx')) {
                    let in_span = edit['input_idx'][0]
                    new_html += `
                        &nbsp${this.hits_data[this.current_hit - 1].source.substring(in_span[0], in_span[1])}&nbsp</span>`;
                } else if (edit.hasOwnProperty('output_idx')) {
                    let out_span = edit['output_idx'][0]
                    new_html += `
                        &nbsp${this.hits_data[this.current_hit - 1].target.substring(out_span[0], out_span[1])}&nbsp</span>`;
                }
            }

            return new_html
        },
        process_edits_html() {
            let new_html = ''

            let hit_edits = _.cloneDeep(this.hits_data[this.current_hit - 1].edits)

            // Sort edits
            const getSmallestValue = (arr) => (arr ? Math.min(...arr.map((arr) => arr[0])) : Infinity);
            hit_edits.sort((a, b) => {
                const aMin = Math.min(getSmallestValue(a.input_idx), getSmallestValue(a.output_idx));
                const bMin = Math.min(getSmallestValue(b.input_idx), getSmallestValue(b.output_idx));
                return aMin - bMin;
            });

            for (let edit of hit_edits) {
                let i = edit['id']
                let key = edit['category'];
                let light = !this.hasAnnotation(edit) ? "-light" : ""
                new_html += `
                    <div class='cf'>
                        <div class="fl w-80 edit">`;

                // Render edit
                const edit_config = this.getEditConfig(key)
                const edit_label = edit_config.label ? edit_config.label : key
                if (edit_config['type'] == 'composite') {
                    const composite_icon = this.getEditConfig(key)['icon']
                    new_html += `
                        <span data-id="${key}-${i}" data-category="${key}" class="default_cursor" @mouseover="hover_span" @mouseout="un_hover_span">
                            <span class="edit-type txt-${key}${light} f3">${edit_label} </span>
                            <span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">
                                &nbsp<i class="fa-solid ${composite_icon}"></i>&nbsp</span>
                                <span class="edit-type txt-${key}${light} f3"> (</span>`;

                    for (let j = 0; j < edit['constituent_edits'].length; j++) {
                        const constituent_edit = edit['constituent_edits'][j];
                        const constituent_key = constituent_edit['category'];

                        new_html += this.render_edit_text(constituent_edit, i, constituent_key, light)
                        new_html += `</span>`;
                        if (j != edit['constituent_edits'].length - 1) {
                            new_html += `<span class="edit-type txt-${key}${light} f3"> , </span>`;
                        } else {
                            new_html += `<span class="edit-type txt-${key}${light} f3"> )</span>`;
                        }
                    }
                } else {
                    new_html += this.render_edit_text(edit, i, key, light)
                }

                if (!this.config.disable || !Object.values(this.config.disable).includes('annotation')) {
                    new_html += ` : `;
                }

                // Render annotation
                if (!this.hasAnnotation(edit)) {
                    if (!this.config.disable || !Object.values(this.config.disable).includes('annotation')) {
                        new_html += `
                            <span class="f4 i black-60">${this.config.interface_text.annotation_viewer.not_annotated_text_1} <i class="fa-solid fa-pencil"></i> ${this.config.interface_text.annotation_viewer.not_annotated_text_2}</span>
                        `;
                    }
                } else {
                    const edit_config = this.getEditConfig(key)
                    let ann_html = this.getAnnotationHtml(edit_config['annotation'], edit['annotation'])
                    new_html += `<span class="f4 i">${ann_html}</span>`;
                }

                let disabled = ''
                if (this.config.disable && Object.values(this.config.disable).includes('annotation')) {
                    disabled = 'disabled'
                }

                new_html += `
                        </span>
                    </div>
                    <div class="fl w-20 mb4 operation tr">
                        <i @click="annotate_edit" class="annotation-icon fa-solid fa-pencil mr3 pointer dim ${disabled}" data-id="${key}-${i}" data-category="${key}"></i>
                        <i @click="trash_edit" class="fa-solid fa-trash-can ml4 pointer dim" data-id="${key}-${i}" data-category="${key}"></i>
                    </div>
                </div>`;
            }

            this.set_edits_dict(hit_edits);
            this.edits_html = new_html;
        },
        clear_lines: function() {
            // Remove existing lines as defined by LeaderLine
            const lines_list = [].concat(...Object.values(this.lines).map(e => Object.values(e)));
            for (let line of lines_list) {
                if (line instanceof Array) {
                    Object.values(line).forEach(l => {
                        try {l.remove()} catch (e) { console.warn(e) }
                    });
                } else {
                    try { line.remove() } catch (e) { console.warn(e) }
                }
            }
            $('.leader-line').remove();
        },
        draw_lines: function() {
            // There's some latency in this function, the locking ensures no line references are lost
            if (this.line_locked) { return }
            if (!this.config.hasOwnProperty('edits') || this.linesDisabled()) { return }
            this.line_locked = true

            try {
                this.clear_lines()
            } catch (e) { console.warn(e) }

            let new_lines = Object.fromEntries(this.config.edits.map(t => [t.name, {}]));
            let hit_edits = _.cloneDeep(this.hits_data[this.current_hit - 1].edits)

            for (let edit of hit_edits) {
                let id = edit['id']
                let key = edit['category'];
                const edit_config = this.getEditConfig(key)

                const line_config = {
                    endPlug: "behind",
                    size: 3,
                    path: "straight"
                }

                let color = edit_config.color
                if (COLORS.hasOwnProperty(color)) {
                    color = COLORS[color]
                }
                if (!this.hasAnnotation(edit)) {
                    color = tinycolor(color).lighten(25).toHexString();
                }
                line_config.color = color

                try {
                    if (edit_config['type'] == 'composite') {
                        for (let constituent_edit of edit['constituent_edits']) {
                            new_lines[key][id] = []
                            const cid = constituent_edit['id']
                            const ccategory = constituent_edit['category']
                            const constituent_edit_config = this.getEditConfig(ccategory)

                            if (constituent_edit_config['enable_input'] && constituent_edit_config['enable_output']) {
                                new_lines[key][id].push(
                                    LeaderLine.setLine(
                                        $(`.${key}.source_span[data-id='${key}-${id}'][data-childcategory=${ccategory}][data-childid=${cid}]`)[0],
                                        $(`.${key}.target_span[data-id='${key}-${id}'][data-childcategory=${ccategory}][data-childid=${cid}]`)[0],
                                        line_config
                                    )
                                )
                            }
                        }
                    } else if (edit_config['enable_input'] && edit_config['enable_output']) {
                        if ($(`.${key}.source_span`)[0] == null) {
                            console.warn("Something went wrong!")
                        }

                        new_lines[key][id] = LeaderLine.setLine(
                            $(`.${key}.source_span[data-id='${key}-${id}']`)[0],
                            $(`.${key}.target_span[data-id='${key}-${id}']`)[0],
                            line_config
                        )

                        // My attempt to fix line drawing in builder via mutation observers
                        // var draw_lines = this.draw_lines
                        // const targetElement = $(`.${key}.source_span[data-id='${key}-${id}']`)[0]
                        // let initialRect = targetElement.getBoundingClientRect();
                        // function checkPositionChange() {
                        //     const currentRect = targetElement.getBoundingClientRect();
                        //     if (currentRect.x !== initialRect.x || currentRect.y !== initialRect.y) {
                        //         draw_lines()
                        //         initialRect = currentRect;
                        //     }
                        // }
                        // const observer = new MutationObserver(() => {
                        //     checkPositionChange();
                        // });
                        // observer.observe(targetElement, { attributes: true });
                        // $('#sandbox')[0].addEventListener('scroll', checkPositionChange);
                    }
                } catch (e) { console.warn(e) }
            }

            // TODO: This is essentially code which points from split edits to other edits
            // let split_edits_dict = this.edits_dict["split"]
            // if (split_edits_dict != {}) {
            //     for (let id in split_edits_dict) {
            //         let color = "rgba(250, 229, 175, 0.4)"
            //         if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (id in this.hits_data[[this.current_hit - 1]].annotations["split"])) {
            //             color = "rgba(247, 206, 70, 0.46)"
            //         }
            //         new_lines["split"][id] = []
            //         for (let span_category in split_edits_dict[id]) {
            //             for (let span_id in split_edits_dict[id][span_category]) {
            //                 let css_config = `[data-id='split-${id}'][data-childcategory=${span_category}][data-childid=${span_id}]`
            //                 const line_config = {
            //                     endPlug: "arrow3",
            //                     size: 3,
            //                     path: "arc",
            //                     color: color
            //                 }
            //                 if (span_category == "deletion") {
            //                     new_lines["split"][id].push(
            //                         LeaderLine.setLine(
            //                         $(`.split.source_span${css_config}`)[0],
            //                         $(`.split.split-sign[data-id='split-${id}']`)[0],
            //                         line_config)
            //                     )
            //                 } else if (span_category =="insertion") {
            //                     new_lines["split"][id].push(
            //                         LeaderLine.setLine(
            //                         $(`.split.target_span${css_config}`)[0],
            //                         $(`.split.split-sign[data-id='split-${id}']`)[0],
            //                         line_config)
            //                     )
            //                 } else if (span_category == "substitution" || span_category == "reorder") {
            //                     new_lines["split"][id].push(
            //                         LeaderLine.setLine(
            //                         $(`.split.source_span${css_config}`)[0],
            //                         $(`.split.target_span${css_config}`)[0],
            //                         line_config)
            //                     )

            //                     new_lines["split"][id].push(
            //                         LeaderLine.setLine(
            //                         $(`.split.target_span${css_config}`)[0],
            //                         $(`.split.split-sign[data-id='split-${id}']`)[0],
            //                         line_config)
            //                     )
            //                 }
            //             }
            //         }
            //     }
            // }

            this.set_lines(new_lines)
            this.line_locked = false
        },
        reposition_lines() {
            // this.draw_lines()
            const lines_list = [].concat(...Object.values(this.lines).map(e => Object.values(e)));
            for (let line of lines_list) {
                if (line instanceof Array) {
                    Object.values(line).forEach(l => {
                        try {l.position()} catch (e) { console.warn(e) }
                    });
                } else {
                    try { line.position() } catch (e) { console.warn(e) }
                }
            }
        },
        // TODO: Implement these via referencing using jquery
        hover_span() {},
        un_hover_span() {}
    },
    computed: {
        get_edits_html() {
            return {
                template: `<div id="edits_html" class="f4 lh-paras">${this.edits_html}</div>`,
                methods: {
                    annotate_edit: this.annotate_edit,
                    trash_edit: this.trash_edit,
                    hover_span: this.hover_span,
                    un_hover_span: this.un_hover_span,
                }
            }
        }
    },
    created() {
        $(window).on("resize", this.reposition_lines);

        if ($('#sandbox').length) {
            $("#sandbox").on("scroll", this.reposition_lines);
            $("#sandbox").on("resize", this.reposition_lines);
            const sandboxObserver = new ResizeObserver(entries => {
                for (const e of entries) {
                    if (e.target.id === 'sandbox') { this.reposition_lines() }
                }
            });
            sandboxObserver.observe(document.getElementById('sandbox'));
        }
    },
    // destroyed() {
    //     window.removeEventListener("resize", this.reposition_lines);
    // },
}
</script>

<template>
    <component :is="get_edits_html"></component>
</template>
