<template>
    <div>
        <h1 class="maintitle">用户管理</h1>
        <!-- 筛选框 -->
        <div style="margin-top: 20px;" class="form-container">
            <el-form :inline="true" size="small" @submit.native.prevent class="demo-form-inline">
                <el-form-item label="用户名">
                    <el-input v-model="filters.username" placeholder="输入用户名" clearable></el-input>
                </el-form-item>
                <el-form-item label="微信昵称">
                    <el-input v-model="filters.wechat_nickname" placeholder="输入微信昵称" clearable></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="fetchSecondLevelUsers">筛选</el-button>
                </el-form-item>
            </el-form>
        </div>

        <!-- 用户表格 -->
        <el-table :data="paginatedUsers">
            <!-- <el-table-column prop="id" label="ID" width="100px"></el-table-column> -->
            <el-table-column label="用户名">
                <template #default="scope">
                    <div>
                        <div>{{ scope.row.user.username }}</div>
                        <div>(该用户全网共开通 {{ getTotalShopCount(scope.row.user.username) }} 个店铺会员)</div>
                    </div>
                </template>
            </el-table-column>
            <el-table-column prop="wechat_nickname" label="微信昵称" width="150px"></el-table-column>
            <el-table-column label="店铺会员" width="500px">
                <template #default="scope">
                    <el-checkbox-group v-model="userShopAssociations[scope.row.id]"
                        @change="updateAssociation(scope.row.id)">
                        <el-checkbox v-for="shop in shops" :value="shop.id" :key="shop.id">{{ shop.name }}</el-checkbox>
                    </el-checkbox-group>
                </template>
            </el-table-column>
            <el-table-column label="备注" width="300px">
                <template #default="scope">
                    <div>
                        <p v-if="scope.row.blacklist_info.total_blacklist_count > 0">
                            被店主拉黑次数: {{ scope.row.blacklist_info.total_blacklist_count }}
                        </p>
                        <ul v-if="Object.keys(scope.row.blacklist_info.reasons).length > 0">
                            <li v-for="(count, reason) in scope.row.blacklist_info.reasons" :key="reason">
                                有{{ count }}个店主将该微信标记为{{ reason }}
                            </li>
                        </ul>
                    </div>
                </template>
            </el-table-column>
            <el-table-column label="操作">
                <template #default="scope">
                    <!-- 显示拉黑或取消拉黑的按钮 -->
                    <el-button v-if="scope.row.is_blacklisted" class="cancel-blacklist-btn" type="warning"
                        @click="removeFromBlacklist(scope.row)">取消拉黑</el-button>
                    <el-button v-else type="danger" @click="openBlacklistDialog(scope.row)">拉黑用户</el-button>
                </template>
            </el-table-column>
        </el-table>

        <!-- 分页栏 -->
        <div class="pagination-container">
            <Pagination :currentPage="currentPage" :pageSize="pageSize" :total="filteredTotalUsers" :pageCount="pageCount"
                @update:currentPage="handleCurrentChange" @update:pageSize="handleSizeChange" />
        </div>

        <!-- 拉黑对话框 -->
        <el-dialog title="拉黑用户" v-model="blacklistDialogVisible" width="380px" :custom-class="'custom-blacklist-dialog'">
            <div class="blacklist-content">
                <div class="reason-selection">
                    选择拉黑原因：
                    <el-select v-model="selectedReason" placeholder="请选择拉黑原因" class="select-reason">
                        <el-option label="白嫖" value="white_piao"></el-option>
                        <el-option label="同行" value="competition"></el-option>
                        <el-option label="欺诈" value="fraud"></el-option>
                        <el-option label="差评" value="bad_review"></el-option>
                    </el-select>
                </div>
                <div style="margin-top: 20px;">
                    <el-alert title="提示：该操作将拉黑该用户及其关联用户（包括关联的购买用户和该用户的其他微信）" type="warning" show-icon>
                    </el-alert>
                </div>
            </div>
            <span slot="footer" class="dialog-footer">
                <el-button @click="blacklistDialogVisible = false">取消</el-button>
                <el-button type="danger" @click="addToBlacklist">确认拉黑</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import apiClient from '@/api/index.js';
import Pagination from '@/components/Pagination.vue';

const secondLevelUsers = ref([]);
const shops = ref([]);
const userShopAssociations = ref({});
const userShopCounts = ref({});
const filters = ref({
    username: '',
    wechat_nickname: ''
});
const currentPage = ref(1);
const pageSize = ref(10);

// 拉黑相关
const blacklistDialogVisible = ref(false);
const selectedUser = ref(null); // 被选中拉黑的用户
const selectedReason = ref('white_piao'); // 默认拉黑原因

// 打开拉黑对话框
const openBlacklistDialog = (user) => {
    selectedUser.value = user;
    blacklistDialogVisible.value = true;
};

