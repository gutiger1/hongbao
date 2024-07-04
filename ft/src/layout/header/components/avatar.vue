<template>
    <div> </div>
    <el-dropdown>
        <span class="el-dropdown-link">
            <el-avatar shape="square" :size="50" :src="squareUrl" />
        </span>
        <template #dropdown>
            <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出</el-dropdown-item>
            </el-dropdown-menu>
        </template>
    </el-dropdown>
</template>
  
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';

const squareUrl = ref('https://img0.baidu.com/it/u=1009785316,3242535060&fm=253&fmt=auto&app=138&f=JPEG?w=200&h=200');
const userStore = useUserStore();
const router = useRouter();

const handleLogout = () => {
    userStore.logout();
    router.push('/login'); // 确保这里没有报错
};
</script>
  
<style scoped>
:v-deep .el-dropdown-item {
    white-space: nowrap;
}
</style>
  