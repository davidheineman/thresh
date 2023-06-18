<script setup>
  import SelectedSpan from "./SelectedSpan.vue";
  import CompiledSpan from "./CompiledSpan.vue";
  import Question from "./Question.vue";
  import _ from 'lodash';
  import { CONFIG, EMPTY_CONSTITUENT_TYPES } from "../assets/js/constants.js";
</script>

<script>
export default {
    props: [
        'edits_dict',
        'hits_data',
        'current_hit',
        'selected_edits_html',
        'selected_edits',
        'selected_split',
        'selected_split_id',
        'selected_span_in_original',
        'selected_span_in_simplified',
        'selected_span_in_original_indexs',
        'selected_span_in_simplified_indexs',
        'set_span_text',
        'set_span_indices',
        'set_hits_data',
        'refresh_interface_edit',
        'editor_open',
        'set_editor_state',
        'annotating_edit_span_category_id',
        'set_annotating_edit_span_category_id',
        'annotating_edit_span',
        'set_annotating_edit_span'
    ],
    data() {
        let edit_state = this.initalize_edit_state()

        return {
            edit_state: edit_state,
        }
    },
    methods: {
        initalize_edit_state() {
            function parse_options(edit_config) {
                if (typeof edit_config !== "object") { return null }
                let edit_options = {}
                for (const option_idx in edit_config) {
                    edit_options['val'] = null
                    edit_options[edit_config[option_idx].name] = parse_options(edit_config[option_idx].options)
                } 
                return edit_options
            }
            let edit_state = {}
            for (const edit_idx in CONFIG.edits) {
                let edit_type = CONFIG.edits[edit_idx]
                edit_state[edit_type.name] = parse_options(edit_type.annotation)
            }
            return edit_state
        },
        set_edit_state(edit_state) {
            console.log(edit_state)
            this.edit_state = edit_state
        },
        cancel_click() {
            $(".icon-default").removeClass("open")
            this.refresh_edit();
            // this.process_original_html();
            this.original_html = this.original_html + "1"
            this.original_html = this.original_html.slice(0, -1);

            // this.process_simplified_html();
            this.simplified_html = this.simplified_html + "1"
            this.simplified_html = this.simplified_html.slice(0, -1);

            // this.process_edits_html();
            this.edits_html = this.edits_html + "1"
            this.edits_html = this.edits_html.slice(0, -1);
        },
        save_click() {
            let new_hits_data = _.cloneDeep(this.hits_data);

            $(".icon-default").removeClass("open")
            this.set_editor_state(!this.editor_open)
            
            let selected_category = $("input[name=edit_cotegory]:checked").val();
            const edits_data = new_hits_data[this.current_hit - 1].edits

            // Get highest key
            let max_key = 0;
            for (const edit of edits_data) {
                console.log(edit)
                if (edit['category'] == selected_category && parseInt(edit['id']) > max_key) {
                    max_key = parseInt(edit['id']);
                }
            }

            const config_category = CONFIG.edits.find((edit) => edit.name === selected_category)

            let new_span = {
                'category': selected_category,
                'id': max_key + 1,
                'annotation': null
            }

            if (config_category['type'] == 'primitive') {
                if (config_category['enable_input']) {
                    new_span['input_idx'] = [this.selected_span_in_original_indexs]
                }
                if (config_category['enable_output']) {
                    new_span['output_idx'] = [this.selected_span_in_simplified_indexs]
                }
            }

            if (config_category['type'] == 'composite') {
                // TODO: Fix this implementation

                let selected_edits_key_map = EMPTY_CONSTITUENT_TYPES

                for (let temp_category in this.selected_edits) {
                    let j = 1;
                    for (let temp_id in this.selected_edits[temp_category]) {
                        selected_edits_key_map[temp_category][temp_id] = j;
                        j++;
                    }
                }

                let newspans = []
                for (let i = 0; i < original_spans.length; i++) {
                    let span = original_spans[i]
                    let span_category = this.id_to_category[span[0]]
                    let span_id = span[3]
                    if ((span_category in this.selected_edits) && (span[3] in this.selected_edits[span_category])) {
                        span.push(span[0])
                        span.push(selected_edits_key_map[span_category][span[3]])
                        span[0] = this.category_to_id[selected_category]
                        if (selected_category == "split") {
                            span[3] = this.selected_split_id
                        } else if (selected_category == "structure") {
                            span[3] = max_key + 1
                        }

                        if (span_id in this.hits_data[this.current_hit - 1]["annotations"][span_category]) {
                            let new_hits_data = _.cloneDeep(this.hits_data);
                            delete new_hits_data[this.current_hit - 1]["annotations"][span_category][span_id]
                            this.set_hits_data(new_hits_data)
                        }
                    }
                    newspans.push(span)
                }
            }

            new_hits_data[this.current_hit - 1].edits.push(new_span)
            
            this.set_hits_data(new_hits_data)
            this.refresh_edit();
        },
        save_annotation_click(category, e) {
            let edit_id = this.annotating_edit_span_category_id
            
            let new_hits_data = _.cloneDeep(this.hits_data);
            let new_annotation = _.cloneDeep(this.edit_state[category])

            let annotating_span = new_hits_data[this.current_hit - 1]['edits'].find(function(entry) {
                return entry['category'] === category && entry['id'] === edit_id;
            });

            annotating_span.annotation = new_annotation

            this.set_hits_data(new_hits_data)
            this.refresh_edit();
        },
        refresh_edit() {
            this.set_editor_state(false);
            this.refresh_interface_edit()

            $("input[name=edit_cotegory]").prop("checked", false);
            $(".checkbox-tools").prop("checked", false);
            $(".checkbox-tools-yes-no").prop("checked", false);
            $(".annotation-icon").removeClass('txt-substitution txt-insertion txt-deletion txt-split');
            $('.quality-selection').hide(400);
            $(".span-selection-div").hide(400);

            $(".child-question").hide();

            this.edit_state = this.initalize_edit_state()
        },
        show_span_selection(e) {
            $(`.span-selection-div`).hide(400);
            $(`.span-selection-div[data-category=${e.target.value}]`).slideDown(400);
            this.selected_add_edit_category_temp = e.target.value;

            // This is where edit-specific logic is implemented

            // if (e.target.value == 'deletion') {
            //     this.enable_select_original_sentence = true;
            //     this.enable_select_simplified_sentence = false;
            //     this.enable_multi_select_original_sentence = false;
            //     this.enable_multi_select_simplified_sentence = false;
            // }  else if (e.target.value == 'substitution' || e.target.value == 'reorder') {
            //     this.enable_select_original_sentence = true;
            //     this.enable_select_simplified_sentence = true;
            //     if (e.target.value == 'substitution') {
            //         this.enable_multi_select_original_sentence = true;
            //         this.enable_multi_select_simplified_sentence = true;
            //     } else {
            //         this.enable_multi_select_original_sentence = false;
            //         this.enable_multi_select_simplified_sentence = false;
            //     }
            // } else if (e.target.value == 'split' || e.target.value == 'structure') {
            //     this.enable_select_original_sentence = false;
            //     this.enable_select_simplified_sentence = false;
            //     this.enable_multi_select_original_sentence = false;
            //     this.enable_multi_select_simplified_sentence = false;
            // } else {
            //     this.enable_select_simplified_sentence = true;
            //     this.enable_select_original_sentence = false;
            //     this.enable_multi_select_original_sentence = false;
            //     this.enable_multi_select_simplified_sentence = false;
            // }

            this.set_span_text("", "original");
            this.set_span_text("", "simplified");
            this.set_span_indices("", "original");
            this.set_span_indices("", "simplified");
        },
    }
}
</script>

