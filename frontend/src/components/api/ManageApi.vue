<template>
  <v-app>
    <v-container fluid>
      <v-layout align-center justify-center>
        <v-flex xs12 sm12 md10>
          <template v-if="!user.api_key">
            <v-card>
              <v-card-text>
                <v-layout align-center mb-3>
                  <strong class="title">Ключ API</strong>
                  <v-spacer></v-spacer>
                </v-layout>
                <div class="subheading">
                  <p>
                    Ключ API позволит программно взаимодействовать к функциям
                    NVR, такими как:
                  </p>
                  <ul>
                    <li>Авторизовываться через NVR</li>
                    <li>Создать или удалить комнату</li>
                    <li>Получить данные комнат</li>
                    <li>Конфигурировать настройки комнаты</li>
                    <li>Запросить запись</li>
                    <li>Включить/Отключить трекинг</li>
                    <li>
                      Включить/Отключить автовозрат камер на default позиции
                    </li>
                    <li>Запускать/Останавливать стриминг в YouTube</li>
                    <li>Управлять своим API-ключом</li>
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
              >Создать ключ API</v-btn
            >
          </template>

          <template v-else>
            <v-card>
              <v-card-title primary-title>
                <h3 class="title mb-0">
                  Ваш ключ API:
                  <b v-if="showKey" class="subheading">{{ user.api_key }}</b>
                  <b v-else class="subheading">{{ "&#8226;".repeat(32) }}</b>
                </h3>
                <v-spacer></v-spacer>
                <v-btn icon @click="showKey = !showKey">
                  <v-icon>{{
                    showKey ? "visibility_off" : "visibility"
                  }}</v-icon>
                </v-btn>
              </v-card-title>

              <v-card-text>
                <div class="subheading">
                  <div>API url: {{ API_URL }}</div>
                  <div v-if="showKey">
                    Добавьте в headers вашего запроса: {"key": "{{
                      user.api_key
                    }}"}
                  </div>
                  <div v-else>
                    Добавьте в headers вашего запроса: {"key": "{{
                      "&#8226;".repeat(32)
                    }}"}
                  </div>
                </div>
              </v-card-text>

              <v-card-actions>
                <v-btn
                  depressed
                  color="warning"
                  :loading="loader"
                  @click="updateKey"
                  >Обновить</v-btn
                >
                <v-btn
                  depressed
                  color="error"
                  :loading="loader"
                  @click="deleteKey"
                  >Удалить</v-btn
                >
              </v-card-actions>
            </v-card>

            <div style="text-align: right">
              <v-btn @click="all" icon>
                <v-icon>list</v-icon>
              </v-btn>
            </div>

            <v-expansion-panel expand v-model="panel">
              <v-expansion-panel-content
                :id="i"
                v-for="(route, i) in routes"
                :key="i"
              >
                <template v-slot:header>
                  <div>
                    <b>{{ route.method }}</b>
                    {{ route.name }}
                  </div>
                </template>

                <template>
                  <v-card :color="isDarkMode ? '#2d2d2d' : '#F5F5F5'">
                    <v-card-text>
                      <div class="subheading">
                        {{ route.doc }}
                        <v-tooltip bottom>
                          <template v-slot:activator="{ on }">
                            <v-btn small v-on="on" icon @click="copyText(i)">
                              <v-icon>link</v-icon>
                            </v-btn>
                          </template>
                          <span>Скопировать ссылку на метод</span>
                        </v-tooltip>
                      </div>
                    </v-card-text>
                  </v-card>
                  <v-card
                    v-if="route.request"
                    :color="isDarkMode ? '#2d2d2d' : '#F5F5F5'"
                  >
                    <v-card-text>
                      <div class="font-weight-bold">Request</div>
                      <pre>{{ route.request }}</pre>
                    </v-card-text>
                  </v-card>
                  <v-card
                    v-if="route.responses"
                    :color="isDarkMode ? '#2d2d2d' : '#F5F5F5'"
                  >
                    <div class="font-weight-bold ml-3">Responses</div>
                    <v-card-text
                      v-for="(response, i) in route.responses"
                      :key="i"
                    >
                      <b>{{ response.code }}</b>
                      <pre>
                            {{ response.body }}
                      </pre>
                    </v-card-text>
                    <v-card-text v-if="route.name !== '/login'">
                      <b>401</b>
                      <pre><br />  {"error": "Access error"} <br /> </pre>
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
      API_URL: process.env.NVR_URL + "/api",
      showKey: false,
      routes: [
        {
          name: "/login",
          method: "POST",
          doc: `Авторизация через NVR`,
          request: `
  {
    "email": string,
    "password": string
  }`,
          responses: [
            {
              code: 202,
              body: `
  {"token": string}`,
            },
            {
              code: 401,
              body: `
  {"error": "Неверные данные", "authenticated": false}`,
            },
            {
              code: 401,
              body: `
  {"error": "Почта не подтверждена", "authenticated": false}`,
            },
            {
              code: 401,
              body: `
  {
    "error": "Администратор ещё не открыл доступ для этого аккаунта",
    "authenticated": false
  }`,
            },
          ],
        },
        {
          name: "/rooms",
          method: "GET",
          doc: "Возвращает массив словарей данных о комнатах",
          responses: [
            {
              code: 200,
              body: `
  [
    {
      "calendar": "auditory.ru_rgc7bjcechrr0f2hnmacnmer58@group.calendar.google.com",
      "drive": "https://drive.google.com/drive/u/1/folders/1zAPs-2GP_SQj6tHLWwgohjuwCS_7o3yu",
      "id": 1,
      "main_source": "172.18.191.24/0",
      "name": "504",
      "screen_source": "172.18.191.21/0",
      "sound_source": "172.18.191.21/0",
      "sources": [
        { "id": 110, "ip": "172.18.191.21/0", "name": "Трибуна", "room_id": 1 }
      ],
    }
  ]`,
            },
          ],
        },
        {
          name: "/rooms/{room_id}",
          method: "GET",
          doc: "Возвращает комнату с указанным room_id",
          responses: [
            {
              code: 200,
              body: `
  {
    "calendar": "auditory.ru_rgc7bjcechrr0f2hnmacnmer58@group.calendar.google.com",
    "drive": "https://drive.google.com/drive/u/1/folders/1zAPs-2GP_SQj6tHLWwgohjuwCS_7o3yu",
    "id": 1,
    "main_source": "172.18.191.24/0",
    "name": "504",
    "screen_source": "172.18.191.21/0",
    "sound_source": "172.18.191.21/0",
    "sources": [
      { "id": 110, "ip": "172.18.191.21/0", "name": "Трибуна", "room_id": 1 }
    ],
  }`,
            },
            {
              code: 400,
              body: `
  Bad request`,
            },
          ],
        },
        {
          name: "/rooms",
          method: "POST",
          doc: "Создаёт комнату с указанным name",
          request: `
  {"name": str}`,
          responses: [
            {
              code: 201,
              body: `
  {"message": "Started creating '{room name}'"}`,
            },
            {
              code: 400,
              body: `
  Bad request`,
            },
          ],
        },
        {
          name: "/rooms/{room_id}",
          method: "DELETE",
          doc: "Удаляет комнату с указанным room_id",
          responses: [
            {
              code: 200,
              body: `
  {"message": "Room deleted"}`,
            },
            {
              code: 400,
              body: `
  Bad request`,
            },
          ],
        },
        {
          name: "/auto-control/{room_id}",
          method: "POST",
          doc:
            "Включает или отключает автоматический контроль камер в указанной комнате",
          request: `
  {"auto_control": bool}`,
          responses: [
            {
              code: 200,
              body: `
  {"message": "Automatic control within room {room name} has been set to {auto_control}"}`,
            },
            {
              code: 400,
              body: `
  {"error": "Boolean value not provided"}`,
            },
            {
              code: 404,
              body: `
  {"error": "Room not found"}`,
            },
          ],
        },
        {
          name: "/montage-event/{room_id}",
          method: "POST",
          doc: `Создаёт событие на склеку материала в указанной комнате в указанный промежуток времени. Формат даты: "YYYY-MM-DD", Например: ${new Date()
            .toISOString()
            .slice(0, 10)}`,
          request: `
  {
    "start_time": string,
    "end_time": string,
    "date": string,
    "event_name": string,
    "user_email": string
  }`,
          responses: [
            {
              code: 201,
              body: `
  {"message": "Record event created"}`,
            },
            {
              code: 400,
              body: `
  Bad request`,
            },
          ],
        },
      ],
    };
  },
  computed: {
    isDarkMode() {
      return this.$store.getters.isDarkMode;
    },
    loader() {
      return this.$store.getters.loading;
    },
    user() {
      return this.$store.getters.user;
    },
    openPanel() {
      let arr = [];
      if (window.location.href.indexOf("#") > -1) {
        for (let i = 0; i < Number(window.location.href.split("#")[1]); i++)
          arr.push(null);
        arr.push(true);
      }
      return arr;
    },
  },
  methods: {
    createKey() {
      this.$store.dispatch("createKey");
    },
    updateKey() {
      if (confirm("Вы уверены, что хотите обновить ключ API?")) {
        this.$store.dispatch("updateKey");
      }
    },
    deleteKey() {
      if (confirm("Вы уверены, что хотите удалить ключ API?")) {
        this.$store.dispatch("deleteKey");
      }
    },
    all() {
      this.panel =
        this.panel.length !== this.routes.length
          ? [...Array(this.routes.length).keys()].map((_) => true)
          : [];
    },

    copyText(i) {
      let textToCopy = window.location.href;
      if (textToCopy.indexOf("#")) {
        textToCopy = textToCopy.split("#")[0];
      }
      textToCopy += "#" + i;
      navigator.clipboard.writeText(textToCopy);
    },
  },
  mounted() {
    this.panel = this.openPanel;
    let el = this.$router.currentRoute.hash;
    if (el) {
      el = el.replace("#", "");
      console.log(el);
      document.getElementById(el).scrollIntoView(el);
    }
  },
  beforeCreate() {
    this.$store.dispatch("getKey");
  },
};
</script>

<style scoped></style>
