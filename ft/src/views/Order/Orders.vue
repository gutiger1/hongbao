<template>
  <div>
    <!-- 暂未有其他用处 -->
    <div class="form-container">
      <el-form :inline="true" size="small" class="demo-form-inline" @submit.native.prevent>
        <el-form-item label="订单编号">
          <el-input v-model="filters.order_number" placeholder="输入订单号" clearable></el-input>
        </el-form-item>
        <el-form-item label="店铺名称">
          <el-input v-model="filters.shop" placeholder="输入店铺名称" clearable></el-input>
        </el-form-item>
        <el-form-item label="提交人">
          <el-input v-model="filters.tijiao" placeholder="输入提交人" clearable></el-input>
        </el-form-item>
        <el-form-item label="订单状态">
          <el-select v-model="filters.status" placeholder="选择订单状态" clearable>
            <el-option label="全部" value=""></el-option>
            <el-option label="已发放" value="distributed"></el-option>
            <el-option label="待处理" value="pending"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchOrders">筛选</el-button>
        </el-form-item>
      </el-form>
      <!-- 新增订单按钮 -->
      <el-button type="primary" class="add-order-button" @click="dialogFormVisible = true">新增订单</el-button>
    </div>
    <!-- 新增订单弹窗 -->
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
    <!-- 表格 -->
    <el-table :data="paginatedOrders" style="width: 100%">
      <el-table-column prop="order_number" label="订单编号"></el-table-column>
      <el-table-column prop="amount" label="订单金额"></el-table-column>
      <el-table-column prop="status" label="状态" :formatter="formatStatus"></el-table-column>
      <el-table-column prop="shop.name" label="店铺名称"></el-table-column>
      <el-table-column prop="tijiao" label="提交人" width="300"></el-table-column>
      <el-table-column prop="add_time" label="创建时间" :formatter="formatDateTime" width="260"></el-table-column>
      <el-table-column prop="update_time" label="更新时间" :formatter="formatDateTime" width="260"></el-table-column>
    </el-table>
    <!-- 分页 -->
    <Pagination :currentPage="currentPage" :pageSize="pageSize" :total="totalOrders" :pageCount="pageCount"
      @update:currentPage="updateCurrentPage" @update:pageSize="updatePageSize" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import apiClient from '@/api/index.js';
import { formatDateTime } from '@/utils/date';
import Pagination from '@/components/Pagination.vue';

const orders = ref([]);
const shops = ref([]);
const filters = ref({
  order_number: '',
  shop: '',
  tijiao: '',
  status: ''
});
const newOrder = ref({
  order_number: '',
  amount: 0,
  shop: ''
});
const dialogFormVisible = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);

const statusMap = {
  pending: '待处理',
  distributed: '已发放',
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

const fetchShops = () => {
  apiClient.get('shops/')
    .then(response => {
      shops.value = response.data;
      console.log('Fetched shops:', shops.value);
    })
    .catch(error => {
      ElMessage.error('获取店铺信息失败');
      console.error(error);
    });
};

// 格式化状态值
const formatStatus = (row, column, cellValue) => {
  return statusMap[cellValue] || cellValue;
};

// 表格的数据
const filteredOrders = computed(() => {
  return orders.value.filter(order => {
    return (
      (!filters.value.order_number || order.order_number.includes(filters.value.order_number)) &&
      (!filters.value.shop || order.shop.name.includes(filters.value.shop)) &&
      (!filters.value.tijiao || (order.tijiao && order.tijiao.includes(filters.value.tijiao))) &&
      (!filters.value.status || order.status === filters.value.status)
    );
  });
});

const paginatedOrders = computed(() => {
  const sortedOrders = filteredOrders.value.sort((a, b) => new Date(b.add_time) - new Date(a.add_time));
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredOrders.value.slice(start, end);
});

const totalOrders = computed(() => filteredOrders.value.length);

const pageCount = computed(() => Math.ceil(totalOrders.value / pageSize.value));

const addOrder = async () => {
  try {
    const orderData = {
      order_number: newOrder.value.order_number,
      amount: parseFloat(newOrder.value.amount),
      shop: newOrder.value.shop
    };

    console.log("addOrder called", orderData);
    const response = await apiClient.post('orders/', orderData);
    ElMessage.success('订单新增成功');
    dialogFormVisible.value = false;
    fetchOrders();
    fetchShops();
  } catch (error) {
    ElMessage.error('订单新增失败');
    console.error('Failed to add order:', error);
  }
};

// 分页相关方法
const updatePageSize = (size) => {
  pageSize.value = size;
  currentPage.value = 1; // 重置当前页为第一页
};

const updateCurrentPage = (page) => {
  currentPage.value = page;
};

onMounted(() => {
  fetchOrders();
  fetchShops();
});
</script>

<style scoped>
.form-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.demo-form-inline {
  flex: 1;
  display: flex;
  align-items: center;
}

.demo-form-inline .el-form-item {
  margin-right: 10px;
  margin-bottom: 0;
  display: flex;
  align-items: center;
}

.demo-form-inline .el-input,
.demo-form-inline .el-select,
.demo-form-inline .el-button {
  height: 32px;
  line-height: 32px;
}

.demo-form-inline .el-input__inner,
.demo-form-inline .el-select__inner {
  height: 32px;
  line-height: 32px;
  padding: 0 10px;
}

.dialog-footer {
  text-align: right;
}

.add-order-button {
  height: 32px;
  line-height: 32px;
  padding: 0 15px;
}

.el-button--primary {
  height: 32px;
  line-height: 32px;
}
</style>
