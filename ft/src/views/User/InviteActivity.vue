<template>
    <div class="invite-container">
        <!-- 邀请活动卡片 -->
        <el-card class="invite-card">
            <div class="invite-card-content">
                <h2>邀请活动</h2>
                <p>每邀请一名用户，并成功升级，您将获得 30 天的服务到期奖励。</p>
                <p>您的邀请链接：</p>
                <el-input v-model="inviteUrl" readonly style="width: 100%; margin-bottom: 10px;" />
                <el-button type="primary" @click="copyInviteLink">复制邀请链接</el-button>
            </div>
        </el-card>

        <!-- 已邀请用户卡片 -->
        <el-card class="invited-users-card" style="margin-top: 20px;">
            <div class="invited-users-content">
                <h3>已邀请的用户</h3>
                <el-table :data="invitees" style="width: 100%">
                    <el-table-column prop="username" label="用户名" />
                    <el-table-column prop="created_at" label="邀请时间" />
                    <el-table-column prop="rewarded_at" label="赠送时间" />
                    <el-table-column prop="is_rewarded" label="是否已奖励">
                        <template #default="scope">
                            <el-tag v-if="scope.row.is_rewarded" type="success">已赠送30天</el-tag>
                            <el-tag v-else type="warning">未奖励</el-tag>
                        </template>
                    </el-table-column>
                </el-table>
            </div>
        </el-card>
    </div>
</template>
  
<script setup>
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import apiClient from "@/api/index.js";

const inviteUrl = ref("");
const invitees = ref([]);

onMounted(async () => {
    try {
        // 获取邀请链接
        const linkResponse = await apiClient.get("/generate-invite-link/");
        inviteUrl.value = linkResponse.data.invite_url;

        // 获取邀请的用户信息
        const inviteResponse = await apiClient.get("/invite-info/");
        invitees.value = inviteResponse.data.invitees;
    } catch (error) {
        ElMessage.error("获取邀请信息失败");
    }
});

const copyInviteLink = () => {
    navigator.clipboard.writeText(inviteUrl.value)
        .then(() => {
            ElMessage.success("邀请链接已复制");
        })
        .catch(() => {
            ElMessage.error("复制失败");
        });
};
</script>
  
<style scoped>
.invite-container {
    padding: 30px;
    background-color: #f9f9f9;
}

.invite-card,
.invited-users-card {
    width: 100%;
    margin: 0 auto;
    border-radius: 10px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.invite-card-content,
.invited-users-content {
    padding: 20px;
}

h2,
h3 {
    margin-bottom: 20px;
    color: #333;
}

p {
    margin-bottom: 15px;
    line-height: 1.6;
    color: #555;
}

.el-input {
    margin-bottom: 15px;
}

.el-button {
    margin-top: 10px;
}

.el-table {
    margin-top: 15px;
}

.el-card {
    background-color: #ffffff;
    transition: transform 0.3s;
}

.el-card:hover {
    transform: translateY(-5px);
}

.el-tag {
    font-size: 14px;
    padding: 5px 10px;
}
</style>
