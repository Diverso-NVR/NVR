import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import Vuetify from "vuetify";
import VSwitch from "v-switch-case";

import "vuetify/dist/vuetify.min.css";
import store from "./store";
import { isAdmin, isAdminOrEditor } from "@/utils";

import VueSocketIOExt from "vue-socket.io-extended";
import io from "socket.io-client";

const SOCKET_URL = `${process.env.NVR_URL}/websocket`;
const socket = io(SOCKET_URL);
Vue.use(VueSocketIOExt, socket, { store });

Vue.use(VSwitch);
Vue.use(Vuetify);
Vue.config.productionTip = false;

if (store.getters.isAutheticated) {
  store.dispatch("setDataFromToken").then(userRole => {
    store.dispatch("loadRooms");
    store.dispatch("loadRecords");
    if (isAdmin()) {
      store.dispatch("getUsers");
    }
    if (isAdminOrEditor()) {
      store.dispatch("getKey");
    }
  });
}

new Vue({
  el: "#app",
  router,
  store,
  render: h => h(App)
});
