# 《儿童原创视觉表达训练平台》
## DOCUMENT MAP

---

## 1. 文档地图的目的

本项目当前已经形成多层文档体系。  
如果没有一份“文档地图”，后续很容易出现以下问题：

- 白皮书和 PRD 内容混写
- PRD 和开发包职责不清
- SMVP 文件与普通需求文档重复
- 规则文件散落，技术和运营口径不一致
- 新协作者进入后不知道先看什么

因此，需要一份统一的文档地图来明确：

**每一类文档负责什么，不负责什么。**

---

## 2. 项目文档的五层结构

当前项目文档建议分为五层：

### 第一层：价值层
回答“为什么做”。

### 第二层：产品层
回答“产品是什么”。

### 第三层：首发战略层
回答“第一版做到什么程度才算对”。

### 第四层：开发落地层
回答“技术怎么做”。

### 第五层：运营规则层
回答“规则怎么跑”。

---

## 3. 五层文档结构说明

---

### 3.1 第一层：价值层（Whitepaper）

#### 代表文档
- `WHITEPAPER_FULL.md`
- `WHITEPAPER_EXEC_SUMMARY.md`
- `WHITEPAPER_CHAPTER_OUTLINE.md`
- `WHITEPAPER_PITCH_VERSION.md`

#### 负责什么
这一层负责讲清楚：

- 为什么创造力重要
- 为什么儿童原创作品不能只停留在练习本逻辑
- 为什么数字经济时代需要数字保存、存证与可选确权
- 为什么未来个性专属文创重要
- 为什么这个项目不是普通绘画软件，而是新的创作基础设施

#### 不负责什么
这一层**不负责**：

- 页面设计
- API 设计
- 数据对象设计
- 后台功能细节
- 开发排期

#### 一句话理解
**白皮书讲“意义”。**

---

### 3.2 第二层：产品层（PRD）

#### 代表文档
- `PRD_MASTER.md`
- `PRD_DIRECTORY_VERSION.md`
- `PRD_CH1_TO_CH5_EXPANDED.md`
- `PAGE_STRUCTURE_AND_FUNCTION_LIST.md`
- `SHARE_REFERRAL_CENTER_SPEC.md`
- `FUTURE_MODULE_INTERFACES.md`

#### 负责什么
这一层负责讲清楚：

- 平台定位
- 用户角色
- 双训练模块逻辑
- 页面结构
- 用户流程
- 家长系统
- 展示系统
- 分享推广中心
- 未来模块接口预留

#### 不负责什么
这一层**不负责**：

- 为什么创造力重要（这是白皮书）
- 数据字段表（这是开发包）
- 结算公式细节（这是规则文档）
- 开发排期（这是 SMVP 和 Roadmap）

#### 一句话理解
**PRD 讲“产品长什么样”。**

---

### 3.3 第三层：首发战略层（SMVP）

#### 代表文档
- `SMVP_SCOPE.md`
- `SMVP_ROADMAP.md`
- `STRATEGIC_V1_DEV_PACKAGE_INDEX.md`
- `STRATEGIC_V1_ACCEPTANCE.md`

#### 负责什么
这一层负责讲清楚：

- 为什么本项目不按普通 MVP 做
- 什么必须第一版就立住
- 什么可以先做结构占位
- 第一版按什么阶段推进
- 第一版的战略验收标准是什么

#### 不负责什么
这一层**不负责**：

- 详细页面字段
- 详细接口定义
- 详细后台表单
- 白皮书式论述

#### 一句话理解
**SMVP 文档讲“第一版做到什么程度才算像这个产品”。**

---

### 3.4 第四层：开发落地层（Dev Package）

#### 代表文档
- `DATA_OBJECTS.md`
- `API_LIST.md`
- `ADMIN_REQUIREMENTS.md`
- `TESTING_CHECKLIST.md`
- `DEPLOYMENT_NOTES.md`

#### 负责什么
这一层负责讲清楚：

- 数据对象是什么
- 接口有哪些
- 后台要支持什么
- 测试要测什么
- 部署需要注意什么

#### 不负责什么
这一层**不负责**：

- 白皮书价值表达
- 产品愿景论述
- 为什么是双训练平台
- 长篇规则解释（只对接规则）

#### 一句话理解
**开发包讲“怎么把它做出来”。**

---

### 3.5 第五层：运营规则层（Rules）

#### 代表文档
- `REFERRAL_RULES.md`
- `REWARD_SETTLEMENT_RULES.md`
- `CONTENT_OPS.md`
- `FEATURED_WORKS_RULES.md`
- `SHOWCASE_RULES.md`
- `RISK_AND_MODERATION.md`

#### 负责什么
这一层负责讲清楚：

- 邀请规则
- 奖励规则
- 净收益分配规则
- 精选规则
- 展示规则
- 风险与审核规则

#### 不负责什么
这一层**不负责**：

- 解释产品是什么
- 解释为什么创造力重要
- 具体技术字段结构（但可引用）
- 页面交互逻辑细节

#### 一句话理解
**规则文档讲“平台怎么运行才不乱”。**

---

## 4. 文档之间的关系图（文字版）

下面这张“文字图”很重要，能帮助协作者快速理解全局。

### 第一步：白皮书定方向
白皮书回答：
**这个项目为什么值得做。**

↓

### 第二步：PRD 定产品
PRD 回答：
**这个产品长什么样。**

↓

### 第三步：SMVP 定第一版边界
SMVP 回答：
**第一版必须做到什么程度。**

