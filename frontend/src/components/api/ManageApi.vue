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
                    <li>Включить/Отключить автовозрат камер на default позиции</li>
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
            >Создать ключ API</v-btn>
          </template>

          <template v-else>
            <v-card>
              <v-card-title primary-title>
                <h3 class="title mb-0">
                  Ваш ключ API:
                  <b class="subheading">{{ user.api_key }}</b>
                </h3>
              </v-card-title>

              <v-card-text>
                <div class="subheading">
                  <div>API url: {{ API_URL }}</div>
                  <div>Добавьте в headers вашего запроса: {"key": "{{ user.api_key }}"}</div>
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
              <v-expansion-panel-content v-for="(route, i) in routes" :key="i">
                <template v-slot:header>
                  <div>
                    <b>{{ route.method }}</b>
                    {{ route.name }}
                  </div>
                </template>

                <template>
                  <v-card :color="isDarkMode ? '#2d2d2d' : '#F5F5F5'">
                    <v-card-text>
                      <div class="subheading">{{ route.doc }}</div>
                    </v-card-text>
                  </v-card>
                  <v-card v-if="route.request" :color="isDarkMode ? '#2d2d2d' : '#F5F5F5'">
                    <v-card-text>
                      <div class="font-weight-bold">Request</div>
                      <pre>{{ route.request }}</pre>
                    </v-card-text>
                  </v-card>
                  <v-card v-if="route.responses" :color="isDarkMode ? '#2d2d2d' : '#F5F5F5'">
                    <div class="font-weight-bold ml-3">Responses</div>
                    <v-card-text v-for="(response, i) in route.responses" :key="i">
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
  {"token": string}`
            },
            {
              code: 401,
              body: `
  {"error": "Неверные данные", "authenticated": false}`
            },
            {
              code: 401,
              body: `
  {"error": "Почта не подтверждена", "authenticated": false}`
            },
            {
              code: 401,
              body: `
  {
    "error": "Администратор ещё не открыл доступ для этого аккаунта",
    "authenticated": false
  }`
            }
          ]
        },
        {
          name: "/rooms/",
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
      "tracking_source": "admin:Supervisor@172.18.191.23",
      "tracking_state": false
    }
  ]`
            }
          ]
        },
        {
          name: "/rooms/{room_name}",
          method: "GET",
          doc: "Возвращает комнату с указанным room_name",
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
    "tracking_source": "admin:Supervisor@172.18.191.23",
    "tracking_state": false
  }`
            },
            {
              code: 400,
              body: `
  Bad request`
            }
          ]
        },
        {
          name: "/rooms/{room_name}",
          method: "POST",
          doc: "Создаёт комнату с указанным room_name",
          responses: [
            {
              code: 201,
              body: `
  {"message": "Started creating '{room_name}'"}`
            },
            {
              code: 400,
              body: `
  Bad request`
            },
            {
              code: 409,
              body: `
  {"error": "Room '{room_name}' already exist"}`
            }
          ]
        },
        {
          name: "/rooms/{room_name}",
          method: "DELETE",
          doc: "Удаляет комнату с указанным room_name",
          responses: [
            {
              code: 200,
              body: `
  {"message": "Room deleted"}`
            },
            {
              code: 400,
              body: `
  Bad request`
            }
          ]
        },
        {
          name: "/rooms/{room_name}",
          method: "PUT",
          doc: "Изменяет данные об источниках в комнате с room_name",
          request: `
  {
    "sources": []
  }`,
          responses: [
            {
              code: 200,
              body: `
  {"message": "Room edited"}`
            }
          ]
        },
        {
          name: "/sources/",
          method: "GET",
          doc: "Возвращает массив словарей данных об источниках",
          responses: [
            {
              code: 200,
              body: `
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
            }
          ]
        },
        {
          name: "/sources/{ip}",
          method: "GET",
          doc: "Возвращает источник с указанным ip",
          responses: [
            {
              code: 200,
              body: `
  {
    "id": 2,
    "ip": "admin:Supervisor@172.18.199.30",
    "name": "у доски слева на зал",
    "room_id": 1
  }`
            }
          ]
        },
        {
          name: "/sources/{ip}",
          method: "POST",
          doc: "Создаёт источник с указанным ip. room_name - обязательное поле",
          request: `
  {
    "room_name": string,
    main_cam: bool,
    "name": string,
    "sound": string,
    "tracking": bool
  }`,
          responses: [
            {
              code: 200,
              body: `
  {"message": "Added"}`
            },
            {
              code: 400,
              body: `
  Bad request`
            }
          ]
        },
        {
          name: "/sources/{ip}",
          method: "DELETE",
          doc: "Удаляет источник с указанным ip",
          responses: [
            {
              code: 200,
              body: `
  {"message": "Deleted"}`
            },
            {
              code: 400,
              body: `
  Bad request`
            }
          ]
        },
        {
          name: "/sources/{ip}",
          method: "PUT",
          doc:
            "Обновляет данные в источнике с указанным ip. room_name используется для соотношения источника к комнате",
          request: `
  {
    "room_name": string,
    "main_cam": bool,
    "name": string,
    "sound": string,
    "tracking": bool
  }`,
          responses: [
            {
              code: 200,
              body: `
  {"message": "Updated"}`
            },
            {
              code: 400,
              body: `
  Bad request`
            }
          ]
        },
        {
          name: "/auto-control/{room_name}",
          method: "POST",
          doc:
            "Включает или отключает автоматический контроль камер в указанной комнате",
          request: `
  {"auto_control": bool}`,
          responses: [
            {
              code: 200,
              body: `
  {"message": "Automatic control within room {room_name} has been set to {auto_control}"}`
            },
            {
              code: 400,
              body: `
  {"error": "Boolean value not provided"}`
            },
            {
              code: 404,
              body: `
  {"error": "Room {room_name} not found"}`
            }
          ]
        },
        {
          name: "/streaming-start/{room_name}",
          method: "POST",
          doc: `Запускает стрим`,
          request: `
  {
    "sound_ip": string,
    "camera_ip": string,
    "title": string
  }`,
          responses: [
            {
              code: 200,
              body: `
  {
    "message": "Streaming started"
  }`
            },
            {
              code: 500,
              body: `
  {"error": "Unable to start stream"}`
            }
          ]
        },
        {
          name: "/streaming-stop/{room_name}",
          method: "POST",
          doc: `Останавливает стрим`,
          responses: [
            {
              code: 200,
              body: `
  {"message": "Streaming stopped"}`
            }
          ]
        },
        {
          name: "/set-source/{room_name}/{source_type}/{ip}",
          method: "POST",
          doc:
            "Меняет источник ответственный за source_type: [main - главная камера, screen - экран, sound - звук, track - трекинг]",
          responses: [
            {
              code: 200,
              body: `
  {"message": "Source set"}`
            },
            {
              code: 400,
              body: `
  Bad request`
            }
          ]
        },
        {
          name: "/gcalendar-event/{room_name}",
          method: "POST",
          doc: `Создаёт событие в календаре в указанной комнате в указанное время. Формат дат: "YYYY-MM-DDTHH:mm", Например: ${new Date()
            .toISOString()
            .slice(0, 16)}`,
          request: `
  {
    "start_time": string,
    "end_time": string,
    "summary": string
  }`,
          responses: [
            {
              code: 201,
              body: `
  {"message": "Successfully created event: {event_link}"}`
            },
            {
              code: 400,
              body: `
  Bad request`
            }
          ]
        },
        {
          name: "/gdrive-upload/{room_name}",
          method: "POST",
          doc: `Загружает переданный в запросе видео-файл в папку комнаты. Важно чтобы файл был в формате YYYY-MM-DD_HH:mm`,
          responses: [
            {
              code: 201,
              body: `
  {"message": "Upload to disk started"}`
            },
            {
              code: 400,
              body: `
  Bad request`
            }
          ]
        },
        {
          name: "/montage-event/{room_name}",
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
  {"message": "Record event created"}`
            },
            {
              code: 400,
              body: `
  Bad request`
            }
          ]
        },
        {
          name: "/tracking/{room_name}",
          method: "POST",
          doc: `Взаимодействие с трекингом в указанной комнате. command принимает значения "start", "stop", "status"`,
          request: `
  {
    "command": string
  }`,
          responses: [
            {
              code: 200,
              body: `
  {}`
            },
            {
              code: 400,
              body: `
  Bad request`
            },
            {
              code: 500,
              body: `
  {"error": string}`
            }
          ]
        },
        {
          name: "/api-key/{email}",
          method: "POST",
          doc: `Создаёт ключ API`,
          responses: [
            {
              code: 201,
              body: `
  {"key": string}`
            }
          ]
        },
        {
          name: "/api-key/{email}",
          method: "GET",
          doc: `Возвращает ключ API`,
          responses: [
            {
              code: 200,
              body: `
  {"key": string}`
            }
          ]
        },
        {
          name: "/api-key/{email}",
          method: "PUT",
          doc: `Обновляет ключ API`,
          responses: [
            {
              code: 202,
              body: `
  {"key": string}`
            }
          ]
        },
        {
          name: "/api-key/{email}",
          method: "DELETE",
          doc: `Удаляет ключ API`,
          responses: [
            {
              code: 200,
              body: `
  {'message': "API key deleted"}`
            }
          ]
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
    },
    user() {
      return this.$store.getters.user;
    }
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
          ? [...Array(this.routes.length).keys()].map(_ => true)
          : [];
    }
  },
  beforeCreate() {
    this.$store.dispatch("getKey");
  }
};
</script>

<style scoped></style>
