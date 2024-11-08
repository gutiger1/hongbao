import axios from "axios";
import { ElMessage } from "element-plus";
import router from "../router";

const apiClient = axios.create({
  baseURL: "https://dingdanbaob.top",
  withCredentials: false,
  headers: {
    "Content-Type": "application/json",
  },
});

// 处理令牌过期
function handleTokenExpired() {
  ElMessage.error("登录已过期，请重新登录");
  sessionStorage.removeItem("access");
  sessionStorage.removeItem("refresh");
  router.push("/login");
}

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem("access");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const refreshToken = sessionStorage.getItem("refresh");

    // 刷新令牌
    if (
      error.response?.status === 401 &&
      refreshToken &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;
      try {
        const response = await apiClient.post("token/refresh/", {
          refresh: refreshToken,
        });
        sessionStorage.setItem("access", response.data.access);
        apiClient.defaults.headers.Authorization = `Bearer ${response.data.access}`;
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return apiClient(originalRequest); // 重试原始请求
      } catch (refreshError) {
        if (refreshError.response?.status === 401) {
          handleTokenExpired(); // 如果刷新失败，处理令牌过期
        } else {
          ElMessage.error("网络错误，请稍后重试"); // 其他错误弹出提示
        }
        return Promise.reject(refreshError);
      }
    } else if (error.response?.status === 401 && !refreshToken) {
      handleTokenExpired();
    }
    return Promise.reject(error);
  }
);

export default apiClient;
