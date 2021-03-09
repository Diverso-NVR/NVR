export default {
  state: {
    records: [],
    eruditeRecords: []
  },

  mutations: {
    setRecords(state, payload) {
      state.records = payload;
    },

    setEruditeRecords(state, payload) {
      state.eruditeRecords = payload;
    },

    DateSort(state) {
      if (state.records.length === 0) return;
      state.records.sort(function(a, b) {
        var dateA = new Date(a.date),
          dateB = new Date(b.date);
        return dateB - dateA;
      });
    }
  }
};
