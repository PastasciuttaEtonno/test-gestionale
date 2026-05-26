import { createApp } from "vue";
import { createPinia } from "pinia";
import PrimeVue from "primevue/config";
import Tooltip from "primevue/tooltip";

import App from "./App.vue";
import { createCanDirective } from "./directives/can";
import router from "./router";
import "./style.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(PrimeVue, {
  unstyled: true,
  pt: {
    tooltip: {
      root: {
        class:
          "pointer-events-none absolute z-50 max-w-xs rounded-lg bg-steel-900 px-2.5 py-1.5 text-xs font-medium text-white shadow-lg",
      },
      text: { class: "leading-none" },
      arrow: { class: "hidden" },
    },
  },
});
app.directive("tooltip", Tooltip);
app.directive("can", createCanDirective());

app.mount("#app");
