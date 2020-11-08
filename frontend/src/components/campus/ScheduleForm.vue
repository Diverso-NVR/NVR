<template>
<v-dialog v-model="show" max-width="1500px" :dark="isDarkMode">
  <v-card>
	<div id="app" max-width="1280px">
		<div class="container">
			<audio id="audio" autoplay></audio>
			<video id="video" width="100%" autoplay muted playsinline></video>
        </div>
	</div>
    <v-btn color="black" id="startbutton" onClick="c2method=true">Start</v-btn>
	<v-btn color="black" id="stopbutton" style="display: none">Stop</v-btn>
	<v-card-actions>
      <v-btn color="black" flat @click.stop="show=false">Закрыть</v-btn>
    </v-card-actions>
  </v-card>
</v-dialog>
</template>

<script src='./client.js'>
mount () {
        this.$root.$on('component1', () => {
            // ваш код идет сюда
            this.start ()
        }
    }
	</script>
<script>
export default {
  props: ['visible'],
  computed: {
	isDarkMode() {
      return this.$store.getters.isDarkMode;
    },
    show: {
      get () {
		this.$root.$emit('./ScheduleForm')
        return this.visible
      },
      set (value) {
        if (!value) {
          this.$emit('close')
        }
      }
    }
  },
  c2method: function () {
     this.$root.$emit('component1') // как это
    },
}
</script>