<template>
  <v-layout align-center justify-center v-resize="onResize">
    <v-flex xs12 sm8 md6>
      <v-layout row wrap>
        <v-flex xs5>
          <v-text-field
            append-icon="search"
            label="Search"
            single-line
            hide-details
            v-model="search"
          ></v-text-field>
        </v-flex>
      </v-layout>
      <v-data-table
        :items="users"
        class="elevation-4 mt-2"
        disable-initial-sort
        hide-actions
        :headers="headers"
        :loading="loader"
        :search="search"
      >
        <template v-slot:items="props">
          <td class="text-xs-left">
            <h3 class="subheading mt-1">{{ props.item.email }}</h3>
            <div
              class="mt-1 mb-2 time"
              :color="isDarkMode ? '#6a737d' : '#F5F5F5'"
            >
              Активность: {{ lastLogin(props.item) }}
            </div>
          </td>
          <td class="text-xs-left">
            {{ props.item.role }}
          </td>
          <td class="text-xs-left">
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn
                  icon
                  color="warning"
                  v-on="on"
                  @click="changeRole(props.item)"
                >
                  <v-icon>supervisor_account</v-icon>
                </v-btn>
              </template>
              <span>Изменить роль</span>
            </v-tooltip>

            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn
                  icon
                  color="error"
                  v-on="on"
                  @click="deleteUser(props.item)"
                >
                  <v-icon>block</v-icon>
                </v-btn>
              </template>
              <span>Удалить</span>
            </v-tooltip>
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn
                  icon
                  color="primary"
                  v-on="on"
                  @click="banUser(props.item)"
                >
                  <v-icon>lock</v-icon>
                </v-btn>
              </template>
              <span>Заблокировать</span>
            </v-tooltip>
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
      search: "",
      isLarge: false,
      options: {
        year: "numeric",
        month: "numeric",
        day: "numeric",
        hour: "numeric",
        minute: "numeric",
      },
      headers: [
        {
          text: "Email",
          align: "left",
          sortable: true,
          value: "email",
        },
        { text: "Role", align: "left", sortable: true, value: "role" },
        { text: "Actions", align: "left", value: "actions" },
      ],
    };
  },
  computed: mapState({
    users: (state) =>
      state.users.filter(
        (user) =>
          user.access === true &&
          user.email !== state.user.email &&
          user.role !== "superadmin" &&
          user.banned === false
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
    banUser(user) {
      if (user.banned === false);
      this.$store.dispatch("emitBanUser", { user });
    },
    lastLogin(user) {
      if (user.online === false) {
        let postDate = new Date(user.last_login);
        return postDate.toLocaleString("ru", this.options);
      } else return "Online";
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
