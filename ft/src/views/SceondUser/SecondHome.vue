<template>
    <div class="container">
        <div class="image-container">
            <img v-if="currentImage" :src="currentImage" alt="广告图" class="event-image" />
            <!-- <div v-else class="placeholder">这整个黄色为图片展示区域</div> -->
        </div>

        <el-form :model="orderForm" class="form-container">
            <el-form-item class="form-item">
                <el-input v-model="orderForm.order_number" :placeholder="currentCommandDescription"
                    style="height: 60px; font-size: 20px;" class="input-field">
                    <template #prefix>
                        <span class="input-prefix"
                            style="font-size: 20px;margin-right: 30px;font-weight: bolder;color: black;">{{
                                currentCommandTitle
                            }}</span>
                    </template>
                </el-input>
            </el-form-item>
            <el-form-item class="form-item">
                <el-button type="primary" @click="submitOrder" class="submit-button">确认提交</el-button>
            </el-form-item>
        </el-form>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/api/index.js';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const orderForm = ref({ order_number: '' });
const currentImage = ref(sessionStorage.getItem('currentImage') || '');
const newEventImage = ref('');
const currentCommandTitle = ref(sessionStorage.getItem('currentCommandTitle') || '');
const currentCommandDescription = ref(sessionStorage.getItem('currentCommandDescription') || '');
const newCommandTitle = ref('');
const newCommandDescription = ref('');

const sendLogToServer = async (message) => {
    try {
        await apiClient.post('/log/', { message });
    } catch (error) {
        console.error('Failed to send log to server:', error);
    }
};

onMounted(async () => {
    const token = route.query.token;
    const refreshToken = route.query.refresh_token;
    const firstLevelUserUserId = route.query.fuser_id;
    const secondLevelUserUserId = route.query.suser_id;

    await sendLogToServer(`onMounted: token: ${token}`);
    await sendLogToServer(`onMounted: refreshToken: ${refreshToken}`);
    await sendLogToServer(`onMounted: firstLevelUserUserId: ${firstLevelUserUserId}`);
    await sendLogToServer(`onMounted: secondLevelUserUserId: ${secondLevelUserUserId}`);

    if (token) {
        sessionStorage.setItem('access', token);
        apiClient.defaults.headers.Authorization = `Bearer ${token}`;
    }
    if (refreshToken) {
        sessionStorage.setItem('refresh', refreshToken);
    }
    await sendLogToServer(`onMounted: sessionStorage.getItem('access'): ${sessionStorage.getItem('access')}`);
    await sendLogToServer(`onMounted: sessionStorage.getItem('refresh'): ${sessionStorage.getItem('refresh')}`);

    if (firstLevelUserUserId) {
        sessionStorage.setItem('fuser_id', firstLevelUserUserId);
        fetchEventImage(firstLevelUserUserId); // 获取广告图和文字
    }
    if (secondLevelUserUserId) {
        sessionStorage.setItem('suser_id', secondLevelUserUserId);
    }
});

const fetchEventImage = async (firstLevelUserUserId) => {
    try {
        const token = sessionStorage.getItem('access');
        await sendLogToServer(`fetchEventImage: token from sessionStorage: ${token}`);

        if (!token) {
            throw new Error('Unauthorized');
        }

        const response = await apiClient.get('/fetch-event/', {
            headers: {
                Authorization: `Bearer ${token}`,
            },
            params: { first_level_user_user_id: firstLevelUserUserId }
        });
        await sendLogToServer(`fetchEventImage: response: ${JSON.stringify(response.data)}`);

        const imagePath = response.data.image;
        const baseURL = apiClient.defaults.baseURL; // 使用 apiClient 的 baseURL
        newEventImage.value = `${baseURL}${imagePath}`;
        newCommandTitle.value = response.data.commandTitle;
        newCommandDescription.value = response.data.commandDescription;

        // 等待新图片加载完成后再更新 currentImage
        const img = new Image();
        img.onload = async () => {
            await sendLogToServer(`Image loaded: ${img.src}`);
            currentImage.value = newEventImage.value;
            currentCommandTitle.value = newCommandTitle.value;
            currentCommandDescription.value = newCommandDescription.value;
            sessionStorage.setItem('currentImage', newEventImage.value);
            sessionStorage.setItem('currentCommandTitle', newCommandTitle.value);
            sessionStorage.setItem('currentCommandDescription', newCommandDescription.value);
        };
        img.onerror = async (error) => {
            await sendLogToServer(`Image failed to load: ${error}`);
        };
        await sendLogToServer(`Starting image load: ${newEventImage.value}`);
        img.src = newEventImage.value;

    } catch (error) {
        await sendLogToServer(`fetchEventImage: error: ${error}`);
        if (error.response && error.response.status === 401) {
            alert('未找到令牌，请重新登录');
            router.push('/login');
        } else {
            console.error('Failed to fetch event image:', error);
        }
    }
};

const submitOrder = async () => {
    const token = sessionStorage.getItem('access');
    const firstLevelUserUserId = sessionStorage.getItem('fuser_id');

    if (!token) {
        alert('未找到令牌，请重新登录');
        router.push('/login');
        return;
    }

    try {
        const response = await apiClient.post('/claim-order/', {
            order_number: orderForm.value.order_number,
            first_level_user_user_id: firstLevelUserUserId  // 提交时传递一级用户的 user_id
        }, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        alert(response.data.success ? '提交成功' : '提交失败');
    } catch (error) {
        alert(`提交失败: ${error.response.data.error || '未知错误'}`);
    }
};
</script>


<style scoped>
.container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    width: 100%;
    height: 100vh;
    background-color: #f5f5f5;
}

.image-container {
    width: 100%;
    flex-shrink: 0;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    background-color: #ffcc66;
}

.event-image {
    width: 100%;
    height: auto;
    object-fit: contain;
}

.placeholder {
    font-size: 24px;
    color: #333;
}

.form-container {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 20px;
    border-radius: 10px;
    box-sizing: border-box;
    margin-top: 40px;
}

.form-item {
    width: 100%;
}

.input-with-label {
    display: flex;
    align-items: center;
}

.input-field .el-input__inner {
    width: 100%;
    height: 60px;
    padding: 10px;
    font-size: 20px;
}

.input-prefix {
    font-size: 20px;
    margin-right: 30px;
    font-weight: bolder;
    color: black;
}

.submit-button {
    width: 100%;
    height: 60px;
    font-size: 20px;
    margin-top: -20px;
}
</style>
