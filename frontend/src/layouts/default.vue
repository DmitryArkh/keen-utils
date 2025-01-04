<template>
  <v-app>
    <v-app-bar
      color="primary"
      prominent
    >
      <v-app-bar-nav-icon
        variant="text"
        @click.stop="drawer = !drawer"
      />

      <v-toolbar-title>KeenUtils</v-toolbar-title>
    </v-app-bar>
    <v-navigation-drawer
      v-model="drawer"
    >
      <NavDrawer />
    </v-navigation-drawer>
    <v-main>
      <router-view />
    </v-main>
    <StatusBar />
  </v-app>
</template>

<script setup>
const drawer = ref(true);
</script>
