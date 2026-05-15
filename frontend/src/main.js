import { createApp } from "vue";
import PrimeVue from "primevue/config";

import App from "./App.vue";
import router from "./router";
import "./style.css";

createApp(App)
  .use(router)
  .use(PrimeVue, { unstyled: true })
  .mount("#app");
