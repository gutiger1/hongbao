<template>
    <div>
        正在重定向到微信授权...
        <p v-if="weChatAuthUrl">微信授权链接: {{ weChatAuthUrl }}</p>
    </div>
</template>
  
<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const weChatAuthUrl = ref('');

onMounted(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('user_id');

    if (userId) {
        const redirectUri = encodeURIComponent('http://192.168.158.138:8000/api/wechat-auth');
        weChatAuthUrl.value = `https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxb5b1322aaf1cd850&redirect_uri=${redirectUri}&response_type=code&scope=snsapi_userinfo&state=${userId}#wechat_redirect`;

        console.log('微信授权链接:', weChatAuthUrl.value);

        // 延迟3秒后执行重定向，以便查看调试信息
        setTimeout(() => {
            window.location.href = weChatAuthUrl.value;
        }, 500);
    } else {
        router.push('/login');
    }
});
</script>
  