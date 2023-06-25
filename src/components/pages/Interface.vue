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
        config: {},
        edits_dict: {},
        lines: {},
        selected_edits: {},

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
      }
    },
    props: [
      'input_data',
      'consumed_config'
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
          let data = _.cloneDeep(this.input_data.data)
          this.set_hits_data(data)
          this.set_hit(1)
        },
        consume_config() {
          if (this.consumed_config.hasOwnProperty('consumed_config')) {
            this.config = _.cloneDeep(this.consumed_config.consumed_config)
          } else if (this.consumed_config.hasOwnProperty('config')) { 
            this.config = _.cloneDeep(this.consumed_config.config)
          } else {
            this.config = _.cloneDeep(this.consumed_config)
          }
          
          if (this.config.template_label) {
            $('title').text(this.config.template_label);
            // TODO: Add - tagline
          }
        },
        set_hit(hit_num) {
            this.current_hit = hit_num;
        },
        set_hits_data(hit_data) {
            this.hits_data = hit_data;
            this.total_hits = hit_data.length;
        },
        set_edits_dict(edits_dict) {
            this.edits_dict = edits_dict;
        },
        set_span_text(text, type) {
          if (type == "original") {
            this.selected_state.original_span = text;
          } else if (type == "simplified") {
            this.selected_state.simplified_span = text;
          }
        },
        set_span_indices(indices, type) {
          if (type == "original") {
            this.selected_state.original_idx = indices;
          } else if (type == "simplified") {
            this.selected_state.simplified_idx = indices;
          }
        },
        set_span_category(category, type) {
          if (type == "original") {
            this.selected_state.original_category = category;
          } else if (type == "simplified") {
            this.selected_state.simplified_category = category;
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
            enable_select_original_sentence: false,
            enable_select_simplified_sentence: false,
            enable_multi_select_original_sentence: false,
            enable_multi_select_simplified_sentence: false,
          }
          const DEFAULT_SELECTED_STATE = {
            original_span: '',
            original_idx: [],
            original_category: '',
            simplified_span: '',
            simplified_idx: [],
            simplified_category: '',
            split: '',
            split_id: null
          }
          const DEFAULT_ANNOTATING_EDIT_SPAN = {
            original: '',
            simplified: '',
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
          if (sent_type == 'original') {
            this.annotating_edit_span.original = data;
          } else if (sent_type == 'simplified') {
            this.annotating_edit_span.simplified = data;
          } else if (sent_type == 'composite') {
            this.annotating_edit_span.composite = data;
          } else {
            console.warn(`Invalid sent_type : ${sent_type}`)
          }
        },
        set_lines(lines) {
          this.lines = lines;
        },
        compile_style() {
          if (!this.config.hasOwnProperty('edits')) { return }

          let css = ``
          for (const edit of this.config.edits) {
            let color = edit.color
            if (COLORS.hasOwnProperty(color)) {
              color = COLORS[color]
            }

            let light_color = tinycolor(color).lighten(25).toHexString();
            
            css += `
              .border-${edit.name} { border-bottom: 3px solid ${color}; }
              .border-${edit.name}-all { border: 2px solid ${color}; }
              .bg-${edit.name} { background-color: ${color}; }
              .txt-${edit.name} { color: ${color}; }
              .bg-${edit.name}-light { background-color: ${light_color}; }
              .border-${edit.name}-light { border-bottom: 3px solid ${light_color}; }
              .border-${edit.name}-light-all { border: 2px solid ${light_color}; }
              .txt-${edit.name}-light { color: ${light_color}; }
            `
          }
          return css
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
  <div class="container w-65 mv3 mb-3 card-body">
    <div class='custom_style' id='custom_style'>Custom style has not loaded!</div>
    <!-- <Instructions :config="config" /> -->
    <!-- <CommentBox v-bind="$data" :config="config" /> -->
    <HitBox v-bind="$data" :config="config" />
    <AnnotationEditor v-bind="$data" :config="config" />
    <AnnotationViewer v-bind="$data" :config="config" />
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
