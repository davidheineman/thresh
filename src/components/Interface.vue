<script setup>
  import AnnotationEditor from "./AnnotationEditor.vue";
  import AnnotationViewer from "./AnnotationViewer.vue";
  import CommentBox from "./CommentBox.vue";
  import Instructions from "./Instructions.vue";
  import HitBox from "./HitBox.vue";

  import { download_data, get_file_path } from "../assets/js/file-util.js";
  import { EMPTY_ANNOTATION, EMPTY_CONSTITUENT_TYPES, EMPTY_CONNECTED_TYPES, CONFIG } from "../assets/js/constants.js";
</script>

<script>
  export default {
    data() {
        return {
            ann_state: {
                total_hits: 0,
                current_hit: 1,
                hits_data: null,
                edits_dict: EMPTY_ANNOTATION,

                selected_span_in_original: '',
                selected_span_in_simplified: '',
                selected_span_in_original_indexs: [],
                selected_span_in_simplified_indexs: [],
                selected_span_in_original_category: '',
                selected_span_in_simplified_category: '',
                selected_edits_html: '',
                selected_edits: EMPTY_CONSTITUENT_TYPES,
                selected_split: '',
                selected_split_id: null,

                lines: EMPTY_CONNECTED_TYPES,
                set_lines: this.set_lines,
                
                set_hit: this.set_hit,
                set_hits_data: this.set_hits_data,
                set_edits_dict: this.set_edits_dict,
                set_span_text: this.set_span_text,
                set_span_indices: this.set_span_indices,
                set_span_category: this.set_span_category,
                set_edit_html: this.set_edit_html,
                set_selected_edits: this.set_selected_edits,
                refresh_interface_edit: this.refresh_interface_edit,

                editor_open: false,
                set_editor_state: this.set_editor_state,

                annotating_edit_span_category_id: null,
                set_annotating_edit_span_category_id: this.set_annotating_edit_span_category_id,
            
                annotating_edit_span: {
                  original: '',
                  original_for_substitution: '',
                  simplified: '',
                  simplified_for_substitution: '',
                  split: '',
                  structure: ''
                },
                set_annotating_edit_span: this.set_annotating_edit_span,

                css: this.compile_style()
            }
        }
    },
    methods: {
        set_hit(hit_num) {
            this.ann_state.current_hit = hit_num;
        },
        set_hits_data(hit_data) {
            this.ann_state.hits_data = hit_data;
            this.ann_state.total_hits = hit_data.length;
        },
        set_edits_dict(edits_dict) {
            this.ann_state.edits_dict = edits_dict;
        },
        set_span_text(text, type) {
          if (type == "original") {
            this.ann_state.selected_span_in_original = text;
          } else if (type == "simplified") {
            this.ann_state.selected_span_in_simplified = text;
          }
        },
        set_span_indices(indices, type) {
          if (type == "original") {
            this.ann_state.selected_span_in_original_indexs = indices;
          } else if (type == "simplified") {
            this.ann_state.selected_span_in_simplified_indexs = indices;
          }
        },
        set_span_category(category, type) {
          if (type == "original") {
            this.ann_state.selected_span_in_original_category = category;
          } else if (type == "simplified") {
            this.ann_state.selected_span_in_simplified_category = category;
          }
        },
        set_edit_html(html) {
          this.ann_state.selected_edits_html = html;
        },
        set_selected_edits(edits) {
          this.ann_state.selected_edits = edits;
        },
        refresh_interface_edit() {
          this.selected_split = ""
          this.selected_add_edit_category_temp = "";
          this.selected_span_in_original = '',
          this.selected_span_in_simplified = '',
          this.selected_span_in_original_indexs = [],
          this.selected_span_in_simplified_indexs = [],
          this.selected_edits = EMPTY_CONSTITUENT_TYPES,
          this.selected_edits_html = "",
          this.enable_select_original_sentence = false;
          this.enable_select_simplified_sentence = false;
          this.enable_multi_select_original_sentence = false;
          this.enable_multi_select_simplified_sentence = false;
        },
        set_editor_state(state) {
          this.ann_state.editor_open = state;
        },
        set_annotating_edit_span_category_id(id) {
          this.ann_state.annotating_edit_span_category_id = id;
        },
        set_annotating_edit_span(data, sent_type = null, special_type = null) {
          if (special_type == 'split') {
            this.ann_state.annotating_edit_span.split = data;
          } else if (special_type == 'structure') {
            this.ann_state.annotating_edit_span.structure = data;
          }
          if (sent_type == 'original') {
            if (special_type == 'substitution') {
              this.ann_state.annotating_edit_span.original_for_substitution = data;
            } else {
              this.ann_state.annotating_edit_span.original = data;
            }
          } else if (sent_type == 'simplified') {
            if (special_type == 'substitution') {
              this.ann_state.annotating_edit_span.simplified_for_substitution = data;
            } else {
              this.ann_state.annotating_edit_span.simplified = data;
            }
          }
        },
        set_lines(lines) {
          this.ann_state.lines = lines;
        },
        compile_style() {
          var colors = {
            'red': '#ee2a2a',
            'green': '#64c466',
            'blue': '#2186eb',
            'yellow': '#ee2a2a',
            'light_green': '#3ca3a7',
            'orange': '#e67c43'
          }

          let css = ``
          for (const edit of CONFIG.edits) {
            let color = edit.color
            if (colors.hasOwnProperty(color)) {
              color = colors[color]
            }
            
            css += `
              .border-${edit.name} { border-bottom: 3px solid ${color}; }
              .border-${edit.name}-all { border: 2px solid ${color}; }
              .bg-${edit.name} { background-color: ${color}; }
              .txt-${edit.name} { color: ${color}; }
              .bg-${edit.name}-light { background-color: #F4B8B1; }
              .border-${edit.name}-light { border-bottom: 3px solid #F4B8B1; }
              .border-${edit.name}-light-all { border: 2px solid #F4B8B1; }
              .txt-${edit.name}-light { color: #F4B8B1; }
            `
          }
          // return `<style>${css}</style>`
          return css
        }
    },
    created: function() {
        let file_path = get_file_path();
        download_data(file_path).then((data) => {
          this.set_hits_data(data);
        })
    }
  }
  
</script>

<template>
  <main>
    <component :is="compile_style"></component>
    <div class="container w-65 mv3 mb-3 card-body" :style="css">
      <Instructions />
      <CommentBox v-bind="ann_state" />
      <HitBox v-bind="ann_state" />
      <AnnotationEditor v-bind="ann_state" />
      <AnnotationViewer v-bind="ann_state" />
    </div>
  </main>
</template>

