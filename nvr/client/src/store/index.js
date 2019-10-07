import Vue from "vue";
import Vuex from "vuex";
import shared from "./shared";
import {
  getUsers,
  delUser,
  changeUserRole,
  grantUser,
  getRooms,
  soundSwitch,
  start,
  stop,
  del,
  add,
  edit,
  authenticate,
  register
} from "@/api";
import { isValidJwt } from "@/utils";

Vue.use(Vuex);

const state = {
  rooms: [],
  user: {},
  jwt: "",
  users: []
};
const mutations = {
  setUserData(state, payload) {
    state.userData = payload.userData;
  },
  setJwtToken(state, payload) {
    localStorage.token = payload.jwt.token;
    state.jwt = payload.jwt;
  },
  cleaUserData(state) {
    state.userData = {};
    state.jwt = "";
    localStorage.token = "";
  },
  setRooms(state, payload) {
    state.rooms = payload;

    state.rooms.forEach(room => {
      if (room.processing) room.status = "processing";
      else room.status = room.free ? "free" : "busy";
      room.timer = room.free
        ? null
        : setInterval(() => {
            room.timestamp++;
          }, 1000);
    });
  },
  setUsers(state, payload) {
    state.users = payload;
  },
  deleteUser(state, payload) {
    let i = state.users.indexOf(payload);
    state.users.splice(i, 1);
  },
  grantAccess(state, payload) {
    let i = state.users.indexOf(payload);
    state.users[i].access = true;
  },
  deleteRoom(state, payload) {
    let i = state.rooms.indexOf(payload);
    state.rooms.splice(i, 1);
  }
};
const actions = {
  async login({ commit, state }, userData) {
    try {
      commit("setUserData", { userData });
      commit("switchLoading");
      let res = await authenticate(userData);
      commit("setJwtToken", { jwt: res.data });
      const tokenParts = res.data.token.split(".");
      const body = JSON.parse(atob(tokenParts[1]));
      state.user.email = body.sub.email;
      state.user.role = body.sub.role;
      commit("switchLoading");
      return true;
    } catch (error) {
      commit("setError", error);
      commit("switchLoading");
      return false;
    }
  },
  async getUsers({ commit, state }) {
    try {
      let res = await getUsers(state.jwt.token);
      commit("setUsers", res.data);
    } catch (error) {
      commit("setError", error);
    }
  },
  async register({ commit }, userData) {
    try {
      commit("switchLoading");
      commit("setUserData", { userData });
      await register(userData);
      commit("setMessage", "Письмо с подтверждением выслано на почту");
      commit("switchLoading");
    } catch (error) {
      commit("setError", error);
      commit("switchLoading");
    }
  },
  logout({ commit }) {
    commit("cleaUserData");
  },
  async deleteUser({ commit, state }, { user }) {
    try {
      await delUser(user.id, state.jwt.token);
      commit("deleteUser", user);
      commit("setMessage", `Пользователь ${user.email} удалён`);
    } catch (error) {
      commit("setError", error);
    }
  },
  async changeRole({ commit, state }, { user }) {
    try {
      await changeUserRole({
        id: user.id,
        role: user.role,
        token: state.jwt.token
      });
    } catch (error) {
      commit("setError", error);
    }
  },
  async grantAccess({ commit, state }, { user }) {
    try {
      await grantUser(user.id, state.jwt.token);
      commit("grantAccess", user);
    } catch (error) {
      commit("setError", error);
    }
  },
  async loadRooms({ commit }) {
    try {
      let res = await getRooms();
      commit("setRooms", res.data);
    } catch (error) {
      commit("setError", error);
    }
  },
  async switchSound({ commit, state }, { room, sound }) {
    try {
      await soundSwitch({ id: room.id, sound, token: state.jwt.token });
      room.chosen_sound = sound;
    } catch (error) {
      commit("setError", error);
    }
  },
  async startRec({ commit, state }, { room }) {
    try {
      room.timer = setInterval(() => {
        room.timestamp++;
      }, 1000);
      room.free = false;
      room.status = "busy";
      await start(room.id, state.jwt.token);
    } catch (error) {
      commit("setError", error);
    }
  },
  async stopRec({ commit, state }, { room }) {
    try {
      room.timestamp = 0;
      room.status = "processing";
      clearInterval(room.timer);

      await stop(room.id, state.jwt.token);

      room.free = true;
      room.status = "free";
    } catch (error) {
      room.free = true;
      room.status = "free";
      commit("setError", error);
    }
  },
  async deleteRoom({ commit, state }, { room }) {
    try {
      await del(room.id, state.jwt.token);
      commit("deleteRoom", room);
      commit("setMessage", `Комната ${room.name} удалена`);
    } catch (error) {
      commit("setError", error);
    }
  },
  async addRoom({ commit, state }, { name }) {
    try {
      let res = await add(name, state.jwt.token);
      commit("setMessage", `Процесс создания комнаты ${res.data.name} запущен`);
    } catch (error) {
      commit("setError", error);
    }
  },
  async editRoom({ commit, state }, { id, sources }) {
    try {
      await edit({ id, sources, token: state.jwt.token });
      commit("setMessage", "Изменения сохранены");
    } catch (error) {
      commit("setError", error);
    }
  }
};
const getters = {
  isAutheticated(state) {
    return isValidJwt(state.jwt.token);
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
