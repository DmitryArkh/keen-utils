<template>
  <v-card class="ma-8 px-4 py-2">
    <v-card-title class="d-flex justify-space-between">
      <span>Static DNS Records</span>
      <v-btn
        variant="flat"
        prepend-icon="mdi-refresh"
        @click="getRecords"
      >
        Refresh
      </v-btn>
    </v-card-title>
  </v-card>

  <v-card class="ma-8 pa-4">
    <v-card-title class="d-flex justify-space-between">
      <span>DNS Records - A</span>
      <DnsNewRecord @add="getRecords" />
    </v-card-title>
    <v-data-table
      :loading="isFetching"
      hide-default-footer
      density="compact"
      :headers="[ ...headers, { title: 'Actions', value: 'actions'} ]"
      :items="records.static_a"
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

  <v-card class="ma-8 pa-4">
    <v-card-title>DNS Records - AAAA</v-card-title>
    <v-data-table
      :loading="isFetching"
      hide-default-footer
      density="compact"
      :headers="headers"
      :items="records.static_aaaa"
    />
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
import { onMounted } from "vue";
import Dns from "@/api/dns.js";

const records = ref({
  static_a: [],
  static_aaaa: []
});

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
    records.value = await Dns.getRecords();
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
    const result = await Dns.deleteRecord(recordToDelete.value.hostname, recordToDelete.value.ip);
    recordToDelete.value = null;
    if (!result.ok) {
      throw new Error(result.message);
    }
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
