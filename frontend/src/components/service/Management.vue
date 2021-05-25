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
                      <v-text-field label="Дни записи" v-model="params.days"></v-text-field>
                    </v-flex>
                    <v-flex xs12 sm6 md3>
                      <v-text-field label="Время начала записи" v-model="params.record_start"></v-text-field>
                    </v-flex>
                    <v-flex xs12 sm6 md3>
                      <v-text-field label="Время конца записи" v-model="params.record_end"></v-text-field>
                    </v-flex>
                    <v-flex xs12 sm6 md3>
                      <v-text-field label="Длительность одного видео" v-model="params.duration"></v-text-field>
                    </v-flex>
                  </v-layout>
                  <v-flex xs12 sm6 md3>
                    <v-checkbox label="Загружать видео без звука" v-model="params.upload_without_sound"></v-checkbox>
                  </v-flex>
                  <div>
                    <v-btn color="primary" @click="deploy">
                      Развернуть приложение
                    </v-btn>
                    <v-btn @click="monitoring"> Мониторинг</v-btn>
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
  data() {
    return {
      params: {
        days: "",
        record_start: "",
        record_end: "",
        duration: "",
        upload_without_sound: false
      }
    };
  },
  methods: {
    deploy() {
      this.$store.dispatch(
        "deployAutorec",
        {
          days: this.params.days,
          record_start: parseInt(this.params.record_start),
          record_end: parseInt(this.params.record_end),
          duration: parseInt(this.params.duration),
          upload_without_sound: this.params.upload_without_sound
        }
      ).then(res => {
        this.$store.dispatch(
          "setMessage",
          "Сервис автоматической записи развернут"
        );
      }).catch(error => {
        this.$store.dispatch("setError", {
          response: {
            data: {
              error: "Ошибка развертывания приложения",
            },
          },
        });
      });
    },
    monitoring() {
      this.$store.dispatch(
        "getMonitoring"
      ).then(res => {
        this.$router.push(res.data.link);
      }).catch(error => {
        this.$store.dispatch("setError", {
          response: {
            data: {
              error: "Приложение ещё не развернуто",
            },
          },
        });
      });
    },
  },
  created() {
    this.$store.dispatch(
      "getAutorecParameters"
    ).then(res => {
      this.params = res.data;
    }).catch(error => {
    });
  }
};
</script>
