<template>
  <v-dialog
    v-model="dialog"
    max-width="300"
  >
    <template #activator="{ props: activatorProps }">
      <v-btn
        variant="flat"
        color="primary"
        prepend-icon="mdi-plus"
        v-bind="activatorProps"
      >
        Add new
      </v-btn>
    </template>

    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <div class="text-medium-emphasis ps-2">
          New DNS Record
        </div>
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="dialog = false"
        />
      </v-card-title>
      <v-card-text>
        <v-form
          v-model="valid"
          @submit.prevent="addRecord"
        >
          <v-text-field
            v-model="hostname"
            :rules="hostnameRules"
            label="Hostname"
            required
            class="mb-3"
          />

          <v-text-field
            v-model="ip"
            :rules="ipRules"
            label="IP Address"
            required
            class="my-3"
          />

          <v-btn
            type="submit"
            color="primary"
            :loading="isSending"
            block
          >
            Add
          </v-btn>
        </v-form>
      </v-card-text>
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
import Dns from "@/api/dns.js";

const emit = defineEmits(['add']);

const dialog = ref(false);
const valid = ref(false);

const hostname = ref('');
const ip = ref('');

const hostnameRules = [
  value => {
    if (value) return true
    return 'You must enter a hostname.'
  },
];
const ipRules = [
  value => {
    if (value) return true
    return 'You must enter an IP address.'
  },
  value => {
    if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(value)) return true
    return 'You must enter a valid IPv4 address.'
  },
];

const snackbar = ref(false);
const snackbarMessage = ref(null);
const snackbarColor = ref(null);

const isSending = ref(false);
const addRecord = async () => {
  if (!valid.value) return;
  isSending.value = true;
  try {
    const result = await Dns.addRecord(hostname.value, ip.value);
    if (!result.ok) {
      throw new Error(result.message);
    }
    dialog.value = false;
    hostname.value = '';
    ip.value = '';
    emit('add');
    snackbarMessage.value = 'Record added successfully.';
    snackbarColor.value = 'success';
    snackbar.value = true;
  } catch (e) {
    snackbarMessage.value = e.message;
    snackbarColor.value = 'error';
    snackbar.value = true;
  } finally {
    isSending.value = false;
  }
};
</script>

<style scoped lang="sass">

</style>
