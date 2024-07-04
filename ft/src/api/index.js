import axios from "axios";
import { ElMessage } from "element-plus";
import router from "../router"; // 确保引入路由实例

const apiClient = axios.create({
  baseURL: "http://192.168.158.138:8000/api/",
  withCredentials: false,
  headers: {
    "Content-Type": "application/json",
  },
});

// 添加请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 添加响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem("refresh");
      if (refreshToken) {
        try {
          const response = await axios.post(
            "http://192.168.158.138:8000/api/token/refresh/",
            {
              refresh: refreshToken,
            }
          );
          localStorage.setItem("access", response.data.access);
          apiClient.defaults.headers.Authorization = `Bearer ${response.data.access}`;
          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
          return apiClient(originalRequest);
        } catch (refreshError) {
          ElMessage.error("刷新令牌失败，请重新登录");
          localStorage.removeItem("access");
          localStorage.removeItem("refresh");
          router.push("/login");
          return Promise.reject(refreshError);
        }
      } else {
        ElMessage.error("未找到刷新令牌，请重新登录");
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        router.push("/login");
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
