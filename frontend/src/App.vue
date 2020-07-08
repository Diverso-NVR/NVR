<template>
  <v-app :dark="isDarkMode">
    <v-navigation-drawer v-if="isMobile" v-model="drawer" app absolute v-resize="onResize">
      <v-list style="margin-top:0px">
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

    <v-navigation-drawer v-else app absolute v-resize="onResize" :mini-variant="!drawer">
      <v-list style="margin-top:70px">
        <v-list-tile v-for="link of links" :key="link.title" :to="link.url">
          <v-list-tile-action>
            <v-icon>{{link.icon}}</v-icon>
          </v-list-tile-action>

          <v-list-tile-content>
            <v-list-tile-title>{{link.title}}</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
      </v-list>
    </v-navigation-drawer>

    <v-toolbar dark color="black" clipped-left>
      <v-toolbar-side-icon @click.prevent="switchDrawer()"></v-toolbar-side-icon>
      <v-toolbar-side-icon class="ml-5" disabled>
        <v-img src="../static/logo.png" min-height="30" min-width="77"></v-img>
      </v-toolbar-side-icon>
      <v-spacer></v-spacer>
      <v-toolbar-items>
        <v-btn flat @click="onLogout" v-if="isUserLoggedIn && !isMobile">
          <v-icon left>exit_to_app</v-icon>Выход
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>

    <v-content>
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

    <!-- fix google localStorage disappear on reload
    because it must be all the time-->
    <div v-show="false" id="google-signin-button"></div>
  </v-app>
</template>

<script>
export default {
  data() {
    return {
      drawer: localStorage.drawer === "true" ? true : false,
      isMobile: false
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
          { title: "Стриминг", icon: "stream", url: "/streaming" }
        ];
        if (/^\w*admin$/.test(this.user.role)) {
          links = [
            ...links,
            {
              title: "Пользователи",
              icon: "supervised_user_circle",
              url: "/users"
            },
            {
              title: "Запросы на доступ",
              icon: "verified_user",
              url: "/access-requests"
            },
            { title: "API", icon: "code", url: "/manage-api" }
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
    async switchColorMode() {
      await this.$store.dispatch("switchColorMode");
    },
    switchDrawer() {
      this.drawer = !this.drawer;
      localStorage.drawer = this.drawer;
    },
    onResize() {
      this.isMobile = window.innerWidth < 769;
    },
    async closeError() {
      await this.$store.dispatch("clearError");
    },
    async closeMessage() {
      await this.$store.dispatch("clearMessage");
    },
    async onLogout() {
      if (localStorage.googleOAuth == "true") {
        try {
          // OAuth logout
          var auth2 = await gapi.auth2.getAuthInstance();
          await auth2.signOut();
        } catch (error) {}
      }

      await this.$store.dispatch("logout");
      await this.$router.push("/login");
    }
  },
  beforeMount() {
    this.$store.dispatch("setColorMode");
  },
  mounted() {
    gapi.signin2.render("google-signin-button", {});
  }
};
</script>

<style scoped>
.pointer {
  cursor: pointer;
}
</style>