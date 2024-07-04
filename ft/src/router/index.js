import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/Login.vue";
import Register from "../views/Register.vue";
import Home from "../views/Home.vue";
import Layout from "../layout/index.vue"; // 更新为 Layout
import Accountinfo from "../views/Account/Accountinfo.vue";
import FinancialRecords from "../views/Account/FinancialRecords.vue";
import ApprovedOrders from "../views/Order/ApprovedOrders.vue";
import PendingOrders from "../views/Order/PendingOrders.vue";
import UnappliedOrders from "../views/Order/UnappliedOrders.vue";
import UserManagement from "../views/User/UserManagement.vue";
import UploadOrder from "../views/UploadOrder.vue"; // 导入上传页面
import EventLink from "../views/EventLink.vue"; // 导入活动链接页面
import WeChatAuth from "../views/WeChatAuth.vue"; // 导入微信授权页面
import ClaimOrder from "../views/ClaimOrder.vue"; // 导入提交订单编号页面

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", name: "Login", component: Login },
  { path: "/register", name: "Register", component: Register },
  { path: "/wechat-auth", name: "WeChatAuth", component: WeChatAuth },
  { path: "/claim-order", name: "ClaimOrder", component: ClaimOrder },
  {
    path: "/",
    component: Layout, // 使用 Layout 作为父组件
    meta: { requiresAuth: true },
    children: [
      { path: "home", name: "Home", component: Home },
      { path: "accountinfo", name: "Accountinfo", component: Accountinfo },
      {
        path: "financialrecords",
        name: "FinancialRecords",
        component: FinancialRecords,
      },
      {
        path: "approvedorders",
        name: "ApprovedOrders",
        component: ApprovedOrders,
      },
      {
        path: "pendingorders",
        name: "PendingOrders",
        component: PendingOrders,
      },
      {
        path: "unappliedorders",
        name: "UnappliedOrders",
        component: UnappliedOrders,
      },
      {
        path: "usermanagement",
        name: "UserManagement",
        component: UserManagement,
      },
      {
        path: "uploadorder",
        name: "UploadOrder",
        component: UploadOrder, // 添加上传订单页面路由
      },
      { path: "/event-link", name: "EventLink", component: EventLink },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// 路由守卫 暂时注释 方便开发
// router.beforeEach((to, from, next) => {
//   const isAuthenticated = !!localStorage.getItem("access"); // 检查是否有访问令牌
//   if (to.matched.some((record) => record.meta.requiresAuth)) {
//     if (!isAuthenticated) {
//       next({ path: "/login" }); // 重定向到登录页面
//     } else {
//       next(); // 继续导航
//     }
//   } else {
//     next(); // 继续导航
//   }
// });

export default router;
