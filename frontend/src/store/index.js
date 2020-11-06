import Vue from "vue";
import Vuex from "vuex";
import shared from "./shared";
import {
  authenticate,
  googleLog,
  register,
  sendResetEmail,
  resetPass,
  getUsers,
  createAPIKey,
  updateAPIKey,
  deleteAPIKey,
  getAPIKey,
  getRooms,
  getRecords,
  createMontageEvent
} from "@/api";
import { isValidToken } from "@/utils";

Vue.use(Vuex);

const state = {
  rooms: [],
  user: {},
  jwt: { token: localStorage.token || "" },
  users: []
};
const mutations = {
  TRACKING_CHANGE(state, message) {
    let room = state.rooms.find(room => {
      return room.id === message.id;
    });

    room.tracking_state = message.tracking_state;
  },
  AUTO_CONTROL_CHANGE(state, message) {
    let room = state.rooms.find(room => {
      return room.id === message.id;
    });

    room.auto_control = message.auto_control;
  },
  SET_STREAM_URL(state, message) {
    let room = state.rooms.find(room => {
      return room.name === message.name;
    });

    room.stream_url = message.stream_url;
  },
  DELETE_ROOM(state, message) {
    let i;
    state.rooms.forEach((room, index) => {
      if (room.id === message.id) {
        i = index;
        return;
      }
    });

    state.rooms.splice(i, 1);
  },
  ADD_ROOM(state, message) {
    state.rooms.push(message.room);
  },
  EDIT_ROOM(state, message) {
    let room = state.rooms.find(room => {
      return room.id === message.id;
    });
    room = message;
  },
  ADD_USER(state, message) {
    state.users.push(message.user);
  },
  DELETE_USER(state, message) {
    let i;
    state.users.forEach((user, index) => {
      if (user.id === message.id) {
        i = index;
        return;
      }
    });
    state.users.splice(i, 1);
  },
  CHANGE_ROLE(state, message) {
    let user = state.users.find(user => {
      return user.id === message.id;
    });

    user.role = message.role;
  },
  GRANT_ACCESS(state, message) {
    let user = state.users.find(user => {
      return user.id === message.id;
    });
    user.access = true;
  },
  setJwtToken(state, payload) {
    localStorage.token = payload.jwt.token;
    state.jwt = payload.jwt;
  },
  clearUserData(state) {
    localStorage.removeItem("token");
    localStorage.removeItem("googleOAuth");
    state.jwt = "";
    state.user = {};
  },
  setKey(state, payload) {
    state.user.api_key = payload.key;
  },
  setRooms(state, payload) {
    state.rooms = payload;
  },
  setRecords(state, payload) {
    state.records = payload;
  },
  setUsers(state, payload) {
    state.users = payload;
  }
};
const actions = {
  async emitTrackingStateChange({}, { room, tracking_state }) {
    await this._vm.$socket.client.emit("tracking_state_change", {
      id: room.id,
      tracking_state
    });
  },
  async socket_trackingStateChange({ commit }, message) {
    try {
      await commit("TRACKING_CHANGE", message);
      let msg = `Трекинг комнаты ${message.room_name}`;
      msg += message.tracking_state ? " включён" : " отключён";
      commit("setMessage", msg);
    } catch (error) {
      console.error(error);
    }
  },
  async socket_trackingSwitchError({ commit }, message) {
    try {
      await commit("TRACKING_CHANGE", message);
      await commit("setErrorFromText", message);
    } catch (error) {
      console.error(error);
    }
  },
  async emitAutoControlChange({}, { room, auto_control }) {
    await this._vm.$socket.client.emit("auto_control_change", {
      id: room.id,
      auto_control
    });
  },
  async socket_autoControlChange({ commit }, message) {
    try {
      await commit("AUTO_CONTROL_CHANGE", message);
      let msg = `Автоматический контроль камер комнаты ${message.room_name}`;
      msg += message.auto_control ? " включён" : " отключён";
      commit("setMessage", msg);
    } catch (error) {
      console.error(error);
    }
  },
  async emitDeleteRoom({}, { room }) {
    await this._vm.$socket.client.emit("delete_room", { id: room.id });
  },
  socket_deleteRoom({ commit }, message) {
    try {
      commit("DELETE_ROOM", message);
      commit("setMessage", `Комната ${message.name} удалена`);
    } catch (error) {}
  },
  async emitAddRoom({ commit }, { name }) {
    await this._vm.$socket.client.emit("add_room", { name });
  },
  socket_addRoom({ commit }, message) {
    try {
      commit("ADD_ROOM", message);
      commit("setMessage", `Комната ${message.room.name} создана`);
    } catch (error) {
      console.error(error);
    }
  },
  async emitEditRoom({ commit }, payload) {
    await this._vm.$socket.client.emit("edit_room", payload);
    commit("setMessage", "Изменения сохранены");
  },
  socket_editRoom({ commit }, message) {
    commit("EDIT_ROOM", message);
  },
  async emitDeleteUser({ commit }, { user }) {
    await this._vm.$socket.client.emit("delete_user", { id: user.id });
    commit("setMessage", `Пользователь ${user.email} удалён`);
  },
  socket_deleteUser({ commit }, message) {
    commit("DELETE_USER", message);
  },
  async emitChangeRole({}, { user }) {
    await this._vm.$socket.client.emit("change_role", {
      id: user.id,
      role: user.role
    });
  },
  socket_changeRole({ commit }, message) {
    commit("CHANGE_ROLE", message);
  },
  async emitGrantAccess({}, { user }) {
    await this._vm.$socket.client.emit("grant_access", { id: user.id });
  },
  socket_grantAccess({ commit }, message) {
    commit("GRANT_ACCESS", message);
  },
  socket_newUser({ commit }, message) {
    commit("ADD_USER", message);
    commit("setMessage", "Новый запрос на доступ");
  },
  async emitStreamingStart({}, payload) {
    await this._vm.$socket.client.emit("streaming_start", payload);
  },
  socket_streamingStart({ commit }, message) {
    commit("setMessage", `Начат стрим в ${message.name}`);
    commit("SET_STREAM_URL", message);
  },
  async emitStreamingStop({}, payload) {
    await this._vm.$socket.client.emit("streaming_stop", payload);
  },
  socket_streamingStop({ commit }, message) {
    commit("setMessage", `Остановлен стрим в ${message.name}`);
    commit("SET_STREAM_URL", message);
  },
  socket_error({ commit }, message) {
    commit("setErrorFromText", message);
  },
  async loadRooms({ commit, state }) {
    try {
      commit("switchLoading");
      // let res = await getRooms(state.jwt.token);
      let res = {
        data: [
          {
            auto_control: true,
            calendar:
              "auditory.ru_tc7n0tiofie384h5jvbcq3cso0@group.calendar.google.com",
            drive:
              "https://drive.google.com/drive/u/1/folders/1qZNnDJpIBZI52CcEcwAJP69QR9LyIPi2",
            id: 10,
            main_source: "172.18.191.72",
            name: "307",
            screen_source: "172.18.191.71",
            sound_source: "172.18.191.71",
            sources: [
              {
                audio: "main",
                external_id: "39726436535",
                id: 180,
                ip: "172.18.191.71",
                merge: "main",
                name: "\u041a\u043e\u0434\u0435\u0440",
                port: "80",
                room_id: 10,
                rtsp: "rtsp://172.18.191.71/0",
                time_editing: "Tue, 27 Oct 2020 10:53:43 GMT",
                tracking: "backup"
              },
              {
                audio: "no",
                external_id: "96725436510",
                id: 184,
                ip: "172.18.191.73",
                merge: "no",
                name:
                  "\u041b\u0435\u0432\u0430\u044f \u0443 \u043e\u043a\u043d\u0430",
                port: "80",
                room_id: 10,
                rtsp: "rtsp://172.18.191.73:554/Streaming/Channels/1",
                time_editing: "Tue, 27 Oct 2020 10:53:43 GMT",
                tracking: "backup"
              },
              {
                audio: "no",
                external_id: "13024928121",
                id: 177,
                ip: "172.18.191.74",
                merge: "no",
                name: "\u041f\u0440\u0430\u0432\u0430\u044f",
                port: "80",
                room_id: 10,
                rtsp: "rtsp://172.18.191.74:554/Streaming/Channels/1",
                time_editing: "Tue, 27 Oct 2020 10:53:43 GMT",
                tracking: "backup"
              },
              {
                audio: "no",
                external_id: "52425936257",
                id: 182,
                ip: "172.18.191.72",
                merge: "no",
                name: "\u041b\u0435\u0432\u0430\u044f",
                port: "80",
                room_id: 10,
                rtsp: "rtsp://172.18.191.72:554/Streaming/Channels/1",
                time_editing: "Tue, 27 Oct 2020 10:53:43 GMT",
                tracking: "backup"
              }
            ],
            stream_url: null,
            tracking_source: "172.18.191.72",
            tracking_state: false
          }
        ]
      };

      commit("setRooms", res.data);
    } catch (error) {
      commit("setError", error);
    } finally {
      commit("switchLoading");
    }
  },
  createMontageEvent({ commit }, payload) {
    try {
      createMontageEvent(payload, state.jwt.token);
      commit("setMessage", "Событие создано");
    } catch (error) {
      commit("setError", error);
    }
  },
  async getUsers({ commit, state }) {
    try {
      commit("switchLoading");
      let res = await getUsers(state.jwt.token);
      commit("setUsers", res.data);
    } catch (error) {
      commit("setError", error);
    } finally {
      commit("switchLoading");
    }
  },
  async setDataFromToken({ commit, state }) {
    try {
      commit("switchLoading");
      const tokenParts = localStorage.token.split(".");
      const body = JSON.parse(atob(tokenParts[1]));
      state.user.email = body.sub.email;
      state.user.role = body.sub.role;
      return body.sub.role;
    } catch (error) {
      commit("setError", error);
      return "";
    } finally {
      commit("switchLoading");
    }
  },
  async login({ commit, state }, userData) {
    try {
      commit("switchLoading");
      let res = await authenticate(userData);
      commit("setJwtToken", { jwt: res.data });
      const tokenParts = res.data.token.split(".");
      const body = JSON.parse(atob(tokenParts[1]));
      state.user.email = body.sub.email;
      state.user.role = body.sub.role;
      localStorage.googleOAuth = false;
      return body.sub.role;
    } catch (error) {
      commit("setError", error);
      return "";
    } finally {
      commit("switchLoading");
    }
  },
  async googleLogin({ commit, state }, userData) {
    try {
      commit("switchLoading");
      let res = await googleLog(userData);
      commit("setJwtToken", { jwt: res.data });
      const tokenParts = res.data.token.split(".");
      const body = JSON.parse(atob(tokenParts[1]));
      state.user.email = body.sub.email;
      state.user.role = body.sub.role;
      localStorage.googleOAuth = true;
      return body.sub.role;
    } catch (error) {
      commit("setError", error);
      return "";
    } finally {
      commit("switchLoading");
    }
  },
  async register({ commit }, userData) {
    try {
      commit("switchLoading");
      await register(userData);
      commit("setMessage", "Письмо с подтверждением выслано на почту");
    } catch (error) {
      commit("setError", error);
    } finally {
      commit("switchLoading");
    }
  },
  async sendResetEmail({ commit }, email) {
    try {
      commit("switchLoading");
      await sendResetEmail(email);
      commit("setMessage", "Письмо с инструкцией выслано на почту");
    } catch (error) {
      commit("setError", error);
    } finally {
      commit("switchLoading");
    }
  },
  async resetPass({ commit }, data) {
    try {
      commit("switchLoading");
      await resetPass(data);
      commit("setMessage", "Пароль обновлён");
    } catch (error) {
      commit("setError", error);
    } finally {
      commit("switchLoading");
    }
  },
  logout({ commit }) {
    commit("clearUserData");
  },
  async createKey({ commit, state }) {
    try {
      commit("switchLoading");
      let res = await createAPIKey(state.user.email, state.jwt.token);
      await commit("setKey", res.data);
    } catch (error) {
      commit("setError", error);
    } finally {
      commit("switchLoading");
    }
  },

  async updateKey({ commit, state }) {
    try {
      commit("switchLoading");
      let res = await updateAPIKey(state.user.email, state.jwt.token);
      await commit("setKey", res.data);
    } catch (error) {
      commit("setError", error);
    } finally {
      commit("switchLoading");
    }
  },
  async deleteKey({ commit, state }) {
    try {
      commit("switchLoading");
      let res = await deleteAPIKey(state.user.email, state.jwt.token);
      await commit("setKey", { key: null });
    } catch (error) {
      commit("setError", error);
    } finally {
      commit("switchLoading");
    }
  },
  async loadRecords({ commit, state }) {
    try {
      commit("switchLoading");
      // let res = await getRecords(state.user.email, state.jwt.token);
      let res = {
        data: [
          {
            date: "2020-09-01",
            done: true,
            drive_file_url:
              "https://drive.google.com/file/d/1QoCbVyyAIu-_oIHr8jBr4Org_FQmJX8h/preview",
            end_time: "14:20",
            event_id: "02j3pfnmg3cut70t7rrcsdhrhk",
            event_name: "testttt",
            id: 203,
            processing: false,
            room_name: "305",
            start_time: "13:00",
            user_email: "dakudryavtsev@miem.hse.ru"
          }
        ]
      };
      commit("setRecords", res.data);
    } catch (error) {
      commit("setError", error);
    } finally {
      commit("switchLoading");
    }
  },
  async getKey({ commit, state }) {
    try {
      let res = await getAPIKey(state.user.email, state.jwt.token);
      await commit("setKey", res.data);
    } catch (error) {
      commit("setError", error);
    }
  }
};
const getters = {
  isAutheticated(state) {
    // return isValidToken(state.jwt.token);
    return true;
  },
  user(state) {
    return state.user;
  }
};

export default new Vuex.Store({
  modules: {
    shared
  },
  state,
  mutations,
  actions,
  getters
});
