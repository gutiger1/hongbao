<template>
    <div>
        <h1 class="maintitle">资金记录</h1>
        <div style="margin-bottom: 20px;">
            <el-form :inline="true" size="small" class="demo-form-inline" @submit.native.prevent>
                <el-form-item label="订单编号">
                    <el-input v-model="filters.order_number" placeholder="输入订单编号" clearable></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="applyFilters">筛选</el-button>
                </el-form-item>
            </el-form>
        </div>

        <!-- 表格展示资金记录 -->
        <el-table :data="paginatedRecords">
            <el-table-column prop="balance" label="账户余额"></el-table-column>
            <el-table-column prop="change_type" label="业务类型"></el-table-column>
            <el-table-column prop="change_amount" label="业务金额"></el-table-column> <!-- 显示佣金金额 -->
            <el-table-column :formatter="formatDateTime" prop="time" label="时间"></el-table-column>
            <el-table-column prop="order_number" label="单号"></el-table-column>
        </el-table>

        <!-- 分页 -->
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 30, 40]"
            layout="total, sizes, prev, pager, next, jumper" :total="totalRecords" @size-change="handleSizeChange"
            @current-change="handleCurrentChange" class="paginationbox">
            <template #total> 总数: {{ totalRecords }} </template>
            <template #jumper> 去往 <el-input-number v-model="currentPage" :min="1" :max="pageCount"
                    @change="handleCurrentChange"></el-input-number> 页 </template>
        </el-pagination>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import apiClient from '@/api/index.js';
import { formatDateTime } from '@/utils/date'; // 导入工具函数

const financialRecords = ref([]);
const currentPage = ref(1);
const pageSize = ref(10);
const totalRecords = ref(0);
const filters = ref({
    order_number: ''
});

const fetchFinancialRecords = async () => {
    try {
        const response = await apiClient.get('/balance-change-records/');
        financialRecords.value = response.data.sort((a, b) => new Date(b.time) - new Date(a.time)); // 按时间倒序排序;
        totalRecords.value = financialRecords.value.length;
    } catch (error) {
        ElMessage.error('获取财务记录失败');
    }
};

// 应用过滤器
const applyFilters = () => {
    currentPage.value = 1; // 重置到第一页
    totalRecords.value = filteredRecords.value.length; // 更新总记录数
};

// 过滤数据
const filteredRecords = computed(() => {
    return financialRecords.value.filter(record => {
        return (!filters.value.order_number || record.order_number.includes(filters.value.order_number));
    });
});

// 分页数据
const paginatedRecords = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value;
    const end = start + pageSize.value;
    return filteredRecords.value.slice(start, end);
});

onMounted(() => {
    fetchFinancialRecords();
});
</script>