// 提交拉黑请求
const addToBlacklist = async () => {
    const userId = selectedUser.value.id;
    const reason = selectedReason.value;

    try {
        const response = await apiClient.post('/add-to-blacklist/', {
            second_level_user_id: userId,
            reason: reason
        });
        ElMessage.success('用户已拉黑');
        blacklistDialogVisible.value = false;

        // 更新该用户的拉黑状态
        const user = secondLevelUsers.value.find(user => user.id === userId);
        if (user) {
            user.is_blacklisted = true; // 更新用户的拉黑状态为 true
        }

    } catch (error) {
        console.error("拉黑失败：", error);
        ElMessage.error('拉黑失败');
    }
};

// 取消拉黑请求
const removeFromBlacklist = async (user) => {
    const userId = user.id;
    try {
        const response = await apiClient.post('/remove-from-blacklist/', {
            second_level_user_id: userId
        });
        ElMessage.success('已取消拉黑');
        user.is_blacklisted = false; // 直接更新用户的拉黑状态为 false
    } catch (error) {
        console.error("取消拉黑失败：", error);
        ElMessage.error('取消拉黑失败');
    }
};

// 获取用户列表
const fetchSecondLevelUsers = async () => {
    try {
        const response = await apiClient.get('second-level-users/');
        secondLevelUsers.value = response.data;
        response.data.forEach(user => {
            userShopAssociations.value[user.id] = user.shops.map(shop => shop.id);
        });
    } catch (error) {
        ElMessage.error('获取用户列表失败');
    }
};

// 获取店铺列表
const fetchShops = async () => {
    try {
        const response = await apiClient.get('shops/');
        shops.value = response.data;
    } catch (error) {
        ElMessage.error('获取店铺列表失败');
    }
};

// 获取用户店铺统计
const fetchUserShopCounts = async () => {
    try {
        const response = await apiClient.get('user-shop-counts/');
        userShopCounts.value = response.data.reduce((acc, user) => {
            acc[user.user__username] = user.total_shops;
            return acc;
        }, {});
    } catch (error) {
        ElMessage.error('获取用户店铺统计失败');
    }
};

// 更新用户店铺关联
const updateAssociation = async (userId) => {
    const selectedShopIds = userShopAssociations.value[userId];
    const allShopIds = shops.value.map(shop => shop.id);

    for (const shopId of allShopIds) {
        const action = selectedShopIds.includes(shopId) ? 'add' : 'remove';
        try {
            await apiClient.post('manage-user-shop/', {
                second_level_user_id: userId,
                shop_id: shopId,
                action: action,
            });
            ElMessage.success('更新成功');
        } catch (error) {
            ElMessage.error('更新失败');
        }
    }
};

const handleSizeChange = (size) => {
    pageSize.value = size;
};

const handleCurrentChange = (page) => {
    currentPage.value = page;
};

// 获取用户总店铺数
const getTotalShopCount = (username) => {
    return userShopCounts.value[username] || 0;
};

const filteredUsers = computed(() => {
    return secondLevelUsers.value.filter(user => {
        return (
            (!filters.value.username || user.user.username.includes(filters.value.username)) &&
            (!filters.value.wechat_nickname || user.wechat_nickname.includes(filters.value.wechat_nickname))
        );
    });
});

const paginatedUsers = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value;
    const end = start + pageSize.value;
    return filteredUsers.value.slice(start, end);
});

const filteredTotalUsers = computed(() => filteredUsers.value.length);

const pageCount = computed(() => Math.ceil(filteredTotalUsers.value / pageSize.value));

onMounted(() => {
    fetchSecondLevelUsers();
    fetchShops();
    fetchUserShopCounts(); // 获取用户总店铺数
});
</script>

<style scoped>
.pagination-container {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-top: 20px;
}

/* 取消拉黑按钮样式 */
.cancel-blacklist-btn {
    background-color: #ff9800;
    /* 橙色背景 */
    color: white;
    /* 白色文字 */
}

/* 拉黑对话框美化 */
.custom-blacklist-dialog .el-dialog__header {
    background-color: #f2f2f2;
    padding: 10px 15px;
    font-size: 18px;
    color: #333;
}

.custom-blacklist-dialog .el-dialog__body {
    background-color: #fefefe;
    padding: 20px;
}

.blacklist-content {
    margin-bottom: 20px;
}

.reason-selection {
    display: flex;
    align-items: center;
    font-size: 14px;
}

.el-select.select-reason {
    margin-left: 10px;
    width: 160px;
}

.dialog-footer {
    display: flex;
    justify-content: flex-end;
    padding: 10px 0;
}

.el-button {
    font-size: 14px;
    padding: 8px 20px;
}
</style>
