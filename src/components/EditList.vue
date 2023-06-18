<script setup>
import VRuntimeTemplate from "vue3-runtime-template";
import _ from 'lodash';
import { LeaderLine } from '../assets/js/leader-line.min.js';
import { EMPTY_ANNOTATION, EMPTY_CONNECTED_TYPES, EMPTY_CONSTITUENT_TYPES, CONFIG } from "../assets/js/constants.js";
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
        'set_lines'
    ],
    data() {
        return {
            edits_html: "",
        }
    },
    watch: {
        current_hit() {
            $(`#circle-${this.current_hit}`).addClass('circle-active');
            this.process_edits_html();
        },
        hits_data() {
            this.process_edits_html();
        },
        edits_dict() {
            this.draw_lines();
        },
    },
    methods: {
        annotate_edit(e) {
            const original_sentence = this.hits_data[this.current_hit - 1].original
            const simplified_sentence = this.hits_data[this.current_hit - 1].simplified
            const edit_dict = this.edits_dict

            const category = e.target.dataset.category
            const id = e.target.dataset.id
            const real_id = parseInt(e.target.dataset.id.split("-")[1])


            $(".child-question").hide();
            if (this.editor_open) {
                $(`.quality-selection[data-category=${category}]`).hide(400);
                this.refresh_interface_edit();
                return;
            } else {
                $(`.quality-selection`).hide(400)
                $(`.quality-selection[data-category=${category}]`).slideDown(400);
                $(e.target).addClass(`txt-${category}`)
                this.set_editor_state(!this.editor_open)
            }
            $(`.${category}[data-id=${id}]`).removeClass(`border-${category}-light`).addClass(`white border-${category} bg-${category}`)

            // Need to change the span selection format before modifying this:

            if (category == "substitution") {
                let original_spans_for_subs = edit_dict[category][real_id]["original"]
                let simplified_spans_for_subs = edit_dict[category][real_id]["simplified"]
                let new_edit_span = ""
                for (let i = 0; i < original_spans_for_subs.length; i++) {
                    if (i != 0) {
                        new_edit_span += `<span class="edit-type txt-${category} f3"> and </span>`
                    }
                    new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${category} border-${category}-all ${category}_below">
                        &nbsp${original_sentence.substring(original_spans_for_subs[i][1], original_spans_for_subs[i][2])}&nbsp</span>`
                }
                this.set_annotating_edit_span(new_edit_span, 'original')
                new_edit_span = ""
                for (let i = 0; i < simplified_spans_for_subs.length; i++) {
                    if (i != 0) {
                        new_edit_span += `<span class="edit-type txt-${category} f3"> and </span>`
                    }
                    new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${category} border-${category}-all ${category}_below">
                        &nbsp${simplified_sentence.substring(simplified_spans_for_subs[i][1], simplified_spans_for_subs[i][2])}&nbsp</span>`
                }
                this.set_annotating_edit_span(new_edit_span, 'simplified')
            } else if (category == "split") {
                let new_edit_span = ""
                let category_id_dict = edit_dict[category][real_id]
                let key = category
                let light = ""
                let first_span = 0
                for (let current_category in category_id_dict) {
                    if (current_category == "split") {
                        continue
                    }
                    for (let j in category_id_dict[current_category]) {
                        if (first_span == 0) {
                            new_edit_span += `<span class="edit-type txt-${key}${light} f3"> (</span>`;
                            first_span = 1;
                        } else {
                            new_edit_span += `<span class="edit-type txt-${key}${light} f3"> , </span>`;
                        }
                        if (current_category == "insertion") {
                            new_edit_span += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                            new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below">`;
                            new_edit_span += `&nbsp${simplified_sentence.substring(category_id_dict[current_category][j][1], category_id_dict[current_category][j][2])}&nbsp`;
                            new_edit_span += `</span>`;
                        } else if (current_category == "deletion") {
                            new_edit_span += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                            new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below">`;
                            new_edit_span += `&nbsp${original_sentence.substring(category_id_dict[current_category][j][1], category_id_dict[current_category][j][2])}&nbsp`;
                            new_edit_span += `</span>`;
                        } else if (current_category == "substitution") {
                           new_edit_span += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                            let original_spans_for_subs_under_split = category_id_dict[current_category][j]["original"]
                            let simplified_spans_for_subs_under_split = category_id_dict[current_category][j]["simplified"]
                            for (let k = 0; k < original_spans_for_subs_under_split.length; k++) {
                                if (k != 0) {
                                    new_edit_span += `<span class="edit-type txt-${key}${light} f3"> and </span>`
                                }
                                new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below">`
                                new_edit_span += `&nbsp${original_sentence.substring(original_spans_for_subs_under_split[k][1], original_spans_for_subs_under_split[k][2])}&nbsp`;
                                new_edit_span += `</span>`
                            }
                            this.annotating_edit_span_for_split += `<span class="edit-type txt-${key}${light} f3"> with </span>`;
                            for (let k = 0; k < simplified_spans_for_subs_under_split.length; k++) {
                                if (k != 0) {
                                    new_edit_span += `<span class="edit-type txt-${key}${light} f3"> and </span>`
                                }
                                new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below">`
                                new_edit_span += `&nbsp${simplified_sentence.substring(simplified_spans_for_subs_under_split[k][1], simplified_spans_for_subs_under_split[k][2])}&nbsp`;
                                new_edit_span += `</span>`
                            }
                        } else if (current_category == "reorder") {
                            new_edit_span += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                            new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${real_id}" data-category="${key}">`;
                            new_edit_span += `&nbsp${original_sentence.substring(category_id_dict[current_category][j][0][1], category_id_dict[current_category][j][0][2])}&nbsp`;
                            new_edit_span += `</span>`;
                        }
                    }
                }
                if (first_span == 1) {
                    new_edit_span += `<span class="edit-type txt-${key}${light} f3"> ) </span>`;
                }
                this.set_annotating_edit_span(new_edit_span, '', 'split')
            } else if (category == "structure") {
                let new_edit_span = ""
                let category_id_dict = edit_dict[category][real_id]
                let key = category
                let light = ""
                let first_span = 0
                for (let current_category in category_id_dict) {
                    for (let j in category_id_dict[current_category]) {
                        if (first_span == 0) {
                            new_edit_span += `<span class="edit-type txt-${key}${light} f3"> (</span>`;
                            first_span = 1;
                        } else {
                            new_edit_span += `<span class="edit-type txt-${key}${light} f3"> , </span>`;
                        }
                        if (current_category == "insertion") {
                            new_edit_span += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                            new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${real_id}" data-category="${key}">`;
                            new_edit_span += `&nbsp${simplified_sentence.substring(category_id_dict[current_category][j][1], category_id_dict[current_category][j][2])}&nbsp`;
                            new_edit_span += `</span>`;
                        } else if (current_category == "deletion") {
                            new_edit_span += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                            new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${real_id}" data-category="${key}">`;
                            new_edit_span += `&nbsp${original_sentence.substring(category_id_dict[current_category][j][1], category_id_dict[current_category][j][2])}&nbsp`;
                            new_edit_span += `</span>`;
                        } else if (current_category == "substitution") {
                            new_edit_span += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                            let original_spans_for_subs_under_split = category_id_dict[current_category][j]["original"]
                            let simplified_spans_for_subs_under_split = category_id_dict[current_category][j]["simplified"]
                            for (let k = 0; k < original_spans_for_subs_under_split.length; k++) {
                                if (k != 0) {
                                    new_edit_span += `<span class="edit-type txt-${key}${light} f3"> and </span>`
                                }
                                new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below">`
                                new_edit_span += `&nbsp${original_sentence.substring(original_spans_for_subs_under_split[k][1], original_spans_for_subs_under_split[k][2])}&nbsp`;
                                new_edit_span += `</span>`
                            }
                            new_edit_span += `<span class="edit-type txt-${key}${light} f3"> with </span>`;
                            for (let k = 0; k < simplified_spans_for_subs_under_split.length; k++) {
                                if (k != 0) {
                                    new_edit_span += `<span class="edit-type txt-${key}${light} f3"> and </span>`
                                }
                                new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below">`
                                new_edit_span += `&nbsp${simplified_sentence.substring(simplified_spans_for_subs_under_split[k][1], simplified_spans_for_subs_under_split[k][2])}&nbsp`;
                                new_edit_span += `</span>`
                            }
                        } else if (current_category == "reorder") {
                            new_edit_span += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                            new_edit_span += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${real_id}" data-category="${key}">`;
                            new_edit_span += `&nbsp${original_sentence.substring(category_id_dict[current_category][j][0][1], category_id_dict[current_category][j][0][2])}&nbsp`;
                            new_edit_span += `</span>`;
                        }
                    }
                }
                if (first_span == 1) {
                    new_edit_span += `<span class="edit-type txt-${key}${light} f3"> ) </span>`;
                }
                this.set_annotating_edit_span(new_edit_span, '', 'structure')
            } else {
                let annotating_span = edit_dict.find(function(entry) {
                    return entry['category'] === category && entry['id'] === real_id;
                });

                if (annotating_span.hasOwnProperty('input_idx')) {
                    let span_idx = annotating_span['input_idx'][0]
                    this.set_annotating_edit_span(original_sentence.substring(span_idx[0], span_idx[1]), 'original')
                } 

                if (annotating_span.hasOwnProperty('output_idx')) {
                    let span_idx = annotating_span['output_idx'][0]
                    this.set_annotating_edit_span(simplified_sentence.substring(span_idx[0], span_idx[1]), 'simplified')
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
            return edit['annotation'] != null
        },
        getEditConfig(category) {
            return CONFIG['edits'].find(function(entry) {
                return entry['name'] === category;
            });
        },
        getAnnotationHtml(ann_config, ann) {
            if (ann == null) {
                return '';
            }
            
            let ann_html = ''
            for (let edit_ann_type of ann_config) {
                let ann_type_name = edit_ann_type['name']

                if (!edit_ann_type.hasOwnProperty('options')) {
                    continue
                }

                if (edit_ann_type['options'] == 'binary') {
                    if (ann[ann_type_name] == "yes") {
                        // ann_html += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                        // ann_html += ` <span class="brown ba bw1 pa1 br-pills">Coref error</span>`;
                        ann_html += ` <span class="brown ba bw1 pa1 br-pills">${ann_type_name}</span>`;
                    }
                } else if (edit_ann_type['options'] == 'likert-3') {
                    if (ann[ann_type_name] != null) {
                        ann_html += `<span class="light-pink br-pills ba bw1 pa1">${ann_type_name}: ${ann[ann_type_name]}</span>`;
                    }
                } else {
                    // custom edit types
                    let selected = ann[ann_type_name]["val"]
                    if (selected != null && selected != "") {
                        ann_html = `<span class="light-purple ba bw1 pa1">${selected}</span>`

                        if (edit_ann_type.hasOwnProperty('options')) {
                            ann_html += this.getAnnotationHtml(edit_ann_type['options'], ann[ann_type_name])
                        }
                    }                            
                } 
            }
            return ann_html
        },
        process_edits_html() {
            let new_html = ''

            let hit_edits = _.cloneDeep(this.hits_data[this.current_hit - 1].edits)

            // TODO: Sort edits

            for (let edit of hit_edits) {
                let i = edit['id']
                let key = edit['category'];
                let light = !this.hasAnnotation(edit) ? "-light" : ""
                new_html += `
                    <div class='cf'>
                        <div class="fl w-80 mb4 edit">
                            <span data-id="${key}-${i}" data-category="${key}" class="default_cursor" @mouseover="hover_span" @mouseout="un_hover_span">
                                <span class="edit-type txt-${key}${light} f3">${key} </span>
                                <span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;

                // Render edit
                if (edit.hasOwnProperty('input_idx')) {
                    let in_span = edit['input_idx'][0]
                    new_html += `
                        &nbsp${this.hits_data[this.current_hit - 1].original.substring(in_span[0], in_span[1])}&nbsp</span>`;
                } else if (edit.hasOwnProperty('output_idx')) {
                    let out_span = edit['output_idx'][0]
                    new_html += `
                        &nbsp${this.hits_data[this.current_hit - 1].simplified.substring(out_span[0], out_span[1])}&nbsp</span>`;
                }
                
                if (this.getEditConfig(key)['multi_span']) {
                    if (edit.hasOwnProperty('input_idx')) {
                        let original_spans_for_subs = edit['input_idx'].slice(1)
                        for (let original_span of original_spans_for_subs) {
                            if (original_span[0] != in_span[0] || original_span[1] != in_span[1]) {
                                new_html += `
                                    <span class="edit-type txt-${key}${light} f3"> and </span>
                                        <span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">
                                            &nbsp${this.hits_data[this.current_hit - 1].original.substring(original_span[0], original_span[1])}&nbsp
                                        </span>`;
                            }
                        }
                    }
                    new_html += `<span class="edit-type txt-${key}${light} f3"> with </span>`;
                    if (edit.hasOwnProperty('output_idx')) {
                        let simplified_spans_for_subs = edit['output_idx'] // .slice(1)
                        for (let j = 0; j < simplified_spans_for_subs.length; j++) {
                            let simplified_span = simplified_spans_for_subs[j];
                            if (j != 0) {
                                new_html += `<span class="edit-type txt-${key}${light} f3"> and </span>`;
                            }
                            new_html += `
                                <span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">
                                    &nbsp${this.hits_data[this.current_hit - 1].simplified.substring(simplified_span[0], simplified_span[1])}&nbsp</span>`;
                        }
                    }
                } 
                // else if (key == "split") {
                //     new_html += `
                //         &nbsp${this.hits_data[this.current_hit - 1].simplified.substring(span[1], span[2])}&nbsp</span>`;
                //     let first_span = 0
                //     for (let current_category in new_edits_dict[key][i]) {
                //         if (current_category == "split") {
                //             continue;
                //         }
                //         for (let j in new_edits_dict[key][i][current_category]) {
                //             if (first_span == 0) {
                //                 new_html += `<span class="edit-type txt-${key}${light} f3"> (</span>`;
                //                 first_span = 1;
                //             } else {
                //                 new_html += `<span class="edit-type txt-${key}${light} f3"> , </span>`;
                //             }
                //             if (current_category == "insertion") {
                //                 new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                //                 new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                //                 new_html += `&nbsp${this.hits_data[this.current_hit - 1].simplified.substring(new_edits_dict[key][i][current_category][j][1], new_edits_dict[key][i][current_category][j][2])}&nbsp`;
                //                 new_html += `</span>`;
                //             } else if (current_category == "deletion") {
                //                 new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                //                 new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                //                 new_html += `&nbsp${this.hits_data[this.current_hit - 1].original.substring(new_edits_dict[key][i][current_category][j][1], new_edits_dict[key][i][current_category][j][2])}&nbsp`;
                //                 new_html += `</span>`;
                //             } else if (current_category == "substitution") {
                //                 new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                //                 let original_spans_for_subs_under_split = new_edits_dict[key][i][current_category][j]["original"];
                //                 for (let k = 0; k < original_spans_for_subs_under_split.length; k++) {
                //                     if (k != 0) {
                //                         new_html += `<span class="edit-type txt-${key}${light} f3"> and </span>`;
                //                     }
                //                     new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                //                     new_html += `&nbsp${this.hits_data[this.current_hit - 1].original.substring(original_spans_for_subs_under_split[k][1], original_spans_for_subs_under_split[k][2])}&nbsp`;
                //                     new_html += `</span>`;
                //                 }
                //                 new_html += `<span class="edit-type txt-${key}${light} f3"> with </span>`;
                //                 let simplified_spans_for_subs_under_split = new_edits_dict[key][i][current_category][j]["simplified"];
                //                 for (let k = 0; k < simplified_spans_for_subs_under_split.length; k++) {
                //                     if (k != 0) {
                //                         new_html += `<span class="edit-type txt-${key}${light} f3"> and </span>`;
                //                     }
                //                     new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                //                     new_html += `&nbsp${this.hits_data[this.current_hit - 1].simplified.substring(simplified_spans_for_subs_under_split[k][1], simplified_spans_for_subs_under_split[k][2])}&nbsp`;
                //                     new_html += `</span>`;
                //                 }
                //             } else if (current_category == "reorder") {
                //                 new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                //                 new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                //                 new_html += `&nbsp${this.hits_data[this.current_hit - 1].original.substring(new_edits_dict[key][i][current_category][j][0][1], new_edits_dict[key][i][current_category][j][0][2])}&nbsp`;
                //                 new_html += `</span>`;
                //             }
                //         }
                //     }
                //     if (first_span == 1) {
                //         new_html += `<span class="edit-type txt-${key}${light} f3"> )</span>`;
                //     }
                // } else if (key == "structure") {
                //     new_html += `&nbsp<i class="fa-solid fa-tree"></i>&nbsp</span>`;
                //     let first_span = 0
                //     for (let current_category in new_edits_dict[key][i]) {
                //         for (let j in new_edits_dict[key][i][current_category]) {
                //             if (first_span == 0) {
                //                 new_html += `<span class="edit-type txt-${key}${light} f3"> (</span>`;
                //                 first_span = 1;
                //             } else {
                //                 new_html += `<span class="edit-type txt-${key}${light} f3"> , </span>`;
                //             }
                //             if (current_category == "insertion") {
                //                 new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                //                 new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                //                 new_html += `&nbsp${this.hits_data[this.current_hit - 1].simplified.substring(new_edits_dict[key][i][current_category][j][1], new_edits_dict[key][i][current_category][j][2])}&nbsp`;
                //                 new_html += `</span>`;
                //             } else if (current_category == "deletion") {
                //                 new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                //                 new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                //                 new_html += `&nbsp${this.hits_data[this.current_hit - 1].original.substring(new_edits_dict[key][i][current_category][j][1], new_edits_dict[key][i][current_category][j][2])}&nbsp`;
                //                 new_html += `</span>`;
                //             } else if (current_category == "substitution") {
                //                 new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                //                 let original_spans_for_subs_under_split = new_edits_dict[key][i][current_category][j]["original"];
                //                 for (let k = 0; k < original_spans_for_subs_under_split.length; k++) {
                //                     if (k != 0) {
                //                         new_html += `<span class="edit-type txt-${key}${light} f3"> and </span>`;
                //                     }
                //                     new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                //                     new_html += `&nbsp${this.hits_data[this.current_hit - 1].original.substring(original_spans_for_subs_under_split[k][1], original_spans_for_subs_under_split[k][2])}&nbsp`;
                //                     new_html += `</span>`;
                //                 }
                //                 new_html += `<span class="edit-type txt-${key}${light} f3"> with </span>`;
                //                 let simplified_spans_for_subs_under_split = new_edits_dict[key][i][current_category][j]["simplified"];
                //                 for (let k = 0; k < simplified_spans_for_subs_under_split.length; k++) {
                //                     if (k != 0) {
                //                         new_html += `<span class="edit-type txt-${key}${light} f3"> and </span>`;
                //                     }
                //                     new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                //                     new_html += `&nbsp${this.hits_data[this.current_hit - 1].simplified.substring(simplified_spans_for_subs_under_split[k][1], simplified_spans_for_subs_under_split[k][2])}&nbsp`;
                //                     new_html += `</span>`;
                //                 }
                //             } else if (current_category == "reorder") {
                //                 new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category} </span>`;
                //                 new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                //                 new_html += `&nbsp${this.hits_data[this.current_hit - 1].original.substring(new_edits_dict[key][i][current_category][j][0][1], new_edits_dict[key][i][current_category][j][0][2])}&nbsp`;
                //                 new_html += `</span>`;
                //             }
                //         }
                //     }
                //     if (first_span == 1) {
                //         new_html += `<span class="edit-type txt-${key}${light} f3"> )</span>`;
                //     }
                // } 
                
                new_html += ` : `;

                // Render annotation
                if (!this.hasAnnotation(edit)) {
                    new_html += `
                        <span class="f4 i black-60">this edit is not annotated yet, click <i class="fa-solid fa-pencil"></i> to start!</span>
                    `;
                } else {
                    const EDIT_CONFIG = this.getEditConfig(key)
                    let ann_html = this.getAnnotationHtml(EDIT_CONFIG['annotation'], edit['annotation'])
                    new_html += `<span class="f4 i">${ann_html}</span>`;
                }

                new_html += `
                        </span>
                    </div>
                    <div class="fl w-20 mb4 operation tc">
                        <i @click="annotate_edit" class="annotation-icon fa-solid fa-pencil mr3 pointer dim" data-id="${key}-${i}" data-category="${key}"></i>
                        <i @click="trash_edit" class="fa-solid fa-trash-can ml4 pointer dim" data-id="${key}-${i}" data-category="${key}"></i>
                    </div>
                </div>`;
            }
            
            this.set_edits_dict(hit_edits);
            this.edits_html = new_html;
        },
        draw_lines: function() {
            let new_lines = _.cloneDeep(this.lines);
            for (let category in new_lines) {
                for (let i in new_lines[category]) {
                    if (category == "substitution" || category == "reorder") {
                        new_lines[category][i].remove()
                    } else {
                        for (let j in new_lines[category][i]) {
                            new_lines[category][i][j].remove()
                        }
                    }
                }
            }
            new_lines = EMPTY_CONNECTED_TYPES

            let substitution_edits_dict = this.edits_dict["substitution"]
            if ($('.substitution.original_span')[0] != null) {
                for (let id in substitution_edits_dict) {
                    let color = "rgba(173, 197, 250, 0.4)"
                    if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (id in this.hits_data[[this.current_hit - 1]].annotations["substitution"])) {
                        color = "rgba(33, 134, 235, 0.46)"
                    }
                    new_lines["substitution"][id] = new LeaderLine(
                        $(`.substitution.original_span[data-id='substitution-${id}']`)[0],
                        $(`.substitution.simplified_span[data-id='substitution-${id}']`)[0],
                        {endPlug: "behind",
                        size: 3,
                        path: "straight",
                        color: color,}
                    )
                }
            }
            
            let reorder_edits_dict = this.edits_dict["reorder"]
            if ($('.reorder.original_span')[0] != null) {
                for (let id in reorder_edits_dict) {
                    let color = "rgba(182, 227, 229, 0.4)"
                    if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (id in this.hits_data[[this.current_hit - 1]].annotations["reorder"])) {
                        color = "rgba(60, 163, 167, 0.46)"
                    }
                    new_lines["reorder"][id] = new LeaderLine(
                        $(`.reorder.original_span[data-id='reorder-${id}']`)[0],
                        $(`.reorder.simplified_span[data-id='reorder-${id}']`)[0],
                        {endPlug: "behind",
                        size: 3,
                        path: "straight",
                        color: color,}
                    )
                }
            }


            let split_edits_dict = this.edits_dict["split"]
            if (split_edits_dict != {}) {
                for (let id in split_edits_dict) {
                    let color = "rgba(250, 229, 175, 0.4)"
                    if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (id in this.hits_data[[this.current_hit - 1]].annotations["split"])) {
                        color = "rgba(247, 206, 70, 0.46)"
                    }
                    new_lines["split"][id] = []
                    for (let span_category in split_edits_dict[id]) {
                        for (let span_id in split_edits_dict[id][span_category]) {
                            let span = split_edits_dict[id][span_category][span_id]
                            if (span_category == "deletion") {
                                new_lines["split"][id].push(
                                    new LeaderLine(
                                    $(`.split.original_span[data-id='split-${id}'][data-childcategory=${span_category}][data-childid=${span_id}]`)[0],
                                    $(`.split.split-sign[data-id='split-${id}']`)[0],
                                    {endPlug: "arrow3",
                                    size: 3,
                                    path: "straight",
                                    color: color,})
                                )
                            } else if (span_category =="insertion") {
                                new_lines["split"][id].push(
                                    new LeaderLine(
                                    $(`.split.simplified_span[data-id='split-${id}'][data-childcategory=${span_category}][data-childid=${span_id}]`)[0],
                                    $(`.split.split-sign[data-id='split-${id}']`)[0],
                                    {endPlug: "arrow3",
                                    size: 3,
                                    path: "arc",
                                    color: color,})
                                )
                            } else if (span_category == "substitution" || span_category == "reorder") {
                                new_lines["split"][id].push(
                                    new LeaderLine(
                                    $(`.split.original_span[data-id='split-${id}'][data-childcategory=${span_category}][data-childid=${span_id}]`)[0],
                                    $(`.split.simplified_span[data-id='split-${id}'][data-childcategory=${span_category}][data-childid=${span_id}]`)[0],
                                    {endPlug: "behind",
                                    size: 3,
                                    path: "straight",
                                    color: color,})
                                )

                                new_lines["split"][id].push(
                                    new LeaderLine(
                                    $(`.split.simplified_span[data-id='split-${id}'][data-childcategory=${span_category}][data-childid=${span_id}]`)[0],
                                    $(`.split.split-sign[data-id='split-${id}']`)[0],
                                    {endPlug: "arrow3",
                                    size: 3,
                                    path: "arc",
                                    color: color,})
                                )
                            }
                        }
                    }
                }
            }

            let structure_edits_dict = this.edits_dict["structure"]
            if (structure_edits_dict != {}) {
                for (let id in structure_edits_dict) {
                    let color = "rgba(242, 189, 161, 0.4)"
                    if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (id in this.hits_data[[this.current_hit - 1]].annotations["structure"])) {
                        color = "rgba(230, 124, 67, 0.46)"
                    }
                    new_lines["structure"][id] = []
                    for (let span_category in structure_edits_dict[id]) {
                        for (let span_id in structure_edits_dict[id][span_category]) {
                            let span = structure_edits_dict[id][span_category][span_id]
                            if (span_category == "substitution" || span_category == "reorder") {
                                new_lines["structure"][id].push(
                                    new LeaderLine(
                                    $(`.structure.original_span[data-id='structure-${id}'][data-childcategory=${span_category}][data-childid=${span_id}]`)[0],
                                    $(`.structure.simplified_span[data-id='structure-${id}'][data-childcategory=${span_category}][data-childid=${span_id}]`)[0],
                                    {endPlug: "behind",
                                    size: 3,
                                    path: "straight",
                                    color: color,})
                                )
                            }
                        }
                    }
                }
            }

            this.set_lines(new_lines)
        }
    },
    computed: {
        get_edits_html() {
            return {
                template: `<div id="edits_html" class="f4 lh-paras">${this.edits_html}</div>`,
                methods: {
                    annotate_edit: this.annotate_edit,
                    trash_edit: this.trash_edit,
                }
            }
        }
        // Unused methods
        // hover_span: this.hover_span,
        // un_hover_span: this.un_hover_span,
    }
}
</script>

<template>
    <component :is="get_edits_html"></component> 
</template>