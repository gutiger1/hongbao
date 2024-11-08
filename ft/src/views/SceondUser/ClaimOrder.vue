<template>
    <div class="claim-order-page">
        <div class="page-container">
            <router-view />
        </div>
        <NavBar />
    </div>
</template>

<script setup>
import NavBar from './NavBar.vue';
import { onMounted } from 'vue';
import { useRoute } from 'vue-router';

// 有效期为86400秒
function setCookie(name, value, maxAge = 86400) {
    document.cookie = `${name}=${value}; path=/; max-age=${maxAge}; secure`;
}

const route = useRoute();

onMounted(() => {
    const encodedUserId = route.query.user_id; // 从URL中获取 user_id
    const token = route.query.token;
    const refreshToken = route.query.refresh_token;
    const redirectUrl = window.location.href; // 最终跳转链接

    // 确保令牌被正确存储
    if (token) {
        sessionStorage.setItem('access', token);
    }
    if (refreshToken) {
        sessionStorage.setItem('refresh', refreshToken);
    }

    if (encodedUserId) {
        // 使用加密的 user_id 作为键名存储最终的 redirect_url
        setCookie(`redirect_${encodedUserId}`, redirectUrl);
        console.log("Saved redirect URL:", redirectUrl);
    } else {
        console.error("No encoded user_id found in URL parameters.");
    }
});
</script>

<style scoped>
.claim-order-page {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    height: 100vh;
    margin: 0;
    padding: 0;
}

.page-container {
    width: 100%;
    max-width: 650px;
    margin: 0 auto;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-sizing: border-box;
    padding: 0;
}

:deep(#app) {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
}
</style>
