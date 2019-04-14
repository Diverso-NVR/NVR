let app = new Vue({
  el: "#app",
  data: () => ({
    cameras: []
  }),
  delimiters: ["[[", "]]"],
  computed: {
    getCamName(camera) {
      return camera.building + "-" + camera.auditorium;
    }
  },
  methods: {
    getTsSting(ts) {
      let h = Math.floor(ts / 60 / 60);
      ts -= h * 60 * 60;
      let m = Math.floor(ts / 60);
      ts -= m * 60;
      return `${h} ч. ${m} м. ${ts} с.`;
    },
    startCamera(camera) {
      axios
        .post(
          "/cameras/" +
            camera.id +
            "/" +
            camera.sound_source +
            "/" +
            camera.building +
            "/start",
          {
            sound_source: camera.sound_source
          }
        )
        .then(res => {
          camera.status = "busy";
        });
    },
    // stopTimer(camera) {
    //   axios
    //     .post(
    //       "/cameras/" +
    //         camera.id +
    //         "/" +
    //         camera.sound_source +
    //         "/" +
    //         camera.building +
    //         "/is_stopped"
    //     )
    //     .then(res => {
    //       camera.is_stopped = "yes";
    //     });
    // },
    stopCamera(camera) {
      axios
        .post(
          "/cameras/" +
            camera.id +
            "/" +
            camera.sound_source +
            "/" +
            camera.building +
            "/stop"
        )
        .then(res => {
          camera.status = "free";
          camera.is_stopped = "yes";
          camera.timestamp = 0;
        });
    }
  },
  created() {
    axios.get("/status").then(res => {
      for (building in res.data)
        res.data[building].forEach(camera => {
          this.cameras.push(
            Object.assign(
              {
                id: 0,
                building: "",
                auditorium: "",
                status: "",
                sound_source: "enc",
                is_stopped: "no"
              },
              camera
            )
          );
        });
    });
    let updateStatus = () => {
      axios.get("/status").then(res => {
        for (building in res.data)
          res.data[building].forEach(cam => {
            this.cameras.forEach(camera => {
              if (camera.id === cam.id && camera.building === cam.building) {
                camera.status = cam.status;
                camera.timestamp = cam.timestamp;
                camera.is_stopped = cam.is_stopped;
              }
            });
          });
      });
    };
    updateStatus();
    setInterval(() => {
      updateStatus();
    }, 1000);
  }
});
