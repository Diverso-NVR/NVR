<template>
  <v-container fluid fill-height>
    <v-layout align-center justify-center>
      <v-flex xs12 sm8 md6>
        <v-card class="elevation-12">
          <v-toolbar dark color="black">
            <v-toolbar-title>Авторизация</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-form ref="form" validation v-model="valid">
              <v-text-field
                color="black"
                prepend-icon="person"
                name="email"
                label="Почта"
                type="email"
                @keyup.enter="onSubmit"
                v-model.trim="email"
                :rules="emailRules"
              ></v-text-field>
              <v-text-field
                prepend-icon="lock"
                color="black"
                name="password"
                label="Пароль"
                type="password"
                @keyup.enter="onSubmit"
                v-model.trim="password"
                :rules="passwordRules"
              ></v-text-field>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="black"
              depressed
              class="white--text"
              @click="onSubmit"
              :loading="loading"
            >Вход</v-btn>
            <v-btn depressed @click="getEmail">Забыли пароль</v-btn>
          </v-card-actions>
          <div class="separator">или</div>

          <template class="gsb-outer">
            <div id="google-signin-button" class="gsb-inner py-2"></div>
          </template>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      email: "",
      password: "",
      errorMsg: "",
      valid: false,
      emailRules: [
        v => !!v || "Обязательное поле",
        v =>
          /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/.test(v) ||
          "Некорректный адрес почты"
      ],
      passwordRules: [
        v => !!v || "Обязательное поле",
        v =>
          (v && v.length >= 6) || "Пароль должен содержать не менее 6 символов"
      ]
    };
  },
  computed: {
    loading() {
      return this.$store.getters.loading;
    }
  },
  mounted() {
    gapi.signin2.render("google-signin-button", {
      // theme: "dark",
      scope: "profile email",
      onsuccess: this.onSignIn
    });
  },
  methods: {
    async onSignIn(user) {
      const email = user.getBasicProfile().getEmail();
      const token = user.getAuthResponse().id_token;
      let res = await this.$store.dispatch("googleLogin", { token });
      await this.loadData(res);
    },
    async onSubmit() {
      if (this.$refs.form.validate()) {
        let res = await this.$store.dispatch("login", {
          email: this.email,
          password: this.password
        });
        await this.loadData(res);
      }
    },
    async loadData(res) {
      if (res) {
        await this.$store.dispatch("loadRooms");
        this.$router.push("/rooms");
        if (/^\w*admin$/.test(res)) {
          await this.$store.dispatch("getUsers");
          await this.$store.dispatch("getKey");
        }
      }
    },
    getEmail() {
      this.$router.push("/reset-pass");
    }
  }
};
</script>

<style  scoped>
.separator {
  display: flex;
  align-items: center;
  text-align: center;
}
.separator::before,
.separator::after {
  content: "";
  flex: 1;
  border-bottom: 2px solid #757575;
}
.separator::before {
  margin-right: 0.25em;
}
.separator::after {
  margin-left: 0.25em;
}
.gsb-outer {
  width: 100%;
}
.gsb-inner {
  display: table;
  margin: 0 auto;
}
</style>