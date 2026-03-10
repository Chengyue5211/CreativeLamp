# 《儿童原创视觉表达训练平台》
## API LIST
### ——核心接口清单

---

## 0. 文件说明

### 0.1 文件名称
`API_LIST.md`

### 0.2 文件用途
定义平台主要业务接口，包括：
- 用户与权限
- 训练与任务
- 上传与作品
- 展示与成长档案
- 家长中心
- 分享推广中心
- 后台管理
- 未来扩展接口预留

### 0.3 设计原则
- 先满足 SMVP 闭环
- 命名稳定
- 按业务域拆分
- 后续扩展不推翻现有接口

---

# 1. API 域划分总览

建议按业务域划分接口：

1. 认证与用户 `auth / users`
2. 用户关系 `relations`
3. 训练模块 `modules`
4. 任务与模板 `tasks / templates`
5. 打印模板 `printables`
6. 上传与作品 `works / uploads`
7. 展示与成长档案 `gallery / archives`
8. 家长中心 `parent`
9. 分享推广中心 `referrals / rewards`
10. 后台管理 `admin`
11. 未来扩展 `merch / evidence / rights`

---

# 2. 认证与用户接口

---

## 2.1 登录

### `POST /auth/login`
用于账号登录。

### 请求体
```json
{
  "mobile": "13800000000",
  "password": "******"
}