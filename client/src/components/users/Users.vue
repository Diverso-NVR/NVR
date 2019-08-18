<template>
  <v-layout align-center justify-center>
    <v-flex xs12 sm8 md6>
      <v-card>
        <v-list v-if="users.length > 0">
          <template v-for="(user,index) in users">
            <v-list-tile avatar :key="user.id">
              <v-list-tile-content>
                <v-list-tile-title v-text="user.email"></v-list-tile-title>
                <v-list-tile-sub-title>{{ user.role }}</v-list-tile-sub-title>
              </v-list-tile-content>
              <v-btn color="warning" @click="changeRole(user)">Изменить роль</v-btn>
              <v-btn color="error" @click="deleteUser(user)">Удалить</v-btn>
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
  computed: mapState({
    users: state =>
      state.users.filter(
        user => user.access === true && user.email !== state.user.email
      )
  }),
  methods: {
    changeRole(user) {
      user.role = user.role === "user" ? "admin" : "user";
      this.$store.dispatch("changeRole", { user });
    },
    deleteUser(user) {
      confirm("Вы уверены, что хотите удалить этого пользователя?") &&
        this.$store.dispatch("deleteUser", { user });
    }
  },
  beforeMount() {
    this.$store.dispatch("getUsers");
  }
};
</script>
