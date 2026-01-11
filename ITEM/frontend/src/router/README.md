# Router 说明（frontend/src/router/index.js）

目的
- 描述项目路由表、路由守卫行为、关键实现细节与常见故障排查步骤，便于前端与运维协作调试。

主要要点
- 路由使用 `vue-router` 的 `createRouter` + `createWebHistory`。
- `Auth`（登录/鉴权相关）组件使用**静态导入**以避免首次加载出现 500/白屏。
- 其余页面组件采用动态导入并配合 `.catch()` 返回兜底组件，防止异步加载失败导致全局白屏。
- 路由表在初始化时完整声明（不在运行时动态新增），便于一致性与 SSR/预渲染场景。

路由表（概述）
- `/` (`Home`)：首页，`requiresAuth: false`（示例项目中可能改为 true，根据业务调整）。
- `/auth` (`Auth`)：鉴权入口页（静态导入）。
- `/login` (`Login`)：登录表单页。
- `/register` (`Register`)：注册页。
- `/spider` (`Spider`)：爬虫管理页，`requiresAuth: true`。
- `/analysis` (`Analysis`)：综合分析页，`requiresAuth: true`，有 `title` 元数据用于动态设置页面标题。
- `/:pathMatch(.*)*`：兜底，重定向到登录页，避免未知路径导致 404 空白。

路由守卫行为
- 在 `beforeEach` 中：
  - 优先设置 `document.title`（使用 `to.meta.title` 或默认标题）。
  - 若 `to.meta.requiresAuth` 为真，则从 `getToken()` 检查 token：
    - 无 token → 跳转到 `/login` 并保留 `redirect` 查询参数（便于登录后回跳）。
    - 有 token → 允许通行。
  - 否则直接放行。

关键建议与注意事项
- 确保 `Auth` 组件静态导入（避免首次路由到登录页时的异步模块错误）。
- 动态导入时使用 `.catch()` 并返回简单的错误组件，可以防止因打包或网络问题导致的白屏。
- 推荐在 `Auth` 或全局 store 中提供 `bootstrap` 初始化方法并带 `bootstrapped` 标识，避免每次路由守卫重复初始化（提升性能并减少 race 条件）。
- 路由 `name` 建议使用短小稳定的英文标识，便于程序内跳转与测试。

常见问题与排查步骤
1. 白屏/500 错误在访问某页时：
   - 检查浏览器控制台与网络请求，看是否为动态导入的 `.js` 404/500。
   - 若为模块加载失败，暂时把该页面改为静态导入确认是否与打包配置有关。
2. 无法跳转到受保护页面：
   - 检查 `getToken()` 的实现与 token 存储位置（localStorage/cookie）。
   - 使用浏览器 DevTools 手动查看存储的 token，并用 curl/postman 测试后端鉴权接口。
3. 登录后无法回跳原目标页：
   - 检查登录成功后的跳转逻辑是否使用 `route.query.redirect`，并在跳转前对其进行合法性校验。

本地验证命令（开发）
```bash
# 前端（在项目根或 frontend 目录）
cd frontend
npm install
npm run dev
```

快速代码检查点
- 文件：frontend/src/router/index.js
- 核心：确认 `Auth` 静态导入、动态导入带 `.catch()`，路由表完整且 `beforeEach` 守卫健壮。

如需我：
- 我可直接把 README 的核心注释合并到 `index.js` 文件顶部，或把示例错误兜底组件改得更健壮。
- 如需我同步生成运维/QA 的简短验证脚本也可一并添加。