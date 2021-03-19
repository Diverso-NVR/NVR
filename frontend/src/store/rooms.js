export default {
  state: {
    rooms: []
  },

  mutations: {
    TRACKING_CHANGE(state, message) {
      let room = state.rooms.find(room => {
        return room.id === message.id;
      });

      room.tracking_state = message.tracking_state;
    },
    AUTO_CONTROL_CHANGE(state, message) {
      let room = state.rooms.find(room => {
        return room.id === message.id;
      });

      room.auto_control = message.auto_control;
    },
    SET_STREAM_URL(state, message) {
      let room = state.rooms.find(room => {
        return room.name === message.name;
      });

      room.stream_url = message.stream_url;
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

    setRooms(state, payload) {
      state.rooms = payload;
    }
  }
};
