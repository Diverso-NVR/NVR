<template>
  <v-container fluid fill-height>
    <v-layout align-center justify-center>
      <v-flex xs12 sm8 md6>
        <v-card class="elevation-12">
          <v-toolbar dark color="black">
            <v-toolbar-title>Сброс пароля</v-toolbar-title>
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
            >Подтвердить</v-btn>
          </v-card-actions>
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
      errorMsg: "",
      valid: false,
      emailRules: [
        v => !!v || "Обязательное поле",
        v =>
          /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/.test(v) ||
          "Некорректный адрес почты"
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
        let res = await this.$store.dispatch("sendResetEmail", this.email);
        this.$router.push("/login");
      }
    }
  }
};
</script>
