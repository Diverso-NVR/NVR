<template>
  <v-app>
    <v-container fluid>
      <v-layout align-center justify-center>
        <v-flex xs12 sm12 md112>
          <v-card>
            <v-card-text>
              <v-layout align-center mb-3>
                <strong class="title">Сервис автоматической записи</strong>
                <v-spacer></v-spacer>
              </v-layout>
              <v-form>
                <v-container>
                  <v-layout row wrap>
                    <v-flex xs12 sm6 md3>
                      <v-text-field label="Дни записи"></v-text-field>
                    </v-flex>
                    <v-flex xs12 sm6 md3>
                      <v-text-field label="Время начала записи"></v-text-field>
                    </v-flex>
                    <v-flex xs12 sm6 md3>
                      <v-text-field label="Время конца записи"></v-text-field>
                    </v-flex>
                    <v-flex xs12 sm6 md3>
                      <v-text-field
                        label="Длительность одного видео"
                      ></v-text-field>
                    </v-flex>
                  </v-layout>
                  <v-flex xs12 sm6 md3>
                    <v-checkbox label="Загружать видео без звука"></v-checkbox>
                  </v-flex>
                  <div>
                    <v-btn color="primary" :click="hui()">
                      Развернуть приложение
                    </v-btn>
                    <v-btn :click="hui()"> Мониторинг </v-btn>
                  </div>
                </v-container>
              </v-form>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </v-app>
</template>


<script>
export default {
  methods: {
    norm() {
      this.$store.dispatch(
        "setMessage",
        "Сервис автоматической записи развернут"
      );
    },
    hui() {
      this.$store.dispatch("setError", {
        response: {
          data: {
            error: "Приложение ещё не развернуто",
          },
        },
      });
    },
  },
};
</script>