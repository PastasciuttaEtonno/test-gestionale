import { createApp } from "vue";
import { createPinia } from "pinia";
import PrimeVue from "primevue/config";

import App from "./App.vue";
import { createCanDirective } from "./directives/can";
import router from "./router";
import "./style.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(PrimeVue, { unstyled: true });
app.directive("can", createCanDirective());
app.mount("#app");
