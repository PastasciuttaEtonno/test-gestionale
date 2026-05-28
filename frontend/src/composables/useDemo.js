import { ref } from "vue";

// Stato modalita demo condiviso a livello di modulo (come useSidebar).
const readonly = ref(false);
const avviso = ref("");
let timer = null;

export function useDemo() {
  return {
    readonly,
    avviso,
    impostaReadonly: (value) => {
      readonly.value = Boolean(value);
    },
    segnalaBlocco: (messaggio) => {
      avviso.value = messaggio || "Modalità demo: le modifiche non vengono salvate.";
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => {
        avviso.value = "";
      }, 4000);
    },
  };
}
