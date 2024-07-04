import "./assets/main.css";

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import "./styles/main.scss";
import { createPinia } from "pinia";
import { useUserStore } from "@/stores/user"; // 导入 user store

const app = createApp(App);

const pinia = createPinia();
app.use(pinia);

const userStore = useUserStore();
userStore.initialize(); // 初始化用户信息

app.use(router);
app.use(ElementPlus);
app.mount("#app");
