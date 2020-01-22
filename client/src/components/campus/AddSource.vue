<template>
  <v-dialog v-model="modal" max-width="600px" :dark="isDarkMode">
    <v-btn block color="black" class="white--text" slot="activator">Добавить</v-btn>

    <v-card>
      <v-card-text>
        <v-form ref="form" validation v-model="valid">
          <v-layout wrap>
            <v-flex xs12 sm6 md8>
              <v-text-field label="Название" :rules="fieldsRules" v-model="newSource.name"></v-text-field>
            </v-flex>
            <v-flex xs12 sm6 md8>
              <v-text-field label="IP" :rules="fieldsRules" v-model="newSource.ip"></v-text-field>
            </v-flex>
          </v-layout>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="black" flat @click="modal = false">Закрыть</v-btn>
        <v-btn color="black" flat :disabled="!valid" @click="addSource">Сохранить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: ["room"],
  data() {
    return {
      modal: false,
      valid: false,
      newSource: {},
      fieldsRules: [v => !!v || "Обязательное поле"]
    };
  },
  computed: {
    isDarkMode() {
      return this.$store.getters.isDarkMode;
    }
  },
  methods: {
    addSource() {
      this.modal = false;
      this.room.sources.push(this.newSource);
      this.newSource = {};
    }
  }
};
</script>
