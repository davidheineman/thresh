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
            force_update: false,
            edit_state: edit_state,
            empty_edit_state: this.initalize_edit_state()
        }
    },
    watch: {
        config() {
            this.edit_state = this.initalize_edit_state()
            this.fix_edit_box_formatting()
        },
        editor_open() {
            this.fix_edit_box_formatting()
        }
    },
    methods: {
        fix_edit_box_formatting() {
            // Fix edit box formatting
            let editBoxes = $(".edit-box label");
            let heightDiff = 0;
            let maxHeight = 0;
            for (let i = 0; i < editBoxes.length; i++) {
                const height = editBoxes[i].offsetHeight;
                if (height > maxHeight) {
                    maxHeight = height;
                    heightDiff += 1;
                }
            }
            if (heightDiff > 0) {
                $(".edit-box label").css('justify-content', 'flex-start');
                $(".edit-box label").css('height', maxHeight-25 + "px");
            }
        },
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
            this.force_update = !this.force_update
        },
        force_update_f() {
            this.force_update = !this.force_update
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

            if (config_category.type == undefined || config_category.type == 'primitive') {
                if (config_category['enable_input']) {
                    let new_idx = this.selected_state.source_idx
                    if (!config_category['multi_span']) {
                        new_idx = [new_idx]
                    }
                    new_span['input_idx'] = new_idx
                }
                if (config_category['enable_output']) {
                    let new_idx = this.selected_state.target_idx
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
            function removeNullElements(obj) {
                if (typeof obj !== 'object' || obj === null) {
                    return obj;
                }

                if (Array.isArray(obj)) {
                    return obj.map((item) => removeNullElements(item)).filter((item) => item !== null);
                }

                const newObj = {};
                let hasNonNullChild = false;

                for (const key in obj) {
                    if (obj.hasOwnProperty(key)) {
                        const value = removeNullElements(obj[key]);
                        if (value !== null) {
                            newObj[key] = value;
                            hasNonNullChild = true;
                        }
                    }
                }
                return hasNonNullChild ? newObj : null;
            }

            let edit_id = this.annotating_edit_span_category_id
            
            let new_hits_data = _.cloneDeep(this.hits_data);
            let new_annotation = _.cloneDeep(this.edit_state[category])

            let annotating_span = new_hits_data[this.current_hit - 1]['edits'].find(function(entry) {
                return entry['category'] === category && entry['id'] === edit_id;
            });

            annotating_span.annotation = removeNullElements(new_annotation)

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
                $('#source-sentence').removeClass(`select-color-${cat}`)
                $('#target-sentence').removeClass(`select-color-${cat}`)
            }

            $("input[name=edit_cotegory]").prop("checked", false);
            $(".checkbox-tools").prop("checked", false);
            $(".checkbox-tools-yes-no").prop("checked", false);
            $('.quality-selection').slideUp(300);
            $(".span-selection-div").hide(300);

            $(".child-question").hide();

            this.edit_state = this.initalize_edit_state()
            this.refresh_interface_edit()
        },
        show_span_selection(e) {
            $(`.span-selection-div`).hide();
            $(`.span-selection-div[data-category=${e.target.value}]`).show();
            const edit_config = this.getEditConfig(e.target.value);

            this.refresh_interface_edit()

            let new_hit_box_config = {
                enable_select_source_sentence: false,
                enable_select_target_sentence: false,
                enable_multi_select_source_sentence: false,
                enable_multi_select_target_sentence: false,
            }
                        
            if (edit_config['enable_input']) {
                new_hit_box_config.enable_select_source_sentence = true;
                if (edit_config['multi_span']) {
                    new_hit_box_config.enable_multi_select_source_sentence = true;
                }
            } 
            if (edit_config['enable_output']) {
                new_hit_box_config.enable_select_target_sentence = true;
                if (edit_config['multi_span']) {
                    new_hit_box_config.enable_multi_select_target_sentence = true;
                }
            }

            this.set_hit_box_config(new_hit_box_config)

            this.set_span_text("", "source");
            this.set_span_text("", "target");
            this.set_span_indices("", "source");
            this.set_span_indices("", "target");
        },
        annotate_edit_disabled(item) {
            const force_update = this.force_update
            const category = item.name
            const edit_config = this.getEditConfig(category)

            if (!this.editor_open) { return true }
            if (!$(`.quality-selection[data-category=${category}]`).is(':visible')) { return true }
            if (!edit_config || !edit_config.annotation) { return false }

            let filled_out = true

            for (let question of edit_config.annotation) {
                const q_object = $(`#question_${category}_${question.name}`)
                if (q_object == undefined || q_object == {} || q_object.length == 0) { continue }
                const annotation = this.edit_state[category][question.name]

                // TODO: Improve annotation disabling. Currently it just checks if the root questions
                // are answered. I could implement this recursively by checking the "annotated" attribute
                // but this creates circular updating so we need a better solution.
                if (
                    annotation != null && 
                    (
                        (annotation.val != null && annotation.val != '') ||
                        (annotation.val == null && annotation != '' )
                    )) { 
                        continue 
                }

                if ($(q_object[0]).attr('annotated') != 'true') {
                    filled_out = false
                }
            }
            return !filled_out
        }
    },
    computed: {
        add_edit_disabled() {
            if (!this.editor_open) { return true }
            const selected_state = this.selected_state;
            const selected_category = $("input[name=edit_cotegory]:checked").val();
            const config_category = this.config.edits.find((edit) => edit.name === selected_category)
            if (selected_category == undefined || config_category == undefined) { return true }

            // TODO: Support multi-span edits

            let filled_out = false
            if (config_category.type == undefined || config_category.type == 'primitive') {
                const src = this.selected_state.source_span, tg = this.selected_state.target_span
                if (config_category['enable_input'] && config_category['enable_output']) {
                    if (src != null && src != '' && tg != null && tg != '') {
                        filled_out = true
                    }
                } else if (config_category['enable_input']) {
                    if (src != null && src != '') {
                        filled_out = true
                    }
                } else if (config_category['enable_output']) {
                    if (tg != null && tg != '') {
                        filled_out = true
                    }
                }
            }
            if (config_category['type'] == 'composite') {
                if (this.selected_edits.length > 0) {
                    filled_out = true
                }
            }
            return !filled_out
        }
    }
}
</script>

