import "./assets/main.css";

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import "./styles/main.scss";
import { createPinia } from "pinia";
import { useUserStore } from "@/stores/user"; // 导入 user store
import Pagination from "@/components/Pagination.vue";
import zhCn from "element-plus/es/locale/lang/zh-cn";

const app = createApp(App);

const pinia = createPinia();
app.use(pinia);

const userStore = useUserStore();
userStore.initialize(); // 初始化用户信息

app.use(router);
app.use(ElementPlus, { locale: zhCn });

// 全局注册 Pagination 组件
app.component("Pagination", Pagination);

// 挂载到全局
app.mount("#app");
