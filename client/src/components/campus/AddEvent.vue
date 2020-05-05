<template>
  <v-dialog v-model="modal" max-width="600px" :dark="isDarkMode">
    <v-btn depressed color="primary" slot="activator">Запросить</v-btn>
    <v-card>
      <v-card-text>
        <v-form ref="form" validation v-model="valid">
          <v-layout wrap>
            <v-flex xs12 sm6 md8>
              <v-text-field
                v-model="eventName"
                label="Название"
                :rules="nameRules"
                prepend-icon="label"
              ></v-text-field>
              <v-menu
                v-model="dateMenu"
                :close-on-content-click="false"
                :nudge-right="40"
                lazy
                transition="scale-transition"
                offset-y
                full-width
                min-width="290px"
              >
                <template v-slot:activator="{ on }">
                  <v-text-field
                    v-model="date"
                    :rules="fieldsRules"
                    label="Дата"
                    prepend-icon="event"
                    readonly
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-date-picker v-model="date" @input="dateMenu = false"></v-date-picker>
              </v-menu>
            </v-flex>
            <v-flex xs11 sm5>
              <v-menu
                ref="menu"
                v-model="startTimeMenu"
                :close-on-content-click="false"
                :nudge-right="40"
                :return-value.sync="startTime"
                lazy
                transition="scale-transition"
                offset-y
                full-width
                max-width="290px"
                min-width="290px"
              >
                <template v-slot:activator="{ on }">
                  <v-text-field
                    :rules="fieldsRules"
                    v-model="startTime"
                    label="Начало"
                    prepend-icon="access_time"
                    readonly
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-time-picker
                  format="24hr"
                  v-if="startTimeMenu"
                  v-model="startTime"
                  full-width
                  @click:minute="$refs.menu.save(startTime)"
                ></v-time-picker>
              </v-menu>
              <v-menu
                ref="menu2"
                v-model="endTimeMenu"
                :close-on-content-click="false"
                :nudge-right="40"
                :return-value.sync="endTime"
                lazy
                transition="scale-transition"
                offset-y
                full-width
                max-width="290px"
                min-width="290px"
              >
                <template v-slot:activator="{ on }">
                  <v-text-field
                    :rules="fieldsRules"
                    v-model="endTime"
                    label="Окончание"
                    prepend-icon="access_time"
                    readonly
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-time-picker
                  format="24hr"
                  v-if="endTimeMenu"
                  v-model="endTime"
                  full-width
                  @click:minute="$refs.menu2.save(endTime)"
                ></v-time-picker>
              </v-menu>
            </v-flex>
          </v-layout>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="black" flat @click="modal = false">Закрыть</v-btn>
        <v-btn color="black" flat :disabled="!valid" @click="addEvent()">Сохранить</v-btn>
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
      fieldsRules: [v => !!v || "Обязательное поле"],
      nameRules: [
        v =>
          /^[^_\\\/!@#$%^&*]([a-zA-Z0-9 А-Яа-я()\-])*$/.test(v) ||
          "Некорректное название"
      ],
      eventName: "",
      date: new Date().toISOString().substr(0, 10),
      dateMenu: false,
      startTime: null,
      startTimeMenu: false,
      endTime: null,
      endTimeMenu: false
    };
  },
  computed: {
    isDarkMode() {
      return this.$store.getters.isDarkMode;
    }
  },
  methods: {
    async addEvent() {
      this.modal = false;

      await this.$store.dispatch("createMontageEvent", {
        room_name: this.room.name,
        event_name: this.eventName,
        date: this.date,
        start_time: this.startTime,
        end_time: this.endTime
      });
      this.date = new Date().toISOString().substr(0, 10);
      this.startTime = this.endTime = null;
      this.eventName = "";
    }
  }
};
</script>
