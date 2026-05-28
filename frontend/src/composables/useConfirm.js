import { reactive } from "vue";

const state = reactive({
  open: false,
  title: "",
  message: "",
  confirmLabel: "Conferma",
  cancelLabel: "Annulla",
  danger: false,
  showCancel: true,
});

let resolver = null;

function settle(result) {
  state.open = false;
  if (resolver) {
    resolver(result);
    resolver = null;
  }
}

export function confirm(options = {}) {
  state.title = options.title ?? "Confermare l'operazione";
  state.message = options.message ?? "";
  state.confirmLabel = options.confirmLabel ?? "Conferma";
  state.cancelLabel = options.cancelLabel ?? "Annulla";
  state.danger = options.danger ?? false;
  state.showCancel = true;
  state.open = true;
  return new Promise((resolve) => {
    resolver = resolve;
  });
}

export function notify(options = {}) {
  state.title = options.title ?? "Avviso";
  state.message = options.message ?? "";
  state.confirmLabel = options.confirmLabel ?? "Ho capito";
  state.danger = options.danger ?? false;
  state.showCancel = false;
  state.open = true;
  return new Promise((resolve) => {
    resolver = resolve;
  });
}

export function useConfirm() {
  return { confirmState: state, confirm, notify, settle };
}
