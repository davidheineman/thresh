<script setup>
import VueMarkdown from 'vue-markdown-render'
</script>

<script>
export default {
  components: {
    VueMarkdown
  },
  props: [
    'config',
    'instructions_open',
    'toggle_instructions'
  ],
  mounted() {
    $('.container').removeClass('container-extra-space')
    if (this.config.prepend_instructions) {
      $('.container').addClass('container-extra-space')
    }
  }
}
</script>


<template>
  <main>
    <section v-if="config.instructions && config.prepend_instructions">
        <vue-markdown :source=config.instructions :options="options" class="mt0 mb0" />
        <br /><hr /><br />
    </section>

    <div class="overlay" v-if="instructions_open" @click="toggle_instructions"></div>
    <section v-if="instructions_open" class="modal br-pill-ns">
        <vue-markdown :source=config.instructions :options="options" class="mt0 mb0" />
    </section>
  </main>
</template>