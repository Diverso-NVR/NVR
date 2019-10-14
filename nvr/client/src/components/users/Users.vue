<template>
  <v-layout align-center justify-center>
    <v-flex xs12 sm8 md6>
      <v-card>
        <v-list v-if="users.length > 0" v-resize="onResize">
          <template v-for="(user,index) in users">
            <v-list-tile avatar :key="user.id">
              <v-list-tile-content>
                <v-list-tile-title v-text="user.email"></v-list-tile-title>
                <v-list-tile-sub-title>{{ user.role }}</v-list-tile-sub-title>
              </v-list-tile-content>
              <div v-if="isMobile">
                <v-btn icon color="warning" @click="changeRole(user)">
                  <v-icon>supervisor_account</v-icon>
                </v-btn>
                <v-btn icon color="error" @click="deleteUser(user)">
                  <v-icon>block</v-icon>
                </v-btn>
              </div>
              <div v-else>
                <v-btn color="warning" depressed @click="changeRole(user)">Изменить роль</v-btn>
                <v-btn color="error" depressed @click="deleteUser(user)">Удалить</v-btn>
              </div>
            </v-list-tile>
            <v-divider v-if="index + 1 < users.length" :key="index"></v-divider>
          </template>
        </v-list>
        <v-alert v-else :value="true" color="info" icon="info">Список пользователей пуст</v-alert>
      </v-card>
    </v-flex>
  </v-layout>
</template>
<script>
import { mapState } from "vuex";
export default {
  data() {
    return {
      isMobile: false
    };
  },
  computed: mapState({
    users: state =>
      state.users.filter(
        user =>
          user.access === true &&
          user.email !== state.user.email &&
          user.role !== "superadmin"
      )
  }),
  methods: {
    onResize() {
      this.isMobile = window.innerWidth < 769;
    },
    changeRole(user) {
      user.role = user.role === "user" ? "admin" : "user";
      this.$store.dispatch("changeRole", { user });
    },
    deleteUser(user) {
      if (confirm("Вы уверены, что хотите удалить этого пользователя?")) {
        this.$store.dispatch("deleteUser", { user });
      }
    }
  },
  beforeMount() {
    this.$store.dispatch("getUsers");
  }
};
</script>
