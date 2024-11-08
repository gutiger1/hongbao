<template>
    <div>
        <h1 class="maintitle">已返佣的订单</h1>
        <div style="margin-top: 20px;" class="form-container">
            <el-form :inline="true" size="small" @submit.native.prevent class="demo-form-inline">
                <el-form-item label="订单编号">
                    <el-input v-model="filters.order_number" placeholder="输入订单编号" clearable></el-input>
                </el-form-item>
                <el-form-item label="店铺名称">
                    <el-input v-model="filters.shop" placeholder="输入店铺名称" clearable></el-input>
                </el-form-item>
                <el-form-item label="提交用户">
                    <el-input v-model="filters.tijiao" placeholder="输入提交用户" clearable></el-input>
                </el-form-item>
                <el-form-item label="购买用户">
                    <el-input v-model="filters.buyer_open_uid" placeholder="输入购买用户" clearable></el-input>
                </el-form-item>
                <el-form-item label="微信支付单号">
                    <el-input v-model="filters.wx_batch_id" placeholder="输入微信支付单号" clearable></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="fetchOrders">筛选</el-button>
                </el-form-item>
            </el-form>
        </div>

        <el-table :data="paginatedOrders" @selection-change="handleSelectionChange">
            <el-table-column prop="order_number" label="订单编号"></el-table-column>
            <el-table-column prop="amount" label="订单金额" width="110"></el-table-column>
            <el-table-column prop="commission_amount" label="佣金" width="100"></el-table-column>
            <el-table-column prop="shop.name" label="店铺名称"></el-table-column>
            <el-table-column prop="tijiao" label="提交用户" width="270"></el-table-column> <!-- 添加提交用户 -->
            <el-table-column prop="buyer_open_uid" label="购买用户" width="250"></el-table-column>
            <el-table-column prop="wx_batch_id" label="微信支付单号" width="400"></el-table-column>
            <el-table-column prop="update_time" label="更新时间" :formatter="formatDateTime"></el-table-column>
        </el-table>

        <div class="pagination-container">
            <Pagination :currentPage="currentPage" :pageSize="pageSize" :total="totalOrders" :pageCount="pageCount"
                prev-text="上一页" next-text="下一页" @update:currentPage="handleCurrentChange"
                @update:pageSize="handleSizeChange" />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import apiClient from '@/api/index.js';
import Pagination from '@/components/Pagination.vue';

const orders = ref([]);
const selectedOrders = ref([]);
const filters = ref({
    order_number: '',
    shop: '',
    tijiao: '',
    buyer_open_uid: '',
    wx_batch_id: ''
});
const currentPage = ref(1);
const pageSize = ref(10);
const totalOrders = ref(0);

// 获取已发放的订单
const fetchOrders = async () => {
    try {
        const response = await apiClient.get('orders/', {
            params: {
                status: 'distributed',  // 请求已发放的订单
                order_number: filters.value.order_number,
                shop: filters.value.shop,
                tijiao: filters.value.tijiao,
                buyer_open_uid: filters.value.buyer_open_uid,
                wx_batch_id: filters.value.wx_batch_id,
                page: currentPage.value,
                page_size: pageSize.value
            }
        });
        orders.value = response.data.results;  // 获取后端分页结果
        totalOrders.value = response.data.count;  // 总订单数
    } catch (error) {
        ElMessage.error('获取订单信息失败');
    }
};

// 处理分页
const handleSizeChange = (size) => {
    pageSize.value = size;
    currentPage.value = 1;
    fetchOrders();
};

const handleCurrentChange = (page) => {
    currentPage.value = page;
    fetchOrders();
};

// 计算分页数据
const paginatedOrders = computed(() => {
    return orders.value;
});

// 时间格式化函数
const formatDateTime = (row, column, cellValue) => {
    if (cellValue) {
        return new Date(cellValue).toLocaleString();
    }
    return '';
};

onMounted(() => {
    fetchOrders();
});
</script>

<style scoped>
.pagination-container {
    display: flex;
    justify-content: flex-end;
    /* 分页栏右对齐 */
    align-items: center;
    margin-top: 20px;
}
</style>
