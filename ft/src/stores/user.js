import { defineStore } from "pinia";
import apiClient from "@/api/index"; // 引入 apiClient

export const useUserStore = defineStore("user", {
  state: () => ({
    token: localStorage.getItem("access") || "",
    expiryDate: "",
    balance: 0.0, // 新增余额状态
    // 其他用户状态
  }),
  actions: {
    setToken(token) {
      this.token = token;
    },
    logout() {
      this.token = "";
      this.expiryDate = "";
      this.balance = 0.0;
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      localStorage.removeItem("user");
    },
    async fetchUserInfo() {
      try {
        const response = await apiClient.get("user-info/");
        this.expiryDate = response.data.expiryDate;
        this.balance = response.data.balance; // 存储余额信息
        // 处理其他用户信息
      } catch (error) {
        console.error("Failed to fetch user info:", error);
      }
    },
    async initialize() {
      if (this.token) {
        await this.fetchUserInfo();
      }
    },
  },
  getters: {
    isLoggedIn: (state) => !!state.token,
    getExpiryDate: (state) => state.expiryDate,
    getBalance: (state) => state.balance, // 新增余额getter
  },
});

// 在应用初始化时调用 userStore.initialize()
