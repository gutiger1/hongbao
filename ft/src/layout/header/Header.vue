<template>
    <div class="navbar">
        <el-icon class="hamburger-container" @click="toggleClick">
            <component :is="iconType" />
        </el-icon>
        <div class="navbar-right">
            <span class="expiry-date">服务到期：{{ formattedExpiryDate }}</span>
            <el-button class="renew-button" type="primary" size="small" @click="dialogFormVisibleRenew = true">
                续费
            </el-button>

            <span class="balance">账户余额: {{ balance }}</span>
            <el-button class="recharge-button" type="primary" size="small" @click="dialogFormVisibleRecharge = true">
                充值
            </el-button>
            <!-- 新增一行 -->
            <span class="contact-customer-service">微信客服</span>
            <span class="help-tutorial" @click="openHelpPage">帮助教程</span>
            <div class="user-info">
                <Avatar />
                <span class="username">{{ username }}</span>
            </div>
        </div>

        <!-- 续费弹窗 -->
        <el-dialog v-model="dialogFormVisibleRenew" title="续费" width="500px">
            <el-form :model="activationFormRenew" label-width="100px">
                <el-form-item label="激活码">
                    <el-input v-model="activationFormRenew.code" placeholder="请输入续费激活码" />
                </el-form-item>
            </el-form>
            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="dialogFormVisibleRenew = false">取消</el-button>
                    <el-button type="primary" @click="submitActivationCodeRenew">提交</el-button>
                </div>
            </template>
        </el-dialog>

        <!-- 充值弹窗 -->
        <el-dialog v-model="dialogFormVisibleRecharge" title="充值" width="500px">
            <el-form :model="activationFormRecharge" label-width="100px">
                <el-form-item label="激活码">
                    <el-input v-model="activationFormRecharge.code" placeholder="请输入充值激活码" />
                </el-form-item>
            </el-form>
            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="dialogFormVisibleRecharge = false">取消</el-button>
                    <el-button type="primary" @click="submitActivationCodeRecharge">提交</el-button>
                </div>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { Fold, Expand } from '@element-plus/icons-vue';
import { useSidebarStore } from '@/stores/sidebar';
import { useUserStore } from '@/stores/user';
import Avatar from './components/avatar.vue'; // 引入头像组件
import apiClient from '@/api';
import { ElMessage } from 'element-plus';

const sidebarStore = useSidebarStore();
const userStore = useUserStore();

const dialogFormVisibleRenew = ref(false); // 续费弹窗
const dialogFormVisibleRecharge = ref(false); // 充值弹窗

const activationFormRenew = ref({ code: '' }); // 续费激活码表单
const activationFormRecharge = ref({ code: '' }); // 充值激活码表单

const openHelpPage = () => {
    window.open('https://docs.qq.com/doc/DVXlIRGxkZE9jSkpp', '_blank');
};

// 续费激活码提交
const submitActivationCodeRenew = async () => {
    try {
        const response = await apiClient.post('/use-activation-code/', {
            code: activationFormRenew.value.code,
            action_type: 'renew', // 续费操作
        });

        ElMessage({
            message: response.data.success || '续费成功！',
            type: 'success',
            duration: 3000,
            showClose: true,
        });

        dialogFormVisibleRenew.value = false;
        activationFormRenew.value.code = '';
        await userStore.fetchUserInfo();
    } catch (error) {
        ElMessage.error(error.response?.data?.error || '续费激活码使用失败');
    }
};

// 充值激活码提交
const submitActivationCodeRecharge = async () => {
    try {
        const response = await apiClient.post('/use-activation-code/', {
            code: activationFormRecharge.value.code,
            action_type: 'recharge', // 充值操作
        });

        ElMessage({
            message: response.data.success || '充值成功！',
            type: 'success',
            duration: 3000,
            showClose: true,
        });

        dialogFormVisibleRecharge.value = false;
        activationFormRecharge.value.code = '';
        await userStore.fetchUserInfo();
    } catch (error) {
        ElMessage.error(error.response?.data?.error || '充值激活码使用失败');
    }
};

// 切换菜单
const toggleClick = () => {
    sidebarStore.toggleCollapse();
};

// 根据菜单状态选择图标
const iconType = computed(() => {
    return sidebarStore.isFold ? Fold : Expand;
});

// 格式化到期日期
const formattedExpiryDate = computed(() => {
    const expiryDate = userStore.getExpiryDate;
    if (!expiryDate) return '';
    const date = new Date(expiryDate);
    return date.toLocaleDateString();
});

// 获取用户余额
const balance = computed(() => userStore.getBalance);

// 获取用户名
const username = computed(() => userStore.getUsername);

// 组件挂载时获取用户信息
onMounted(() => {
    userStore.fetchUserInfo();
});
</script>

<style lang="scss" scoped>
.hamburger-container {
    margin-right: 16px;
    box-sizing: border-box;
    cursor: pointer;
    font-size: 28px;
}

.navbar {
    width: 100%;
    height: 60px;
    overflow: visible;
    background-color: #fff;
    box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
    padding: 0 16px;
    display: flex;
    align-items: center;
    box-sizing: border-box;
    position: relative;
    margin: 0;
    z-index: 1000;

    .navbar-right {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: flex-end;

        .expiry-date {
            margin-right: 20px;
        }

        .balance {
            margin-left: 20px;
            margin-right: 20px;
            font-size: 14px;
            color: #333;
        }

        .renew-button {
            height: 25px;
            line-height: 25px;
        }

        .recharge-button {
            height: 25px;
            margin-right: 20px;
            line-height: 25px;
        }

        .user-info {
            display: flex;
            align-items: center;

            .username {
                margin-left: 10px;
                font-size: 14px;
                color: #333;
            }
        }
    }
}

.dialog-footer {
    display: flex;
    justify-content: flex-end;
    padding: 10px 0;

    .el-button {
        margin-left: 10px;
    }
}


// 下面是新增的
.contact-customer-service {
    position: relative;
    margin-right: 20px;
    cursor: pointer;
    color: #409EFF;
    z-index: 1001;
}

/* 悬浮图片样式 */
.contact-customer-service::after {
    content: "";
    position: absolute;
    top: 120%;
    /* 位于文字下方 */
    left: 50%;
    /* 水平居中 */
    transform: translateX(-50%);
    width: 150px;
    height: 150px;
    background-image: url('https://dingdanbaob.top/static/erweima.png');
    /* 替换为实际图片路径 */
    background-size: cover;
    display: none;
    z-index: 1002;
    /* 确保悬浮图片在所有内容上方 */
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
}

/* 悬停时显示图片 */
.contact-customer-service:hover::after {
    display: block;
}

.help-tutorial {
    margin-right: 20px;
    cursor: pointer;
    color: #409EFF;
}
</style>
