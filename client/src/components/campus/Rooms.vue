<template>
  <v-app>
    <v-data-table
      :headers="headers"
      :items="rooms"
      class="elevation-4"
      hide-actions
      disable-initial-sort
    >
      <template v-slot:items="props">
        <td class="text-xs-center subheading">{{ props.item.name }}</td>

        <td class="text-xs-center">
          <v-btn-toggle mandatory v-model="props.item.chosenSound">
            <v-btn
              flat
              value="enc"
              :disabled="!props.item.free"
              @click="soundSwitch(props.item, 'enc')"
            >Кодер</v-btn>
            <v-btn
              flat
              value="cam"
              :disabled="!props.item.free"
              @click="soundSwitch(props.item, 'cam')"
            >Камера</v-btn>
          </v-btn-toggle>
        </td>

        <td class="text-xs-center">
          <v-btn-toggle mandatory v-model="props.item.status">
            <v-btn
              flat
              color="green"
              value="free"
              @click="startRec(props.item)"
              :disabled="!props.item.free"
            >Старт</v-btn>
            <v-btn
              flat
              color="error"
              value="busy"
              @click="stopRec(props.item)"
              :disabled="props.item.free"
            >Стоп</v-btn>
          </v-btn-toggle>
        </td>

        <td
          class="text-xs-center body-2"
          :class="[props.item.free ? 'green lighten-4' : 'red lighten-4']"
        >
          <span class="green--text text--darken-4" v-if="props.item.free">Свободна</span>
          <span
            class="red--text text--darken-4"
            v-else-if="props.item.daemon"
          >Идёт запись по календарю</span>
          <span class="red--text text--darken-4" v-else>Идёт запись</span>
        </td>

        <td class="text-xs-center">
          <div v-if="!props.item.free">{{getTsString(props.item.timestamp)}}</div>
        </td>

        <td class="text-xs-center">
          <v-btn icon target="_blank" href="https://calendar.google.com/calendar/r">
            <v-icon>calendar_today</v-icon>
          </v-btn>
        </td>
        <td class="text-xs-center">
          <v-btn icon v-bind:href="props.item.drive" target="_blank">
            <v-icon>folder</v-icon>
          </v-btn>
        </td>
        <td class="text-xs-center" v-if="user.role === 'admin'">
          <app-edit-room :room="props.item"></app-edit-room>
          <v-btn icon @click="del(props.item)" :disabled="!props.item.free">
            <v-icon>delete</v-icon>
          </v-btn>
        </td>
      </template>
    </v-data-table>

    <v-layout row wrap class="addRoom" v-if="user.role === 'admin'">
      <v-flex xs6 sm4 md2>
        <v-text-field v-model.trim="newRoom" label="Новая аудитория" :disabled="newRoomDownload"></v-text-field>
      </v-flex>
      <v-btn
        color="black"
        class="white--text"
        @click="addRoom"
        :loading="newRoomDownload"
        :disabled="newRoomDownload"
      >Добавить</v-btn>
    </v-layout>
  </v-app>
</template>

<script>
import { mapState } from "vuex";

import EditRoom from "./EditRoom";

export default {
  data() {
    return {
      headers: [
        {
          text: "Аудитория",
          align: "center",
          sortable: true,
          value: "name"
        },
        {
          text: "Источник звука",
          value: "chosenSound",
          sortable: false,
          align: "center"
        },
        { text: "Запись", value: "record", sortable: true, align: "center" },
        { text: "Статус", value: "free", sortable: true, align: "center" },
        {
          text: "Время записи",
          value: "timestamp",
          sortable: true,
          align: "center"
        },
        {
          text: "Календарь",
          value: "calendar",
          sortable: false,
          align: "center"
        },
        { text: "Диск", value: "drive", sortable: false, align: "center" }
      ],
      newRoom: "",
      newRoomDownload: false,
      campus: "ФКМД"
    };
  },
  components: {
    appEditRoom: EditRoom
  },
  computed: mapState({
    rooms: state => state.rooms,
    user: state => state.user
  }),
  methods: {
    getTsString(seconds) {
      let h = Math.floor(seconds / 60 / 60);
      seconds -= h * 60 * 60;
      let m = Math.floor(seconds / 60);
      seconds -= m * 60;
      return `${h} ч. ${m} м. ${seconds} с.`;
    },
    soundSwitch(room, sound) {
      this.$store.dispatch("switchSound", { room, sound });
    },
    startRec(room) {
      this.$store.dispatch("startRec", { room });
    },
    stopRec(room) {
      this.$store.dispatch("stopRec", { room });
    },
    del(room) {
      confirm("Вы уверены, что хотите удалить эту аудиторию?") &&
        this.$store.dispatch("deleteRoom", { room });
    },
    addRoom() {
      if (this.newRoom === "") {
        return;
      }

      this.newRoomDownload = true;
      this.$store.dispatch("addRoom", { name: this.newRoom }).then(() => {
        this.newRoomDownload = false;
        this.newRoom = "";
      });
    }
  },
  beforeMount() {
    if (this.user.role === "admin")
      this.headers.push({
        text: "Изменить",
        value: "edit",
        sortable: false,
        align: "center"
      });
    this.$store.dispatch("loadRooms");
    if (!this.$store.getters.timer) {
      let roomsUpdateTimer = setInterval(() => {
        this.$store.dispatch("loadRooms");
      }, 3000);
      this.$store.dispatch("setTimer", roomsUpdateTimer);
    }
  }
};
</script>

<style scoped>
.addRoom {
  margin-top: 15px;
}
</style>
