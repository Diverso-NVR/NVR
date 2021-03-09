<template>
  <v-layout align-center justify-center v-resize="onResize">
    <v-flex xs12 sm8 md6>
      <v-layout row wrap style="margin-bottom: 3%">
        <v-flex xs5>
          <v-text-field
            append-icon="search"
            label="E-mail"
            single-line
            hide-details
            v-model="search"
          ></v-text-field>
        </v-flex>
      </v-layout>
      <v-data-table
        :items="users"
        class="elevation-4"
        hide-actions
        hide-headers
        :loading="loader"
        :search="search"
      >
        <template v-slot:items="props">
          <td class="text-xs-center subheading">{{ props.item.email }}</td>
          <td>
            <div class="text-xs-center">
              <v-tooltip bottom>
                <template v-slot:activator="{ on }">
                  <v-btn
                    icon
                    color="success"
                    v-on="on"
                    @click="grantAccess(props.item)"
                  >
                    <v-icon>verified_user</v-icon>
                  </v-btn>
                </template>
                <span>Подтвердить</span>
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
                <span>Отклонить</span>
              </v-tooltip>
            </div>
          </td>
        </template>
        <template v-slot:no-data>
          <v-alert :value="true" color="primary" icon="info"
            >Нет новых запросов на доступ</v-alert
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
    };
  },
  computed: mapState({
    users: (state) =>
      state.users.users.filter(
        (user) => user.email_verified === true && user.access === false
      ),
    loader() {
      return this.$store.getters.loading;
    },
  }),
  methods: {
    onResize() {
      this.isLarge = window.innerWidth < 1521;
    },
    grantAccess(user) {
      this.$store.dispatch("emitGrantAccess", { user });
    },
    deleteUser(user) {
      this.$store.dispatch("emitDeleteUser", { user });
    },
  },
};
</script>
