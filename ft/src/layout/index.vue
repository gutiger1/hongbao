<template>
  <el-container>
    <el-aside :class="['sidebar-container', { collapsed: sidebarStore.isCollapsed }]">
      <AsideMenu />
    </el-aside>
    <el-container :class="['container', { expanded: sidebarStore.isCollapsed }]">
      <el-header>
        <Headers />
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import AsideMenu from '@/layout/sidebar/AsideMenu.vue'
import Headers from '@/layout/header/Header.vue'
import { useSidebarStore } from '@/stores/sidebar'

const sidebarStore = useSidebarStore()
</script>

<style scoped lang="scss">
.sidebar-container {
  height: 100%;
  width: $sideBarWidth;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 1001;
  overflow: hidden;
  background-color: $menuBg;
  transition: width 0.3s ease;

  &.collapsed {
    width: $hideSideBarWidth; // 折叠时的宽度
  }
}

.container {
  width: calc(100% - $sideBarWidth);
  height: 100%;
  position: fixed;
  top: 0;
  right: 0;
  z-index: 9;
  transition: width 0.3s ease;

  &.expanded {
    width: calc(100% - $hideSideBarWidth); // 侧边栏折叠时的宽度调整
  }
}

.el-header,
.el-main {
  transition: width 0.3s ease;
  background-color: #f5f5f5; // 确保背景颜色一致
}
</style>
