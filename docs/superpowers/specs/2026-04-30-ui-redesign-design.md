# UI  redesign 设计文档 — 克莱因蓝主题

## 设计目标

将 CaseGen 前端界面从传统的 Element Plus 后台管理风格，升级为**明亮、圆润、有设计感**的现代 SaaS 界面，以**克莱因蓝（#002FA7）**作为品牌主色，提升产品的专业度和辨识度。

## 整体风格方向

- **参考风格**：Figma / Slack 的明亮活泼感 + 克莱因蓝的艺术高级感
- **核心关键词**：明亮、圆润、简洁、有层次、艺术感
- **信息密度**：从"高密度后台"降低到"适中密度 SaaS"，增加留白和呼吸感

## 色彩系统

| 用途 | 色值 | 说明 |
|------|------|------|
| **品牌主色** | `#002FA7` | 克莱因蓝，纯粹不渐变，用于按钮、高亮、图标、链接 |
| **品牌浅蓝** | `#3B82F6` | 用于辅助图标、hover 状态 |
| **品牌淡蓝** | `#60A5FA` | 用于三级图标、装饰性元素 |
| **页面背景** | `#F8FAFC` | 中性冷灰白，衬托主色 |
| **卡片背景** | `#FFFFFF` | 纯白，大圆角 |
| **卡片边框** | `#E2E8F0` | 浅冷灰，区分卡片层级 |
| **主文字** | `#0F172A` | Slate 900，比纯黑更柔和 |
| **次要文字** | `#64748B` | Slate 500，标签、说明 |
| **辅助文字** | `#94A3B8` | Slate 400，时间、占位符 |
| **成功** | `#059669` | 保持趋势箭头等状态 |
| **警告** | `#B45309` | 解析中等进行中状态 |
| **错误** | `#B91C1C` | 失败状态 |
| **状态标签背景** | `#DBEAFE` / `#FEF3C7` / `#FEE2E2` | 对应蓝/黄/红状态底色 |

## 布局结构

### 全局框架

```
+--------------------------------------------------+
|  Sidebar (56px)  |  Header (52px, sticky)        |
|                  |  --------------------------------
|  ◆ (brand)       |  Content Area                   |
|  📁              |  - 统计卡 / 卡片网格 / 表格      |
|  ⚙               |                                 |
|  ─────────────── |                                 |
|  U (avatar)      |                                 |
+--------------------------------------------------+
```

### Sidebar（左侧边栏）

- **宽度**：56px（icon-only），hover 可展开显示文字（可选）
- **品牌区**：52px 高，纯色 `#002FA7`，白色毛玻璃 logo 圆角方块
- **菜单区**：纯白背景，icon 16px，激活态用 `#EFF6FF` 浅蓝圆底 + `#002FA7` 图标色
- **用户区**：底部 avatar，克莱因蓝底色圆角方块
- **阴影**：右侧 `2px 0 12px rgba(0,47,167,0.12)`

### Header（顶部栏）

- **高度**：52px
- **样式**：半透明毛玻璃 `rgba(248,250,252,0.85)` + `backdrop-filter: blur(12px)`
- **底部边框**：1px `#E2E8F0`
- **左侧**：页面标题 16px / font-weight:600 + 项目数 Pill 标签（`#EFF6FF` 底 + `#002FA7` 字）
- **右侧**：搜索框（圆角 8px，白底灰边框）+ 主按钮（克莱因蓝纯色，圆角 8px，带投影）
- **定位**：`position: sticky; top: 0`

### Content Area（主内容区）

- **背景**：`#F8FAFC`
- **内边距**：24px
- **内容组织**：统计卡 → 操作栏 → 卡片网格 / 表格

## 组件规范

### 统计卡片（Dashboard Stats）

