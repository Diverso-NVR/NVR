<template>
  <v-dialog v-model="modal" max-width="600px">
    <v-btn icon slot="activator">
      <v-icon>edit</v-icon>
    </v-btn>
    <v-card>
      <v-card-text>
        <v-form ref="form" validation v-model="valid">
          <v-layout wrap>
            <v-flex xs12 sm6 md8>
              <v-text-field label="Название" :rules="fieldsRules" v-model="source.name"></v-text-field>
            </v-flex>
            <v-flex xs12 sm6 md8>
              <v-text-field label="IP" :rules="fieldsRules" v-model="source.ip"></v-text-field>
            </v-flex>

            <v-flex xs12 sm6 md8>
              <v-select
                :items="['enc', 'cam', false]"
                label="Источник звука"
                required
                v-model="source.sound"
              ></v-select>
            </v-flex>
            <v-flex xs12 sm6 md8>
              <v-checkbox v-model="source.tracking" :label="`Трекинг`"></v-checkbox>
            </v-flex>
            <v-flex xs12 sm6 md8>
              <v-checkbox v-model="source.mainCam" :label="`Главная камера`"></v-checkbox>
            </v-flex>
          </v-layout>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="black" flat :disabled="!valid" @click="modal = false">Закрыть</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: ["source"],
  data() {
    return {
      modal: false,
      valid: false,
      fieldsRules: [v => !!v || "Обязательное поле"]
    };
  }
};
</script>
