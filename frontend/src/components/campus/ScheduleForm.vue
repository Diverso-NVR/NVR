<template>
<v-dialog v-model="show" height="1000px" width="1500px" :dark="isDarkMode">
	<v-card>
		<div id="media" height="1000px" width="1280px">
			<audio id="audio" autoplay></audio>
			<video id="video" autoplay muted playsinline></video>
		</div>
		<v-btn color="black" id="start" @click="start()">Start</v-btn>
		<v-btn color="black" id="stop" @click="stop()" style="display: none">Stop</v-btn>
		<v-card-actions>
			<v-btn color="black" flat @click.stop="show=false">Закрыть</v-btn>
		</v-card-actions>
	</v-card>
</v-dialog>
</template>

<script>
	var pc = null;
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
		methods: {
			negotiate() {
				pc.addTransceiver('video', {direction: 'recvonly'});
				pc.addTransceiver('audio', {direction: 'recvonly'});
				return pc.createOffer().then(function(offer) {
					return pc.setLocalDescription(offer);
				}).then(function() {
					// wait for ICE gathering to complete
					return new Promise(function(resolve) {
						if (pc.iceGatheringState === 'complete') {
							resolve();
						} else {
							function checkState() {
								if (pc.iceGatheringState === 'complete') {
									pc.removeEventListener('icegatheringstatechange', checkState);
									resolve();
								}
							}
							pc.addEventListener('icegatheringstatechange', checkState);
						}
					});
				}).then(function() {
					var offer = pc.localDescription;
					var server_link = "https://media.auditory.ru:443/media/192"
					return fetch(server_link, {
						body: JSON.stringify({
							sdp: offer.sdp,
							type: offer.type,
						}),
						headers: {
							'Content-Type': 'application/json'
						},
						method: 'POST'
					});
				}).then(function(response) {
					return response.json();
				}).then(function(answer) {
					return pc.setRemoteDescription(answer);
				}).catch(function(e) {
					alert(e);
				});
			},

			start() {
				var config = {
					sdpSemantics: 'unified-plan'
				};

				config.iceServers = [{urls: ['stun:stun.l.google.com:19302']}];

				pc = new RTCPeerConnection(config);

				// connect audio / video
				pc.addEventListener('track', function(evt) {
					if (evt.track.kind == 'video') {
						document.getElementById('video').srcObject = evt.streams[0];
					} else {
						document.getElementById('audio').srcObject = evt.streams[0];
					}
				});

				document.getElementById('start').style.display = 'none';
				document.getElementById('stop').style.display = 'inline-block';
				this.negotiate();
			},

			stop() {
				document.getElementById('stop').style.display = 'none';

				// close peer connection
				setTimeout(function() {
					pc.close();
				}, 500);
				document.getElementById('start').style.display = 'inline-block';
			},
		},
	}
</script>