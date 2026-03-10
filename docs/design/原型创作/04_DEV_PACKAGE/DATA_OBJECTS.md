# 《儿童原创视觉表达训练平台》
## DATA OBJECTS
### ——核心数据对象定义

---

## 0. 文件说明

### 0.1 文件名称
`DATA_OBJECTS.md`

### 0.2 文件用途
定义平台 SMVP 及后续扩展阶段需要的核心数据对象、字段结构、字段含义与对象关系。

### 0.3 当前原则
本版以 **SMVP 可落地** 为优先，字段设计遵循：

- 先满足当前闭环
- 预留未来扩展
- 训练模块可扩展
- 作品系统统一
- 推广与收益逻辑可接入
- 存证 / 确权与文创先留状态位

---

# 1. 数据对象总览

平台核心对象建议分成 14 组：

1. 用户对象 `users`
2. 用户关系对象 `user_relations`
3. 训练模块对象 `training_modules`
4. 任务模板对象 `task_templates`
5. 任务实例对象 `tasks`
6. 打印模板对象 `printable_templates`
7. 作品对象 `works`
8. 作品元数据对象 `work_metadata`
9. 成长档案对象 `archives`
10. 展示对象 `showcases`
11. 邀请关系对象 `referrals`
12. 奖励记录对象 `referral_rewards`
13. 文创候选对象 `merch_candidates`
14. 存证 / 确权状态对象 `evidence_rights_status`

其中 SMVP 必须先做的是：

- users
- user_relations
- training_modules
- task_templates
- tasks
- printable_templates
- works
- work_metadata
- archives
- referrals
- referral_rewards

---

# 2. 用户对象 `users`

## 2.1 作用
统一管理所有角色账户：

- 孩子
- 家长
- 老师
- 管理员

## 2.2 字段定义

| 字段名 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| id | bigint / uuid | 是 | 用户唯一ID |
| role | varchar | 是 | 用户角色：child / parent / teacher / admin |
| nickname | varchar | 是 | 昵称 |
| avatar_url | varchar | 否 | 头像 |
| mobile | varchar | 否 | 手机号 |
| email | varchar | 否 | 邮箱 |
| password_hash | varchar | 否 | 登录密码哈希 |
| status | varchar | 是 | 状态：active / disabled / pending |
| invite_code | varchar | 否 | 用户自己的邀请码 |
| created_at | datetime | 是 | 创建时间 |
| updated_at | datetime | 是 | 更新时间 |

## 2.3 说明
- `role` 决定前端看到的页面和权限
- `invite_code` 用于分享推广中心
- SMVP 可先只支持手机号登录

---

# 3. 用户关系对象 `user_relations`

## 3.1 作用
建立孩子与家长、老师等关系。

## 3.2 字段定义

| 字段名 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| id | bigint / uuid | 是 | 关系ID |
| user_id | bigint / uuid | 是 | 主体用户ID |
| related_user_id | bigint / uuid | 是 | 关联用户ID |
| relation_type | varchar | 是 | parent_child / teacher_child / guardian_child |
| status | varchar | 是 | active / inactive |
| created_at | datetime | 是 | 创建时间 |

## 3.3 示例
- 家长A 绑定孩子B
- 老师C 绑定孩子B

---

# 4. 训练模块对象 `training_modules`

## 4.1 作用
注册平台中所有训练模块。

## 4.2 字段定义

| 字段名 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| id | bigint / uuid | 是 | 模块ID |
| code | varchar | 是 | 唯一编码，如 module_a / module_b |
| name | varchar | 是 | 模块名称 |
| description | text | 否 | 模块说明 |
| status | varchar | 是 | active / inactive |
| sort_order | int | 否 | 排序 |
| created_at | datetime | 是 | 创建时间 |

## 4.3 当前模块
- `module_a`：原型组合创意绘画
- `module_b`：图形变形与结构生成

---

# 5. 任务模板对象 `task_templates`

## 5.1 作用
保存后台配置好的任务模板，供任务引擎生成具体任务。

## 5.2 字段定义

| 字段名 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| id | bigint / uuid | 是 | 模板ID |
| module_code | varchar | 是 | 所属模块 |
| level_code | varchar | 是 | 难度层级编码 |
| task_type | varchar | 是 | 任务类型 |
| title | varchar | 是 | 模板标题 |
| prompt_text | text | 是 | 给前端展示的任务说明 |
| requirement_json | json | 是 | 任务规则JSON |
| printable_template_id | bigint / uuid | 否 | 关联打印模板 |
| demo_asset_url | varchar | 否 | 示范图 / 示范资源 |
| status | varchar | 是 | active / inactive |
| created_at | datetime | 是 | 创建时间 |
| updated_at | datetime | 是 | 更新时间 |

## 5.3 `requirement_json` 设计建议

### 模块A 示例
```json
{
  "prototype_count": 3,
  "prototype_pool": ["arc", "dot", "wave"],
  "contour_type": "leaf",
  "constraints": ["at_least_3_zones", "must_have_density_change"]
}