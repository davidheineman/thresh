<script>
export default {
  props: [
    'config'
  ],
}
</script>


<template>
    <section id="helper_list" class="w-15">
        <!-- <p class="mt0 mb2">Please make sure you select all the edits, some edits <b>may be easily missed</b> when the sentence is too long.</p>
        <p class="mv2">If you encounter any bug or have any suggestion on this tool, please write it at this <a href="https://docs.google.com/document/d/1oQpOMZij_keFGonBr9ZvXUn4cmgTgfpfueME_bVU-FI/edit" class="link dim">google doc link</a>.</p>
        <p class="mv2">If you have any question, please don't hesitate to ask us over <b>slack</b>.</p>
        <p class="mt2 mb0">Have fun!!!</p> -->

        <p class="mt0 mb2">{{ config.instructions }}</p>
    </section>
</template>