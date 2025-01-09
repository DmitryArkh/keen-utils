<template>
  <div class="d-flex flex-column ga-2 align-end">
    <div
      v-if="status"
      class="flex-row d-flex align-center"
    >
      <v-badge
        dot
        offset-y="-3"
        :color="status === 'running' ? 'success' : 'error'"
      />
      <div class="ml-2 text-medium-emphasis text-h6 text-uppercase">
        {{ status }}
      </div>
    </div>

    <div class="d-flex align-center ga-4">
      <v-btn
        v-if="status === 'stopped'"
        variant="flat"
        color="primary"
        prepend-icon="mdi-play"
        :loading="isStarting"
        @click="start"
      >
        Start
      </v-btn>

      <v-btn
        v-if="status === 'running'"
        variant="flat"
        color="primary"
        prepend-icon="mdi-restart"
        :loading="isRestarting"
        @click="restart"
      >
        Restart
      </v-btn>

      <v-btn
        v-if="status === 'running'"
        variant="flat"
        color="error"
        prepend-icon="mdi-stop"
        :loading="isStopping"
        @click="stop"
      >
        Stop
      </v-btn>
    </div>
  </div>

  <v-snackbar
    v-model="snackbar"
    :color="snackbarColor"
  >
    {{ snackbarMessage }}
    <template #actions>
      <v-btn
        variant="text"
        @click="snackbar = false"
      >
        Close
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script setup>
import XKeen from "@/api/xkeen.js";

const status = ref(null)

const getStatus = async () => {
  status.value = (await XKeen.getStatus()).status;
};

onMounted(() => {
  getStatus();
  setInterval(() => {
    getStatus();
  }, 5000);
});

const isStarting = ref(false);
const start = async () => {
  if (isChangingStatus.value) {
    return;
  }
  isStarting.value = true;
  try {
    await XKeen.start();
    snackbarMessage.value = 'XKeen started.';
    snackbarColor.value = 'success';
    snackbar.value = true;
  } catch (e) {
    snackbarMessage.value = e.message;
    snackbarColor.value = 'error';
    snackbar.value = true;
  } finally {
    isStarting.value = false;
    getStatus();
  }
};

const isRestarting = ref(false);
const restart = async () => {
  if (isChangingStatus.value) {
    return;
  }
  isRestarting.value = true;
  try {
    await XKeen.restart();
    snackbarMessage.value = 'XKeen restarted.';
    snackbarColor.value = 'success';
    snackbar.value = true;
  } catch (e) {
    snackbarMessage.value = e.message;
    snackbarColor.value = 'error';
    snackbar.value = true;
  } finally {
    isRestarting.value = false;
    getStatus();
  }
};

const isStopping = ref(false);
const stop = async () => {
  if (isChangingStatus.value) {
    return;
  }
  isStopping.value = true;
  try {
    await XKeen.stop();
    snackbarMessage.value = 'XKeen stopped.';
    snackbarColor.value = 'success';
    snackbar.value = true;
  } catch (e) {
    snackbarMessage.value = e.message;
    snackbarColor.value = 'error';
    snackbar.value = true;
  } finally {
    isStopping.value = false;
    getStatus();
  }
};

const isChangingStatus = computed(() => {
  return isStarting.value || isRestarting.value || isStopping.value;
});

const snackbar = ref(false);
const snackbarMessage = ref(null);
const snackbarColor = ref(null);
</script>

<style scoped lang="scss">

</style>
