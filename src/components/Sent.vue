<script setup>
    import _ from 'lodash';
    import OriginalSent from "./OriginalSent.vue";
    import SimplifiedSent from "./SimplifiedSent.vue";
</script>

<script>
export default {
    data() {
        return {

        }
    },
    props: [
        'hits_data',
        'current_hit',
        'edits_dict',
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

        'sent_type',

        'selected_span_in_original',
        'selected_span_in_original_indexs',
        'selected_span_in_original_category',
        'selected_span_in_simplified',
        'selected_span_in_simplified_indexs',
        'selected_span_in_simplified_category',
    ],
    methods: {
        process_edit_list(edits, sent_type) {
            edits = edits.map(edit => {
                let flattened_edits = []
                if (edit.hasOwnProperty('constituent_edits')) {
                    for (const const_edit of edit['constituent_edits']) {
                        if (const_edit.hasOwnProperty(sent_type)) {
                            for (const in_idx of const_edit[sent_type]) {
                                flattened_edits.push({
                                    [sent_type]: in_idx,
                                    'category': edit['category'],
                                    'child_category': const_edit['category'],
                                    'id': edit['id'],
                                    'child_id': const_edit['id'],
                                    'annotation': edit['annotation']
                                })
                            }
                        }
                    }
                }
                if (edit.hasOwnProperty(sent_type)) {
                    for (const in_idx of edit[sent_type]) {
                        flattened_edits.push({
                            [sent_type]: in_idx,
                            'category': edit['category'],
                            'id': edit['id'],
                            'annotation': edit['annotation']
                        })
                    }
                }
                return flattened_edits
            })
            edits = [].concat(...edits); // flatten list
            edits.sort(function(a, b) {
                return a[sent_type][0] - b[sent_type][0] || a[sent_type][1] - b[sent_type][1];
            });
            return edits
        },
        hasAnnotations(edit) {
            return ("annotation" in edit) && edit["annotation"] != null && edit["annotation"] != ""
        },
        is_selected(edit, sent_type, selected_category) {
            let whether_is_selected
            const selected_idx = this.get_selected_index(sent_type)
            if (this.multi_select_enabled(sent_type)) {
                whether_is_selected = selected_idx.some(span => next_edit[sent_type][0] == span[0] && next_edit[sent_type][1] == span[1] && next_edit['category'] == selected_category);
                // for (let j = 0; j < selected_idx.length; j++) {
                //     if (edit[sent_type][0] == selected_idx[j][0] && edit[sent_type][1] == selected_idx[j][1] && edit['category'] == selected_category) {
                //         whether_is_selected = true
                //         break
                //     }
                // }
            } else {
                whether_is_selected = edit[sent_type][0] == selected_idx[0] && edit[sent_type][1] == selected_idx[1] && edit['category'] == selected_category
            }
            return whether_is_selected
        },
        get_selected_index(sent_type) {
            if (sent_type == 'input_idx') {
                return _.cloneDeep(this.selected_span_in_original_indexs)
            }
            if (sent_type == 'output_idx') {
                return _.cloneDeep(this.selected_span_in_simplified_indexs)
            }
            return undefined
        },
        multi_select_enabled(sent_type) {
            if (sent_type == 'input_idx') {
                return this.enable_multi_select_original_sentence
            }
            if (sent_type == 'output_idx') {
                return this.enable_multi_select_simplified_sentence
            }
            return undefined
        },
        render_sentence(sent, sent_type, span_class, selected_category) {
            let prev_idx = 0
            let sentence_html = ''

            let hit_edits = _.cloneDeep(this.hits_data[this.current_hit - 1].edits)

            // Add selected edits
            const includes_selection = selected_category != null
            if (includes_selection) {
                const selected_idx = this.get_selected_index(sent_type)
                if (this.multi_select_enabled(sent_type) && Array.isArray(selected_idx[0])) {
                    for (let i = 0; i < selected_idx.length; i++) {
                        hit_edits.push({
                            "category": selected_category, 
                            [sent_type]: [selected_idx[i]],
                        })
                    }
                } else {
                    hit_edits.push({
                        "category": selected_category, 
                        [sent_type]: [selected_idx]
                    })
                }
            }
            
            const edits = this.process_edit_list(hit_edits, sent_type)

            for (let i = 0; i < edits.length; i++) {
                let edit = edits[i]
                let next_edit = edits[i + 1]

                sentence_html += sent.substring(prev_idx, edit[sent_type][0]);
                
                let light = !this.hasAnnotations(edit) ? "-light" : "";
                let outside = i < edits.length - 1 && next_edit[sent_type][0] <= edit[sent_type][1] ? "outside" : ""
                let composite_info = edit.hasOwnProperty('child_category') ? `data-childcategory=${edit['child_category']} data-childid=${edit['child_id']}` : ""

                if (includes_selection && this.is_selected(edit, sent_type, selected_category)) {
                    sentence_html += `
                        <span @mouseover.stop @mouseout.stop class="bg-${edit['category']}-light span ${outside}">`;
                } else {
                    sentence_html += `
                        <span @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${edit['category']} border-${edit['category']}${light} pointer span ${span_class} ${outside}" data-category="${edit['category']}" data-id="${edit['category']}-${edit['id']}" ${composite_info}>`;
                }

                let start_i = i
                let whether_more_overlap = false
                while (i < edits.length - 1 && next_edit[sent_type][0] <= edits[start_i][sent_type][1]) {
                    if (i == start_i) {
                        sentence_html += sent.substring(edit[sent_type][0], next_edit[sent_type][0]);
                    } else {
                        let j = i
                        if (whether_more_overlap) {
                            j -= 1
                        }
                        sentence_html += sent.substring(edits[j][sent_type][1], next_edit[sent_type][0]);
                    }
                    whether_more_overlap = false             
                    
                    let outside = i < edits.length - 2 && edits[i + 2][sent_type][0] <= next_edit[sent_type][1] ? "middleside" : ""
                    
                    let light = !this.hasAnnotations(edit) ? "-light" : "";
                    // TODO: Add case for all split chars, in all three contexts
                    // This looks like the only difference, there's an edge case for the || chars
                    // if (category == "split" && (simplified_sentence.substring(simplified_spans[i][1], simplified_spans[i][2]) =="||")) {
                    //     sentence_html += `<span @mousedown.stop @mouseup.stop  @click="click_span"  @mouseover="hover_span" @mouseout="un_hover_span" class="${category} pointer span simplified_span txt-split${light} split-sign ${outside}" data-category="${category}" data-id="${category}-` + simplified_spans[i][3] + `">`;
                    // }
                    let composite_info = edit.hasOwnProperty('child_category') ? `data-childcategory=${edit['child_category']} data-childid=${edit['child_id']}` : "" 

                    if (includes_selection && this.is_selected(edit, sent_type, selected_category)) {
                        sentence_html += `
                            <span @mouseover.stop @mouseout.stop class="bg-${edit['category']}-light span ${outside}">`;
                    } else {
                        sentence_html += `
                            <span @mouseover.stop @mouseout.stop @click.stop @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${next_edit['category']} border-${next_edit['category']}${light} pointer span ${span_class} ${outside}" data-category="${next_edit['category']}" data-id="${next_edit['category']}-${next_edit['id']}" ${composite_info}>`;
                    }

                    i++;
                    edit = edits[i]
                    next_edit = edits[i + 1]

                    if (i < edits.length - 1 && next_edit[sent_type][0] <= edit[sent_type][1]) {
                        whether_more_overlap = true
                        let next_next_edit = edits[i + 1]
                        sentence_html += sent.substring(edit[sent_type][0], next_next_edit[sent_type][0]);  

                        let light = !this.hasAnnotations(next_next_edit) ? "-light" : "";
                        composite_info = next_next_edit.hasOwnProperty('child_category') ? `data-childcategory=${next_next_edit['child_category']} data-childid=${next_next_edit['child_id']}` : ""
                        
                        if (includes_selection && this.is_selected(edit, sent_type, selected_category)) {
                            sentence_html += `
                                <span @mouseover.stop @mouseout.stop class="bg-${next_category}-light span">`;
                        } else {
                            sentence_html += `
                                <span @mouseover.stop @mouseout.stop @click.stop @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${next_next_edit['category']} border-${next_next_edit['category']}${light} pointer span ${span_class}" data-category="${next_next_edit['category']}" data-id="${next_next_edit['category']}-${next_next_edit['id']}" ${composite_info}>`;
                        }

                        sentence_html += `
                                ${sent.substring(next_next_edit[sent_type][0], next_next_edit[sent_type][1])}</span>
                            ${sent.substring(next_next_edit[sent_type][1], edit[sent_type][1])}</span>`;

                        i++;
                        edit = edits[i]
                        next_edit = edits[i + 1]

                    } else {
                        next_edit = edits[i + 1]
                        sentence_html += `
                            ${sent.substring(next_edit[sent_type][0], next_edit[sent_type][1])}</span>`;
                    }
                }

                if (start_i != i) {
                    let final_idx = i
                    if (start_i != i && whether_more_overlap) {
                        final_idx -= 1                        
                    }
                    sentence_html += `
                        ${sent.substring(edits[final_idx][sent_type][1], edits[start_i][sent_type][1])}</span>`;
                    prev_idx = edits[start_i][sent_type][1];
                } else {
                    sentence_html += `
                        ${sent.substring(edits[start_i][sent_type][0], edits[start_i][sent_type][1])}</span>`;
                    prev_idx = edits[start_i][sent_type][1];
                }
            }

            sentence_html += sent.substring(prev_idx);
            return sentence_html;
        },
    },
}
</script>

<template>
    <div>
        <template v-if="sent_type === 'original'">
            <OriginalSent sent_type="original" v-bind="$props" :remove_selected="remove_selected" :process_edit_list="process_edit_list" :hasAnnotations="hasAnnotations" :is_selected="is_selected" :get_selected_index="get_selected_index" :multi_select_enabled="multi_select_enabled" :render_sentence="render_sentence" />
        </template>
        <template v-else-if="sent_type === 'simplified'">
            <SimplifiedSent sent_type="simplified" v-bind="$props" :remove_selected="remove_selected" :process_edit_list="process_edit_list" :hasAnnotations="hasAnnotations" :is_selected="is_selected" :get_selected_index="get_selected_index" :multi_select_enabled="multi_select_enabled" :render_sentence="render_sentence" />
        </template>
    </div>
</template>
