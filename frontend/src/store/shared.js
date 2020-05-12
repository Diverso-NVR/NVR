export default {
  state: {
    loading: false,
    error: "",
    timer: null,
    message: "",
    isDarkMode: false
  },
  mutations: {
    switchLoading(state) {
      state.loading = !state.loading;
    },
    setError(state, payload) {
      try {
        state.error = payload["response"].data.error;
      } catch (error) {}
    },
    setErrorFromText(state, payload) {
      state.error = payload.error;
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
    },
    switchColorMode(state) {
      state.isDarkMode = !state.isDarkMode;
      localStorage.isDarkMode = state.isDarkMode;
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
    },
    switchColorMode({ commit }) {
      commit("switchColorMode");
    },
    setColorMode({ state }) {
      state.isDarkMode = localStorage.isDarkMode === "true" ? true : false;
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
    },
    isDarkMode(state) {
      return state.isDarkMode;
    }
  }
};
