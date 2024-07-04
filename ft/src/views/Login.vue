<template>
  <el-form :model="form" @submit.prevent="login">
    <el-form-item label="用户名">
      <el-input v-model="form.username" autocomplete="off"></el-input>
    </el-form-item>
    <el-form-item label="密码">
      <el-input type="password" v-model="form.password" autocomplete="off"></el-input>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="login">登录</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user'; // 导入 user store
import apiClient from '../api/index.js';
import { ElMessage } from 'element-plus';

const router = useRouter();
const userStore = useUserStore(); // 使用 user store
const form = reactive({
  username: '',
  password: ''
});

const login = async () => {
  try {
    const response = await apiClient.post('token/', form);
    localStorage.setItem('access', response.data.access);
    localStorage.setItem('refresh', response.data.refresh);
    localStorage.setItem('user', form.username);

    userStore.setToken(response.data.access); // 设置 token
    await userStore.fetchUserInfo(); // 获取用户信息

    router.push('/home');
  } catch (error) {
    ElMessage.error('登录失败');
    console.error(error);
  }
};
</script>
