<template>
  <v-card>
    <v-card-title>DNS Entries</v-card-title>
    <v-data-table
      :loading="isFetching"
      hide-default-footer
      density="compact"
      :headers="headers"
      :items="records.static_a"
    >
      <template v-slot:item.actions="{ item }">
        <v-icon
          size="small"
          @click="deleteRecord(item)"
        >
          mdi-delete
        </v-icon>
      </template>
    </v-data-table>
  </v-card>
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
  },
  {
    title: 'Actions',
    value: 'actions'
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

const deleteRecord = async (record) => {
  console.log(record);
}

onMounted(() => {
  getRecords();
});
</script>

<style scoped lang="sass">

</style>
