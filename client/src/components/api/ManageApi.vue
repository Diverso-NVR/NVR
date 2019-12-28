<template>
  <v-app>
    <v-container fluid>
      <v-layout align-center justify-center>
        <v-flex xs12 sm12 md10>
          <template v-if="!api_key">
            <v-card>
              <v-card-text>
                <v-layout align-center mb-3>
                  <strong class="title">Ключ API</strong>
                  <v-spacer></v-spacer>
                </v-layout>
                <div class="subheading">
                  <p>Ключ API позволит программно взаимодействовать к функциям NVR, такими как:</p>
                  <ul>
                    <li>Создать или удалить комнату</li>
                    <li>Изменить список камер/кодеров комнаты</li>
                    <li>Начать или остановить запись</li>
                    <li>Выбрать источник звука для комнаты</li>
                  </ul>
                </div>
              </v-card-text>
            </v-card>

            <v-btn
              @click="createKey"
              :loading="loader"
              depressed
              block
              color="info"
            >Создать ключ API</v-btn>
          </template>

          <template v-else>
            <v-card>
              <v-card-title primary-title>
                <h3 class="title mb-0">
                  Ваш ключ API:
                  <b class="subheading">{{ api_key }}</b>
                </h3>
              </v-card-title>

              <v-card-text>
                <div class="subheading">
                  <div>API url: {{API_URL}}</div>
                  <div>Добавьте в headers вашего запроса: {"key": "{{api_key}}"}</div>
                </div>
              </v-card-text>

              <v-card-actions>
                <v-btn depressed color="warning" :loading="loader" @click="updateKey">Обновить</v-btn>
                <v-btn depressed color="error" :loading="loader" @click="deleteKey">Удалить</v-btn>
              </v-card-actions>
            </v-card>

            <div style="text-align:right">
              <v-btn @click="all" icon>
                <v-icon>list</v-icon>
              </v-btn>
            </div>
            <v-expansion-panel expand v-model="panel">
              <v-expansion-panel-content v-for="(route,i) in routes" :key="i">
                <template v-slot:header>
                  <div>
                    <b>{{route.method}}</b>
                    {{route.name}}
                  </div>
                </template>

                <template>
                  <v-card :color="isDarkMode ? 'grey darken-4' : 'grey lighten-3'">
                    <v-card-text>
                      <div class="subheading font-weight-bold">Описание</div>
                      <div class="subheading">{{route.doc}}</div>
                    </v-card-text>
                  </v-card>
                  <v-card
                    v-if="route.json"
                    :color="isDarkMode ? 'grey darken-4' : 'grey lighten-3'"
                  >
                    <v-card-text>
                      <div class="subheading font-weight-bold">Параметры json</div>
                      <div class="subheading">{{route.json}}</div>
                    </v-card-text>
                  </v-card>
                </template>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </template>
        </v-flex>
      </v-layout>
    </v-container>
  </v-app>
</template>

<script>
export default {
  data() {
    return {
      panel: [],
      api_key: "",
      API_URL: "",
      routes: [
        {
          name: "/rooms/",
          method: "GET",
          doc: "Возвращает массив словарей данных о комнатах в формате json"
        },
        {
          name: "/rooms/{room_name}",
          method: "GET",
          doc: "Возвращает комнату с названием room_name в формате json"
        },
        {
          name: "/rooms/{room_name}",
          method: "POST",
          doc: "Создаёт комнату с названием 'room_name'"
        },
        {
          name: "/rooms/{room_name}",
          method: "DELETE",
          doc: "Удаляет комнату по названию"
        },
        {
          name: "/rooms/{room_name}",
          method: "PUT",
          doc: "Изменяет данные об источниках в комнате с room_name",
          json: "{sources: array}"
        },
        {
          name: "/start-record/{room_name}",
          method: "POST",
          doc: "Запускает запись в комнате с переданным room_name"
        },
        {
          name: "/stop-record/{room_name}",
          method: "POST",
          doc: "Останавливает запись в комнате с переданным room_name"
        },
        {
          name: "/sound-change/{room_name}",
          method: "POST",
          doc: `Изменяет источник звука для комнаты. 
            sound принимает одно из значений: "enc" -- кодер, "cam" -- камера`,
          json: `{sound: string}`
        },
        {
          name: "/create-event/{room_name}",
          method: "POST",
          doc: `Создаёт событие в календаре в указанной комнате в указанное время. Формат дат: "YYYY-MM-DDTHH:mm", Например: 2019-08-21T15:00`,
          json: "{start_time: string, end_time: string, summary: string}"
        },
        {
          name: "/tracking/{room_name}",
          method: "POST",
          doc: `Взаимодействие с трекингом в указанной комнате. command принимает значения "start", "stop", "status"`,
          json: `{command: string}`
        },
        {
          name: "/login",
          method: "POST",
          doc: `Авторизация через NVR`,
          json: `{email: string, password: string}`
        }
      ]
    };
  },
  computed: {
    isDarkMode() {
      return this.$store.getters.isDarkMode;
    },
    loader() {
      return this.$store.getters.loading;
    }
  },
  methods: {
    async createKey() {
      let res = await this.$store.dispatch("createKey");
      this.api_key = res.data.api_key;
    },
    async updateKey() {
      if (confirm("Вы уверены, что хотите обновить ключ API?")) {
        let res = await this.$store.dispatch("updateKey");
        this.api_key = res.data.api_key;
      }
    },
    async deleteKey() {
      if (confirm("Вы уверены, что хотите удалить ключ API?")) {
        await this.$store.dispatch("deleteKey");
        this.api_key = "";
      }
    },
    all() {
      this.panel =
        this.panel.length !== this.routes.length
          ? [...Array(this.routes.length).keys()].map(_ => true)
          : [];
    }
  },
  created() {
    this.api_key = this.$store.getters.user.api_key;
    this.API_URL = process.env.NVR_URL + "/api";
  }
};
</script>

<style scoped>
</style>
