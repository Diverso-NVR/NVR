<template >
  <v-dialog
    :dark="isDarkMode"
    v-model="modal"
    :disabled="!room.free"
    fullscreen
    hide-overlay
    transition="dialog-bottom-transition"
    scrollable
  >
    <v-btn icon slot="activator" :disabled="!room.free">
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
          <template v-slot:items="props">
            <tr v-if="!isMobile">
              <td class="text-xs-center">{{ props.item.name }}</td>
              <td class="text-xs-center">{{props.item.ip}}</td>
              <td class="text-xs-center">{{props.item.sound}}</td>
              <td class="text-xs-center">{{props.item.tracking}}</td>
              <td class="text-xs-center">{{props.item.main_cam}}</td>
              <td class="text-xs-center">
                <app-edit-source :source="props.item"></app-edit-source>
                <v-btn icon @click="del(props.item)">
                  <v-icon>delete</v-icon>
                </v-btn>
              </td>
            </tr>
            <tr v-else>
              <td>
                <ul class="flex-content">
                  <li
                    class="flex-item key-elems subheading"
                    data-label="Название"
                  >{{ props.item.name }}</li>
                  <li class="flex-item key-elems subheading" data-label="IP">{{props.item.ip}}</li>
                  <li class="flex-item subheading" data-label="Источник звука">{{props.item.sound}}</li>
                  <li class="flex-item subheading" data-label="Трекинг">{{props.item.tracking}}</li>
                  <li
                    class="flex-item subheading"
                    data-label="Главная камера"
                  >{{props.item.main_cam}}</li>
                  <li class="flex-item subheading" data-label="Изменить">
                    <app-edit-source :source="props.item"></app-edit-source>
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
import EditSource from "./EditSource";
import AddSource from "./AddSource";

export default {
  props: ["room"],
  components: {
    appEditSource: EditSource,
    appAddSource: AddSource
  },
  data() {
    return {
      modal: false,
      search: "",
      isMobile: "",
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
          text: "Источник звука",
          value: "sound",
          sortable: true,
          align: "center"
        },
        { text: "Трекинг", value: "tracking", sortable: true, align: "center" },
        {
          text: "Главная камера",
          value: "main_cam",
          sortable: true,
          align: "center"
        },
        {
          text: "Изменить",
          value: "change",
          sortable: false,
          align: "center"
        }
      ],
      roomCopy: Object.assign({}, this.room)
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
    saveChanges(room) {
      this.$store
        .dispatch("editRoom", { id: room.id, sources: room.sources })
        .then(() => {
          this.modal = false;
        });
    }
  }
};
</script>
