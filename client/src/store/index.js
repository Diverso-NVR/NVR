import Vue from "vue";
import Vuex from "vuex";
import shared from "./shared";
import {
  authenticate,
  register,
  getUsers,
  createAPIKey,
  updateAPIKey,
  deleteAPIKey,
  getRooms,
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
    state.jwt = "";
    localStorage.token = "";
  },
  setKey(state, payload) {
    state.user.api_key = payload.api_key;
  },
  setRooms(state, payload) {
    state.rooms = payload;
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
  async emitStreamingStart({}, payload) {
    await this._vm.$socket.client.emit("streaming_start", payload);
  },
  socket_streamingStart({ commit }, message) {
    commit("setMessage", `Начат стрим в ${message.name}`);
  },
  async emitStreamingStop({}, payload) {
    await this._vm.$socket.client.emit("streaming_stop", payload);
  },
  socket_streamingStop({ commit }, message) {
    commit("setMessage", `Остановлен стрим в ${message.name}`);
  },
  socket_error({ commit }, message) {
    commit("setErrorFromText", message);
  },
  async loadRooms({ commit, state }) {
    try {
      commit("switchLoading");
      let res = await getRooms(state.jwt.token);
      commit("setRooms", res.data);
    } catch (error) {
      commit("setError", error);
    } finally {
      commit("switchLoading");
    }
  },
  async createMontageEvent({ commit }, payload) {
    try {
      await createMontageEvent(payload, state.jwt.token);
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
      state.user.api_key = body.sub.api_key;
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
      state.user.api_key = body.sub.api_key;
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
  logout({ commit }) {
    commit("clearUserData");
  },
  async createKey({ commit, state }) {
    try {
      commit("switchLoading");
      let res = await createAPIKey(state.user.email, state.jwt.token);
      commit("setKey", res.data);
      return res;
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
      commit("setKey", res.data);
      return res;
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
      commit("setKey", res.data);
    } catch (error) {
      commit("setError", error);
    } finally {
      commit("switchLoading");
    }
  }
};
const getters = {
  isAutheticated(state) {
    return isValidToken(state.jwt.token);
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
