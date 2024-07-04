<template>
  <div>
    <h1>我的店铺</h1>
    <el-table :data="shops" style="width: 100%">
      <el-table-column prop="name" label="店铺名称"></el-table-column>
      <el-table-column prop="second_level_users_count" label="二级用户数量"></el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api/index.js';
import { ElMessage } from 'element-plus';

const shops = ref([]);

const fetchShops = async () => {
  try {
    const response = await apiClient.get('shops/');
    shops.value = response.data;
  } catch (error) {
    ElMessage.error('获取店铺信息失败');
    console.error('Failed to fetch shops:', error);
  }
};

onMounted(fetchShops);
</script>