<template>
    <div class="quality-selection-divs">
        <div class="quality-selection w-100" id="add_an_edit">
            <div id="dropdown-button-container">
                <div class="over-hide z-bigger mt2 editor-container">
                    <p class="f3 annotation-label ttu mv1">{{ config.interface_text.annotation_editor.add_edit_header }} <i class="fa-solid fa-plus"></i></p>
                    <div class="row">
                        <p class="mb2 b tracked-light"><i>{{ config.interface_text.annotation_editor.select_edit_header }}.</i>
                        </p>
                        <div class="tc mb3">
                            <div v-for="item in config.edits" :key="item.id" class="edit-box mr2 dib">
                                <input @click="show_span_selection" class="checkbox-tools-edit-category checkbox-tools" type="radio" name="edit_cotegory"
                                    :id="`edit_cotegory-${item.name}`" :value="item.name">
                                <label :class="`txt-${item.name}`" :for="`edit_cotegory-${item.name}`">
                                    <i :class="`fa-solid ${item.icon} fa-1-5x mb1`"></i>
                                    {{ item.label }}
                                </label>
                            </div>
                        </div>

                        <div v-for="item in config.edits" :key="item.id" class="span-selection-div" :data-category="item.name">
                            <div v-if="item.enable_input">
                                <p class="mt0 mb2 b tracked-light">{{ config.interface_text.annotation_editor.select_instructions }} <i>{{ config.interface_text.typology.source_label }}</i>.</p>
                                <p class="tracked-light lh-paras-2">{{ config.interface_text.annotation_editor.selected_label }} {{ config.interface_text.typology.span_unit_name }}: <span v-html="selected_state.source_span"></span></p>
                            </div>
                            <div v-if="item.enable_output">
                                <div class="span-selection-div" :data-category="item.name">
                                    <p class="mt0 mb2 b tracked-light">{{ config.interface_text.annotation_editor.select_instructions }} <i>{{ config.interface_text.typology.target_label }}</i>.</p>
                                    <p class="tracked-light lh-paras-2">{{ config.interface_text.annotation_editor.selected_label }} {{ config.interface_text.typology.span_unit_name }}: <span v-html="selected_state.target_span"></span></p>
                                </div>
                            </div>
                            <div v-if="item.type == 'composite'">
                                <div class="span-selection-div" :data-category="item.name">
                                    <!-- <p class="mt0 mb2 b tracked-light">Click a split sign <i class="fa-solid fa-grip-lines-vertical fa-lg txt-split"></i> : <span class="txt-split">{{selected_state.split}}</span></p> -->
                                    <p class="mt0 mb2 b tracked-light">{{ config.interface_text.annotation_editor.composite_seletion_instructions }} {{ item.name }}.</p>
                                    <p class="tracked-light lh-paras-2">{{ config.interface_text.annotation_editor.selected_label }} {{ config.interface_text.typology.edits_unit_name }}: <span v-html="selected_edits_html"></span></p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="buttons tc mt2">
                    <button @click="cancel_click" class="cancel-button b quality_button bw0 ba mr2 br-pill-ns grow" type="button">{{ config.interface_text.buttons.cancel_label }} <i class="fa-solid fa-close"></i></button>
                    <button @click="save_click" :class="{'o-40': add_edit_disabled, 'grow': !add_edit_disabled}" :disabled="add_edit_disabled" 
                        class="confirm-button b quality_button bw0 ba ml2 br-pill-ns" type="button">{{ config.interface_text.buttons.save_label }} <i class="fa-solid fa-check"></i></button>
                </div>
            </div>
        </div>

        <div v-for="item in config.edits" :key="item.id">
            <div class="quality-selection w-100" :id="`${item.name}_edit_annotation`" :data-category="item.name">
                <div id="dropdown-button-container">
                    <div class="over-hide z-bigger mt3 editor-container">
                        <p class="f3 annotation-label ttu mv1">{{ config.interface_text.annotation_editor.add_edit_header }} <i class="fa-solid fa-pencil"></i></p>
                        <div class='single_part' />
                        <div class="f4 mt0 mb2 tc">
                            <span :class="`edit-type txt-${item.name} f3`">{{ item.label }}:  </span>

                            <span v-if="item.enable_input" v-html="annotating_edit_span.source"></span>
                            <span v-if="item.enable_input && item.enable_output" :class="`edit-type txt-${item.name} f3`">&nbsp;{{ config.interface_text.annotation_editor.composite_span_unification }}&nbsp;</span>
                            <span v-if="item.enable_output" v-html="annotating_edit_span.target"></span>
                            
                            <span v-if="item.type == 'composite'" v-html="annotating_edit_span.composite"></span>
                        </div>

                        <div class="row">
                            <div v-for="question in item.annotation" :key="question.id">
                                <Question :edit_state="edit_state" :empty_question_state="empty_edit_state[item.name][question.name]" :question_state="edit_state[item.name][question.name]" :question="question" :edit_type="item" :set_edit_state="set_edit_state"
                                    :config="config" :parent_show_next_question="null" isRoot=true :ref="`${item.name}_${question.name}`" :force_update="force_update_f" />
                            </div>
                        </div>
                    </div>
                    <div class="buttons tc">
                        <button @click="cancel_annotation_click(item.name, $e)" class="cancel-button b quality_button bw0 ba mr2 br-pill-ns grow" type="button">{{ config.interface_text.buttons.cancel_label }} <i class="fa-solid fa-close"></i></button>
                        <button @click="save_annotation_click(item.name, $e)" class="confirm-button b quality_button bw0 ba ml2 br-pill-ns"
                            :class="{'o-40': annotate_edit_disabled(item), 'grow': !annotate_edit_disabled(item)}" :disabled="annotate_edit_disabled(item)">{{ config.interface_text.buttons.save_label }} <i class="fa-solid fa-check"></i></button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
