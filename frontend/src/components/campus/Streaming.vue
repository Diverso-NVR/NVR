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
              <v-select dense class="body-1" :items="props.item.ips" v-model="props.item.defCod"></v-select>
            </td>

            <td class="text-xs-center">
              <v-select dense class="body-1" :items="props.item.ips" v-model="props.item.defCam"></v-select>
            </td>

            <td>
              <v-text-field v-model.trim="props.item.streamName"></v-text-field>
            </td>

            <td class="text-xs-center">
              <div>
                <v-btn
                  depressed
                  color="success"
                  :disabled="props.item.stream_url !== null"
                  @click="startStream(props.item)"
                >Старт</v-btn>
                <v-btn
                  depressed
                  color="error"
                  :disabled="!props.item.stream_url"
                  @click="stopStream(props.item)"
                >Стоп</v-btn>
              </div>
            </td>

            <td class="text-xs-center">
              <v-btn
                icon
                target="_blank"
                :disabled="!props.item.stream_url"
                :href="props.item.stream_url"
              >
                <v-icon>link</v-icon>
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

                <li class="flex-item subheading key-elems" data-label="Источник звука">
                  <v-select
                    dense
                    class="body-1 ml-8"
                    :items="props.item.ips"
                    v-model="props.item.defCod"
                  ></v-select>
                </li>

                <li class="flex-item subheading key-elems" data-label="Камера">
                  <v-select
                    dense
                    class="body-1 ml-8"
                    :items="props.item.ips"
                    v-model="props.item.defCam"
                  ></v-select>
                </li>

                <li class="flex-item subheading key-elems" data-label="Название стрима">
                  <v-text-field v-model.trim="props.item.streamName"></v-text-field>
                </li>

                <li class="flex-item subheading key-elems" data-label="Стрим">
                  <div>
                    <v-btn
                      depressed
                      color="success"
                      :disabled="props.item.stream_url !== null"
                      @click="startStream(props.item)"
                    >Старт</v-btn>
                    <v-btn
                      depressed
                      color="error"
                      :disabled="!props.item.stream_url"
                      @click="stopStream(props.item)"
                    >Стоп</v-btn>
                  </div>
                </li>

                <li class="flex-item subheading key-elems" data-label="Ссылка">
                  <v-btn
                    icon
                    target="_blank"
                    :disabled="!props.item.stream_url"
                    :href="props.item.stream_url"
                  >
                    <v-icon>link</v-icon>
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
        {
          text: "Источник звука",
          value: "chosen_sound",
          sortable: false,
          align: "center"
        },
        { text: "Камера", value: "tracking", sortable: true, align: "center" },
        {
          text: "Название стрима",
          value: "streamName",
          sortable: true,
          align: "center"
        },
        { text: "Стрим", value: "record", sortable: true, align: "center" },
        { text: "Ссылка", value: "url", sortable: true, align: "center" }
      ],
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
    startStream(room) {
      this.$store.dispatch("emitStreamingStart", {
        soundIp: room.defCod,
        cameraIp: room.defCam,
        roomName: room.name,
        title: room.streamName
      });
    },
    stopStream(room) {
      this.$store.dispatch("emitStreamingStop", {
        roomName: room.name
      });
    },
    config() {
      this.rooms.forEach(element => {
        element.ips = element.sources.map(el => {
          return el.ip;
        });
        element.defCod = element.sound_source;
        element.defCam = element.main_source;
      });
    }
  },
  beforeUpdate() {
    this.config();
  },
  created() {
    this.config();
  }
};
</script>

<style>
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
  .v-select__selection.v-select__selection--comma {
    margin-left: 30px;
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
.v-select__selection {
  padding-left: 30%;
}
</style>
