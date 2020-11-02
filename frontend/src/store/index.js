import Vue from "vue";
import Vuex from "vuex";
import shared from "./shared";
import {
  authenticate,
  googleLog,
  register,
  sendResetEmail,
  resetPass,
  getUsers,
  createAPIKey,
  updateAPIKey,
  deleteAPIKey,
  getAPIKey,
  getRooms,
  getRecords,
  createMontageEvent,
} from "@/api";
import { isValidToken } from "@/utils";

Vue.use(Vuex);

const state = {
  rooms: [],
  user: {},
  jwt: { token: localStorage.token || "" },
  users: [],
};
const mutations = {
  TRACKING_CHANGE(state, message) {
    let room = state.rooms.find((room) => {
      return room.id === message.id;
    });

    room.tracking_state = message.tracking_state;
  },
  AUTO_CONTROL_CHANGE(state, message) {
    let room = state.rooms.find((room) => {
      return room.id === message.id;
    });

    room.auto_control = message.auto_control;
  },
  SET_STREAM_URL(state, message) {
    let room = state.rooms.find((room) => {
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
    let room = state.rooms.find((room) => {
      return room.id === message.id;
    });
    room = message;
  },
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
  CHANGE_ROLE(state, message) {
    let user = state.users.find((user) => {
      return user.id === message.id;
    });

    user.role = message.role;
  },
  GRANT_ACCESS(state, message) {
    let user = state.users.find((user) => {
      return user.id === message.id;
    });
    user.access = true;
  },
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
  setRooms(state, payload) {
    state.rooms = payload;
  },
  setRecords(state, payload) {
    state.records = payload;
  },
  setUsers(state, payload) {
    state.users = payload;
  },
};
const actions = {
  async emitTrackingStateChange({}, { room, tracking_state }) {
    await this._vm.$socket.client.emit("tracking_state_change", {
      id: room.id,
      tracking_state,
    });
  },
  async socket_trackingStateChange({ commit }, message) {
    try {
      await commit("TRACKING_CHANGE", message);
      let msg = `Трекинг комнаты ${message.room_name}`;
      msg += message.tracking_state ? " включён" : " отключён";
      commit("setMessage", msg);
    } catch (error) {
      console.error(error);
    }
  },
  async socket_trackingSwitchError({ commit }, message) {
    try {
      await commit("TRACKING_CHANGE", message);
      await commit("setErrorFromText", message);
    } catch (error) {
      console.error(error);
    }
  },
  async emitAutoControlChange({}, { room, auto_control }) {
    await this._vm.$socket.client.emit("auto_control_change", {
      id: room.id,
      auto_control,
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
      role: user.role,
    });
  },
  socket_changeRole({ commit }, message) {
    commit("CHANGE_ROLE", message);
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
  async emitStreamingStart({}, payload) {
    await this._vm.$socket.client.emit("streaming_start", payload);
  },
  socket_streamingStart({ commit }, message) {
    commit("setMessage", `Начат стрим в ${message.name}`);
    commit("SET_STREAM_URL", message);
  },
  async emitStreamingStop({}, payload) {
    await this._vm.$socket.client.emit("streaming_stop", payload);
  },
  socket_streamingStop({ commit }, message) {
    commit("setMessage", `Остановлен стрим в ${message.name}`);
    commit("SET_STREAM_URL", message);
  },
  socket_error({ commit }, message) {
    commit("setErrorFromText", message);
  },
  async loadRooms({ commit, state }) {
    try {
      commit("switchLoading");
      // let res = await getRooms(state.jwt.token);
      let res = {
        data: [{"auto_control":true,"calendar":"auditory.ru_86kaj1tmqd62i49aubdd1u12h0@group.calendar.google.com","drive":"https://drive.google.com/drive/u/1/folders/1hjRds9U673yqZq6sjPuoLT3R0-zzr-B3","id":5,"main_source":"172.18.212.10","name":"520","screen_source":"172.18.212.24","sound_source":"172.18.212.24","sources":[{"audio":"main","external_id":"67689296401","id":162,"ip":"172.18.212.16","merge":"main","name":"\u0418\u0433\u0440\u0443\u0448\u0435\u0447\u043d\u0430\u044f","port":"80","room_id":5,"rtsp":"rtsp://172.18.212.16:554/live/ch0","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"main","external_id":"37885855134","id":155,"ip":"172.18.212.14","merge":"main","name":"\u041a\u043e\u0440\u043f\u0443\u0441\u043d\u0430\u044f Sunell","port":"80","room_id":5,"rtsp":"rtsp://172.18.212.14:554/snl/live/1/1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"main","external_id":"65588844116","id":161,"ip":"172.18.212.10","merge":"main","name":"Axis \u043d\u0430 \u043f\u043e\u0442\u043e\u043b\u043a\u0435","port":"80","room_id":5,"rtsp":"rtsp://172.18.212.10/onvif-media/media.amp?profile=profile_1_h264&sessiontimeout=60&streamtype=unicast","time_editing":"Tue, 27 Oct 2020 10:53:44 GMT","tracking":"backup"},{"audio":"main","external_id":"98592232270","id":165,"ip":"172.18.212.17","merge":"main","name":"\u041b\u0430\u0431\u043e\u0440\u0430\u0442\u043e\u0440\u043d\u0430\u044f Hikvision","port":"80","room_id":5,"rtsp":"rtsp://172.18.212.17:554/Streaming/Channels/101?transportmode=unicast&profile=Profile_1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"no","external_id":"3458535622","id":154,"ip":"172.18.212.12","merge":"no","name":"Yunch 10x","port":"80","room_id":5,"rtsp":"rtsp://172.18.212.12:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"main","external_id":"10581906591","id":149,"ip":"172.18.212.24","merge":"main","name":"\u041a\u043e\u0434\u0435\u0440/\u0414\u0435\u043a\u043e\u0434\u0435\u0440","port":"80","room_id":5,"rtsp":"rtsp://172.18.212.24/stream0","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"}],"stream_url":null,"tracking_source":null,"tracking_state":false},{"auto_control":true,"calendar":"auditory.ru_tc7n0tiofie384h5jvbcq3cso0@group.calendar.google.com","drive":"https://drive.google.com/drive/u/1/folders/1qZNnDJpIBZI52CcEcwAJP69QR9LyIPi2","id":10,"main_source":"172.18.191.72","name":"307","screen_source":"172.18.191.71","sound_source":"172.18.191.71","sources":[{"audio":"main","external_id":"39726436535","id":180,"ip":"172.18.191.71","merge":"main","name":"\u041a\u043e\u0434\u0435\u0440","port":"80","room_id":10,"rtsp":"rtsp://172.18.191.71/0","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"no","external_id":"96725436510","id":184,"ip":"172.18.191.73","merge":"no","name":"\u041b\u0435\u0432\u0430\u044f \u0443 \u043e\u043a\u043d\u0430","port":"80","room_id":10,"rtsp":"rtsp://172.18.191.73:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"no","external_id":"13024928121","id":177,"ip":"172.18.191.74","merge":"no","name":"\u041f\u0440\u0430\u0432\u0430\u044f","port":"80","room_id":10,"rtsp":"rtsp://172.18.191.74:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"no","external_id":"52425936257","id":182,"ip":"172.18.191.72","merge":"no","name":"\u041b\u0435\u0432\u0430\u044f","port":"80","room_id":10,"rtsp":"rtsp://172.18.191.72:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"}],"stream_url":null,"tracking_source":"172.18.191.72","tracking_state":false},{"auto_control":true,"calendar":"auditory.ru_v4gcsvi2b77302qq42s5c5ovmc@group.calendar.google.com","drive":"https://drive.google.com/drive/u/1/folders/1xAwJGYjqNGtDnFpT9av44fs6JoY2ZWGR","id":2,"main_source":"172.18.200.55","name":"00A","screen_source":"172.18.200.27","sound_source":"172.18.200.27","sources":[{"audio":"no","external_id":"69189797610","id":163,"ip":"172.18.200.51","merge":"no","name":"\u0417\u0430\u043b-\u043b\u0435\u0432\u0430\u044f","port":"80","room_id":2,"rtsp":"rtsp://172.18.200.51:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"main","external_id":"50286355720","id":156,"ip":"172.18.200.27","merge":"main","name":"\u041f\u0440\u0435\u0437\u0435\u043d\u0442\u0430\u0446\u0438\u044f","port":"80","room_id":2,"rtsp":"rtsp://172.18.200.27/0","time_editing":"Tue, 27 Oct 2020 10:53:44 GMT","tracking":"backup"},{"audio":"no","external_id":"62787843427","id":159,"ip":"172.18.200.53","merge":"no","name":"\u041b\u0435\u0432\u0430\u044f","port":"80","room_id":2,"rtsp":"rtsp://172.18.200.53:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:44 GMT","tracking":"backup"},{"audio":"no","external_id":"58387344371","id":158,"ip":"172.18.200.55","merge":"no","name":"\u0421\u0440\u0435\u0434\u043d\u044f\u044f","port":"80","room_id":2,"rtsp":"rtsp://172.18.200.55:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"no","external_id":"64788344669","id":160,"ip":"172.18.200.54","merge":"no","name":"\u0421\u043e \u0441\u0446\u0435\u043d\u044b","port":"80","room_id":2,"rtsp":"rtsp://172.18.200.54:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"}],"stream_url":null,"tracking_source":"172.18.200.55","tracking_state":false},{"auto_control":true,"calendar":"auditory.ru_bh97qh4gkkrbnr2q87jp8l7rus@group.calendar.google.com","drive":"https://drive.google.com/drive/u/1/folders/14JWOQs_dW8aIHpQZfO-KQ9HKQVqrwLN9","id":6,"main_source":"172.18.191.102","name":"505a","screen_source":"172.18.191.50","sound_source":"172.18.191.50","sources":[{"audio":"main","external_id":"8059173287","id":187,"ip":"172.18.191.104","merge":"main","name":"\u041a\u0430\u043c\u0435\u0440\u0430 10x  \u043f\u0440\u0430\u0432\u0430\u044f","port":"80","room_id":6,"rtsp":"rtsp://172.18.191.104:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:44 GMT","tracking":"backup"},{"audio":"main","external_id":null,"id":167,"ip":"172.18.191.50","merge":"main","name":"\u041a\u043e\u0434\u0435\u0440/\u0414\u0435\u043a\u043e\u0434\u0435\u0440","port":"80","room_id":6,"rtsp":"rtsp://172.18.191.50:554/0","time_editing":null,"tracking":"backup"},{"audio":"main","external_id":null,"id":168,"ip":"192.168.15.53","merge":"main","name":"\u041a\u0430\u043c\u0435\u0440\u0430 4k \u0432 \u0446\u0435\u043d\u0442\u0440\u0435","port":"80","room_id":6,"rtsp":null,"time_editing":null,"tracking":"backup"},{"audio":"main","external_id":"15582400821","id":186,"ip":"172.18.191.102","merge":"main","name":"\u041a\u0430\u043c\u0435\u0440\u0430 10x  \u043b\u0435\u0432\u0430\u044f","port":"80","room_id":6,"rtsp":"rtsp://172.18.191.102:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"main","external_id":"18783400109","id":185,"ip":"172.18.191.101","merge":"main","name":"\u041a\u043e\u0434\u0435\u0440/\u0414\u0435\u043a\u043e\u0434\u0435\u0440","port":"80","room_id":6,"rtsp":"rtsp://172.18.191.101:554/0","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"}],"stream_url":null,"tracking_source":"172.18.191.51","tracking_state":false},{"auto_control":true,"calendar":"auditory.ru_1vundejffhnl1ier4nhgctc39k@group.calendar.google.com","drive":"https://drive.google.com/drive/u/1/folders/1INi7xUvLhPJW0as3HO8ugdCgsO-HwfxB","id":11,"main_source":"172.18.191.62","name":"306","screen_source":"172.18.191.61","sound_source":"172.18.191.61","sources":[{"audio":"no","external_id":"25623428792","id":178,"ip":"172.18.191.63","merge":"no","name":"\u041b\u0435\u0432\u0430\u044f \u0443 \u043e\u043a\u043d\u0430","port":"80","room_id":11,"rtsp":"rtsp://172.18.191.63:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:44 GMT","tracking":"backup"},{"audio":"no","external_id":"36423928449","id":179,"ip":"172.18.191.62","merge":"no","name":"\u041b\u0435\u0432\u0430\u044f","port":"80","room_id":11,"rtsp":"rtsp://172.18.191.62:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"no","external_id":"4122928870","id":181,"ip":"172.18.191.64","merge":"no","name":"\u041f\u0440\u0430\u0432\u0430\u044f","port":"80","room_id":11,"rtsp":"rtsp://172.18.191.64:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:44 GMT","tracking":"backup"},{"audio":"main","external_id":"66124428684","id":183,"ip":"172.18.191.61","merge":"main","name":"\u041a\u043e\u0434\u0435\u0440","port":"80","room_id":11,"rtsp":"rtsp://172.18.191.61/0","time_editing":"Tue, 27 Oct 2020 10:53:44 GMT","tracking":"backup"}],"stream_url":null,"tracking_source":"172.18.191.62","tracking_state":false},{"auto_control":true,"calendar":null,"drive":"https://drive.google.com/drive/u/1/folders/1AHYh62Q18rtUbii5IlwI_tRIjmBXXbl-","id":17,"main_source":null,"name":"CCTV","screen_source":null,"sound_source":null,"sources":[{"audio":"main","external_id":"72518932519","id":192,"ip":"172.18.191.200","merge":"main","name":"505-\u0421\u0442\u0443\u0434\u0438\u044f","port":"8899","room_id":17,"rtsp":"rtsp://172.18.191.200:554/user=admin_password=BhcGS01Q_channel=1_stream=0.sdp?real_stream","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"main","external_id":"42784680326","id":191,"ip":"172.18.191.201","merge":"main","name":"505-\u0430\u043f\u043f\u0430\u0440\u0430\u0442\u043d\u0430\u044f","port":"8899","room_id":17,"rtsp":"rtsp://172.18.191.201:554/user=admin_password=BhcGS01Q_channel=1_stream=0.sdp?real_stream","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"}],"stream_url":null,"tracking_source":null,"tracking_state":false},{"auto_control":true,"calendar":"auditory.ru_rgc7bjcechrr0f2hnmacnmer58@group.calendar.google.com","drive":"https://drive.google.com/drive/u/1/folders/1zAPs-2GP_SQj6tHLWwgohjuwCS_7o3yu","id":1,"main_source":"172.18.191.24","name":"504","screen_source":"172.18.191.21","sound_source":"172.18.191.21","sources":[{"audio":"no","external_id":"2858435516","id":152,"ip":"172.18.191.23","merge":"no","name":"\u041f\u0440\u0430\u0432\u0430\u044f","port":"9000","room_id":1,"rtsp":"rtsp://172.18.191.23:554/user=admin_password=BhcGS01Q_channel=1_stream=0.sdp?real_stream","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"main"},{"audio":"no","external_id":"30284856195","id":153,"ip":"172.18.191.26","merge":"no","name":"\u0417\u0430\u043b","port":"80","room_id":1,"rtsp":"rtsp://172.18.191.26:554","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"no","external_id":"5718684418","id":157,"ip":"172.18.191.25","merge":"no","name":"\u041b\u0435\u0432\u0430\u044f","port":"80","room_id":1,"rtsp":"rtsp://172.18.191.25:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"no","external_id":"24283899994","id":151,"ip":"172.18.191.24","merge":"no","name":"\u0421\u0440\u0435\u0434\u043d\u044f\u044f","port":"80","room_id":1,"rtsp":"rtsp://172.18.191.24:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"no","external_id":"6990296193","id":164,"ip":"172.18.191.22","merge":"no","name":"\u0417\u0430\u043b \u043e\u0431\u0449\u0430\u044f","port":"9000","room_id":1,"rtsp":"rtsp://172.18.191.22:554/user=admin_password=BhcGS01Q_channel=1_stream=0.sdp?real_stream","time_editing":"Tue, 27 Oct 2020 10:53:44 GMT","tracking":"backup"},{"audio":"main","external_id":"16682899584","id":150,"ip":"172.18.191.21","merge":"main","name":"\u041f\u0440\u0435\u0437\u0435\u043d\u0442\u0430\u0446\u0438\u044f","port":"80","room_id":1,"rtsp":"rtsp://172.18.191.21/0","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"}],"stream_url":null,"tracking_source":"172.18.191.23","tracking_state":false},{"auto_control":true,"calendar":"auditory.ru_i494qcfm6h6v4qarkk902u9j6g@group.calendar.google.com","drive":"https://drive.google.com/drive/u/1/folders/1i3j8a60gk-RtX6vS3md8q98xtbc5VSk-","id":13,"main_source":"172.18.191.52","name":"305","screen_source":"172.18.191.54","sound_source":"172.18.191.51","sources":[{"audio":"no","external_id":"27965497981","id":169,"ip":"172.18.191.53","merge":"no","name":"\u041b\u0435\u0432\u0430\u044f \u0443 \u043e\u043a\u043d\u0430","port":"80","room_id":13,"rtsp":"rtsp://172.18.191.53:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"no","external_id":"11664997306","id":189,"ip":"172.18.191.54","merge":"no","name":"\u041f\u0440\u0430\u0432\u0430\u044f","port":"80","room_id":13,"rtsp":"rtsp://172.18.191.54:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"main","external_id":"20366497422","id":166,"ip":"172.18.191.51","merge":"main","name":"\u041a\u043e\u0434\u0435\u0440","port":"80","room_id":13,"rtsp":"rtsp://172.18.191.51/0","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"},{"audio":"no","external_id":"46065997911","id":190,"ip":"172.18.191.52","merge":"no","name":"\u041b\u0435\u0432\u0430\u044f","port":"80","room_id":13,"rtsp":"rtsp://172.18.191.52:554/Streaming/Channels/1","time_editing":"Tue, 27 Oct 2020 10:53:43 GMT","tracking":"backup"}],"stream_url":null,"tracking_source":"172.18.191.52","tracking_state":false},{"auto_control":true,"calendar":"auditory.ru_b9ihlf2otu9pfdkfl3hvjak6u8@group.calendar.google.com","drive":"https://drive.google.com/drive/u/1/folders/1xhUO3HXmOdGvvssIaghO0x-38_cj4JwC","id":16,"main_source":null,"name":"301","screen_source":null,"sound_source":null,"sources":[],"stream_url":null,"tracking_source":null,"tracking_state":false}]
      }
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
  async setDataFromToken({ commit, state }) {
    try {
      commit("switchLoading");
      const tokenParts = localStorage.token.split(".");
      const body = JSON.parse(atob(tokenParts[1]));
      state.user.email = body.sub.email;
      state.user.role = body.sub.role;
      return body.sub.role;
    } catch (error) {
      commit("setError", error);
      return "";
    } finally {
      commit("switchLoading");
    }
  },
  async login({ commit, state }, userData) {
    try {
      commit("switchLoading");
      let res = await authenticate(userData);
      commit("setJwtToken", { jwt: res.data });
      const tokenParts = res.data.token.split(".");
      const body = JSON.parse(atob(tokenParts[1]));
      state.user.email = body.sub.email;
      state.user.role = body.sub.role;
      localStorage.googleOAuth = false;
      return body.sub.role;
    } catch (error) {
      commit("setError", error);
      return "";
    } finally {
      commit("switchLoading");
    }
  },
  async googleLogin({ commit, state }, userData) {
    try {
      commit("switchLoading");
      let res = await googleLog(userData);
      commit("setJwtToken", { jwt: res.data });
      const tokenParts = res.data.token.split(".");
      const body = JSON.parse(atob(tokenParts[1]));
      state.user.email = body.sub.email;
      state.user.role = body.sub.role;
      localStorage.googleOAuth = true;
      return body.sub.role;
    } catch (error) {
      commit("setError", error);
      return "";
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
  logout({ commit }) {
    commit("clearUserData");
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
      let res = await deleteAPIKey(state.user.email, state.jwt.token);
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
  },
  async getKey({ commit, state }) {
    try {
      let res = await getAPIKey(state.user.email, state.jwt.token);
      await commit("setKey", res.data);
    } catch (error) {
      commit("setError", error);
    }
  },
};
const getters = {
  isAutheticated(state) {
    // return isValidToken(state.jwt.token);
    return true;
  },
  user(state) {
    state.user.role = 'editor';
    return state.user;
  },
};

export default new Vuex.Store({
  modules: {
    shared,
  },
  state,
  mutations,
  actions,
  getters,
});
