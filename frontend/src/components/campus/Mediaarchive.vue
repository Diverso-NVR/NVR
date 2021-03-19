<template>
  <v-layout align-center justify-center>
    <v-flex xs12 sm8 md6>
      <v-layout row wrap>
        <v-flex xs5>
          <v-text-field
            append-icon="search"
            label="Search"
            single-line
            hide-details
            v-model="search"
          ></v-text-field>
        </v-flex>
      </v-layout>
      <v-data-table
        :items="records"
        class="elevation-4 mt-2"
        disable-initial-sort
        hide-actions
        :headers="headers"
        :search="search"
      >
        <template v-slot:headers>
          <tr>
            <th>Название</th>
            <th>Дата</th>
            <th>Ключевые слова</th>
          </tr>
        </template>

        <template v-slot:items="props">
          <td class="text-xs-center subheading">
            <v-layout align-center justify-center row fill-height>
              <a :href="props.item.url" target="_blank"
                ><img :src="props.item.thumbnailUrl"
              /></a>

              <span class="pl-3" v-html="props.item.name"></span>
            </v-layout>
          </td>
          <td class="text-xs-center">
            {{ dateFormat(props.item.date + " " + props.item.start_time) }}
          </td>
          <td class="text-xs-center">
            <v-dialog
              v-model="props.item.showKeywords"
              width="600px"
              :dark="isDarkMode"
            >
              <template v-slot:activator="{ on }">
                <v-btn color="primary" depressed v-on="on">Открыть</v-btn>
              </template>
              <v-card>
                <v-card-title>
                  <span class="headline">Ключевые слова</span>
                </v-card-title>
                <v-card-text>{{ props.item.keywords.join(", ") }}</v-card-text>
              </v-card>
            </v-dialog>
          </td>
          <td class="text-xs-center" style="display: none">
            {{ props.item.keywords.join(" ") }}
          </td>
        </template>
        <template v-slot:no-data>
          <v-alert :value="true" color="primary" icon="info">
            Список записей пуст
          </v-alert>
        </template>
      </v-data-table>
    </v-flex>
  </v-layout>
</template>

<script>
import { mapState } from "vuex";

export default {
  data() {
    return {
      headers: [
        { text: "Название", align: "left", sortable: true, value: "name" },
        { text: "Дата", align: "center", sortable: true, value: "date" },
        {
          text: "Ключевые слова",
          align: "center",
          sortable: false,
          value: "keywords",
        },
      ],
      options: {
        year: "numeric",
        month: "numeric",
        day: "numeric",
        hour: "numeric",
        minute: "numeric",
      },
      search: "",
    };
  },
  computed: mapState({
    records: (state) => state.records.eruditeRecords,
    isDarkMode() {
      return this.$store.getters.isDarkMode;
    },
  }),
  methods: {
    dateFormat(date) {
      let ts = Date.parse(date.replace(/-/g, "/"));
      let formattedDate = new Date(ts);
      return formattedDate.toLocaleString("ru", this.options);
    },
  },
  beforeMount() {
    this.records.forEach((record) => {
      record.showKeywords = false;
      if (record.url.includes("youtube")) {
        let arrayOfStrings = record.url.split("=");
        let record_id = arrayOfStrings[arrayOfStrings.length - 1];
        record.thumbnailUrl = `https://img.youtube.com/vi/${record_id}/default.jpg`;
      } else if (record.url.includes("drive")) {
        let arrayOfStrings = record.url.split("/");
        let record_id = arrayOfStrings[arrayOfStrings.length - 2];
        record.thumbnailUrl = `https://drive.google.com/thumbnail?authuser=0&sz=w75&id=${record_id}`;
      } else {
        record.thumbnailUrl = "../../static/logo.png";
      }
    });
  },
};
</script>
