<template>
  <div>
    <!-- 表单 -->
    <el-form :inline="true" size="small" class="demo-form-inline" @submit.native.prevent>
      <el-form-item label="店铺名称">
        <el-input v-model="filters.shop" placeholder="输入店铺名称"></el-input>
      </el-form-item>
      <el-form-item label="提交人">
        <el-input v-model="filters.tijiao" placeholder="输入提交人"></el-input>
      </el-form-item>
      <el-form-item label="订单状态">
        <el-select v-model="filters.status" placeholder="选择订单状态">
          <el-option label="全部" value=""></el-option>
          <el-option label="已发放" value="distributed"></el-option>
          <el-option label="待处理" value="pending"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchOrders">筛选</el-button>
      </el-form-item>
    </el-form>
    <!-- 表格 -->
    <el-table :data="filteredOrders" style="width: 100%">
      <el-table-column prop="order_number" label="订单编号"></el-table-column>
      <el-table-column prop="amount" label="订单金额"></el-table-column>
      <el-table-column prop="status" label="状态" :formatter="formatStatus"></el-table-column>
      <el-table-column prop="shop.name" label="店铺名称" width="200"></el-table-column>
      <el-table-column prop="tijiao" label="提交人" width="200"></el-table-column>
      <el-table-column prop="add_time" label="创建时间" width="200" :formatter="formatDateTime"></el-table-column>
      <el-table-column prop="update_time" label="更新时间" width="200" :formatter="formatDateTime"></el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import apiClient from '../api/index.js';

const orders = ref([]);
const filters = ref({
  shop: '',
  tijiao: '',
  status: ''
});

const statusMap = {
  pending: '待处理',
  distributed: '已发放',
  completed: '已完成'
};

const fetchOrders = () => {
  apiClient.get('orders/')
    .then(response => {
      orders.value = response.data;
    })
    .catch(error => {
      ElMessage.error('获取订单信息失败');
      console.error(error);
    });
};

// 格式化状态值
const formatStatus = (row, column, cellValue) => {
  return statusMap[cellValue] || cellValue;
};


// 时间格式化
const formatDateTime = (row, column, cellValue) => {
  if (!cellValue) return '';
  const date = new Date(cellValue);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

// 表格的数据
const filteredOrders = computed(() => {
  return orders.value.filter(order => {
    return (
      (!filters.value.shop || order.shop.name.includes(filters.value.shop)) &&
      (!filters.value.tijiao || (order.tijiao && order.tijiao.includes(filters.value.tijiao))) &&
      (!filters.value.status || order.status === filters.value.status)
    );
  });
});

onMounted(fetchOrders);
</script>

<style scoped>
.demo-form-inline .el-form-item {
  margin-right: 10px;
}
</style>
