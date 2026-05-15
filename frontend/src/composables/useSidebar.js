import { ref } from "vue";

const drawerAperto = ref(false);

export function useSidebar() {
  return {
    drawerAperto,
    toggleDrawer: () => {
      drawerAperto.value = !drawerAperto.value;
    },
    chiudiDrawer: () => {
      drawerAperto.value = false;
    },
  };
}
