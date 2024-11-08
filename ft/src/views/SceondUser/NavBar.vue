<template>
    <div class="bottom-nav">
        <router-link to="/claim-order" class="nav-item" exact exact-active-class="active">
            <span>首页</span>
        </router-link>
        <router-link to="/claim-order/secondorder" class="nav-item" active-class="active">
            <span>我的</span>
        </router-link>
    </div>
</template>

<script setup>

</script>

<style scoped>
.bottom-nav {
    position: fixed;
    bottom: 0;
    width: 100%;
    max-width: 650px;
    display: flex;
    justify-content: space-around;
    background-color: #fff;
    padding: 10px;
    box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
    left: 50%;
    transform: translateX(-50%);
    z-index: 1000;
    /* 添加更高的 z-index */
}

.nav-item {
    text-decoration: none;
    color: #333;
    font-size: 16px;
    padding: 5px 10px;
    flex-grow: 1;
    display: flex;
    justify-content: center;
    align-items: center;
}

.nav-item.active {
    color: #409EFF;
    /* 定义活动链接的颜色 */
}

/* 响应式设计 */
@media (max-width: 600px) {
    .bottom-nav {
        max-width: 100%;
    }
}
</style>
