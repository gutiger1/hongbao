<template>
    <div class="reset-password-container">
        <h2>重置密码</h2>
        <el-form :model="form" @submit.prevent="resetPassword" label-width="100px">
            <el-form-item label="新密码">
                <el-input type="password" v-model="form.newPassword" autocomplete="off" placeholder="请输入新密码"></el-input>
            </el-form-item>
            <el-form-item label="确认密码">
                <el-input type="password" v-model="form.confirmPassword" autocomplete="off" placeholder="请确认新密码"></el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="resetPassword">重置密码</el-button>
            </el-form-item>
        </el-form>
    </div>
</template>
  
<script setup>
import { reactive, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/api/index.js';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();
const form = reactive({
    newPassword: '',
    confirmPassword: ''
});

const resetPassword = async () => {
    if (form.newPassword !== form.confirmPassword) {
        ElMessage.error('两次输入的密码不一致');
        return;
    }

    try {
        const uid = route.query.uid;
        const token = route.query.token;

        if (!uid || !token) {
            ElMessage.error('无效的重置链接');
            router.push('/login');
            return;
        }

        const response = await apiClient.post(`/reset/${uid}/${token}/`, {
            new_password: form.newPassword
        });

        ElMessage.success('密码重置成功');
        router.push('/login');
    } catch (error) {
        const errorMessage = error.response?.data?.error || '密码重置失败';
        ElMessage.error(errorMessage);
    }
};

onMounted(() => {
    const uid = route.query.uid;
    const token = route.query.token;
    console.log("UID:", uid, "Token:", token);
    if (!uid || !token) {
        ElMessage.error('无效的重置链接');
        router.push('/login');
    }
});

</script>
  
<style scoped>
.reset-password-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    flex-direction: column;
}
</style>
