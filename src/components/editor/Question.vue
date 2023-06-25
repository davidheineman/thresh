<script setup>
  import _ from 'lodash';
</script>

<script>
export default {
    props: [
        'edit_state',
        'question',
        'edit_type',

        'parent_show_next_question',
        'set_edit_state',

        'update_edit_state_parent',
        'question_state',

        'isRoot',
        'parent_div_name'
    ],
    data() { 
        let col_size = 0;
        if ('options' in this.question) {
            switch (this.question.options.length) {
                case 2: col_size = 50; break;
                case 3: col_size = 33; break;
                case 4: col_size = 25; break;
                case 6: col_size = 16; break;
            }
        }

        let div_name;
        if (Boolean(this.isRoot === 'true')) {
            div_name = `question-${this.edit_type.name}-${this.question.name}`
        } else {
            div_name = `${this.parent_div_name}-${this.question.name}`
        }

        return {
            col_size: col_size,
            div_name: div_name
        } 
    },
    methods: {
        has_children() {
            return this.isObject(this.question.options)
        },
        show_next_question(e) {
            let selected_val = e.target.value
            if (this.has_children()) {
                // Hide other children
                for (let i = 0; i < this.question.options.length; i++) {
                    let option = this.question.options[i];
                    let child_div = `.${this.div_name}-${option.name}`
                    $(child_div).hide(400);
                }

                // Show options of selected child
                let child_div = `.${this.div_name}-${selected_val}`
                if (!$(child_div).is(":visible")) {
                    $(child_div).slideDown(400);
                }
            } else {
                // else recurse upwards
                // this.parent_show_next_question(e)
            }
        },
        update_edit_state(val) {
            if (val === "") { val = null }

            if (Boolean(this.isRoot === 'true')) {
                let new_edit_state = _.cloneDeep(this.edit_state);
                if (this.has_children()) {
                    new_edit_state[this.edit_type.name][this.question.name].val = val;
                } else {
                    new_edit_state[this.edit_type.name][this.question.name] = val;
                }
                this.set_edit_state(new_edit_state);
            } else {
                let new_question_state = _.cloneDeep(this.question_state);
                if (this.has_children()) {
                    new_question_state.val = val;
                } else {
                    new_question_state = val;
                }
                this.update_edit_state_parent(this.question.name, new_question_state)
            }
        },
        update_edit_state_child(childName, new_state) {
            let new_question_state = _.cloneDeep(this.question_state);
            new_question_state[childName] = new_state;

            if (Boolean(this.isRoot === 'true')) {
                let new_edit_state = _.cloneDeep(this.edit_state);
                new_edit_state[this.edit_type.name][this.question.name] = new_question_state;
                this.set_edit_state(new_edit_state);
            } else {
                this.update_edit_state_parent(this.question.name, new_question_state);
            }
        },
        getClassNames() {
            let names = []
            names.push(this.div_name)
            if (Boolean(this.isRoot !== 'true')) {
                names.push('child-question')
            }
            return names
        },
        child_state(child) {
            if (this.has_children() && typeof this.question.options !== 'string') {
                return this.question_state[child.name]
            } else {
                return this.question_state//[child.name] // right?
            }
        }
    },
    computed: {
        isObject() {
            return (variable) => {
                return typeof variable === "object" && variable !== null;
            };
        },
    }
}

</script>

<template>
    <div :class="getClassNames()">
        <!-- If the question has children -->
        <div v-if="isObject(question.options)">
            <p class="mb3 b tracked-light">{{ question.question }}</p>
            <div class="tc" >
                <div :class="`column-severity w-${col_size}`" v-for="option in question.options" :key="option.id">
                    <input @click="show_next_question" class="checkbox-tools checkbox-tools-severity " type="radio" :name="question.name"
                        :id="`${div_name}-${option.name}`" :value="option.name" @input="update_edit_state($event.target.value)">
                    <label :class="`for-checkbox-tools-severity question-${edit_type.name}`" :for="`${div_name}-${option.name}`">
                        {{ option.label }}
                    </label>
                </div>
            </div>

            <div v-for="child in question.options" :key="child.id">
                <Question :edit_state="edit_state" :question_state="child_state(child)" :question="child" :edit_type="edit_type" :set_edit_state="set_edit_state" 
                    :parent_show_next_question="show_next_question" isRoot=false :update_edit_state_parent="update_edit_state_child"
                    :parent_div_name="div_name" />
            </div>
        </div>

        <!-- If the question is likert-3 -->
        <div v-if="question.options === 'likert-3'">
            <p class="mb3 b tracked-light">{{ question.question }}</p>
            <div class="tc">
                <div class="column-severity w-33">
                    <input @click="show_next_question" class="checkbox-tools checkbox-tools-severity " type="radio" :name="`${div_name}-severity`"
                        :id="`${div_name}-severity-1`" value="minor" @input="update_edit_state($event.target.value)">
                    <label :class="`for-checkbox-tools-severity question-${edit_type.name}`" :for="`${div_name}-severity-1`">
                        1 - minor
                    </label>
                </div>
                <div class="column-severity w-33">
                    <input @click="show_next_question" class="checkbox-tools checkbox-tools-severity " type="radio" :name="`${div_name}-severity`"
                        :id="`${div_name}-severity-2`" value="somewhat" @input="update_edit_state($event.target.value)">
                    <label :class="`for-checkbox-tools-severity question-${edit_type.name}`" :for="`${div_name}-severity-2`">
                        2 - somewhat
                    </label>
                </div>
                <div class="column-severity w-33">
                    <input @click="show_next_question" class="checkbox-tools checkbox-tools-severity " type="radio" :name="`${div_name}-severity`"
                        :id="`${div_name}-severity-3`" value="a lot" @input="update_edit_state($event.target.value)">
                    <label :class="`for-checkbox-tools-severity question-${edit_type.name}`" :for="`${div_name}-severity-3`">
                        3 - a lot
                    </label>
                </div>
            </div>
        </div>

        <!-- If the question is binary -->
        <div v-if="question.options === 'binary'">
            <p class="mt0 pt2 mb3 b tracked-light"> {{ question.question }}
                <input class="checkbox-tools-yes-no" type="radio" :name="`${div_name}-yes-no`"
                    :id="`${div_name}-yes`" value="yes" @input="update_edit_state($event.target.value)">
                <label :class="`normal for-checkbox-tools-yes-no question-${edit_type.name}`" :for="`${div_name}-yes`">yes</label>
                <input class="checkbox-tools-yes-no" type="radio" :name="`${div_name}-yes-no`"
                    :id="`${div_name}-no`" value="no" @input="update_edit_state($event.target.value)">
                <label :class="`normal for-checkbox-tools-yes-no question-${edit_type.name}`" :for="`${div_name}-no`">no</label>
            </p>
        </div>
    </div>
</template>