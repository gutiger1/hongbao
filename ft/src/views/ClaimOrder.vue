<template>
    <div>
        <el-form :model="orderForm">
            <el-form-item label="订单编号">
                <el-input v-model="orderForm.order_number"></el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="submitOrder">提交</el-button>
            </el-form-item>
        </el-form>
        <p v-if="message">{{ message }}</p>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/api/index.js';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const orderForm = ref({ order_number: '' });
const message = ref('');

onMounted(() => {
    const token = route.query.token;
    const refreshToken = route.query.refresh_token;
    if (token) {
        localStorage.setItem('access', token);
        apiClient.defaults.headers.Authorization = `Bearer ${token}`;
    }
    if (refreshToken) {
        localStorage.setItem('refresh', refreshToken);
    }
});

const submitOrder = async () => {
    const token = localStorage.getItem('access');
    if (!token) {
        message.value = '未找到令牌，请重新登录';
        router.push('/login');
        return;
    }

    try {
        const response = await apiClient.post('/claim-order/', orderForm.value, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        message.value = response.data.success ? '提交成功' : '提交失败';
    } catch (error) {
        message.value = `提交失败: ${error.response.data.error || '未知错误'}`;
    }
};
</script>
