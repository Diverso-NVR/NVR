import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import Vuetify from "vuetify";
import VSwitch from "v-switch-case";

import "vuetify/dist/vuetify.min.css";
import store from "./store";

Vue.use(VSwitch);
Vue.use(Vuetify);
Vue.config.productionTip = false;

new Vue({
  el: "#app",
  router,
  store,
  render: h => h(App)
});
