<template>
  <v-app>
    <template v-if="!user.api_key">
      <v-card>
        <v-card-text>
          <v-layout align-center mb-3>
            <strong class="title">Ключ API</strong>
            <v-spacer></v-spacer>
            <v-btn icon>
              <v-icon>mdi-account</v-icon>
            </v-btn>
          </v-layout>
          <p>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit,
            sed do eiusmod tempor incididuntut labore et dolore magna aliqua.
            Ut enim ad minim veniam,
            quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
            Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
            Excepteur sint occaecat cupidatat non proident,
            sunt in culpa qui officia deserunt mollit anim id est laborum.
          </p>
        </v-card-text>
      </v-card>

      <v-btn @click="createKey" depressed color="info">Создать ключ API</v-btn>
    </template>

    <template v-else>
      <v-card>
        <v-card-title primary-title>
          <h3 class="title mb-0">
            Ваш ключ API:
            <b>{{ user.api_key }}</b>
          </h3>
        </v-card-title>

        <v-card-actions>
          <v-btn depressed color="warning" @click="updateKey">Обновить</v-btn>
          <v-btn depressed color="error" @click="deleteKey">Удалить</v-btn>
        </v-card-actions>
      </v-card>

      <div style="text-align:right">
        <v-btn @click="all" icon>
          <v-icon>list</v-icon>
        </v-btn>
      </div>
      <v-expansion-panel expand v-model="panel">
        <v-expansion-panel-content v-for="(url,i) in urls" :key="i">
          <template v-slot:header>
            <div>{{url.name}}</div>
          </template>
          <v-card>
            <v-card-text>{{url.doc}}</v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </template>
  </v-app>
</template>

<script>
import { mapState } from "vuex";
export default {
  data() {
    return {
      panel: [],
      urls: [
        {
          name: "/rooms/",
          methods: ["GET", "POST", "DELETE", "PUT"],
          doc: "_"
        },
        { name: "/start-record", methods: ["POST"], doc: "start record" },
        { name: "/stop-record", methods: ["POST"], doc: "stop record" },
        { name: "/sound-change", methods: ["POST"], doc: "switches sound" }
      ]
    };
  },
  computed: {
    user() {
      return this.$store.getters.user;
    }
  },
  methods: {
    createKey() {
      this.$store.dispatch("createKey");
    },
    updateKey() {
      this.$store.dispatch("updateKey");
    },
    deleteKey() {
      this.$store.dispatch("deleteKey");
    },
    all() {
      this.panel =
        this.panel.length !== this.urls.length
          ? [...Array(this.urls.length).keys()].map(_ => true)
          : [];
    }
  }
};
</script>

<style scoped>
</style>