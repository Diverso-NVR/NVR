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
    for (let room of state.rooms) {
      if (room.processing) room.status = "processing";
      else room.status = room.free ? "free" : "busy";
      room.timer = room.free
        ? null
        : setInterval(() => {
            room.timestamp++;
          }, 1000);
    }
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
  pushRoom(state, payload) {
    state.rooms.push(payload);
  },
  deleteRoom(state, payload) {
    let i = state.rooms.indexOf(payload);
    state.rooms.splice(i, 1);
  }
};
const actions = {
  login({ commit, state }, userData) {
    commit("setUserData", { userData });
    commit("switchLoading");
    return authenticate(userData)
      .then(res => {
        commit("setJwtToken", { jwt: res.data });
        const tokenParts = res.data.token.split(".");
        const body = JSON.parse(atob(tokenParts[1]));
        state.user.email = body.sub.email;
        state.user.role = body.sub.role;
        commit("switchLoading");
      })
      .catch(error => {
        commit("setError", error);
        commit("switchLoading");
      });
  },
  getUsers({ commit }) {
    return getUsers().then(res => {
      commit("setUsers", res.data);
    });
  },
  register({ commit }, userData) {
    commit("switchLoading");
    commit("setUserData", { userData });
    return register(userData)
      .then(res => {
        commit("setMessage", "Письмо с подтверждением выслано на почту");
        commit("switchLoading");
      })
      .catch(error => {
        commit("setError", error);
        commit("switchLoading");
      });
  },
  logout({ commit }) {
    commit("cleaUserData");
  },
  deleteUser({ commit, state }, { user }) {
    return delUser(user.id, state.jwt.token)
      .then(() => {
        commit("deleteUser", user);
        commit("setMessage", `Пользователь ${user.email} удалён`);
      })
      .catch(error => {
        commit("setError", error);
      });
  },
  changeRole({ commit, state }, { user }) {
    return changeUserRole(user.id, user.role, state.jwt.token)
      .then(() => {})
      .catch(error => {
        commit("setError", error);
      });
  },
  grantAccess({ commit, state }, { user }) {
    return grantUser(user.id, state.jwt.token)
      .then(() => {
        commit("grantAccess", user);
      })
      .catch(error => {
        commit("setError", error);
      });
  },
  loadRooms({ commit }) {
    return getRooms()
      .then(res => {
        commit("setRooms", res.data);
      })
      .catch(error => {
        commit("setError", error);
      });
  },
  switchSound({ commit, state }, { room, sound }) {
    return soundSwitch(room.id, sound, state.jwt.token)
      .then(() => {
        room.chosenSound = sound;
      })
      .catch(error => {
        commit("setError", error);
      });
  },
  startRec({ commit, state }, { room }) {
    room.timer = setInterval(() => {
      room.timestamp++;
    }, 1000);
    room.free = false;
    room.status = "busy";
    return start(room.id, state.jwt.token)
      .then(() => {})
      .catch(error => {
        commit("setError", error);
      });
  },
  stopRec({ commit, state }, { room }) {
    room.timestamp = 0;
    room.status = "processing";
    clearInterval(room.timer);
    return stop(room.id, state.jwt.token)
      .then(() => {
        room.free = true;
        room.status = "free";
      })
      .catch(error => {
        room.free = true;
        room.status = "free";
        commit("setError", error);
      });
  },
  deleteRoom({ commit, state }, { room }) {
    return del(room.id, state.jwt.token)
      .then(res => {
        commit("deleteRoom", room);
        commit("setMessage", `Комната ${room.name} удалена`);
      })
      .catch(error => {
        commit("setError", error);
      });
  },
  addRoom({ commit, state }, { name }) {
    return add(name, state.jwt.token)
      .then(res => {
        commit("pushRoom", res.data);
        commit("setMessage", `Комната ${res.data.name} успешно создана`);
      })
      .catch(error => {
        commit("setError", error);
      });
  },
  editRoom({ commit, state }, { id, sources }) {
    return edit(id, sources, state.jwt.token)
      .then(() => {
        commit("setMessage", "Изменения сохранены");
      })
      .catch(error => {
        commit("setError", error);
      });
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
