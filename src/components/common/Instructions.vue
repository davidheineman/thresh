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
}
</script>


<template>
  <main>
    <div class="overlay" v-if="instructions_open" @click="toggle_instructions"></div>
    <section v-if="instructions_open" class="modal br-pill-ns">
        <vue-markdown :source=config.instructions :options="options" class="mt0 mb0" />
    </section>
  </main>
</template>