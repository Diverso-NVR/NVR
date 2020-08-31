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
              <app-add-event :room="props.item"></app-add-event>
            </td>

            <td class="text-xs-center">
              <v-btn icon target="_blank" href="https://calendar.google.com/calendar/r">
                <v-icon>calendar_today</v-icon>
              </v-btn>
            </td>
            <td class="text-xs-center">
              <v-btn icon :href="props.item.drive" target="_blank" :loading="!props.item.drive">
                <v-icon>folder</v-icon>
              </v-btn>
            </td>
            <td class="text-xs-center" v-if="isAdminOrEditor">
              <v-layout row wrap justify-center>
                <v-flex xs12 md2>
                  <div class="text-xs-center">
                    <v-switch
                      v-model="props.item.tracking_state"
                      class="switch-center"
                      @change="trackingSwitch(props.item)"
                      color="primary"
                      hide-details
                    ></v-switch>
                  </div>
                </v-flex>
              </v-layout>
            </td>

            <td class="text-xs-center" v-if="isAdminOrEditor">
              <v-layout row wrap justify-center>
                <v-flex xs12 md2>
                  <div class="text-xs-center">
                    <v-switch
                      v-model="props.item.auto_control"
                      class="switch-center"
                      @change="autoControlSwitch(props.item)"
                      color="primary"
                      hide-details
                    ></v-switch>
                  </div>
                </v-flex>
              </v-layout>
            </td>

            <td class="text-xs-center" v-if="isAdminOrEditor">
              <app-edit-room :room="props.item"></app-edit-room>
              <v-btn icon @click="del(props.item)">
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

                <li class="flex-item subheading" data-label="Календарь">
                  <v-btn icon target="_blank" href="https://calendar.google.com/calendar/r">
                    <v-icon medium>calendar_today</v-icon>
                  </v-btn>
                </li>

                <li class="flex-item subheading" data-label="Диск">
                  <v-btn icon :href="props.item.drive" target="_blank" :loading="!props.item.drive">
                    <v-icon medium>folder</v-icon>
                  </v-btn>
                </li>

                <li class="flex-item subheading key-elems" data-label="Запись">
                  <app-add-event :room="props.item"></app-add-event>
                </li>

                <li class="flex-item subheading" v-if="isAdminOrEditor" data-label="Трекинг">
                  <v-layout row wrap justify-center>
                    <v-flex xs12 md2>
                      <div class="text-xs-center">
                        <v-switch
                          v-model="props.item.tracking_state"
                          class="switch-center"
                          @change="trackingSwitch(props.item)"
                          color="primary"
                          hide-details
                        ></v-switch>
                      </div>
                    </v-flex>
                  </v-layout>
                </li>

                <li class="flex-item subheading" v-if="isAdminOrEditor" data-label="Автоуправление">
                  <v-layout row wrap justify-center>
                    <v-flex xs12 md2>
                      <div class="text-xs-center">
                        <v-switch
                          v-model="props.item.auto_control"
                          class="switch-center"
                          @change="autoControlSwitch(props.item)"
                          color="primary"
                          hide-details
                        ></v-switch>
                      </div>
                    </v-flex>
                  </v-layout>
                </li>

                <li
                  class="flex-item subheading key-elems"
                  v-if="isAdminOrEditor"
                  data-label="Изменить"
                >
                  <app-edit-room :room="props.item"></app-edit-room>
                  <v-btn icon @click="del(props.item)">
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
      <v-layout row wrap class="addRoom" v-if="isAdminOrEditor">
        <v-flex xs6 sm4 md2>
          <v-text-field v-model.trim="newRoom" label="Новая аудитория"></v-text-field>
        </v-flex>
        <v-btn dark depressed @click="addRoom">Добавить</v-btn>
      </v-layout>
    </v-layout>
  </v-app>
</template>

<script>
import { mapState } from "vuex";
import { isAdmin, isAdminOrEditor } from "@/utils";

import EditRoom from "./EditRoom";
import AddEvent from "./AddEvent";

export default {
  data() {
    return {
      headers: [
        {
          text: "Аудитория",
          align: "center",
          sortable: true,
          value: "name",
        },
        {
          text: "Запись",
          value: "auto_control",
          sortable: true,
          align: "center",
        },
        {
          text: "Календарь",
          value: "calendar",
          sortable: false,
          align: "center",
        },
        {
          text: "Диск",
          value: "drive",
          sortable: false,
          align: "center",
        },
      ],
      newRoom: "",
      background: {
        free: "green lighten-3",
        busy: "red lighten-3",
      },
      isMobile: false,
    };
  },
  components: {
    appEditRoom: EditRoom,
    appAddEvent: AddEvent,
  },
  computed: mapState({
    rooms: (state) => state.rooms,
    user: (state) => state.user,
    loader() {
      return this.$store.getters.loading;
    },
    isAdmin() {
      return isAdmin();
    },
    isAdminOrEditor() {
      return isAdminOrEditor();
    },
  }),
  methods: {
    onResize() {
      this.isMobile = window.innerWidth < 769;
    },
    trackingSwitch(room) {
      this.$store.dispatch("emitTrackingStateChange", {
        room,
        tracking_state: room.tracking_state,
      });
    },
    autoControlSwitch(room) {
      this.$store.dispatch("emitAutoControlChange", {
        room,
        auto_control: room.auto_control,
      });
    },
    del(room) {
      confirm("Вы уверены, что хотите удалить эту аудиторию?") &&
        this.$store.dispatch("emitDeleteRoom", { room });
    },
    async addRoom() {
      if (this.newRoom === "") {
        return;
      }
      await this.$store.dispatch("emitAddRoom", { name: this.newRoom });
      this.newRoom = "";
    },
  },
  beforeMount() {
    if (this.isAdminOrEditor)
      this.headers.push(
        {
          text: "Трекинг",
          value: "montage",
          sortable: true,
          align: "center",
        },
        {
          text: "Автоуправление",
          value: "tracking",
          sortable: true,
          align: "center",
        },
        {
          text: "Изменить",
          value: "edit",
          sortable: false,
          align: "center",
        }
      );
  },
};
</script>

<style>
.addRoom {
  margin-top: 15px;
}

.switch-center {
  display: flex;
  justify-content: center;
}

.v-datatable thead th.column.sortable {
  padding-left: 8px;
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
  margin: 5px 0;
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
