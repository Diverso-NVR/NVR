<template>
  <v-app>
    <div class="d-flex justify-between align-right mb-3">
      <v-btn @click="all" flat>
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
  </v-app>
</template>

<script>
export default {
  data() {
    return {
      panel: [],
      urls: [
        { name: "/startRec", doc: "start rec" },
        { name: "/stopRec", doc: "stop rec" },
        { name: "/sound", doc: "switches sound" }
      ]
    };
  },
  methods: {
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