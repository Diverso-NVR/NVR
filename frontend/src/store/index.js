import Vue from "vue";
import Vuex from "vuex";
import shared from "./shared";
import users from "./users";
import rooms from "./rooms";
import records from "./records";
import login from "./login";

import {
  register,
  sendResetEmail,
  resetPass,
  getUsers,
  inviteUsers,
  createAPIKey,
  updateAPIKey,
  deleteAPIKey,
  getAPIKey,
  getRooms,
  getRecords,
  createMontageEvent,
  getEruditeRecords
} from "@/api";
import { isValidToken } from "@/utils";
import router from "@/router/index";

Vue.use(Vuex);

const state = {
  user: {},
  jwt: { token: localStorage.token || "" },
  pageNumber: 0
};

const mutations = {
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
  setBody(state, body) {
    state.user.email = body.sub.email;
    state.user.role = body.sub.role;
  }
};
const actions = {
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
  async emitBanUser({ commit }, { user }) {
    await this._vm.$socket.client.emit("ban_user", { id: user.id });
    commit("setMessage", `Пользователь ${user.email} заблокирован`);
  },
  socket_blockUser({ commit }, message) {
    commit("BAN_USER", message);
  },
  async emitUnblockUser({ commit }, { user }) {
    await this._vm.$socket.client.emit("unblock_user", { id: user.id });
    commit("setMessage", `Пользователь ${user.email} разблокирован`);
  },
  socket_unblockUser({ commit }, message) {
    commit("UNBLOCK_USER", message);
  },
  async socket_kickBanned({ state, commit }, {}) {
    await this._vm.$socket.client.emit("kick_banned", {
      email: state.user.email
    });
  },
  async socket_kickUser({ state, commit }, { email }) {
    if (state.user.email === email) {
      commit("clearUserData");
      router.push("/login");
      commit("setMessage", "Вам закрыт доступ в NVR");
    }
  },
  async socket_checkOnline({ state, commit }, {}) {
    await this._vm.$socket.client.emit("check_online", {
      email: state.user.email
    });
  },
  async socket_showOnline({ state, commit }, message) {
    commit("CHECK_ONLINE", message);
  },

  async socket_checkSockets({ state, commit }, {}) {
    commit("setMessage", "test sockets");
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
  createMontageEvent({ commit }, payload) {
    try {
      createMontageEvent(payload, state.jwt.token);
      commit("setMessage", "Событие создано");
    } catch (error) {
      commit("setError", error);
    }
  },
  async inviteUsers({ commit, state }, { emails, role }) {
    try {
      await inviteUsers(emails, role, state.jwt.token);
      commit("setMessage", "Приглашения высланы");
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
  async logout({ commit, state }) {
    await this._vm.$socket.client.emit("logout_online", {
      email: state.user.email
    });
    commit("clearUserData");
  },
  socket_falseOnline({ commit }, message) {
    commit("FALSE_ONLINE", message);
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
      await deleteAPIKey(state.user.email, state.jwt.token);
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
      let res = await getRecords(state.user.email, state.jwt.token);
      commit("setRecords", res.data);
    } catch (error) {
      commit("setError", error);
    } finally {
      commit("switchLoading");
    }
    commit("DateSort");
  },
  async loadEruditeRecords({ commit, state }) {
    try {
      commit("switchLoading");
      let res = await getEruditeRecords(state.pageNumber);
      commit("setEruditeRecords", res.data);
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
    return isValidToken(state.jwt.token);
  },
  user(state) {
    return state.user;
  }
};

export default new Vuex.Store({
  modules: {
    shared,
    users,
    rooms,
    records,
    login
  },
  state,
  mutations,
  actions,
  getters
});
