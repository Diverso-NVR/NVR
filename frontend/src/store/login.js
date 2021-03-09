import { authenticate, googleLog } from "@/api";

export default {
  actions: {
    async setDataFromToken({ commit }) {
      try {
        commit("switchLoading");
        const tokenParts = localStorage.token.split(".");
        const body = JSON.parse(atob(tokenParts[1]));
        commit("setBody", body);
        return body.sub.role;
      } catch (error) {
        commit("setError", error);
        return "";
      } finally {
        commit("switchLoading");
      }
    },

    async login({ commit }, userData) {
      try {
        commit("switchLoading");
        let res = await authenticate(userData);
        commit("setJwtToken", { jwt: res.data });
        const tokenParts = res.data.token.split(".");
        const body = JSON.parse(atob(tokenParts[1]));

        commit("setBody", body);

        localStorage.googleOAuth = false;

        return body.sub.role;
      } catch (error) {
        commit("setError", error);
        return "";
      } finally {
        commit("switchLoading");
      }
    },

    async googleLogin({ commit }, userData) {
      try {
        commit("switchLoading");
        let res = await googleLog(userData);
        commit("setJwtToken", { jwt: res.data });
        const tokenParts = res.data.token.split(".");
        const body = JSON.parse(atob(tokenParts[1]));

        commit("setBody", body);

        localStorage.googleOAuth = true;
        return body.sub.role;
      } catch (error) {
        commit("setError", error);
        return "";
      } finally {
        commit("switchLoading");
      }
    }
  }
};
