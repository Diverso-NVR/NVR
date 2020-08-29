<template> 
    <div>
<iframe v-for="record in records" :key="link" width="640" height="480" v-bind:src="record">
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

