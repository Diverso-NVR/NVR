export default {
  state: {
    loading: false,
    error: null,
    timer: null
  },
  mutations: {
    setLoading(state, payload) {
      state.loading = payload;
    },
    setError(state, payload) {
      state.error = payload;
    },
    clearError(state) {
      state.error = null;
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
    setLoading({ commit }, payload) {
      commit("setLoading", payload);
    },
    setError({ commit }, payload) {
      commit("setError", payload);
    },
    clearError({ commit }) {
      commit("clearError");
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
    timer(state) {
      return state.timer;
    }
  }
};
