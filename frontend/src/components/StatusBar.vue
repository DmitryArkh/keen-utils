<template>
  <v-footer
    height="40"
    app
  >
    <v-row
      class="mx-4"
      justify="start"
    >
      <span class="mx-2">
        CPU: {{ cpuLoad }}
      </span>
      <span class="mx-2">
        RAM: {{ memory }}
      </span>
    </v-row>
  </v-footer>
</template>

<script setup>
import { computed, onMounted } from "vue";
import Api from "@/api/index.js";

const status = ref({});

const cpuLoad = computed(() => {
  if (status.value.cpuload) {
    return status.value.cpuload + '%';
  }
  return 'Loading...';
})
const memory = computed(() => {
  if (status.value.mem) {
    return status.value.mem + '%';
  }
  return 'Loading...';
});

const isFetching = ref(false);
const getStatus = async () => {
  if (isFetching.value) {
    return;
  }
  isFetching.value = true;
  try {
    status.value = await Api.getStatus();
  } finally {
    isFetching.value = false;
  }
}

onMounted(() => {
  getStatus();
  setInterval(() => {
    getStatus();
  }, 5000)
})
</script>

<style scoped lang="sass">

</style>
