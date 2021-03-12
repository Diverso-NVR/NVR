export default {
  state: {
    users: []
  },

  mutations: {
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
    BAN_USER(state, message) {
      let i;
      state.users.forEach((user, index) => {
        if (user.id === message.id) {
          i = index;
          return;
        }
      });
      state.users[i].banned = true;
    },
    UNBLOCK_USER(state, message) {
      let i;
      state.users.forEach((user, index) => {
        if (user.id === message.id) {
          i = index;
          return;
        }
      });
      state.users[i].banned = false;
    },
    CHECK_ONLINE(state, message) {
      let i;
      state.users.forEach((user, index) => {
        if (user.id === message.id) {
          i = index;
          return;
        }
      });
      state.users[i].online = true;
    },
    FALSE_ONLINE(state, message) {
      let i;
      state.users.forEach((user, index) => {
        if (user.id === message.id) {
          i = index;
          return;
        }
      });
      state.users[i].online = false;
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
    setUsers(state, payload) {
      state.users = payload;
    }
  }
};
