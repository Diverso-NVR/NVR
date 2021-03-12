<template>
  <v-dialog v-model="modal" max-width="600px" :dark="isDarkMode">
    <v-btn slot="activator">Пригласить</v-btn>
    <v-card>
      <v-card-title> Пригласить пользователей </v-card-title>
      <v-card-text>
        <v-text-field
          v-model.trim="email"
          append-outer-icon="add"
          label="Введите почту"
          type="text"
          @click:append-outer="addEmail"
          @keyup.enter="addEmail"
        ></v-text-field>
        <v-list subheader v-if="emails.length > 0">
          <v-subheader>Почты</v-subheader>
          <v-list-tile v-for="email in emails" :key="email">
            <v-list-tile-avatar>
              <v-icon>account_box</v-icon>
            </v-list-tile-avatar>

            <v-list-tile-content>
              <v-list-tile-title>{{ email }}</v-list-tile-title>
            </v-list-tile-content>

            <v-list-tile-action>
              <v-btn icon ripple>
                <v-icon color="grey lighten-1" @click="deleteEmail(email)">
                  delete
                </v-icon>
              </v-btn>
            </v-list-tile-action>
          </v-list-tile>
        </v-list>

        <v-select :items="roles" v-model="role" label="Роль"></v-select>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="black" flat @click="modal = false">Закрыть</v-btn>
        <v-btn color="black" flat @click="inviteUsers"> Сохранить </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>


<script>
export default {
  data() {
    return {
      modal: false,
      email: "",
      emails: [],
      roles: ["user", "editor", "admin"],
      role: "user",
    };
  },
  computed: {
    isDarkMode() {
      return this.$store.getters.isDarkMode;
    },
  },
  methods: {
    inviteUsers() {
      if (this.emails.length !== 0) {
        this.$store.dispatch("inviteUsers", {
          emails: this.emails,
          role: this.role,
        });
      }
      this.modal = false;
    },
    deleteEmail(emailToDelete) {
      let i;
      this.emails.forEach((email, index) => {
        if (email === emailToDelete) {
          i = index;
          return;
        }
      });

      this.emails.splice(i, 1);
    },
    addEmail() {
      if (
        this.email !== "" &&
        /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(
          this.email
        ) &&
        this.emails.indexOf(this.email) === -1
      ) {
        this.emails.push(this.email);
        this.email = "";
      }
    },
  },
};
</script>