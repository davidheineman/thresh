<script setup>
  import Question from "./Question.vue";
  import _ from 'lodash';
</script>

<script>
export default {
    props: [
        'edits_dict',
        'hits_data',
        'current_hit',
        'selected_edits_html',
        'selected_edits',
        'selected_state',
        'set_span_text',
        'set_span_indices',
        'set_hits_data',
        'refresh_interface_edit',
        'editor_open',
        'set_editor_state',
        'annotating_edit_span_category_id',
        'set_annotating_edit_span_category_id',
        'annotating_edit_span',
        'set_annotating_edit_span',
        'set_hit_box_config',
        'config',
    ],
    data() {
        let edit_state = this.initalize_edit_state()

        return {
            edit_state: edit_state,
        }
    },
    watch: {
        config() {
            this.edit_state = this.initalize_edit_state()
        }
    },
    methods: {
        parse_options(edit_config) {
            if (typeof edit_config !== "object") { return null }
            let edit_options = {}
            for (const option_idx in edit_config) {
                edit_options['val'] = null
                edit_options[edit_config[option_idx].name] = this.parse_options(edit_config[option_idx].options)
            } 
            return edit_options
        },
        initalize_edit_state() {
            let edit_state = {}
            for (const edit of this.config.edits) {
                edit_state[edit.name] = this.parse_options(edit.annotation)
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
                if (edit['category'] == selected_category && parseInt(edit['id']) > max_key) {
                    max_key = parseInt(edit['id']);
                }
            }

            const config_category = this.config.edits.find((edit) => edit.name === selected_category)

            let new_span = {
                'category': selected_category,
                'id': max_key + 1,
                'annotation': null
            }

            if (config_category['type'] == 'primitive') {
                if (config_category['enable_input']) {
                    let new_idx = this.selected_state.original_idx
                    if (!config_category['multi_span']) {
                        new_idx = [new_idx]
                    }
                    new_span['input_idx'] = new_idx
                }
                if (config_category['enable_output']) {
                    let new_idx = this.selected_state.simplified_idx
                    if (!config_category['multi_span']) {
                        new_idx = [new_idx]
                    }
                    new_span['output_idx'] = new_idx
                }
            }

            if (config_category['type'] == 'composite') {
                // 1) Add the existing edits (only certian fields) to constituent_edis
                let constituent_edits = []
                for (let edit of this.selected_edits) {
                    let composite_span = {
                        id: edit.id,
                        category: edit.category
                    }
                    if (edit.input_idx) { composite_span['input_idx'] = edit.input_idx }
                    if (edit.output_idx) { composite_span['output_idx'] = edit.output_idx }
                    constituent_edits.push(composite_span)
                }
                new_span['constituent_edits'] = constituent_edits

                // 2) Delete these edits
                for (let old_edit of constituent_edits) {
                    new_hits_data[this.current_hit - 1].edits = new_hits_data[this.current_hit - 1].edits.filter(
                        o => o.category !== old_edit.category || o.id !== old_edit.id
                    );
                }
            }

            new_hits_data[this.current_hit - 1].edits.push(new_span)
            
            this.set_hits_data(new_hits_data)
            this.refresh_edit();
        },
        cancel_annotation_click(category, e) {
            const id = this.annotating_edit_span_category_id
            $(".icon-default").removeClass("open")

            this.reset_annotation_colors(category, id)
            this.set_hits_data(_.cloneDeep(this.hits_data))
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

            this.reset_annotation_colors(category, edit_id)

            this.set_hits_data(new_hits_data)
            this.refresh_edit();
        },
        reset_annotation_colors(category, id) {
            let annotating_span = this.hits_data[this.current_hit - 1]['edits'].find(function(entry) {
                return entry['category'] === category && entry['id'] === id;
            });

            let color_class, border_class;
            if (!annotating_span.annotation || annotating_span.annotation == null) {
                color_class = `txt-${category}-light`
                border_class = `border-${category}-light`
            } else {
                color_class = `txt-${category}`
                border_class = `border-${category}`
            }

            let spans = $(`.${category}[data-id=${category}-${id}]`)
            let below_spans= $(`.${category}_below[data-id=${category}-${id}]`)
            below_spans.addClass(color_class)
            spans.removeClass(`white bg-${category} bg-${category}-light`)
            spans.addClass(border_class)
            below_spans.removeClass(`white bg-${category} bg-${category}-light`)
        },
        getEditConfig(category) {
            return this.config['edits'].find(function(entry) {
                return entry['name'] === category;
            });
        },
        refresh_edit() {
            this.set_editor_state(false);

            let classList = this.config.edits.map(function(edit) {
                return `txt-${edit.name}`;
            }).join(' ');
            $(".annotation-icon").removeClass(classList);

            for (let cat of classList) {
                $('#original-sentence').removeClass(`select-color-${cat}`)
                $('#simplified-sentence').removeClass(`select-color-${cat}`)
            }

            $("input[name=edit_cotegory]").prop("checked", false);
            $(".checkbox-tools").prop("checked", false);
            $(".checkbox-tools-yes-no").prop("checked", false);
            $('.quality-selection').hide(300);
            $(".span-selection-div").hide(300);

            $(".child-question").hide();

            this.edit_state = this.initalize_edit_state()
            this.refresh_interface_edit()
        },
        show_span_selection(e) {
            $(`.span-selection-div`).hide(300);
            $(`.span-selection-div[data-category=${e.target.value}]`).slideDown(300);
            const edit_config = this.getEditConfig(e.target.value);

            this.refresh_interface_edit()

            let new_hit_box_config = {
                enable_select_original_sentence: false,
                enable_select_simplified_sentence: false,
                enable_multi_select_original_sentence: false,
                enable_multi_select_simplified_sentence: false,
            }
                        
            if (edit_config['enable_input']) {
                new_hit_box_config.enable_select_original_sentence = true;
                if (edit_config['multi_span']) {
                    new_hit_box_config.enable_multi_select_original_sentence = true;
                }
            } 
            if (edit_config['enable_output']) {
                new_hit_box_config.enable_select_simplified_sentence = true;
                if (edit_config['multi_span']) {
                    new_hit_box_config.enable_multi_select_simplified_sentence = true;
                }
            }

            this.set_hit_box_config(new_hit_box_config)

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
            <div id="dropdown-button-container">
                <div class="over-hide z-bigger mt2 editor-container">
                    <p class="f3 annotation-label ttu mv1">Adding an Edit <i class="fa-solid fa-plus"></i></p>
                    <div class="row">
                        <p class="mb2 b tracked-light"><i>Select the Edit Category.</i>
                        </p>
                        <div class="tc mb3">
                            <div v-for="item in config.edits" :key="item.id" class="edit-box mr2 dib">
                                <input @click="show_span_selection" class="checkbox-tools-edit-category checkbox-tools" type="radio" name="edit_cotegory"
                                    :id="`edit_cotegory-${item.name}`" :value="item.name">
                                <label :class="`txt-${item.name}`" :for="`edit_cotegory-${item.name}`" style="text-wrap: nowrap">
                                    <i :class="`fa-solid ${item.icon} fa-1-5x mb1`"></i>
                                    {{ item.label }}
                                </label>
                            </div>
                        </div>

                        <div v-for="item in config.edits" :key="item.id" class="span-selection-div" :data-category="item.name">
                            <div v-if="item.enable_input">
                                <p class="mt0 mb2 b tracked-light">Select the text span from the <i>{{ config.input_label }}</i>.</p>
                                <p class="tracked-light">Selected span: <span v-html="selected_state.original_span"></span></p>
                            </div>
                            <div v-if="item.enable_output">
                                <div class="span-selection-div" :data-category="item.name">
                                    <p class="mt0 mb2 b tracked-light">Select the text span from the <i>{{ config.output_label }}</i>.</p>
                                    <p class="tracked-light">Selected span: <span v-html="selected_state.simplified_span"></span></p>
                                </div>
                            </div>
                            <div v-if="item.type == 'composite'">
                                <div class="span-selection-div" :data-category="item.name">
                                    <!-- <p class="mt0 mb2 b tracked-light">Click a split sign <i class="fa-solid fa-grip-lines-vertical fa-lg txt-split"></i> : <span class="txt-split">{{selected_state.split}}</span></p> -->
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

        <div v-for="item in config.edits" :key="item.id">
            <div class="quality-selection w-100" :id="`${item.name}_edit_annotation`" :data-category="item.name">
                <div id="dropdown-button-container">
                    <div class="over-hide z-bigger mt3 editor-container">
                        <p class="f3 annotation-label ttu mv1">Annotating an Edit <i class="fa-solid fa-pencil"></i></p>
                        <div class='single_part' />
                        <div class="f4 mt0 mb2 tc">
                            <span :class="`edit-type txt-${item.name} f3`">{{ item.label }}:  </span>

                            <span v-if="item.enable_input" v-html="annotating_edit_span.original"></span>
                            <span v-if="item.enable_input && item.enable_output" :class="`edit-type txt-${item.name} f3`"> with </span>
                            <span v-if="item.enable_output" v-html="annotating_edit_span.simplified"></span>
                            
                            <span v-if="item.type == 'composite'" v-html="annotating_edit_span.composite"></span>
                        </div>

                        <div class="row">
                            <div v-for="question in item.annotation" :key="question.id">
                                <Question :edit_state="edit_state" :question_state="edit_state[item.name][question.name]" :question="question" :edit_type="item" :set_edit_state="set_edit_state"
                                    :parent_show_next_question="null" isRoot=true />
                            </div>
                        </div>
                    </div>
                    <div class="buttons tc">
                        <button @click="cancel_annotation_click(item.name, $e)" class="cancel-button b quality_button bw0 ba mr2 br-pill-ns grow" type="button">Cancel <i class="fa-solid fa-close"></i></button>
                        <!-- :class="{'o-40': save_validated_deletion, 'grow': !save_validated_deletion}" :disabled="save_validated_deletion" -->
                        <button @click="save_annotation_click(item.name, $e)" class="confirm-button b quality_button bw0 ba ml2 br-pill-ns">Save <i class="fa-solid fa-check"></i></button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
