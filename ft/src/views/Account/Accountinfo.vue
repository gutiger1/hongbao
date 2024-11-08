<template>
    <div class="account-info">
        <h1 class="maintitle">账户信息</h1>
        <el-form :model="accountInfo" label-width="120px" class="account-form">
            <el-form-item label="账户名">
                <el-input v-model="accountInfo.username" readonly></el-input>
            </el-form-item>
            <el-form-item label="修改密码">
                <el-button type="primary" @click="showChangePasswordDialog = true">修改密码</el-button>
            </el-form-item>
            <el-form-item label="服务到期时间">
                <el-input v-model="accountInfo.expiryDate" readonly></el-input>
            </el-form-item>
            <el-form-item label="账户余额">
                <el-input v-model="accountInfo.balance" readonly></el-input>
            </el-form-item>
        </el-form>

        <!-- 修改密码弹窗 -->
        <el-dialog title="修改密码" v-model="showChangePasswordDialog" width="500px">
            <el-form :model="passwordForm" label-width="120px" ref="passwordFormRef">
                <el-form-item label="当前密码" :rules="[{ required: true, message: '请输入当前密码', trigger: 'blur' }]">
                    <el-input v-model="passwordForm.currentPassword" type="password" autocomplete="off"></el-input>
                </el-form-item>
                <el-form-item label="新密码" :rules="[{ required: true, message: '请输入新密码', trigger: 'blur' }]">
                    <el-input v-model="passwordForm.newPassword" type="password" autocomplete="off"></el-input>
                </el-form-item>
                <el-form-item label="确认新密码" :rules="[{ required: true, message: '请确认新密码', trigger: 'blur' }]">
                    <el-input v-model="passwordForm.confirmNewPassword" type="password" autocomplete="off"></el-input>
                </el-form-item>
            </el-form>
            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="showChangePasswordDialog = false">取消</el-button>
                    <el-button type="primary" @click="changePassword">确认</el-button>
                </div>
            </template>
        </el-dialog>
    </div>
</template>
  
<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import apiClient from '@/api/index.js';

const accountInfo = ref({
    username: '',
    expiryDate: '',
    balance: 0,
});

const showChangePasswordDialog = ref(false);
const passwordForm = ref({
    currentPassword: '',
    newPassword: '',
    confirmNewPassword: '',
});

const fetchAccountInfo = async () => {
    try {
        const response = await apiClient.get('user-info/');
        accountInfo.value = response.data;
    } catch (error) {
        ElMessage.error('获取账户信息失败');
    }
};

const changePassword = async () => {
    if (passwordForm.value.newPassword !== passwordForm.value.confirmNewPassword) {
        ElMessage.error('新密码和确认新密码不一致');
        return;
    }

    try {
        await apiClient.post('change-password/', {
            current_password: passwordForm.value.currentPassword,
            new_password: passwordForm.value.newPassword,
        });
        ElMessage.success('密码修改成功');
        showChangePasswordDialog.value = false;
        // 清空密码表单
        passwordForm.value.currentPassword = '';
        passwordForm.value.newPassword = '';
        passwordForm.value.confirmNewPassword = '';
    } catch (error) {
        ElMessage.error('密码修改失败');
    }
};

onMounted(() => {
    fetchAccountInfo();
});
</script>
  
<style scoped>
.account-info {
    max-width: 600px;
    margin: 0 auto;
}

.account-form {
    margin-top: 20px;
}

.dialog-footer {
    text-align: right;
}
</style>