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
  getEruditeRecords,
  getMonitoringLink,
  getAutorecParams
} from "@/api";
import { isValidToken } from "@/utils";
import router from "@/router/index";
import {autorecDeploy} from "../api";

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
  async emitAutoControlChange({ state }, { room, auto_control }) {
    await this._vm.$socket.client.emit("auto_control_change", {
      id: room.id,
      auto_control,
      token: state.jwt.token
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
  async emitDeleteRoom({ state }, { room }) {
    await this._vm.$socket.client.emit("delete_room", {
      id: room.id,
      token: state.jwt.token
    });
  },
  socket_deleteRoom({ commit }, message) {
    try {
      commit("DELETE_ROOM", message);
      commit("setMessage", `Комната ${message.name} удалена`);
    } catch (error) {}
  },
  async emitAddRoom({ state, commit }, { name }) {
    await this._vm.$socket.client.emit("add_room", {
      name,
      token: state.jwt.token
    });
  },
  socket_addRoom({ commit }, message) {
    try {
      commit("ADD_ROOM", message);
      commit("setMessage", `Комната ${message.room.name} создана`);
    } catch (error) {
      console.error(error);
    }
  },
  async emitEditRoom({ state, commit }, payload) {
    await this._vm.$socket.client.emit("edit_room", {
      payload: payload,
      token: state.jwt.token
    });
    commit("setMessage", "Изменения сохранены");
  },
  socket_editRoom({ commit }, message) {
    commit("EDIT_ROOM", message);
  },
  async emitDeleteUser({ state, commit }, { user }) {
    await this._vm.$socket.client.emit("delete_user", {
      id: user.id,
      token: state.jwt.token
    });
    commit("setMessage", `Пользователь ${user.email} удалён`);
  },
  socket_deleteUser({ commit }, message) {
    commit("DELETE_USER", message);
  },
  async emitChangeRole({ state }, { user }) {
    await this._vm.$socket.client.emit("change_role", {
      id: user.id,
      role: user.role,
      token: state.jwt.token
    });
  },
  socket_changeRole({ commit }, message) {
    commit("CHANGE_ROLE", message);
  },
  async emitBanUser({ state, commit }, { user }) {
    await this._vm.$socket.client.emit("ban_user", {
      id: user.id,
      token: state.jwt.token
    });
    commit("setMessage", `Пользователь ${user.email} заблокирован`);
  },

  socket_blockUser({ commit }, message) {
    commit("BAN_USER", message);
  },
  async emitUnblockUser({ state, commit }, { user }) {
    await this._vm.$socket.client.emit("unblock_user", {
      id: user.id,
      token: state.jwt.token
    });
    commit("setMessage", `Пользователь ${user.email} разблокирован`);
  },
  socket_unblockUser({ commit }, message) {
    commit("UNBLOCK_USER", message);
  },
  async socket_kickBanned({ state, commit }, {}) {
    await this._vm.$socket.client.emit("kick_banned", {
      email: state.user.email,
      token: state.jwt.token
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
      email: state.user.email,
      token: state.jwt.token
    });
  },
  async socket_showOnline({ state, commit }, message) {
    commit("CHECK_ONLINE", message);
  },
  async emitGrantAccess({ state }, { user }) {
    await this._vm.$socket.client.emit("grant_access", {
      id: user.id,
      token: state.jwt.token
    });
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
  async joinRoom({ state, commit }) {
    await this._vm.$socket.client.emit("join_room", { token: state.jwt.token });
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
      email: state.user.email,
      token: state.jwt.token
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
  },
  getMonitoring({ commit, state }) {
    try {
      return getMonitoringLink(state.jwt.token);
    } catch (error) {
      commit("setError", error);
    }
  },
  getAutorecParameters({ commit, state }) {
    try {
      return getAutorecParams(state.jwt.token);
    } catch (error) {
      commit("setError", error);
    }
  },
  deployAutorec({ commit, state }, payload) {
    try {
      commit("switchLoading");
      return autorecDeploy(payload, state.jwt.token);
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
