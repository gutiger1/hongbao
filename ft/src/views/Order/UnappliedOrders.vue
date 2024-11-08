<template>
    <div>
        <h1 class="maintitle">店主上传未申请返佣的订单</h1>
        <div style="margin-top: 20px;" class="form-container">
            <el-form :inline="true" size="small" @submit.native.prevent class="demo-form-inline">
                <el-form-item label="订单编号">
                    <el-input v-model="filters.order_number" placeholder="输入订单编号" clearable></el-input>
                </el-form-item>
                <el-form-item label="店铺名称">
                    <el-input v-model="filters.shop" placeholder="输入店铺名称" clearable></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="fetchOrders">筛选</el-button>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" class="add-order-button" @click="dialogFormVisible = true">新增订单</el-button>
                </el-form-item>
            </el-form>
        </div>

        <el-table :data="orders" @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="55"></el-table-column>
            <el-table-column prop="order_number" label="订单编号"></el-table-column>
            <el-table-column prop="amount" label="订单金额" width="110"></el-table-column>
            <el-table-column prop="commission_amount" label="佣金" width="100"></el-table-column>
            <el-table-column prop="shop.name" label="店铺名称"></el-table-column>
            <el-table-column prop="buyer_open_uid" label="购买用户" width="300"></el-table-column>
            <el-table-column prop="add_time" label="创建时间" :formatter="formatDateTime"></el-table-column>

            <el-table-column label="备注" width="300">
                <template #default="scope">
                    <div v-if="scope.row.blacklist_info && scope.row.blacklist_info.total_blacklist_count > 0">
                        <p>被店主拉黑次数: {{ scope.row.blacklist_info.total_blacklist_count }}</p>
                        <ul>
                            <li v-for="(count, reason) in scope.row.blacklist_info.reasons" :key="reason">
                                有{{ count }}位店主将该买家标记为{{ reason }}
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
                    <el-button size="small" type="danger" @click="deleteOrder(scope.row.id)"
                        style="height: 32px;">删除</el-button>
                    <el-button size="small" type="primary" @click="resubmitOrder(scope.row)"
                        style="height: 32px;">重新提交</el-button>
                </template>
            </el-table-column>
        </el-table>

        <div class="pagination-container">
            <el-button type="danger" @click="deleteSelectedOrders" :disabled="!hasSelectedOrders">批量删除</el-button>
            <Pagination :currentPage="currentPage" :pageSize="pageSize" :total="totalOrders" :pageCount="pageCount"
                @update:currentPage="handleCurrentChange" @update:pageSize="handleSizeChange" />
        </div>

        <el-dialog v-model="dialogFormVisible" title="新增订单" width="500">
            <el-form :model="newOrder" label-width="100px">
                <el-form-item label="订单编号">
                    <el-input v-model="newOrder.order_number"></el-input>
                </el-form-item>
                <el-form-item label="订单金额">
                    <el-input v-model="newOrder.amount" type="number"></el-input>
                </el-form-item>
                <el-form-item label="店铺名称">
                    <el-select v-model="newOrder.shop" placeholder="选择店铺">
                        <el-option v-for="shop in shops" :key="shop.id" :label="shop.name" :value="shop.id"></el-option>
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="dialogFormVisible = false">取消</el-button>
                    <el-button type="primary" @click="addOrder">确定</el-button>
                </div>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import apiClient from '@/api/index.js';
import Pagination from '@/components/Pagination.vue';

const orders = ref([]);
const selectedOrders = ref([]);
const filters = ref({
    order_number: '',
    shop: ''
});
const shops = ref([]);
const dialogFormVisible = ref(false);
const newOrder = ref({
    order_number: '',
    amount: '',
    shop: ''
});

const currentPage = ref(1);
const pageSize = ref(10);
const totalOrders = ref(0);

const fetchOrders = async () => {
    try {
        const response = await apiClient.get('orders/', {
            params: {
                status: 'pending',  // 添加筛选条件
                order_number: filters.value.order_number,  // 订单编号过滤条件
                shop: filters.value.shop,  // 店铺名称过滤条件
                page: currentPage.value,  // 当前页数
                page_size: pageSize.value  // 每页的大小
            }
        });
        orders.value = response.data.results;  // 获取后端分页结果
        totalOrders.value = response.data.count;  // 总订单数
    } catch (error) {
        ElMessage.error('获取订单信息失败');
    }
};

const fetchShops = async () => {
    try {
        const response = await apiClient.get('shops/');
        shops.value = response.data;
    } catch (error) {
        ElMessage.error('获取店铺信息失败');
    }
};

const addOrder = async () => {
    try {
        const orderData = {
            order_number: newOrder.value.order_number,
            amount: parseFloat(newOrder.value.amount),
            shop: newOrder.value.shop
        };
        await apiClient.post('orders/', orderData);
        ElMessage.success('订单新增成功');
        dialogFormVisible.value = false;
        currentPage.value = 1;  // 重置为第一页
        fetchOrders();
    } catch (error) {
        ElMessage.error('订单新增失败');
    }
};

const deleteOrder = async (orderId) => {
    try {
        await ElMessageBox.confirm('此操作将永久删除该订单, 是否继续?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        });
        await apiClient.delete(`orders/${orderId}/`);
        ElMessage.success('订单删除成功');
        fetchOrders();
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
        await apiClient.post('orders/batch-delete/', { ids: selectedOrders.value });
        ElMessage.success('订单批量删除成功');
        fetchOrders();
    } catch (error) {
        if (error !== 'cancel') {
            ElMessage.error('批量删除订单失败');
        }
    }
};

const resubmitOrder = async (order) => {
    try {
        await ElMessageBox.confirm('此操作将重新提交该订单, 是否继续?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        });
        await apiClient.delete(`orders/${order.id}/`);
        await apiClient.post('orders/', {
            order_number: order.order_number,
            amount: order.amount,
            shop: order.shop.id,
            buyer_open_uid: order.buyer_open_uid
        });
        ElMessage.success('订单重新提交成功');
        fetchOrders();
    } catch (error) {
        if (error !== 'cancel') {
            ElMessage.error('重新提交订单失败');
        }
    }
};

const handleSelectionChange = (val) => {
    selectedOrders.value = val.map((item) => item.id);
};

const handleSizeChange = (size) => {
    pageSize.value = size;
    currentPage.value = 1;  // 每次改变页面大小时，重置为第一页
    fetchOrders();
};

const handleCurrentChange = (page) => {
    currentPage.value = page;
    fetchOrders();
};

const hasSelectedOrders = computed(() => selectedOrders.value.length > 0);

const formatDateTime = (row, column, cellValue) => {
    if (cellValue) {
        return new Date(cellValue).toLocaleString();
    }
    return '';
};

onMounted(() => {
    fetchOrders();
    fetchShops();
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
