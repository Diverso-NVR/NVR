<template>
  <v-layout align-center justify-center v-resize="onResize">
    <v-flex xs12 sm8 md6>
      <v-data-table :items="users" class="elevation-4" hide-actions hide-headers :loading="loader">
        <template v-slot:items="props">
          <td>
            <div>
              <h3 class="subheading">{{props.item.email}}</h3>
              <div>{{ props.item.role }}</div>
            </div>
          </td>
          <td class="text-xs-center">
            <div v-if="isLarge">
              <v-btn icon color="success" @click="grantAccess(props.item)">
                <v-icon>verified_user</v-icon>
              </v-btn>
              <v-btn icon color="error" @click="deleteUser(props.item)">
                <v-icon>block</v-icon>
              </v-btn>
            </div>
            <div v-else>
              <v-btn color="success" depressed @click="grantAccess(props.item)">Подтвердить</v-btn>
              <v-btn color="error" depressed @click="deleteUser(props.item)">Отклонить</v-btn>
            </div>
          </td>
        </template>
        <template v-slot:no-data>
          <v-alert :value="true" color="primary" icon="info">Нет новых запросов на доступ</v-alert>
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
      isLarge: false
    };
  },
  computed: mapState({
    users: state =>
      state.users.filter(
        user => user.email_verified === true && user.access === false
      ),
    loader() {
      return this.$store.getters.loading;
    }
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
    }
  }
};
</script>
