<template>
    <div>
        正在重定向到微信授权...
        <p v-if="weChatAuthUrl">微信授权链接: {{ weChatAuthUrl }}</p>
    </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api/index.js';

const router = useRouter();

// 获取 Cookie 的函数
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

onMounted(async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const encodedUserId = urlParams.get('user_id');

    if (encodedUserId) {
        const cachedRedirectUrl = getCookie(`redirect_${encodedUserId}`);

        if (cachedRedirectUrl) {
            console.log('Using cached redirect URL:', cachedRedirectUrl);
            window.location.href = cachedRedirectUrl;
            return;
        } else {
            try {
                // 调用后端 API 获取微信授权链接
                const response = await apiClient.get('/generate-wechat-auth-link/', {
                    params: { user_id: encodedUserId },
                });

                const weChatAuthUrl = response.data.wechat_auth_url;

                console.log('微信授权链接:', weChatAuthUrl);

                // 延迟500毫秒后执行重定向，以便查看调试信息
                setTimeout(() => {
                    window.location.href = weChatAuthUrl;
                }, 500);
            } catch (error) {
                console.error('获取微信授权链接失败', error);
                router.push('/login');
            }
        }
    } else {
        console.error('No encoded user_id found in URL parameters.');
        router.push('/login');
    }
});
</script>
