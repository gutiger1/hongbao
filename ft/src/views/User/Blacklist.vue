<template>
    <div>
        <h1 class="maintitle">黑名单</h1>

        <!-- 黑名单表格 -->
        <el-table :data="paginatedBlacklist">
            <!-- 被拉黑的用户 -->
            <el-table-column prop="second_level_user_username" label="拉黑用户"></el-table-column>
            <!-- buyer_open_uid -->
            <el-table-column prop="buyer_open_uid" label="购买用户"></el-table-column>
            <!-- 拉黑原因 -->
            <el-table-column prop="reason_display" label="拉黑原因"></el-table-column>
            <!-- 关联拉黑的用户 -->
            <el-table-column label="关联拉黑用户">
                <template #default="scope">
                    <ul>
                        <li v-for="(relatedUser, index) in scope.row.related_blacklisted_users" :key="index">
                            {{ relatedUser.username }} - {{ relatedUser.reason }}
                        </li>
                    </ul>
                </template>
            </el-table-column>
            <!-- 操作 -->
            <el-table-column label="操作">
                <template #default="scope">
                    <el-button type="danger" @click="removeFromBlacklist(scope.row)">取消拉黑</el-button>
                </template>
            </el-table-column>
        </el-table>

        <!-- 分页栏 -->
        <div class="pagination-container">
            <Pagination :currentPage="currentPage" :pageSize="pageSize" :total="totalItems" :pageCount="pageCount"
                @update:currentPage="handleCurrentChange" @update:pageSize="handleSizeChange" />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import apiClient from '@/api/index.js';
import Pagination from '@/components/Pagination.vue';

const blacklistedUsers = ref([]);
const totalItems = ref(0);  // 总记录数
const currentPage = ref(1);
const pageSize = ref(10);

// 获取黑名单和关联用户信息
const fetchBlacklist = async () => {
    try {
        const response = await apiClient.get('/blacklist/', {
            params: {
                page: currentPage.value,
                page_size: pageSize.value,
            },
        });
        blacklistedUsers.value = response.data.results;
        totalItems.value = response.data.count;
    } catch (error) {
        ElMessage.error('获取黑名单失败');
    }
};

// 取消拉黑
const removeFromBlacklist = async (user) => {
    try {
        await apiClient.post('/remove-from-blacklist/', {
            second_level_user_id: user.second_level_user_id,
        });
        ElMessage.success('已取消拉黑');
        fetchBlacklist();  // 重新获取黑名单数据
    } catch (error) {
        ElMessage.error('取消拉黑失败');
    }
};

// 分页控制
const handleSizeChange = (size) => {
    pageSize.value = size;
    fetchBlacklist();
};

const handleCurrentChange = (page) => {
    currentPage.value = page;
    fetchBlacklist();
};

// 分页计算属性
const paginatedBlacklist = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value;
    const end = start + pageSize.value;
    return blacklistedUsers.value.slice(start, end);
});

const pageCount = computed(() => Math.ceil(totalItems.value / pageSize.value));

onMounted(() => {
    fetchBlacklist();
});
</script>

<style scoped>
.maintitle {
    margin-bottom: 20px;
}

.pagination-container {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-top: 20px;
}
</style>
