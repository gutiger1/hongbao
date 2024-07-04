<template>
    <div class="navbar">
        <el-icon class="hamburger-container" @click="toggleClick">
            <component :is="iconType" />
        </el-icon>
        <div class="navbar-right">
            <span class="expiry-date">服务到期：{{ formattedExpiryDate }}</span> <!-- 显示格式化后的到期时间 -->
            <span class="balance">账户余额: {{ balance }}</span> <!-- 显示余额 -->
            <Avatar />
        </div>
    </div>
</template>
  
<script setup>
import { computed } from 'vue';
import { Fold, Expand } from '@element-plus/icons-vue';
import { useSidebarStore } from '@/stores/sidebar';
import { useUserStore } from '@/stores/user';
import Avatar from './components/avatar.vue';

const sidebarStore = useSidebarStore();
const userStore = useUserStore();

const toggleClick = () => {
    sidebarStore.toggleCollapse();
};

const iconType = computed(() => {
    return sidebarStore.isFold ? Fold : Expand;
});

const formattedExpiryDate = computed(() => {
    const expiryDate = userStore.getExpiryDate;
    if (!expiryDate) return '';
    const date = new Date(expiryDate);
    return date.toLocaleDateString(); // 格式化日期为年月日
});

const balance = computed(() => userStore.getBalance);  // 使用 computed 属性获取余额
</script>
  
<style lang="scss" scoped>
.hamburger-container {
    margin-right: 16px;
    box-sizing: border-box;
    cursor: pointer;
    font-size: 28px;
}

.navbar {
    width: 100%;
    height: 60px;
    overflow: hidden;
    background-color: #fff;
    box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
    padding: 0 16px;
    display: flex;
    align-items: center;
    box-sizing: border-box;
    position: relative;
    margin: 0; // 确保没有外边距
    --el-header-padding: 0; // 覆盖默认的 padding

    .navbar-right {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: flex-end;

        .balance {
            margin-right: 16px;
            font-size: 14px;
            color: #333;
        }

        .expiry-date {
            margin-right: 16px;
            font-size: 14px;
            color: #333;
        }

        :deep(.navbar-item) {
            display: inline-block;
            margin-right: 0px;
            font-size: 22px;
            color: #5a5e66;
            box-sizing: border-box;
            cursor: pointer;
        }
    }
}
</style>
  