<template>
  <v-app>
    <v-layout v-resize="onResize" column>
      <v-data-table
        :headers="headers"
        :items="rooms"
        class="elevation-4"
        :hide-headers="isMobile"
        :class="{mobile: isMobile}"
        hide-actions
        disable-initial-sort
        :loading="loader"
      >
        <template v-slot:items="props">
          <tr v-if="!isMobile">
            <td class="text-xs-center subheading">{{ props.item.name }}</td>

            <td class="text-xs-center">
              <v-btn-toggle mandatory v-model="props.item.chosen_sound">
                <v-btn
                  depressed
                  value="enc"
                  :disabled="!props.item.free"
                  @click="soundSwitch(props.item, 'enc')"
                >Кодер</v-btn>
                <v-btn
                  depressed
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
              :class="background[props.item.status]"
              v-switch="props.item.status"
            >
              <span class="green--text text--darken-4" v-case="'free'">Свободна</span>
              <span class="red--text text--darken-4" v-case="'busy'">Идёт запись</span>
            </td>

            <td class="text-xs-center">
              <div v-if="props.item.status === 'busy'">{{getTsString(props.item.timestamp)}}</div>
            </td>

            <td class="text-xs-center">
              <v-btn icon target="_blank" href="https://calendar.google.com/calendar/r">
                <v-icon>calendar_today</v-icon>
              </v-btn>
            </td>
            <td class="text-xs-center">
              <v-btn icon :href="props.item.drive" target="_blank">
                <v-icon>folder</v-icon>
              </v-btn>
            </td>
            <td class="text-xs-center" v-if="/^\w*admin$/.test(user.role)">
              <app-edit-room :room="props.item"></app-edit-room>
              <v-btn icon @click="del(props.item)" :disabled="!props.item.free">
                <v-icon>delete</v-icon>
              </v-btn>
            </td>
          </tr>
          <tr v-else>
            <td>
              <ul class="flex-content">
                <li
                  class="flex-item subheading key-elems"
                  data-label="Аудитория"
                >{{ props.item.name }}</li>
                <li class="flex-item subheading" data-label="Запись">
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
                </li>
                <li class="flex-item subheading" data-label="Источник звука">
                  <v-btn-toggle mandatory v-model="props.item.chosen_sound">
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
                </li>

                <li class="flex-item subheading" data-label="Статус" v-switch="props.item.status">
                  <span class="green--text text--darken-4" v-case="'free'">Свободна</span>
                  <span class="red--text text--darken-4" v-case="'busy'">Идёт запись</span>
                </li>
                <li class="flex-item subheading" data-label="Время записи">
                  <div v-if="props.item.status === 'busy'">{{getTsString(props.item.timestamp)}}</div>
                </li>
                <li class="flex-item subheading" data-label="Календарь">
                  <v-btn icon target="_blank" href="https://calendar.google.com/calendar/r">
                    <v-icon medium>calendar_today</v-icon>
                  </v-btn>
                </li>
                <li class="flex-item subheading" data-label="Диск">
                  <v-btn icon :href="props.item.drive" target="_blank">
                    <v-icon medium>folder</v-icon>
                  </v-btn>
                </li>

                <li
                  class="flex-item subheading key-elems"
                  v-if="/^\w*admin$/.test(user.role)"
                  data-label="Изменить"
                >
                  <app-edit-room :room="props.item"></app-edit-room>
                  <v-btn icon @click="del(props.item)" :disabled="!props.item.free">
                    <v-icon medium>delete</v-icon>
                  </v-btn>
                </li>
              </ul>
            </td>
          </tr>
        </template>
      </v-data-table>
      <template v-if="loader && isMobile">
        <v-progress-linear :indeterminate="true"></v-progress-linear>
      </template>
      <v-layout row wrap class="addRoom" v-if="user.role !== 'user'">
        <v-flex xs6 sm4 md2>
          <v-text-field v-model.trim="newRoom" label="Новая аудитория" :loading="newRoomLoader"></v-text-field>
        </v-flex>
        <v-btn
          dark
          depressed
          @click="addRoom"
          :loading="newRoomLoader"
          :disabled="newRoomLoader"
        >Добавить</v-btn>
      </v-layout>
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
          value: "chosen_sound",
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
      background: {
        free: "green lighten-3",
        busy: "red lighten-3"
      },
      newRoomLoader: false,
      isMobile: false
    };
  },
  components: {
    appEditRoom: EditRoom
  },
  computed: mapState({
    rooms: state => state.rooms,
    user: state => state.user,
    loader() {
      return this.$store.getters.loading;
    }
  }),
  methods: {
    onResize() {
      this.isMobile = window.innerWidth < 769;
    },
    getTsString(seconds) {
      let h = Math.floor(seconds / 60 / 60);
      seconds -= h * 60 * 60;
      let m = Math.floor(seconds / 60);
      seconds -= m * 60;
      return `${h} ч. ${m} м. ${seconds} с.`;
    },
    soundSwitch(room, sound) {
      this.$store.dispatch("emitSoundChange", { room, sound });
    },
    startRec(room) {
      this.$store.dispatch("emitStartRec", { room });
    },
    stopRec(room) {
      this.$store.dispatch("emitStopRec", { room });
    },
    del(room) {
      confirm("Вы уверены, что хотите удалить эту аудиторию?") &&
        this.$store.dispatch("emitDeleteRoom", { room });
    },
    async addRoom() {
      if (this.newRoom === "") {
        return;
      }
      this.newRoomLoader = true;
      this.$store.dispatch("emitAddRoom", { name: this.newRoom });
      this.newRoom = "";
      this.newRoomLoader = false;
    }
  },
  beforeMount() {
    if (this.user.role !== "user")
      this.headers.push({
        text: "Изменить",
        value: "edit",
        sortable: false,
        align: "center"
      });
  }
};
</script>

<style>
.addRoom {
  margin-top: 15px;
}
.mobile {
  color: #333;
}

@media screen and (max-width: 768px) {
  .mobile table.v-table tr {
    max-width: 100%;
    position: relative;
    display: block;
  }

  .mobile table.v-table tr:nth-child(odd) {
    border-left: 6px solid;
  }

  .mobile table.v-table tr:nth-child(even) {
    border-left: 6px solid;
  }

  .mobile table.v-table tr td {
    display: flex;
    width: 100%;
    border-bottom: 1px solid black;
    height: auto;
    padding: 10px;
  }

  .mobile table.v-table tr td ul li:before {
    content: attr(data-label);
    padding-right: 0.5em;
    text-align: center;
    display: block;
    color: #999999;
  }
  .v-datatable__actions__select {
    width: 50%;
    margin: 0px;
    justify-content: flex-start;
  }
  .mobile .theme--light.v-table tbody tr:hover:not(.v-datatable__expand-row) {
    background: transparent;
  }
}
.flex-content {
  padding: 0;
  margin: 0;
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  width: 100%;
}

.flex-item {
  padding: auto;
  text-align: center;
  width: 50%;
  height: 75px;
  font-weight: bold;
}
.key-elems {
  width: 100%;
}
</style>
