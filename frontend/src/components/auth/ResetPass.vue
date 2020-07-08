<template>
  <v-container fluid fill-height>
    <v-layout align-center justify-center>
      <v-flex xs12 sm8 md6>
        <v-card class="elevation-12">
          <v-toolbar dark color="black">
            <v-toolbar-title>Сброс пароля</v-toolbar-title>
          </v-toolbar>
          <template v-if="tokenValid">
            <v-card-text>
              <v-form v-model="valid" ref="form" validation>
                <v-text-field
                  prepend-icon="lock"
                  color="black"
                  name="password"
                  label="Пароль"
                  type="password"
                  @keyup.enter="onSubmit"
                  v-model="password"
                  :rules="passwordRules"
                ></v-text-field>
                <v-text-field
                  prepend-icon="lock"
                  color="black"
                  name="confirmPassword"
                  label="Подтвердить пароль"
                  type="password"
                  @keyup.enter="onSubmit"
                  v-model="confirmPassword"
                  :rules="confirmPasswordRules"
                ></v-text-field>
              </v-form>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                depressed
                color="black"
                class="white--text"
                @click="onSubmit"
                :loading="loading"
              >Отправить</v-btn>
            </v-card-actions>
          </template>
          <template v-else>
            <v-card-text>Время на сброс пароля вышло</v-card-text>
          </template>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { isValidToken } from "@/utils";

export default {
  data() {
    return {
      token: this.$router.currentRoute.params["token"],
      tokenValid: false,
      valid: false,
      password: "",
      confirmPassword: "",
      passwordRules: [
        v => !!v || "Обязательное поле",
        v =>
          (v && v.length >= 6) || "Пароль должен содержать не менее 6 символов"
      ],
      confirmPasswordRules: [
        v => !!v || "Обязательное поле",
        v => v === this.password || "Пароли должны совпадать"
      ]
    };
  },
  computed: {
    loading() {
      return this.$store.getters.loading;
    }
  },
  methods: {
    async onSubmit() {
      if (this.$refs.form.validate()) {
        await this.$store.dispatch("resetPass", {
          new_pass: this.password,
          token: this.token
        });
        this.$router.push("/");
      }
    }
  },
  created() {
    this.tokenValid = isValidToken(this.token);
  }
};
</script>
