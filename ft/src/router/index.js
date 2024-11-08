import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/Login.vue";
import Register from "../views/Register.vue";
import Home from "../views/Home.vue";
import Layout from "../layout/index.vue";
import Accountinfo from "../views/Account/Accountinfo.vue";
import FinancialRecords from "../views/Account/FinancialRecords.vue";
import ResetPassword from "../views/Account/ResetPassword.vue";
import ForgetPassword from "../views/Account/ForgetPassword.vue";
import ApprovedOrders from "../views/Order/ApprovedOrders.vue";
import PendingOrders from "../views/Order/PendingOrders.vue";
import UnappliedOrders from "../views/Order/UnappliedOrders.vue";
import UserManagement from "../views/User/UserManagement.vue";
import Blacklist from "../views/User/Blacklist.vue";
import InviteActivity from "../views/User/InviteActivity.vue";
import UploadOrder from "../views/Order/UploadOrder.vue";
import EventLink from "../views/EventLink.vue";
import Shops from "../views/Shops.vue";
import WeChatAuth from "../views/WeChatAuth.vue";
import ClaimOrder from "../views/SceondUser/ClaimOrder.vue";
import SecondHome from "../views/SceondUser/SecondHome.vue";
import SecondOrder from "../views/SceondUser/SecondOrder.vue";
import apiClient from "@/api/index.js"; // 确保 API 客户端可以访问

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", name: "Login", component: Login },
  { path: "/register", name: "Register", component: Register },
  {
    path: "/reset-password",
    name: "ResetPassword",
    component: ResetPassword,
  },
  {
    path: "/forget-password",
    name: "ForgetPassword",
    component: ForgetPassword,
  },
  { path: "/wechat-auth", name: "WeChatAuth", component: WeChatAuth },
  {
    path: "/claim-order",
    name: "ClaimOrder",
    component: ClaimOrder,
    children: [
      { path: "", name: "SecondHome", component: SecondHome },
      { path: "secondorder", name: "SecondOrder", component: SecondOrder },
    ],
  },
  {
    path: "/",
    component: Layout,
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
        path: "shops",
        name: "Shops",
        component: Shops,
      },
      {
        path: "usermanagement",
        name: "UserManagement",
        component: UserManagement,
      },
      {
        path: "/blacklist",
        name: "Blacklist",
        component: Blacklist,
      },
      {
        path: "/inviteactivity",
        name: "InviteActivity",
        component: InviteActivity,
      },
      {
        path: "uploadorder",
        name: "UploadOrder",
        component: UploadOrder,
      },
      { path: "event-link", name: "EventLink", component: EventLink },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// 路由守卫，确保用户已登录并且处理过期账户的逻辑
router.beforeEach(async (to, from, next) => {
  const isAuthenticated = !!sessionStorage.getItem("access"); // 检查是否有访问令牌

  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      // 如果没有令牌，重定向到登录页面
      return next({ path: "/login" });
    }

    try {
      // 检查用户信息（包括是否过期）
      const response = await apiClient.get("/user-info/");
      const { is_expired, level } = response.data;

      if (is_expired && level === "first") {
        // 账户过期，允许访问登录页，但阻止访问其他受保护的页面
        if (to.path === "/home" || to.path === "/login") {
          return next(); // 允许访问主页或登录页
        }
        return next("/home"); // 重定向到主页，显示过期提示
      }

      // 如果账户未过期或是二级用户，允许访问
      return next();
    } catch (error) {
      // 如果请求失败，重定向到登录页
      sessionStorage.removeItem("access");
      sessionStorage.removeItem("refresh");
      return next({ path: "/login" });
    }
  } else {
    // 非受保护页面，允许访问
    return next();
  }
});

export default router;
