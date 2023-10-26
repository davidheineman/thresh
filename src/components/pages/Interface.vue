<script setup>
  import AnnotationEditor from "../editor/AnnotationEditor.vue";
  import AnnotationViewer from "../viewer/AnnotationViewer.vue";
  import CommentBox from "../common/CommentBox.vue";
  import Instructions from "../common/Instructions.vue";
  import HitBox from "../hitbox/HitBox.vue";

  import tinycolor from 'tinycolor2';
  import _ from 'lodash';
  import { COLORS } from '../../assets/js/constants.js';
</script>

<script>
  export default {
    data() {
      return {
        total_hits: 0,
        current_hit: 1,
        hits_data: null,
        config: null,
        edits_dict: {},
        lines: {},
        selected_edits: {},
        timers: [],

        editor_open: false,
        selected_edits_html: '',
        annotating_edit_span_category_id: null,

        hit_box_config: undefined,
        selected_state: undefined,
        annotating_edit_span: undefined,
        
        set_hit: this.set_hit,
        set_hits_data: this.set_hits_data,
        set_edits_dict: this.set_edits_dict,
        set_lines: this.set_lines,
        set_span_text: this.set_span_text,
        set_span_indices: this.set_span_indices,
        set_span_category: this.set_span_category,
        set_edit_html: this.set_edit_html,
        set_selected_edits: this.set_selected_edits,
        set_hit_box_config: this.set_hit_box_config,
        set_editor_state: this.set_editor_state,
        set_annotating_edit_span_category_id: this.set_annotating_edit_span_category_id,
        set_annotating_edit_span: this.set_annotating_edit_span,

        refresh_interface_edit: this.refresh_interface_edit,

        instructions_open: false,
        toggle_instructions: this.toggle_instructions,
      }
    },
    props: [
      'input_data',
      'consumed_config',
      'highlight'
    ],
    watch: {
      input_data() {
        this.consume_data()
      },
      consumed_config() {
        this.consume_config()
      }
    },
    methods: {
        consume_data() {
          let data = _.cloneDeep(this.input_data.data);
          this.set_hits_data(data)
          this.set_hit(1)
        },
        consume_config() {
          let new_config;
          if (this.consumed_config.hasOwnProperty('consumed_config')) {
            new_config = _.cloneDeep(this.consumed_config.consumed_config)
          } else if (this.consumed_config.hasOwnProperty('config')) { 
            new_config = _.cloneDeep(this.consumed_config.config)
          } else {
            new_config = _.cloneDeep(this.consumed_config)
          }
          this.config = new_config
          
          if (this.config.template_label) {
            $('title').text(this.config.template_label);
          }
        },
        set_hit(hit_num) {
          if (hit_num != this.current_hit && this.config.adjudication) {
            $(`.circle-${hit_num}`).click()
          }
          this.stop_timer(this.current_hit)
          this.start_timer(hit_num)
          this.current_hit = hit_num;
        },
        start_timer(hit_num) {
          this.timers[hit_num - 1] = setInterval(() => {
            this.hits_data[hit_num - 1]['_seconds_spent']++;
          }, 1000); // Increment every second
        },
        stop_timer(hit_num) {
          clearInterval(this.timers[hit_num - 1]);
        },
        set_hits_data(hit_data) {
            hit_data.forEach(o => o.edits = o.edits || []);
            hit_data.forEach((o, idx) => { o._thresh_id = idx + 1; });
            hit_data.forEach(o => o._seconds_spent = o._seconds_spent || 0);
            this.hits_data = hit_data;
            this.total_hits = hit_data.length;
        },
        set_edits_dict(edits_dict) {
            this.edits_dict = edits_dict;
        },
        set_span_text(text, type) {
          if (type == "source") {
            this.selected_state.source_span = text;
          } else if (type == "target") {
            this.selected_state.target_span = text;
          }
        },
        set_span_indices(indices, type) {
          if (type == "source") {
            this.selected_state.source_idx = indices;
          } else if (type == "target") {
            this.selected_state.target_idx = indices;
          }
        },
        set_span_category(category, type) {
          if (type == "source") {
            this.selected_state.source_category = category;
          } else if (type == "target") {
            this.selected_state.target_category = category;
          }
        },
        set_edit_html(html) {
          this.selected_edits_html = html;
        },
        set_selected_edits(edits) {
          this.selected_edits = edits;
        },
        refresh_interface_edit() {
          const DEFAULT_HIT_BOX_CONFIG = {
            enable_select_source_sentence: false,
            enable_select_target_sentence: false,
            enable_multi_select_source_sentence: false,
            enable_multi_select_target_sentence: false,
          }
          const DEFAULT_SELECTED_STATE = {
            source_span: '',
            source_idx: [],
            source_category: '',
            target_span: '',
            target_idx: [],
            target_category: '',
            split: '',
            split_id: null
          }
          const DEFAULT_ANNOTATING_EDIT_SPAN = {
            source: '',
            target: '',
            composite: ''
          }

          this.selected_edits = []
          this.selected_edits_html = ""
          this.selected_state = DEFAULT_SELECTED_STATE
          this.hit_box_config = DEFAULT_HIT_BOX_CONFIG
          this.annotating_edit_span = DEFAULT_ANNOTATING_EDIT_SPAN
        },
        set_hit_box_config(config) {
          this.hit_box_config = config;
        },
        set_editor_state(state) {
          this.editor_open = state;
        },
        set_annotating_edit_span_category_id(id) {
          this.annotating_edit_span_category_id = id;
        },
        set_annotating_edit_span(data, sent_type=null) {
          if (sent_type == 'source') {
            this.annotating_edit_span.source = data;
          } else if (sent_type == 'target') {
            this.annotating_edit_span.target = data;
          } else if (sent_type == 'composite') {
            this.annotating_edit_span.composite = data;
          } else {
            console.warn(`Invalid sent_type : ${sent_type}`)
          }
        },
        set_lines(lines) {
          this.lines = lines;
        },
        toggle_instructions() {
          this.instructions_open = !this.instructions_open;
        },
        compile_style() {
          if (!this.config.hasOwnProperty('edits')) { return }

          // Compile color overrides

          let css = ``
          for (const edit of this.config.edits) {
            let color = edit.color
            if (COLORS.hasOwnProperty(color)) {
              color = COLORS[color]
            }

            let light_color = tinycolor(color).lighten(25).toHexString();
            
            css += `
              :root { --${edit.name}: ${color}; --${edit.name}-light: ${light_color}; }
              .border-${edit.name} { border-bottom: 3px solid ${color}; }
              .border-${edit.name}-all { border: 2px solid ${color}; }
              .bg-${edit.name} { background-color: ${color}; }
              .txt-${edit.name} { color: ${color}; }
              .bg-${edit.name}-light { background-color: ${light_color}; }
              .border-${edit.name}-light { border-bottom: 3px solid ${light_color}; }
              .border-${edit.name}-light-all { border: 2px solid ${light_color}; }
              .txt-${edit.name}-light { color: ${light_color}; }
              .checkbox-tools-yes-no:checked + label.question-${edit.name},
              .checkbox-tools:checked + label.question-${edit.name},
              .checkbox-tools:checked + label.txt-${edit.name}{
                border: 2px solid var(--${edit.name});
              }
              .select-color-${edit.name}::selection { background: ${light_color} !important; }
            `
          }

          // Compile font size overrides
          if (this.config.font_size) {
            if (this.config.font_size.source) {
              css += `#source-sentence { font-size: ${this.config.font_size.source}px; }`
            }
            if (this.config.font_size.target) {
              css += `#target-sentence { font-size: ${this.config.font_size.target}px; }`
            }
          }

          return css
        },
        isAdjacent() {
          return this.config.hasOwnProperty('display') && Object.values(this.config.display).includes('side-by-side')
        }
    },
    updated() {
      $('#custom_style').html(`<style>${this.compile_style()}</style>`)
      $(`#circle-${this.current_hit}`).addClass('circle-active');
    }, 
    mounted() {
      this.consume_data()
      this.consume_config()
    },
    created() {
      this.consume_config()
      this.refresh_interface_edit()
    }
  }
  
