<script>
export default {
  props: [
    'config',
    'cite_open',
    'toggle_cite'
  ],
}
</script>


<template>
  <main class="cite-overlay overlay-container">
    <div class="overlay" v-if="cite_open" @click="toggle_cite"></div>
    <section v-if="cite_open" class="modal br-pill-ns">
        <h3>BibTex Citation</h3>
        <pre>{{ config.citation }}</pre>
        <a v-if="config != null && config != undefined && config.paper_link" :href="config.paper_link">
            <button class="pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn">View Paper</button>
        </a>
    </section>
  </main>
</template>