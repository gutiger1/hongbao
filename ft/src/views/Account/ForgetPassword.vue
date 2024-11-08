<template>
    <div class="forget-password-container">
        <h2>忘记密码</h2>
        <el-form :model="form" @submit.prevent="submitForm" label-width="100px">
            <el-form-item label="用户名">
                <el-input v-model="form.username" autocomplete="off" placeholder="请输入用户名"></el-input>
            </el-form-item>
            <el-form-item label="邮箱">
                <el-input v-model="form.email" autocomplete="off" placeholder="请输入邮箱"></el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="submitForm">发送重置链接</el-button>
            </el-form-item>
        </el-form>
    </div>
</template>
  
<script setup>
import { reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import apiClient from '@/api/index.js';

const form = reactive({
    username: '',
    email: ''
});

const router = useRouter();

const submitForm = async () => {
    try {
        const response = await apiClient.post('/send-reset-link/', form);
        ElMessage.success('重置密码链接已发送到您的邮箱');
        router.push('/login');
    } catch (error) {
        ElMessage.error(error.response?.data?.error || '发送重置链接失败');
    }
};
</script>
  
  
<style scoped>
.forget-password-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    flex-direction: column;
}
</style>
  