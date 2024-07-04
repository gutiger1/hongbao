<template>
    <el-menu :default-active="activeMenu" class="el-menu-vertical-demo" background-color="$menuBg" text-color="#fff"
        active-text-color="#ffd04b" unique-opened router :collapse="sidebarStore.isCollapsed" collapse-transition>
        <el-menu-item index="/home">
            <el-icon>
                <HomeFilled />
            </el-icon>
            <transition name="fade">
                <span v-if="!sidebarStore.isCollapsed">首页</span>
            </transition>
        </el-menu-item>

        <el-sub-menu index="2">
            <template #title>
                <el-icon>
                    <User />
                </el-icon>
                <transition name="fade">
                    <span v-if="!sidebarStore.isCollapsed">我的账户</span>
                </transition>
            </template>
            <el-menu-item index="/accountinfo">账户信息</el-menu-item>
            <el-menu-item index="/financialrecords">资金记录</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="3">
            <template #title>
                <el-icon>
                    <Menu />
                </el-icon>
                <transition name="fade">
                    <span v-if="!sidebarStore.isCollapsed">订单管理</span>
                </transition>
            </template>
            <el-menu-item index="/pendingorders">待审核订单</el-menu-item>
            <el-menu-item index="/approvedorders">已通过订单</el-menu-item>
            <el-menu-item index="/unappliedorders">未申请订单</el-menu-item>
            <el-menu-item index="/uploadorder">上传订单</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="4">
            <template #title>
                <el-icon>
                    <UserFilled />
                </el-icon>
                <transition name="fade">
                    <span v-if="!sidebarStore.isCollapsed">用户管理</span>
                </transition>
            </template>
            <el-menu-item index="/usermanagement">用户管理</el-menu-item>
        </el-sub-menu>
    </el-menu>
</template>
  
<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { HomeFilled, User, Menu, UserFilled } from '@element-plus/icons-vue'
import { useSidebarStore } from '@/stores/sidebar'

const route = useRoute()
const activeMenu = ref(route.path)
const sidebarStore = useSidebarStore()

watch(() => route.path, (newPath) => {
    activeMenu.value = newPath
})
</script>
  
<style scoped lang="scss">
.el-menu-vertical-demo {
    background-color: #2b2f3a;
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s;
}

.fade-enter,
.fade-leave-to

/* .fade-leave-active in <2.1.8 */
    {
    opacity: 0;
}
</style>
  