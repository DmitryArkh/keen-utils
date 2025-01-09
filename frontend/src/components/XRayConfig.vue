<template>
  <v-card class="ma-8 px-4 pt-2 pb-6">
    <v-card-title class="d-flex justify-space-between align-center">
      <span>XRay Configs</span>
      <v-card-actions>
        <v-btn
          prepend-icon="mdi-content-save"
          :color="editedFiles.length ? 'primary' : null"
          variant="flat"
          :disabled="!editedFiles.length"
          :loading="isSending"
          @click="save"
        >
          Save All
        </v-btn>
      </v-card-actions>
    </v-card-title>
    <div class="d-flex flex-row">
      <v-tabs
        v-model="currentFile"
        color="primary"
        direction="vertical"
      >
        <v-tab
          v-for="file in Object.keys(files)"
          :key="file"
          :text="file"
          :value="file"
        />
      </v-tabs>
      <JsonEditorVue
        v-model="files[currentFile]['content']"
        :mode="Mode.text"
        class="flex-grow-1 jse-theme-dark"
        style="height: 600px"
        @change="files[currentFile]['isEdited'] = true"
      />
    </div>
  </v-card>

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
import JsonEditorVue from 'json-editor-vue'
import 'vanilla-jsoneditor/themes/jse-theme-dark.css'
import { Mode } from 'vanilla-jsoneditor'
import XKeen from "@/api/xkeen.js";

const currentFile = ref('routing');
const files = ref({
  log: {
    content: '{}',
    isEdited: false,
  },
  transport: {
    content: '{}',
    isEdited: false,
  },
  inbounds: {
    content: '{}',
    isEdited: false,
  },
  outbounds: {
    content: '{}',
    isEdited: false,
  },
  routing: {
    content: '{}',
    isEdited: false,
  },
  policy: {
    content: '{}',
    isEdited: false,
  },
})

const getFile = async (file) => {
  files.value[file]['content'] = await XKeen.getFile(`xray-${file}`);
};

watch(currentFile, (val) => {
  getFile(val);
});

onMounted(() => {
  getFile(currentFile.value);
});

const editedFiles = computed(() => {
  return Object.entries(files.value)
    .filter(([key, value]) => value.isEdited)
    .map(([key]) => key);
});

const isSending = ref(false);
const save = async () => {
  isSending.value = true;
  try {
    for (const file of editedFiles.value) {
      await XKeen.writeFile(`xray-${file}`, files.value[file]['content']);
      files.value[file]['isEdited'] = false;
    }
    snackbarMessage.value = 'Saved successfully.';
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

const snackbar = ref(false);
const snackbarMessage = ref(null);
const snackbarColor = ref(null);
</script>

<style scoped lang="sass">

</style>