<template>
    <div class="quality-selection-divs">
        <div class="quality-selection w-100" id="add_an_edit">
            <p class="f3 courier ttu mv1">Adding an Edit <i class="fa-solid fa-plus"></i></p>
            <div id="dropdown-button-container">
                <div class="over-hide z-bigger mt2">
                    <div class="row">
                        <p class="mb2 b tracked-light"><i>Select the Edit Category.</i>
                        </p>
                        <div class="tc mb3">
                            <div v-for="item in CONFIG.edits" :key="item.id" class="w-15 mr2 dib">
                                <input @click="show_span_selection" class="checkbox-tools-edit-category checkbox-tools" type="radio" name="edit_cotegory"
                                    :id="`edit_cotegory-${item.name}`" :value="item.name">
                                <label :class="`txt-${item.name}`" :for="`edit_cotegory-${item.name}`">
                                    <i :class="`fa-solid ${item.icon} fa-1-5x mb1`"></i>
                                    {{ item.label }}
                                </label>
                            </div>
                        </div>

                        <div v-for="item in CONFIG.edits" :key="item.id" class="span-selection-div" :data-category="item.name">
                            <div v-if="item.enable_input">
                                <p class="mt0 mb2 b tracked-light">Select the text span from the <i>{{ CONFIG.input_label }}</i>.</p>
                                <p class="tracked-light">Selected span: <span :class="`bg-${item.name}-light`">{{selected_span_in_original}}</span></p>
                            </div>
                            <div v-if="item.enable_output">
                                <div class="span-selection-div" :data-category="item.name">
                                    <p class="mt0 mb2 b tracked-light">Select the text span from the <i>{{ CONFIG.output_label }}</i>.</p>
                                    <p class="tracked-light">Selected span: <span :class="`bg-${item.name}-light`">{{selected_span_in_simplified}}</span></p>
                                </div>
                            </div>
                            <div v-if="item.type == 'composite'">
                                <div class="span-selection-div" data-category="item.name">
                                    <!-- <p class="mt0 mb2 b tracked-light">Click a split sign <i class="fa-solid fa-grip-lines-vertical fa-lg txt-split"></i> : <span class="txt-split">{{selected_split}}</span></p> -->
                                    <p class="mt0 mb2 b tracked-light">Click the edits that associated with this {{ item.name }} change edit.</p>
                                    <p class="tracked-light lh-paras-2">Selected edits: <span v-html="selected_edits_html"></span></p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="buttons tc mt2">
                    <button @click="cancel_click" class="cancel-button b quality_button bw0 ba mr2 br-pill-ns grow" type="button">Cancel <i class="fa-solid fa-close"></i></button>
                    <!-- :class="{'o-40': add_validated_edit, 'grow': !add_validated_edit}" :disabled="add_validated_edit" -->
                    <button @click="save_click" class="confirm-button b quality_button bw0 ba ml2 br-pill-ns" type="button">Save <i class="fa-solid fa-check"></i></button>
                </div>
            </div>
        </div>

        <div v-for="item in CONFIG.edits" :key="item.id">
            <div class="quality-selection w-100" :id="`${item.name}_edit_annotation`" :data-category="item.name">
                <p class="f3 courier ttu mv1">Annotating an Edit <i class="fa-solid fa-pencil"></i></p>
                <div class="f4 mt0 mb2 tc">
                    <span :class="`edit-type txt-${item.name} f3`">{{ item.label }}:  </span>
                    
                    <!-- Flesh out this section, it's not the same as the original -->
                    <span v-if="item.enable_input" :class="`pa1 edit-text br-pill-ns border-${item.name}-all ${item.name}_below txt-${item.name}`">&nbsp;{{annotating_edit_span.original}}&nbsp;</span>
                    <span v-if="item.enable_output" :class="`pa1 edit-text br-pill-ns border-${item.name}-all ${item.name}_below txt-${item.name}`">&nbsp;{{annotating_edit_span.simplified}}&nbsp;</span>
                </div>

                <div id="dropdown-button-container">
                    <div class="single_part over-hide z-bigger mt3">
                        <div class="row">
                            <div v-for="question in item.annotation" :key="question.id">
                                <Question :edit_state="this.edit_state" :question_state="this.edit_state[item.name][question.name]" :question="question" :edit_type="item" :set_edit_state="set_edit_state"
                                    :parent_show_next_question="null" isRoot=true />
                            </div>
                        </div>
                    </div>
                    <div class="buttons tc">
                        <button @click="cancel_click" class="cancel-button b quality_button bw0 ba mr2 br-pill-ns grow" type="button">Cancel <i class="fa-solid fa-close"></i></button>
                        <!-- :class="{'o-40': save_validated_deletion, 'grow': !save_validated_deletion}" :disabled="save_validated_deletion" -->
                        <button @click="save_annotation_click(item.name, $e)" class="confirm-button b quality_button bw0 ba ml2 br-pill-ns">Save <i class="fa-solid fa-check"></i></button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