- **尺寸**：flex 均分，gap 16px
- **圆角**：16px
- **背景**：纯白 `#FFFFFF`
- **边框**：1px `#E2E8F0`
- **阴影**：`0 1px 3px rgba(0,0,0,0.04)`
- **icon 区**：36px 圆角方块，背景 `#EFF6FF`，图标色 `#002FA7`
- **数字**：28px / font-weight:700 / `#0F172A`
- **趋势**：12px / `#002FA7`（上升）
- **高亮卡**：第三张卡片用纯色克莱因蓝 `#002FA7` 背景，白色文字，icon 区用 `rgba(255,255,255,0.15)` + `backdrop-filter: blur(4px)`，阴影 `0 4px 20px rgba(0,47,167,0.3)`

### 项目卡片

- **圆角**：16px
- **背景**：纯白
- **边框**：1px `#E2E8F0`
- **阴影**：`0 1px 3px rgba(0,0,0,0.04)`
- **hover**：微妙上移或阴影加深（`transform: translateY(-2px)` + 阴影加深）
- **项目 icon**：40px 圆角方块，使用同色系不同明度（`#002FA7` / `#3B82F6` / `#60A5FA`），白色 emoji
- **标题**：14px / font-weight:600 / `#0F172A`
- **描述**：12px / `#64748B`
- **数据区**：顶部 1px `#F1F5F9` 分隔线，数字 16px / font-weight:700 / `#002FA7`，标签 10px / `#94A3B8`

### 按钮

- **主按钮**：`#002FA7` 纯色背景，白色文字，圆角 8px，padding `7px 16px`，font-weight:500，阴影 `0 2px 8px rgba(0,47,167,0.25)`
- **次按钮**：白底，`#E2E8F0` 边框，`#64748B` 文字，圆角 8px
- **link 按钮**：`#002FA7` 文字，无背景

### 标签（Pill Tags）

- **已完成**：背景 `#DBEAFE`，文字 `#1E40AF`，圆角 999px，padding `3px 12px`，font-weight:500
- **解析中**：背景 `#FEF3C7`，文字 `#B45309`
- **失败**：背景 `#FEE2E2`，文字 `#B91C1C`
- **文件类型**：背景 `#EFF6FF`，文字 `#002FA7`，圆角 6px

### 表格

- **容器**：纯白卡片包裹，圆角 16px，边框 1px `#E2E8F0`
- **表头**：背景 `#F8FAFC`，文字 `#64748B`，font-weight:500，11px
- **行**：无左右边框，底部 1px `#F1F5F9` 分隔线
- **hover 行**：背景 `#F8FAFC`
- **斑马纹**：不使用，改用 hover 高亮
- **文件名**：`#0F172A` / font-weight:500
- **次要信息**：`#64748B`
- **时间**：`#94A3B8`

### 对话框 / Modal

- **圆角**：16px
- **标题**：font-weight:600
- **按钮区**：主按钮用克莱因蓝

### 输入框 / Select

- **圆角**：8px
- **边框**：`#E2E8F0`，focus 时 `#002FA7`
- **背景**：纯白

## 各页面设计要点

### 项目列表页（`/`）

1. Header：标题"项目管理" + 项目数 Pill + 搜索框 + "+ 新建项目" 主按钮
2. 统计卡：文档 / 测试点 / 用例（第三张克莱因蓝高亮）
3. 操作栏："全部项目"标题 + 右侧筛选器（白底圆角边框）
4. 项目卡片网格：3 列，gap 16px，每个卡片含项目 icon、标题、描述、三项数据
5. 空状态：使用 Element Plus Empty，但图标颜色改为 `#94A3B8`

### 项目详情页（`/projects/:id`）

1. Header：项目名称 + "返回列表"次按钮
2. Tabs：使用 Element Plus Tabs，但自定义样式——激活态下划线用 `#002FA7`，文字 font-weight:600
3. 文档标签页：上传按钮（克莱因蓝）+ AI 提取按钮（`#059669` 绿色）+ 表格
4. 测试点标签页：筛选 Select + 手动新增（克莱因蓝）+ 一键生成用例（绿色）+ 表格 + 分页
5. 知识库标签页：折叠面板（Collapse），标题区用 flex 横向排列名称 + 多个 Pill 标签
6. 测试用例标签页：类似测试点，展开行内嵌套步骤表格
7. 所有 AI 操作对话框：圆角 16px，主按钮克莱因蓝

### 系统设置页（`/settings`）

