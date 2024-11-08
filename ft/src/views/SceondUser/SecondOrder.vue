<template>
    <div class="order-page">
        <div class="tabs-header">
            <div class="tab-left" :class="{ active: activeTab === 'pending' }" @click="activeTab = 'pending'">待审核订单</div>
            <div class="tab-right" :class="{ active: activeTab === 'completed' }" @click="activeTab = 'completed'">已完成订单
            </div>
        </div>

        <div class="tab-content">
            <!-- 待审核订单展示 -->
            <div v-if="activeTab === 'pending'">
                <el-card v-for="order in pendingOrders" :key="order.order_number" class="order-card" shadow="never">
                    <div class="card-header">
                        <span>{{ formatDateTime(order.add_time) }}</span>
                        <span class="card-amount">{{ order.commission_amount || '待定' }} 元</span>
                    </div>
                    <div class="divider"></div>
                    <div class="card-footer">
                        <span>订单编号: {{ order.order_number }}</span>
                    </div>
                </el-card>
            </div>

            <!-- 已完成订单展示 -->
            <div v-if="activeTab === 'completed'">
                <el-card v-for="order in completedOrders" :key="order.order_number" class="order-card" shadow="never">
                    <div class="card-header">
                        <span>{{ formatDateTime(order.update_time) }}</span>
                        <span class="card-amount">{{ order.commission_amount }} 元</span>
                    </div>
                    <div class="divider"></div>
                    <div class="card-footer">
                        <span>订单编号: {{ order.order_number }}</span>
                    </div>
                </el-card>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/api/index.js';

// 日期格式化函数
const formatDateTime = (dateString) => {
    const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleString('zh-CN', options);
};

const activeTab = ref('pending');
const pendingOrders = ref([]);
const completedOrders = ref([]);
const firstLevelUserUserId = ref(sessionStorage.getItem('fuser_id')); // 获取存储的一级用户ID

const fetchPendingOrders = async () => {
    try {
        const response = await apiClient.get('/pending-order-requests/', {
            params: { first_level_user_user_id: firstLevelUserUserId.value }
        });
        pendingOrders.value = response.data;
    } catch (error) {
        console.error('Failed to fetch pending orders:', error);
    }
};

const fetchCompletedOrders = async () => {
    try {
        const response = await apiClient.get('/completed-orders/', {
            params: { first_level_user_user_id: firstLevelUserUserId.value }
        });
        completedOrders.value = response.data;
    } catch (error) {
        console.error('Failed to fetch completed orders:', error);
    }
};

onMounted(() => {
    fetchPendingOrders();
    fetchCompletedOrders();
});
</script>

<style>
.order-page {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    height: 100vh;
    background-color: #f5f5f5;
    padding: 20px;
    box-sizing: border-box;
}

.tabs-header {
    position: fixed;
    top: 0;
    width: 100%;
    max-width: 650px;
    background-color: #fff;
    z-index: 1000;
    display: flex;
    justify-content: space-between;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    padding: 10px 0;
    height: 40px;
}

.tab-left,
.tab-right {
    flex: 1;
    text-align: center;
    padding: 10px 0;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
}

.tab-left.active,
.tab-right.active {
    font-weight: bold;
    border-bottom: 2px solid #409EFF;
    color: #409EFF;
}

.tab-left:hover,
.tab-right:hover {
    background-color: #f0f0f0;
}

.tab-content {
    flex: 1;
    margin-top: 50px;
    width: 100%;
    max-width: 650px;
    padding: 10px;
    border-radius: 10px;
    background-color: #fff;
}

/* 控制卡片的高度和内外间距 */
.order-card {
    margin-bottom: 12px;
    /* 控制卡片之间的间距，稍微增加 */
    padding: 8px 12px !important;
    /* 增加卡片内部的 padding */
    height: auto;
    /* 确保卡片高度根据内容自动调整 */
    min-height: 80px;
    /* 增加最小高度，使内容更宽松 */
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    /* 调整卡片阴影 */
    border-radius: 8px;
    background-color: #f9f9f9;
    font-size: 16px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.3s ease;
    /* 添加过渡效果 */
}

/* 悬浮效果 */
.order-card:hover {
    transform: translateY(-5px);
    /* 悬浮时轻微上移 */
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    /* 增加阴影 */
}

/* 覆盖el-card默认样式 */
.el-card__body {
    padding: 0 !important;
    /* 覆盖el-card的padding，确保没有额外空白 */
}

/* 控制卡片头部的样式 */
.card-header {
    display: flex;
    justify-content: space-between;
    font-size: 16px;
    color: #666;
}

/* 控制金额样式 */
.card-amount {
    font-weight: bold;
    color: #409EFF;
}

/* 控制分割线的样式 */
.divider {
    height: 1px;
    background-color: #eee;
    margin: 4px 0;
    /* 增加间距，稍微放宽分割线 */
}

/* 控制卡片底部的样式 */
.card-footer {
    font-size: 16px;
    color: #333;
}</style>
