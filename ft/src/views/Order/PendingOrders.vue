<template>
    <h1 class="maintitle">会员用户上传未返佣的订单</h1>
    <!-- 筛选表单 -->
    <div style="margin-top: 20px;" class="form-container">
        <el-form :inline="true" size="small" @submit.native.prevent class="demo-form-inline">
            <el-form-item label="订单编号">
                <el-input v-model="filters.order_number" placeholder="输入订单编号" clearable></el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="fetchPendingOrders">筛选</el-button>
            </el-form-item>
        </el-form>
    </div>
    <div>
        <el-table :data="paginatedOrders" ref="pendingOrdersTable" @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="55"></el-table-column>
            <el-table-column prop="order_number" label="订单编号"></el-table-column>
            <el-table-column prop="second_level_user" label="用户名" width="350"></el-table-column>
            <el-table-column prop="second_level_user_wechat_nickname" label="微信昵称"></el-table-column>
            <el-table-column prop="add_time" label="上传时间" :formatter="formatDateTime"></el-table-column>

            <!-- 黑名单信息列 -->
            <el-table-column label="备注">
                <template #default="scope">
                    <div v-if="scope.row.blacklist_info && scope.row.blacklist_info.total_blacklist_count > 0">
                        <p>被店主拉黑次数: {{ scope.row.blacklist_info.total_blacklist_count }}</p>
                        <ul>
                            <li v-for="(count, reason) in scope.row.blacklist_info.reasons" :key="reason">
                                有{{ count }}个店主将该用户标记为{{ reason }}
                            </li>
                        </ul>
                    </div>
                    <div v-else>
                        无
                    </div>
                </template>
            </el-table-column>

            <el-table-column label="操作">
                <template #default="scope">
                    <el-button size="small" type="danger" @click="deleteOrder(scope.row.id)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>
        <div class="pagination-container">
            <el-button type="danger" @click="deleteSelectedOrders" :disabled="!hasSelectedOrders">批量删除</el-button>
            <Pagination :currentPage="currentPage" :pageSize="pageSize" :total="totalOrders" :pageCount="pageCount"
                @update:currentPage="handleCurrentChange" @update:pageSize="handleSizeChange" />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import apiClient from '@/api/index.js';
import { formatDateTime } from '@/utils/date';
import Pagination from '@/components/Pagination.vue';

const pendingOrders = ref([]);
const selectedOrders = ref([]);
const filters = ref({
    order_number: ''
});

const currentPage = ref(1);
const pageSize = ref(10);
const totalOrders = ref(0);
const sizes = [10, 20, 30, 40];

const fetchPendingOrders = async () => {
    try {
        const response = await apiClient.get('pending-orders/');

        // 添加黑名单信息到订单数据
        pendingOrders.value = response.data.map(order => {
            return {
                ...order,
                blacklist_info: order.blacklist_info || { total_blacklist_count: 0, reasons: {} }
            };
        });

        totalOrders.value = pendingOrders.value.length;
    } catch (error) {
        ElMessage.error('获取待处理订单失败');
    }
};

const deleteOrder = async (orderId) => {
    try {
        await ElMessageBox.confirm('此操作将永久删除该订单, 是否继续?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        });
        await apiClient.delete(`pending-orders/${orderId}/`);
        ElMessage.success('订单删除成功');
        fetchPendingOrders();
    } catch (error) {
        if (error !== 'cancel') {
            ElMessage.error('删除订单失败');
        }
    }
};

const deleteSelectedOrders = async () => {
    try {
        await ElMessageBox.confirm('此操作将永久删除选中的订单, 是否继续?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        });
        await apiClient.post('pending-orders/batch-delete/', { ids: selectedOrders.value });
        ElMessage.success('订单批量删除成功');
        fetchPendingOrders();
    } catch (error) {
        if (error !== 'cancel') {
            ElMessage.error('批量删除订单失败');
        }
    }
};

const handleSelectionChange = (val) => {
    selectedOrders.value = val.map((item) => item.id);
};

const handleSizeChange = (size) => {
    pageSize.value = size;
};

const handleCurrentChange = (page) => {
    currentPage.value = page;
};

const filteredOrders = computed(() => {
    return pendingOrders.value.filter(order => {
        return (
            (!filters.value.order_number || order.order_number.includes(filters.value.order_number))
        );
    });
});

const paginatedOrders = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value;
    const end = start + pageSize.value;
    return filteredOrders.value.slice(start, end);
});

const hasSelectedOrders = computed(() => selectedOrders.value.length > 0);

const pageCount = computed(() => Math.ceil(totalOrders.value / pageSize.value));

onMounted(() => {
    fetchPendingOrders();
});
</script>

<style scoped>
.pagination-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
}
</style>