↓

### 第四步：开发包定实现方式
开发包回答：
**技术如何实现第一版。**

↓

### 第五步：规则文档定平台运转方式
规则文档回答：
**上线后平台如何按规则运行。**

---

## 5. 当前最重要的主文档关系

如果只看最核心的 7 份文件，它们关系如下：

### 1. `WHITEPAPER_FULL.md`
负责讲：  
为什么做这个项目。

### 2. `PRD_MASTER.md`
负责讲：  
这个产品是什么。

### 3. `SMVP_SCOPE.md`
负责讲：  
第一版必须做到哪些核心表达。

### 4. `SMVP_ROADMAP.md`
负责讲：  
第一版按什么阶段推进。

### 5. `DATA_OBJECTS.md`
负责讲：  
核心数据对象和字段结构。

### 6. `API_LIST.md`
负责讲：  
前后端主要接口清单。

### 7. `REFERRAL_RULES.md` + `REWARD_SETTLEMENT_RULES.md`
负责讲：  
邀请奖励与净收益分配怎么跑。

---

## 6. 新协作者推荐阅读顺序

为了让不同角色快速进入项目，我建议按角色给出阅读顺序。

---

### 6.1 创始人 / 负责人阅读顺序
1. `PROJECT_MASTER_README.md`
2. `SMVP_MASTER_INDEX.md`
3. `WHITEPAPER_FULL.md`
4. `PRD_MASTER.md`
5. `SMVP_SCOPE.md`
6. `SMVP_ROADMAP.md`

### 6.2 产品经理阅读顺序
1. `PROJECT_MASTER_README.md`
2. `PRD_MASTER.md`
3. `PRD_CH1_TO_CH5_EXPANDED.md`
4. `PAGE_STRUCTURE_AND_FUNCTION_LIST.md`
5. `SMVP_SCOPE.md`
6. `SMVP_ROADMAP.md`

### 6.3 技术负责人阅读顺序
1. `PROJECT_MASTER_README.md`
2. `SMVP_SCOPE.md`
3. `SMVP_ROADMAP.md`
4. `DATA_OBJECTS.md`
5. `API_LIST.md`
6. `ADMIN_REQUIREMENTS.md`

### 6.4 运营负责人阅读顺序
1. `PROJECT_MASTER_README.md`
2. `WHITEPAPER_FULL.md`
3. `PRD_MASTER.md`
4. `REFERRAL_RULES.md`
5. `REWARD_SETTLEMENT_RULES.md`
6. `FEATURED_WORKS_RULES.md`（后续）

### 6.5 设计师阅读顺序
1. `PROJECT_MASTER_README.md`
2. `PRD_MASTER.md`
3. `PAGE_STRUCTURE_AND_FUNCTION_LIST.md`
4. `SMVP_SCOPE.md`
5. `SMVP_ROADMAP.md`

---

## 7. 当前文档中必须统一的交叉引用关系

为了防止后面越写越乱，建议统一下面这些“引用方向”。

---

### 7.1 PRD 应引用白皮书，但不重复白皮书
PRD 中出现价值表述时，应简写并指向白皮书。  
不要在 PRD 里重写长篇时代论述。

### 7.2 SMVP 应引用 PRD，但不重写全部产品说明
SMVP 关注“第一版边界”，而不是再写一遍产品全貌。

### 7.3 开发包应引用 PRD 与 SMVP，但不重写理念
开发包只需要对齐：
- 产品结构
- 页面需求
- 第一版边界

### 7.4 规则文档应引用开发包字段，不再自己发明数据口径
例如：
- 奖励状态
- reward_amount
- gross_amount
- cost_amount
- net_amount

都应与 `DATA_OBJECTS.md` 保持一致。

---

## 8. 当前最需要补齐的“文档连接位”

虽然主文档已经很多，但为了真正形成一棵完整的树，还缺几个关键连接件。

### 8.1 `VERSION_HISTORY.md`
负责把版本演进记录下来。

### 8.2 `COLLABORATION_RULES.md`
负责规定：
- 文件命名
- 版本命名
- 修改方式
- 协作注意事项

### 8.3 `STRATEGIC_V1_ACCEPTANCE.md`
负责把“首发版验收标准”独立拉出来。

### 8.4 `STRATEGIC_V1_DEV_PACKAGE_INDEX.md`
负责给技术团队一个更聚焦的首发开发入口。

---

## 9. 当前阶段的文档策略判断

本项目现在的文档体系，已经具备一个很好的特点：

### 不是只停留在“概念层”
而是已经有：
- 白皮书
- 产品
- SMVP
- 开发
- 规则

### 不是只停留在“功能层”
而是已经把：
- 创造力
- 作品系统
- 家长系统
- 文创
- 存证/确权
- 分享推广

这几条逻辑打通了。

这说明项目现在最需要做的，不是再继续无限增加新的抽象内容，  
而是：

**把现有内容更稳地收束成正式交接体系。**

---

## 10. 一句话总图

如果要用一句话概括整套文档关系，可以这样说：

**白皮书定义价值，PRD定义产品，SMVP定义首发边界，开发包定义实现方式，规则文档定义平台运行秩序。**

---

## 11. 建议你下一步最先补的文件

我建议文档地图之后，优先补下面两个：

### 第一
`VERSION_HISTORY.md`  
因为现在文件越来越多，版本追踪会很重要。

### 第二
`COLLABORATION_RULES.md`  
因为你以后不管自己继续写，还是交给别人，都需要统一规则。