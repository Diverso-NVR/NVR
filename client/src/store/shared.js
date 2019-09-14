export default {
  state: {
    loading: false,
    error: null,
    timer: null,
    message: null
  },
  mutations: {
    switchLoading(state, payload) {
      state.loading = !state.loading;
    },
    setError(state, payload) {
      state.error = payload["response"].data.message;
    },
    clearError(state) {
      state.error = null;
    },
    setMessage(state, payload) {
      state.message = payload;
    },
    clearMessage(state) {
      state.message = null;
    },
    setTimer(state, payload) {
      state.timer = payload;
    },
    clearTimer(state) {
      clearInterval(state.timer);
      state.timer = null;
    }
  },
  actions: {
    switchLoading({ commit }) {
      commit("switchLoading");
    },
    setError({ commit }, payload) {
      commit("setError", payload);
    },
    clearError({ commit }) {
      commit("clearError");
    },
    setMessage({ commit }, payload) {
      commit("setMessage", payload);
    },
    clearMessage({ commit }) {
      commit("clearMessage");
    },
    setTimer({ commit }, payload) {
      commit("setTimer", payload);
    },
    clearTimer({ commit }) {
      commit("clearTimer");
    }
  },
  getters: {
    loading(state) {
      return state.loading;
    },
    error(state) {
      return state.error;
    },
    message(state) {
      return state.message;
    },
    timer(state) {
      return state.timer;
    }
  }
};
