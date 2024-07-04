import { defineStore } from "pinia";

export const useSidebarStore = defineStore("sidebar", {
  state: () => ({
    isCollapsed: false,
    isFold: true, // 新增状态管理图标变化
  }),
  actions: {
    toggleCollapse() {
      this.isCollapsed = !this.isCollapsed;
      this.isFold = !this.isFold; // 切换图标状态
    },
  },
});
