<template>
  <div class="app-shell">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">◆</div>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item" :class="{ active: isProjectsActive }">
          <el-icon :size="18"><FolderOpened /></el-icon>
        </router-link>
        <router-link to="/settings" class="nav-item" :class="{ active: route.path === '/settings' }">
          <el-icon :size="18"><Setting /></el-icon>
        </router-link>
      </nav>
      <div class="sidebar-user">
        <div class="user-avatar">U</div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main-area">
      <header class="top-header">
        <div class="header-left">
          <slot name="header-title">
            <h1 class="page-title">{{ pageTitle }}</h1>
          </slot>
        </div>
        <div class="header-right">
          <slot name="header-actions" />
        </div>
      </header>
      <main class="main-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { FolderOpened, Setting } from '@element-plus/icons-vue'

const route = useRoute()

const isProjectsActive = computed(() =>
  route.path === '/' || route.path.startsWith('/projects')
)

const pageTitle = computed(() => {
  if (route.path === '/') return '项目管理'
  if (route.path === '/settings') return '系统设置'
  if (route.name === 'ProjectDetail') return '项目详情'
  return ''
})
</script>

<style scoped>
.app-shell {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  width: 56px;
  display: flex;
  flex-direction: column;
  background: #fff;
  box-shadow: 2px 0 12px rgba(0, 47, 167, 0.08);
  z-index: 10;
  flex-shrink: 0;
}

.sidebar-brand {
  height: 52px;
  background: var(--brand-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-icon {
  width: 28px;
  height: 28px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  font-weight: bold;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 16px;
  gap: 6px;
}

.nav-item {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  text-decoration: none;
  transition: all 0.15s ease;
}

.nav-item:hover {
  background: var(--el-color-primary-light-9);
  color: var(--brand-primary);
}

.nav-item.active {
  background: var(--el-color-primary-light-9);
  color: var(--brand-primary);
}

.sidebar-user {
  height: 52px;
  border-top: 1px solid var(--el-color-primary-light-9);
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar {
  width: 28px;
  height: 28px;
  background: var(--brand-primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
}

/* 主内容区 */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-page);
}

.top-header {
  height: 52px;
  background: rgba(248, 250, 252, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-card);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 5;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.main-content {
  flex: 1;
  overflow: auto;
  padding: 24px;
}
</style>
