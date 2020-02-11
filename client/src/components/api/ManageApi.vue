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
                  <p>
                    Ключ API позволит программно взаимодействовать к функциям
                    NVR, такими как:
                  </p>
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
              >Создать ключ API</v-btn
            >
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
                  <div>API url: {{ API_URL }}</div>
                  <div>
                    Добавьте в headers вашего запроса: {"key": "{{ api_key }}"}
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

            <div style="text-align:right">
              <v-btn @click="all" icon>
                <v-icon>list</v-icon>
              </v-btn>
            </div>
            <v-expansion-panel expand v-model="panel">
              <v-expansion-panel-content v-for="(route, i) in routes" :key="i">
                <template v-slot:header>
                  <div>
                    <b>{{ route.method }}</b>
                    {{ route.name }}
                  </div>
                </template>

                <template>
                  <v-card
                    :color="isDarkMode ? 'grey darken-4' : 'grey lighten-3'"
                  >
                    <v-card-text>
                      <div class="subheading font-weight-bold">Описание</div>
                      <div class="subheading">{{ route.doc }}</div>
                    </v-card-text>
                  </v-card>
                  <v-card
                    v-if="route.json"
                    :color="isDarkMode ? 'grey darken-4' : 'grey lighten-3'"
                  >
                    <v-card-text>
                      <div class="subheading font-weight-bold">
                        Параметры json
                      </div>
                      <div class="subheading">{{ route.json }}</div>
                    </v-card-text>
                  </v-card>
                  <div v-highlight>
                    <pre class="language-javascript">
                      <code max-width>
                        {{ route.response }}
                      </code>
                    </pre>
                  </div>
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
      date: new Date().toISOString(),
      routes: [
        {
          name: "/rooms/",
          method: "GET",
          doc: "Возвращает массив словарей данных о комнатах",
          response: `
  [
    {
      "calendar": "auditory.ru_rgc7bjcechrr0f2hnmacnmer58@group.calendar.google.com",
      "drive": "https://drive.google.com/drive/u/1/folders/1zAPs-2GP_SQj6tHLWwgohjuwCS_7o3yu",
      "free": True,
      "id": 1,
      "main_source": "172.18.191.24/0",
      "name": "504",
      "screen_source": "172.18.191.21/0",
      "sound_source": "172.18.191.21/0",
      "sources": [
        { "id": 110, "ip": "172.18.191.21/0", "name": "Трибуна", "room_id": 1 }
      ],
      "tracking_source": "admin:Supervisor@172.18.191.23",
      "tracking_state": False
    }
  ]`
        },
        {
          name: "/rooms/{room_name}",
          method: "GET",
          doc: "Возвращает комнату с указанным room_name",
          response: `
    {
      "calendar": "auditory.ru_rgc7bjcechrr0f2hnmacnmer58@group.calendar.google.com",
      "drive": "https://drive.google.com/drive/u/1/folders/1zAPs-2GP_SQj6tHLWwgohjuwCS_7o3yu",
      "free": True,
      "id": 1,
      "main_source": "172.18.191.24/0",
      "name": "504",
      "screen_source": "172.18.191.21/0",
      "sound_source": "172.18.191.21/0",
      "sources": [
        { "id": 110, "ip": "172.18.191.21/0", "name": "Трибуна", "room_id": 1 }
      ],
      "tracking_source": "admin:Supervisor@172.18.191.23",
      "tracking_state": False
    }`
        },
        {
          name: "/rooms/{room_name}",
          method: "POST",
          doc: "Создаёт комнату с указанным room_name"
        },
        {
          name: "/rooms/{room_name}",
          method: "DELETE",
          doc: "Удаляет комнату с указанным room_name"
        },
        {
          name: "/rooms/{room_name}",
          method: "PUT",
          doc: "Изменяет данные об источниках в комнате с room_name",
          json: "{sources: array}"
        },
        {
          name: "/sources/",
          method: "GET",
          doc: "Возвращает массив словарей данных об источниках",
          response: `
  [
    {
      "id": 2,
      "ip": "admin:Supervisor@172.18.199.30",
      "name": "у доски слева на зал",
      "room_id": 1
    },
    {
      "id": 5,
      "ip": "admin:Supervisor@172.18.199.42",
      "name": "на доску",
      "room_id": 1
    }
  ]`
        },
        {
          name: "/sources/{ip}",
          method: "GET",
          doc: "Возвращает источник с указанным ip",
          response: `
    {
      "id": 2,
      "ip": "admin:Supervisor@172.18.199.30",
      "name": "у доски слева на зал",
      "room_id": 1
    }`
        },
        {
          name: "/sources/{ip}",
          method: "POST",
          doc: "Создаёт источник с указанным ip. room_name - обязательное поле",
          json:
            "{room_name: string, main_cam: bool, name: string,  sound: string, tracking: bool}"
        },
        {
          name: "/sources/{ip}",
          method: "DELETE",
          doc: "Удаляет источник с указанным ip"
        },
        {
          name: "/sources/{ip}",
          method: "PUT",
          doc:
            "Обновляет данные в источнике с указанным ip. room_name используется для соотношения источника к комнате",
          json:
            "{room_name: string, main_cam: bool, name: string,  sound: string, tracking: bool}"
        },
        {
          name: "/streaming-start",
          method: "POST",
          doc: `Запускает стрим по ссылке yt_url`,
          json: "{sound_ip: string, camera_ip: string, yt_url: string}"
        },
        {
          name: "/streaming-stop",
          method: "POST",
          doc: `Останавливает стрим по ссылке yt_url`,
          json: "{yt_url: string}"
        },
        {
          name: "/set-source/{room_name}/{source_type}/{ip}",
          method: "POST",
          doc:
            "Меняет источник ответственный за source_type: [main - главная камера, screen - экран, sound - звук, track - трекинг]"
        },
        {
          name: "/gcalendar-event/{room_name}",
          method: "POST",
          doc: `Создаёт событие в календаре в указанной комнате в указанное время. Формат дат: "YYYY-MM-DDTHH:mm", Например: ${new Date()
            .toISOString()
            .slice(0, 16)}`,
          json: "{start_time: string, end_time: string, summary: string}"
        },
        {
          name: "/montage-event/{room_name}",
          method: "POST",
          doc: `Создаёт событие на склеку материала в указанной комнате в указанный промежуток времени. Формат даты: "YYYY-MM-DD", Например: ${new Date()
            .toISOString()
            .slice(0, 10)}`,
          json:
            "{start_time: string, end_time: string, date: string, event_name: string}"
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
        },
        {
          name: "/api-key/{email}",
          method: "POST",
          doc: `Создаёт ключ API`
        },
        {
          name: "/api-key/{email}",
          method: "GET",
          doc: `Возвращает ключ API`
        },
        {
          name: "/api-key/{email}",
          method: "PUT",
          doc: `Обновляет ключ API`
        },
        {
          name: "/api-key/{email}",
          method: "DELETE",
          doc: `Удаляет ключ API`
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

<style scoped></style>
