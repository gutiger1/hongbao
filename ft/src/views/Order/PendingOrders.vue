<template>
    <div class="content-wrapper">
        <div class="content-item">用户提交尚未核销 待审核订单</div>
        <Orders class="content-item" />
        <Shops class="content-item" />
    </div>
</template>
  
<script setup>
import Orders from '../Orders.vue';  // 确保路径正确
import Shops from '../Shops.vue';
</script>
  
<style scoped>
.content-wrapper {
    display: flex;
    flex-direction: column;
}

.content-item {
    margin: 10px 0;
    /* 调整间距大小 */
}
</style>
  