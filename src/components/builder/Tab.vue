<script>
export default {
    props: {
        name: { required: true },
        selected: { default: false }
    },
    data() {  
        return {
            isActive: false
        };
    },
    computed: {
        href() {
            return '#' + this.name.toLowerCase().replace(/ /g, '-');
        }
    }
}
</script>

<template>
    <div v-show="selected">
        <slot></slot>
    </div>
</template>