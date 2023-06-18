<script>
export default {
    props: [
        'span_type',
        'selected_span_in_original',
        'selected_span_in_simplified',
        'hits_data',
        'current_hit'
    ],
    methods: {
        
    }
}
</script>

<template>
    <span>{{ this.selected_span_in_original }}</span>
</template>
