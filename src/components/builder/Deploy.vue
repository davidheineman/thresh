<script setup>
import Tab from './Tab.vue'
</script>

<script>
export default {
    data() {  
        return {
            active_tab: 'mturk'
        };
    },
    props: [
        'config',
        'deploy_open',
        'toggle_deploy',
    ],
    watch: {
        deploy_open(newVal) {
            if (newVal) {
                this.$nextTick(() => {
                    this.render_tab_selector();
                });
            }
        }
    },
    methods: {
        selectTab(selectedTab) {
            this.active_tab = selectedTab
        },
        render_tab_selector() {
            var tabs = $('.tabs');
            var activeItem = tabs.find('.active');
            var activeWidth = activeItem.innerWidth();
            $(".selector").css({
                "left": activeItem.position.left + "px", 
                "width": activeWidth + "px"
            });
            $(".tabs").on("click","a",function(e){
                e.preventDefault();
                $('.tabs a').removeClass("active");
                $(this).addClass('active');
                var activeWidth = $(this).innerWidth();
                var itemPos = $(this).position();
                $(".selector").css({
                    "left":itemPos.left + "px", 
                    "width": activeWidth + "px"
                });
            });
        }
    },
    mounted() {
        this.render_tab_selector()
    },
}
</script>

<template>
  <main class="deploy-overlay overlay-container">
    <div class="overlay" v-if="deploy_open" @click="toggle_deploy"></div>
    <section v-if="deploy_open" class="modal br-pill-ns">
        <div class="wrapper">
            <nav class="tabs">
                <div class="selector"></div>
                <!-- :class="{'is-active': active_tab == 'mturk'} -->
                <a @click="selectTab('mturk')" class="active">MTurk</a>
                <a @click="selectTab('serverless')">Serverless</a>
                <a @click="selectTab('hosted')">Hosted</a>
                <a @click="selectTab('python')">Python</a>
            </nav>
        </div>

        <div id="tab-contents">
            <Tab name="mturk" :selected="active_tab == 'mturk'">
                <h2>Deploy to MTurk</h2>
            </Tab>
            <Tab name="serverless" :selected="active_tab == 'serverless'">
                <h2>Package with data and annotate on <code>nlproc.tools</code></h2>
            </Tab>
            <Tab name="hosted" :selected="active_tab == 'hosted'">
                <h2>Host template and annotate on <code>nlproc.tools</code></h2>
            </Tab>
            <Tab name="python" :selected="active_tab == 'python'">
                <h2>Deploy your template using <code>nlproc-tools</code> + Python</h2>
            </Tab>
        </div>
    </section>
  </main>
</template>