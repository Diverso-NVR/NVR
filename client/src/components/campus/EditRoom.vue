<template >
  <v-dialog
    v-model="modal"
    :disabled="!room.free"
    fullscreen
    hide-overlay
    transition="dialog-bottom-transition"
    scrollable
  >
    <v-btn icon slot="activator" :disabled="!room.free">
      <v-icon>edit</v-icon>
    </v-btn>

    <v-card tile>
      <v-toolbar card dark color="black">
        <v-btn icon dark @click="modal = false">
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>{{room.name}}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
          <v-btn dark flat @click="saveChanges(room)">Сохранить</v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card-text>
        <v-spacer></v-spacer>
        <v-text-field v-model="search" append-icon="search" label="Поиск" single-line hide-details></v-text-field>
      </v-card-text>
      <v-data-table
        :headers="headers"
        :items="room.sources"
        :search="search"
        hide-actions
        class="elevation-4"
        disable-initial-sort
      >
        <template v-slot:items="props">
          <td class="text-xs-center">{{ props.item.name }}</td>
          <td class="text-xs-center">{{props.item.ip}}</td>
          <td class="text-xs-center">{{props.item.sound}}</td>
          <td class="text-xs-center">{{props.item.tracking}}</td>
          <td class="text-xs-center">{{props.item.mainCam}}</td>
          <td class="text-xs-center">
            <app-edit-source :source="props.item"></app-edit-source>
            <v-btn icon @click="del(props.item)">
              <v-icon>delete</v-icon>
            </v-btn>
          </td>
        </template>
        <template v-slot:no-results>
          <v-alert
            :value="true"
            color="error"
            icon="warning"
          >Ничего не найдено по запросу "{{ search }}".</v-alert>
        </template>
      </v-data-table>
      <app-add-source :room="room"></app-add-source>
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
      ]
    };
  },
  methods: {
    del(camera) {
      let i = this.room.sources.indexOf(camera);
      confirm("Вы уверены, что хотите удалить этот источник записи?") &&
        this.room.sources.splice(i, 1);
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
