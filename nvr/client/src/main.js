import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import Vuetify from "vuetify";
import VSwitch from "v-switch-case";

import "vuetify/dist/vuetify.min.css";
import store from "./store";

import VueSocketIOExt from "vue-socket.io-extended";
import io from "socket.io-client";

const socket = io(`http://127.0.0.1:5000/test`);

Vue.use(VueSocketIOExt, socket, { store });

Vue.use(VSwitch);
Vue.use(Vuetify);
Vue.config.productionTip = false;

new Vue({
  el: "#app",
  router,
  store,
  render: h => h(App)
});
