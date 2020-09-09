<template> 
  <div>
    <iframe v-for="record in records" :key="record.drive_file_url" width="640" height="480" v-bind:src="record.drive_file_url">
    </iframe>
  </div>
</template>

<script>
import { mapState } from "vuex";
export default {
  computed: mapState({
    records: state => state.records,
  })
};
</script>