1. Header：标题"系统设置"
2. 设置卡片：纯白卡片，16px 圆角，标题用 font-weight:600
3. 保存按钮：大尺寸克莱因蓝主按钮
4. 表单 label：160px 宽，`#374151`
5. 帮助文字：`#94A3B8`，12px

## 技术实现要点

### Element Plus 主题定制

在 `main.ts` 中引入自定义 CSS 变量覆盖 Element Plus 默认主题：

```css
:root {
  --el-color-primary: #002FA7;
  --el-color-primary-light-3: #3B82F6;
  --el-color-primary-light-5: #60A5FA;
  --el-color-primary-light-7: #93C5FD;
  --el-color-primary-light-8: #BFDBFE;
  --el-color-primary-light-9: #EFF6FF;
  --el-color-primary-dark-2: #1E3A8A;
  --el-border-radius-base: 8px;
  --el-border-radius-small: 6px;
}
```

### 全局样式（`App.vue` 或独立 CSS）

```css
body {
  background: #F8FAFC;
  color: #0F172A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 卡片统一样式 */
.card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* 按钮主色 */
.btn-primary {
  background: #002FA7;
  color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,47,167,0.25);
}

/* Pill 标签 */
.pill {
  border-radius: 999px;
  padding: 3px 12px;
  font-size: 12px;
  font-weight: 500;
}
```

### 布局调整

- `AppLayout.vue`：侧边栏宽度从 220px 改为 56px，去掉菜单文字（或 hover 展开），背景改为白色 + 品牌区克莱因蓝
- 移除面包屑（breadcrumb），将页面标题直接融入内容区顶部或 Header
- `el-main` 背景从 `#f0f2f5` 改为 `#F8FAFC`，padding 保持 20px 或改为 24px

### 图标策略

项目卡片的 icon 不使用纯色 emoji 背景，改用：
- 克莱因蓝纯色方块（`#002FA7`）+ 白色 emoji
- 或浅蓝渐变（`#3B82F6` / `#60A5FA`）+ 白色 emoji
每个项目类型分配固定颜色，增加一致性。

### 注意事项

- 所有内联 `style="color: #409EFF"` 需要全局替换为 `#002FA7`
- 所有内联 `style="color: #67c23a"`（成功色）评估是否保留或调整
- 所有内联 `style="color: #f56c6c"`（危险色）调整为 `#B91C1C`
- 所有 `el-tag` 默认样式需要覆盖为 Pill 圆角风格
- 表格的 `border` 属性建议去掉，改用卡片容器 + 行底部分隔线

## 文件改动清单

| 文件 | 改动内容 |
|------|----------|
| `frontend/src/main.ts` | 引入自定义 CSS 变量覆盖 Element Plus 主题 |
| `frontend/src/App.vue` | 添加全局 body 样式 |
| `frontend/src/components/AppLayout.vue` | 重构侧边栏为 56px + 品牌区 + 新配色 |
| `frontend/src/views/ProjectList.vue` | 统计卡 redesign、项目卡片 redesign、按钮/标签配色 |
| `frontend/src/views/ProjectDetail.vue` | Tabs 样式、表格样式、按钮配色、对话框样式 |
| `frontend/src/views/Settings.vue` | 卡片样式、按钮配色、表单间距 |
| `frontend/src/components/AiProgressModal.vue` | 图标色、按钮配色 |
| 新增 `frontend/src/styles/theme.css` | 集中管理 CSS 变量和通用类（可选） |

## 验收标准

- [ ] 侧边栏为 56px 窄边栏，品牌区克莱因蓝
- [ ] 页面背景为 `#F8FAFC`，卡片纯白 + 16px 圆角
- [ ] 所有主操作按钮为克莱因蓝 `#002FA7`
- [ ] 状态标签为 Pill 胶囊形状，低饱和底色
- [ ] 表格无网格线，用行分隔线 + hover 高亮
- [ ] 统计卡片第三张为克莱因蓝高亮卡
- [ ] 整体无 Element Plus 默认蓝色（`#409EFF`）残留
- [ ] Header 为毛玻璃效果，sticky 定位
