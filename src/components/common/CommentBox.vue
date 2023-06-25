<script setup>
import _ from 'lodash';
</script>

<script>
export default {
    props: [
        'hits_data',
        'current_hit'
    ],
    data() {
        return {}
    },
    methods: {
        leave_comment() {
            $("#comment_area_div").show();
        },
        record_comment(e) {
            let new_hits_data = _.cloneDeep(this.hits_data);
            new_hits_data[this.current_hit - 1]["comment"] = e.target.value;
            this.set_hits_data(new_hits_data)
        },
    }
}
</script>

<template>
    <section id="response_box">
        <p @click="leave_comment" class="comment_button mv0 pa2 br-pill-ns ba bw1 grow pointer">
            <span class="f4 mr2">Comment</span>
            <i class="fa-regular fa-comment fa-1-5x icon-default pointer"></i>
        </p>
        <div id="comment_area_div" class="mt2 dn">
            <textarea id="comment_area" class="comment_area br5 bw1 ba br4 ph3 pv2 mid-gray w-100" name="comment" placeholder="Comment on this HIT ..." @input="record_comment"></textarea>
        </div>
    </section>
</template>