</script>

<template>
  <div v-if="config != null" class="container mb0 card-body" v-bind:class="{ 'w-100 w-adjacent': isAdjacent(), 'w-65': !isAdjacent() }">
    <div class='custom_style' id='custom_style'>Custom style has not loaded!</div>
    <div v-if="highlight" class="tc f3 b mb3 mt3 adjudication-highlight">
      {{ config.interface_text.adjudication.highlight_label }}
    </div>
    <main v-bind:class="{ 'adjacent': isAdjacent() }">
      <div v-bind:class="{ 'selection-adjacent': isAdjacent() }">
        <Instructions v-bind="$data" :config="config" />
        <!-- <CommentBox v-bind="$data" :config="config" /> -->
        <HitBox v-bind="$data" :config="config" />
      </div>
      <div v-bind:class="{ 'annotation-adjacent': isAdjacent() }">
        <AnnotationEditor v-bind="$data" :config="config" />
        <AnnotationViewer v-bind="$data" :config="config" />
      </div>
    </main>
  </div>
</template>

<style>
  @import '../../assets/css/index.css';
  @import '../../assets/css/selection.css';
  @import '../../assets/css/button.css';
  @import '../../assets/css/select_box.css';
  @import '../../assets/css/download_upload.css';
  @import 'https://unpkg.com/tachyons@4.10.0/css/tachyons.min.css';
  @import 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css';
  @import 'https://cdnjs.cloudflare.com/ajax/libs/animate.css/3.7.2/animate.min.css';
</style>
