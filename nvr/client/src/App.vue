<template>
  <v-app :dark="isDarkMode">
    <v-navigation-drawer app temporary v-model="drawer" dark color="black">
      <v-list>
        <v-list-tile v-for="link of links" :key="link.title" :to="link.url">
          <v-list-tile-action>
            <v-icon>{{link.icon}}</v-icon>
          </v-list-tile-action>

          <v-list-tile-content>
            <v-list-tile-title>{{link.title}}</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
        <v-list-tile @click="onLogout" v-if="isUserLoggedIn">
          <v-list-tile-action>
            <v-icon>exit_to_app</v-icon>
          </v-list-tile-action>

          <v-list-tile-content>
            <v-list-tile-title>Выход</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
      </v-list>
    </v-navigation-drawer>

    <v-toolbar dark color="black" fixed>
      <v-toolbar-side-icon @click.prevent="drawer = !drawer" class="hidden-md-and-up"></v-toolbar-side-icon>
      <v-toolbar-title>
        <v-btn
          flat
          class="subheading font-weight-bold"
          large
          href="http://nvr.auditory.ru"
          target="_blank"
        >Сетевой видеорекордер</v-btn>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-items class="hidden-sm-and-down">
        <v-btn flat v-for="link of links" :key="link.title" :to="link.url">
          <v-icon left>{{link.icon}}</v-icon>
          {{link.title}}
        </v-btn>
        <v-btn flat @click="onLogout" v-if="isUserLoggedIn">
          <v-icon left>exit_to_app</v-icon>Выход
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>

    <v-content style="margin-top:60px">
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-content>

    <v-fab-transition>
      <v-btn small fab fixed bottom right @click="switchColorMode()">
        <v-icon>invert_colors</v-icon>
      </v-btn>
    </v-fab-transition>

    <template v-if="error">
      <v-snackbar
        :multi-line="true"
        :timeout="3000"
        @input="closeError"
        :value="true"
        color="error"
      >
        {{error}}
        <v-btn dark flat @click="closeError">Закрыть</v-btn>
      </v-snackbar>
    </template>

    <template v-if="message">
      <v-snackbar
        :multi-line="true"
        :timeout="3000"
        @input="closeMessage"
        :value="true"
        color="primary"
      >
        {{message}}
        <v-btn dark flat @click="closeMessage">Закрыть</v-btn>
      </v-snackbar>
    </template>
  </v-app>
</template>

<script>
export default {
  data() {
    return {
      drawer: false
    };
  },
  computed: {
    error() {
      return this.$store.getters.error;
    },
    message() {
      return this.$store.getters.message;
    },
    isUserLoggedIn() {
      return this.$store.getters.isAutheticated;
    },
    user() {
      return this.$store.getters.user;
    },
    isDarkMode() {
      return this.$store.getters.isDarkMode;
    },
    links() {
      let links = [];
      if (this.isUserLoggedIn) {
        links = [
          { title: "Аудитории", icon: "view_list", url: "/rooms" },
          { title: "API", icon: "code", url: "/manage_api" }
        ];
        if (this.user.role === "admin") {
          links = [
            links[0],
            {
              title: "Пользователи",
              icon: "supervised_user_circle",
              url: "/users"
            },
            {
              title: "Запросы на доступ",
              icon: "verified_user",
              url: "/access_requests"
            }
          ];
        }
      } else {
        links = [
          { title: "Вход", icon: "lock", url: "/login" },
          { title: "Регистрация", icon: "account_circle", url: "/register" }
        ];
      }

      return links;
    }
  },
  methods: {
    switchColorMode() {
      this.$store.dispatch("switchColorMode");
    },
    closeError() {
      this.$store.dispatch("clearError");
    },
    closeMessage() {
      this.$store.dispatch("clearMessage");
    },
    onLogout() {
      this.$store.dispatch("logout").then(() => {
        this.$store.dispatch("clearTimer");
        this.$router.push("/");
      });
    }
  }
};
</script>

<style scoped>
.pointer {
  cursor: pointer;
}
</style>
