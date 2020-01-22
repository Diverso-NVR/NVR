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
              <v-btn-toggle mandatory v-model="props.item.status">
                <v-btn flat color="green" value="free" @click="startStream(props.item)">Старт</v-btn>
                <v-btn flat color="error" value="busy" @click="stopStream(props.item)">Стоп</v-btn>
              </v-btn-toggle>
            </td>

            <td
              class="text-xs-center body-2"
              :class="background[props.item.status]"
              v-switch="props.item.status"
            >
              <span class="green--text text--darken-4" v-case="'free'">Свободна</span>
              <span class="red--text text--darken-4" v-case="'busy'">Идёт стрим</span>
            </td>
            <td class="text-xs-center">
              <v-select dense class="caption" :items="props.item.ips" v-model="props.item.defCod"></v-select>
            </td>

            <td class="text-xs-center">
              <v-select dense class="caption" :items="props.item.ips" v-model="props.item.defCam"></v-select>
            </td>

            <td class="text-xs-center url">
              <v-text-field class="caption" v-model="props.item.url"></v-text-field>
            </td>
          </tr>
          <tr v-else>
            <td>
              <ul class="flex-content">
                <li
                  class="flex-item subheading key-elems"
                  data-label="Аудитория"
                >{{ props.item.name }}</li>

                <li class="flex-item subheading" data-label="Стрим">
                  <v-btn-toggle mandatory v-model="props.item.status">
                    <v-btn
                      flat
                      color="green"
                      value="free"
                      @click="startStream(props.item)"
                      :disabled="!props.item.free"
                    >Старт</v-btn>
                    <v-btn
                      flat
                      color="error"
                      value="busy"
                      @click="stopStream(props.item)"
                      :disabled="props.item.free"
                    >Стоп</v-btn>
                  </v-btn-toggle>
                </li>

                <li class="flex-item subheading" data-label="Статус" v-switch="props.item.status">
                  <span class="green--text text--darken-4" v-case="'free'">Свободна</span>
                  <span class="red--text text--darken-4" v-case="'busy'">Идёт стрим</span>
                </li>

                <li class="flex-item subheading" data-label="Источник звука">
                  <v-select
                    dense
                    class="caption"
                    :items="props.item.ips"
                    v-model="props.item.defCod"
                  ></v-select>
                </li>
                <li class="flex-item subheading" data-label="Камера">
                  <v-select
                    dense
                    class="caption"
                    :items="props.item.ips"
                    v-model="props.item.defCam"
                  ></v-select>
                </li>
                <li class="flex-item subheading key-elems" data-label="Ссылка">
                  <v-text-field class="caption" v-model="props.item.url"></v-text-field>
                </li>
              </ul>
            </td>
          </tr>
        </template>
      </v-data-table>
      <template v-if="loader && isMobile">
        <v-progress-linear :indeterminate="true"></v-progress-linear>
      </template>
    </v-layout>
  </v-app>
</template>

<script>
import { mapState } from "vuex";
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
        { text: "Стрим", value: "record", sortable: true, align: "center" },
        { text: "Статус", value: "free", sortable: true, align: "center" },
        {
          text: "Источник звука",
          value: "chosen_sound",
          sortable: false,
          align: "center"
        },
        { text: "Камера", value: "tracking", sortable: true, align: "center" },
        { text: "Ссылка", value: "record", sortable: true, align: "center" }
      ],
      newRoom: "",
      background: {
        free: "green lighten-3",
        busy: "red lighten-3"
      },
      isMobile: false
    };
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
    stopStream(room) {
      this.$store.dispatch("emitStreamingStop", {
        pid: room.url
      });
    },
    startStream(room) {
      this.$store.dispatch("emitStreamingStart", {
        soundIp: room.defCod,
        cameraIp: room.defCam,
        ytUrl: room.url
      });
    }
  },
  beforeMount() {
    this.rooms.forEach(element => {
      element.ips = element.sources.map(el => {
        return el.ip;
      });
      element.defCod = element.sound_source;
      element.defCam = element.main_source;
      element.url = "";
    });
  }
};
</script>

<style>
.url {
  width: 120%;
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