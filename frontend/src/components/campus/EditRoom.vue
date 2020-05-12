<template >
  <v-dialog
    :dark="isDarkMode"
    v-model="modal"
    fullscreen
    hide-overlay
    transition="dialog-bottom-transition"
    scrollable
  >
    <v-btn icon slot="activator">
      <v-icon medium>edit</v-icon>
    </v-btn>

    <v-card tile>
      <v-toolbar card dark color="black">
        <v-btn icon dark @click="modal = false">
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>{{room.name}}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
          <v-btn dark flat @click="saveChanges(roomCopy)">Сохранить</v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card-text>
        <v-spacer></v-spacer>
        <v-text-field v-model="search" append-icon="search" label="Поиск" single-line hide-details></v-text-field>
      </v-card-text>
      <v-layout v-resize="onResize" column>
        <v-data-table
          :headers="headers"
          :items="roomCopy.sources"
          :search="search"
          :hide-headers="isMobile"
          :class="{mobile: isMobile}"
          hide-actions
          class="elevation-4"
          disable-initial-sort
        >
          <template v-slot:items="props" justify="space-around">
            <tr v-if="!isMobile">
              <td class="text-xs-center">
                <v-text-field class="body-1" v-model.trim="props.item.name"></v-text-field>
              </td>
              <td class="text-xs-center">
                <v-text-field class="body-1" v-model.trim="props.item.ip"></v-text-field>
              </td>
              <td class="text-xs-center">
                <v-text-field class="body-1" v-model.trim="props.item.rtsp"></v-text-field>
              </td>
              <td>
                <v-radio-group class="v-c" v-model="soundSource">
                  <v-radio :value="props.item.ip"></v-radio>
                </v-radio-group>
              </td>
              <td>
                <v-radio-group class="v-c" v-model="trackingSource">
                  <v-radio :value="props.item.ip"></v-radio>
                </v-radio-group>
              </td>
              <td>
                <v-radio-group class="v-c" v-model="mainSource">
                  <v-radio :value="props.item.ip"></v-radio>
                </v-radio-group>
              </td>
              <td>
                <v-radio-group class="v-c" v-model="screenSource">
                  <v-radio :value="props.item.ip"></v-radio>
                </v-radio-group>
              </td>

              <td class="text-xs-center">
                <v-btn icon @click="del(props.item)">
                  <v-icon>delete</v-icon>
                </v-btn>
              </td>
            </tr>
            <tr v-else>
              <td>
                <ul class="flex-content">
                  <li class="flex-item key-elems subheading" data-label="Название">
                    <v-text-field class="body-1" v-model.trim="props.item.name"></v-text-field>
                  </li>
                  <li class="flex-item key-elems subheading" data-label="IP">
                    <v-text-field class="body-1" v-model.trim="props.item.ip"></v-text-field>
                  </li>
                  <li class="flex-item key-elems subheading" data-label="RTSP">
                    <v-text-field class="body-1" v-model.trim="props.item.rtsp"></v-text-field>
                  </li>
                  <li class="flex-item subheading" data-label="Звук">
                    <v-radio-group class="v-c" v-model="soundSource">
                      <v-radio :value="props.item.ip"></v-radio>
                    </v-radio-group>
                  </li>
                  <li class="flex-item subheading" data-label="Трекинг">
                    <v-radio-group class="v-c" v-model="trackingSource">
                      <v-radio :value="props.item.ip"></v-radio>
                    </v-radio-group>
                  </li>
                  <li class="flex-item subheading" data-label="Главная камера">
                    <v-radio-group class="v-c" v-model="mainSource">
                      <v-radio :value="props.item.ip"></v-radio>
                    </v-radio-group>
                  </li>
                  <li class="flex-item subheading" data-label="Экран">
                    <v-radio-group class="v-c" v-model="screenSource">
                      <v-radio :value="props.item.ip"></v-radio>
                    </v-radio-group>
                  </li>
                  <li class="flex-item subheading" data-label="Удалить">
                    <v-btn icon @click="del(props.item)">
                      <v-icon medium>delete</v-icon>
                    </v-btn>
                  </li>
                </ul>
              </td>
            </tr>
          </template>
          <template v-slot:no-results>
            <v-alert
              :value="true"
              color="error"
              icon="warning"
            >Ничего не найдено по запросу "{{ search }}".</v-alert>
          </template>
        </v-data-table>
        <app-add-source :room="roomCopy"></app-add-source>
      </v-layout>
    </v-card>
  </v-dialog>
</template>

<script>
import AddSource from "./AddSource";

export default {
  props: ["room"],
  components: {
    appAddSource: AddSource
  },
  data() {
    return {
      modal: false,
      search: "",
      isMobile: "",
      soundSource: this.room.sound_source,
      trackingSource: this.room.tracking_source,
      mainSource: this.room.main_source,
      screenSource: this.room.screen_source,
      headers: [
        {
          text: "Название",
          align: "center",
          sortable: true,
          value: "name"
        },
        {
          text: "IP",
          value: "ip",
          sortable: true,
          align: "center"
        },
        {
          text: "RTSP",
          value: "rtsp",
          sortable: true,
          align: "center"
        },
        {
          text: "Звук",
          value: "sound",
          sortable: true,
          align: "center"
        },
        {
          text: "Трекинг",
          value: "tracking",
          sortable: true,
          align: "center"
        },
        {
          text: "Главная камера",
          value: "main_cam",
          sortable: true,
          align: "center"
        },
        {
          text: "Экран",
          value: "screen",
          sortable: true,
          align: "center"
        },
        {
          text: "Удалить",
          value: "change",
          sortable: false,
          align: "center"
        }
      ]
    };
  },
  computed: {
    isDarkMode() {
      return this.$store.getters.isDarkMode;
    }
  },
  methods: {
    onResize() {
      this.isMobile = window.innerWidth < 769;
    },
    del(camera) {
      let i = this.roomCopy.sources.indexOf(camera);
      confirm("Вы уверены, что хотите удалить этот источник записи?") &&
        this.roomCopy.sources.splice(i, 1);
    },
    saveChanges(roomCopy) {
      this.$store
        .dispatch("emitEditRoom", {
          id: roomCopy.id,
          sources: roomCopy.sources,
          sound_source: this.soundSource,
          tracking_source: this.trackingSource,
          main_source: this.mainSource,
          screen_source: this.screenSource
        })
        .then(() => {
          this.modal = false;
        });
    }
  },
  created() {
    this.roomCopy = { ...this.room };
    this.soundSource = this.room.sound_source;
    this.trackingSource = this.room.tracking_source;
    this.mainSource = this.room.main_source;
    this.screenSource = this.room.screen_source;
  }
};
</script>

<style scoped>
.v-c {
  width: 30px;
  height: 30px;
  margin-left: 45%;
  margin-top: 5%;
  padding: auto;
}
</style>
