<template>
  <v-layout align-center justify-center>
    <v-flex xs12 sm8 md6>
      <v-card>
        <v-list v-if="users.length > 0" v-resize="onResize">
          <template v-for="(user,index) in users">
            <v-list-tile avatar :key="user.id">
              <v-list-tile-content>
                <v-list-tile-title v-text="user.email"></v-list-tile-title>
              </v-list-tile-content>
              <div v-if="isMobile">
                <v-btn icon color="success" @click="grantAccess(user)">
                  <v-icon>verified_user</v-icon>
                </v-btn>
                <v-btn icon color="error" @click="deleteUser(user)">
                  <v-icon>block</v-icon>
                </v-btn>
              </div>
              <div v-else>
                <v-btn color="success" @click="grantAccess(user)">Подтвердить</v-btn>
                <v-btn color="error" @click="deleteUser(user)">Отклонить</v-btn>
              </div>
            </v-list-tile>
            <v-divider v-if="index + 1 < users.length" :key="index"></v-divider>
          </template>
        </v-list>
        <v-alert v-else :value="true" color="info" icon="info">Список запросов на доступ пуст</v-alert>
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
        user => user.email_verified === true && user.access === false
      )
  }),
  methods: {
    onResize() {
      this.isMobile = window.innerWidth < 769;
    },
    grantAccess(user) {
      this.$store.dispatch("grantAccess", { user });
    },
    deleteUser(user) {
      this.$store.dispatch("deleteUser", { user });
    }
  },
  beforeMount() {
    this.$store.dispatch("getUsers");
  }
};
</script>
