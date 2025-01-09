<template>
  <v-card class="ma-8 px-4 pt-2 pb-6">
    <v-card-title class="d-flex justify-space-between align-center">
      <span>Static DNS Records</span>
      <v-card-actions>
        <v-btn
          variant="flat"
          prepend-icon="mdi-refresh"
          @click="getRecords"
        >
          Refresh
        </v-btn>
        <DNSNewRecord @add="getRecords" />
      </v-card-actions>
    </v-card-title>

    <v-data-table
      :loading="isFetching"
      hide-default-footer
      density="compact"
      :headers="[ ...headers, { title: 'Actions', value: 'actions'} ]"
      :items="records"
    >
      <template #item.actions="{ item }">
        <v-icon
          size="small"
          @click="recordToDelete = item"
        >
          mdi-delete
        </v-icon>
      </template>
    </v-data-table>
  </v-card>

  <v-dialog
    v-model="recordToDelete"
    width="auto"
  >
    <v-card
      max-width="400"
      title="Delete DNS Record"
      text="Do you really want to delete this record?"
    >
      <template #actions>
        <v-btn
          :loading="isDeleting"
          text="Delete"
          color="warning"
          @click="deleteRecord"
        />
        <v-btn
          text="Cancel"
          @click="recordToDelete = null"
        />
      </template>
    </v-card>
  </v-dialog>

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
import DNS from "@/api/dns.js";

const records = ref([]);

const headers = [
  {
    title: 'Hostname',
    value: 'hostname'
  },
  {
    title: 'IP Address',
    value: 'ip'
  }
]

const isFetching = ref(false);
const getRecords = async () => {
  if (isFetching.value) {
    return;
  }
  isFetching.value = true;
  try {
    records.value = await DNS.getRecords();
  } finally {
    isFetching.value = false;
  }
};

const snackbar = ref(false);
const snackbarMessage = ref(null);
const snackbarColor = ref(null);

const recordToDelete = ref(null);
const isDeleting = ref(false);
const deleteRecord = async () => {
  isDeleting.value = true;
  try {
    await DNS.deleteRecord(recordToDelete.value.hostname, recordToDelete.value.ip);
    recordToDelete.value = null;
    getRecords();
    snackbarMessage.value = 'Record deleted successfully.';
    snackbarColor.value = 'success';
    snackbar.value = true;
  } catch (e) {
    snackbarMessage.value = e.message;
    snackbarColor.value = 'error';
    snackbar.value = true;
  } finally {
    isDeleting.value = false;
  }
};

onMounted(() => {
  getRecords();
});
</script>

<style scoped lang="sass">

</style>
