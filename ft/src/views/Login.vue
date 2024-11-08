<template>
  <div class="login-container">
    <div class="login-box">
      <h2 class="login-title">登录</h2>
      <el-form :model="form" @submit.prevent="login" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" autocomplete="off" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input type="password" v-model="form.password" autocomplete="off" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="login" class="login-button">登录</el-button>
          <el-button type="default" @click="goToRegister">注册</el-button>
          <el-button type="text" @click="goToResetPassword">忘记密码？</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import apiClient from '../api/index.js';
import { ElMessage } from 'element-plus';

const router = useRouter();
const userStore = useUserStore();
const form = reactive({
  username: '',
  password: ''
});

const login = async () => {
  try {
    console.log('Login form data:', form);

    // 尝试发送登录请求
    const response = await apiClient.post('/token/', form);

    // 存储 token 和用户信息
    sessionStorage.setItem('access', response.data.access);
    sessionStorage.setItem('refresh', response.data.refresh);
    sessionStorage.setItem('user', form.username);

    // 设置用户 store 中的 token
    userStore.setToken(response.data.access);

    // 尝试获取用户信息
    await userStore.fetchUserInfo();

    // 登录成功后重定向到主页
    router.push('/home');
  } catch (error) {
    // 检查是否有更多的错误信息
    const errorMessage = error.response?.data?.detail || '登录失败';
    ElMessage.error(errorMessage);
    console.error('Login error:', error);
  }
};

const goToRegister = () => {
  router.push('/register');
};

const goToResetPassword = () => {
  router.push('/forget-password');
};
</script>

<style scoped>
/* 清除 body 和 html 默认的边距和滚动条 */
body,
html {
  margin: 0;
  padding: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  /* 隐藏水平和垂直滚动条 */
}

/* 设置登录容器的背景图 */
.login-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  /* 确保背景图全屏宽度 */
  height: 100vh;
  /* 确保背景图全屏高度 */
  display: flex;
  justify-content: center;
  align-items: center;
  background-image: url('https://dingdanbaob.top/static/background-image.jpg');
  background-size: cover;
  /* 背景图覆盖整个容器 */
  background-position: center;
  /* 背景图居中 */
  background-repeat: no-repeat;
  /* 防止重复 */
  box-sizing: border-box;
}



.login-box {
  width: 400px;
  padding: 20px;
  background: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.login-title {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-input {
  width: 100%;
}

.login-button {
  margin-right: 10px;
}</style>
