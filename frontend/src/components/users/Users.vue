<template>
  <v-layout align-center justify-center v-resize="onResize">
    <v-flex xs12 sm8 md6>
      <v-data-table
        :items="users"
        class="elevation-4"
        hide-actions
        hide-headers
        :loading="loader"
      >
        <template v-slot:items="props">
          <td>
            <div class="my-2">
              <h3 class="subheading">{{ props.item.email }}</h3>
              <div>{{ props.item.role }}</div>
              <div
                class="mt-2 time"
                :color="isDarkMode ? '#6a737d' : '#F5F5F5'"
              >
                {{ lastLogin(props.item.last_login) }}
              </div>
            </div>
          </td>
          <td class="text-xs-center">
            <div v-if="isLarge">
              <v-btn icon color="warning" @click="changeRole(props.item)">
                <v-icon>supervisor_account</v-icon>
              </v-btn>
              <v-btn icon color="error" @click="deleteUser(props.item)">
                <v-icon>block</v-icon>
              </v-btn>
            </div>
            <div v-else>
              <v-btn color="warning" depressed @click="changeRole(props.item)"
                >Изменить роль</v-btn
              >
              <v-btn color="error" depressed @click="deleteUser(props.item)"
                >Удалить</v-btn
              >
            </div>
          </td>
        </template>
        <template v-slot:no-data>
          <v-alert :value="true" color="primary" icon="info"
            >Список пользователей пуст</v-alert
          >
        </template>
      </v-data-table>
    </v-flex>
  </v-layout>
</template>

<script>
import { mapState } from "vuex";
export default {
  data() {
    return {
      isLarge: false,
      options: {
        year: "numeric",
        month: "numeric",
        day: "numeric",
        hour: "numeric",
        minute: "numeric",
      },
    };
  },
  computed: mapState({
    users: (state) =>
      state.users.filter(
        (user) =>
          user.access === true &&
          user.email !== state.user.email &&
          user.role !== "superadmin"
      ),
    loader() {
      return this.$store.getters.loading;
    },
    isDarkMode() {
      return this.$store.getters.isDarkMode;
    },
  }),
  methods: {
    onResize() {
      this.isLarge = window.innerWidth < 1521;
    },
    changeRole(user) {
      if (user.role === "user") user.role = "editor";
      else if (user.role === "editor") user.role = "admin";
      else user.role = "user";
      this.$store.dispatch("emitChangeRole", { user });
    },
    deleteUser(user) {
      if (confirm("Вы уверены, что хотите удалить этого пользователя?")) {
        this.$store.dispatch("emitDeleteUser", { user });
      }
    },
    lastLogin(timestamp) {
      let postDate = new Date(timestamp);
      return postDate.toLocaleString("ru", this.options);
    },
  },
};
</script>

<style scoped>
.time {
  font-weight: 400;
  font-size: 12px;
}
</style>