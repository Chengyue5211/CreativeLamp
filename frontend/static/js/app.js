/**
 * 绘创前程 — 前端核心
 * 单页应用路由 + API封装 + 状态管理
 */

const APP = {
    token: null,
    user: null,
    childToken: null,
    currentChild: null,
    currentPage: "login",
};

// ============================================================
// API 封装
// ============================================================
const API = {
    base: "/api",

    async request(method, path, data = null, useChildToken = false) {
        const headers = { "Content-Type": "application/json" };
        const token = useChildToken ? APP.childToken : APP.token;
        if (token) headers["Authorization"] = `Bearer ${token}`;

        const opts = { method, headers };
        if (data && method !== "GET") opts.body = JSON.stringify(data);

        const resp = await fetch(this.base + path, opts);
        const json = await resp.json();

        if (!resp.ok) {
            throw new Error(json.detail || "请求失败");
        }
        return json;
    },

    // 认证
    register: (data) => API.request("POST", "/auth/register", data),
    login: (data) => API.request("POST", "/auth/login", data),
    getMe: () => API.request("GET", "/auth/me"),
    getChildren: () => API.request("GET", "/auth/children"),
    addChild: (data) => API.request("POST", "/auth/children", data),
    switchChild: (childId) => API.request("POST", `/auth/switch-child/${childId}`),

    // 训练（用孩子token）
    getPrototypes: (params = "") => API.request("GET", `/training/prototypes${params}`, null, true),
    getTransforms: (params = "") => API.request("GET", `/training/transforms${params}`, null, true),
    getLevels: () => API.request("GET", "/training/levels", null, true),
    generateDailyTask: () => API.request("POST", "/training/daily-task", null, true),
    getTodayTasks: () => API.request("GET", "/training/today", null, true),
    getTaskDetail: (id) => API.request("GET", `/training/task/${id}`, null, true),
    updateTaskStatus: (id, status) => API.request("POST", `/training/task/${id}/status?status=${status}`, null, true),
};

// ============================================================
// 路由
// ============================================================
function navigate(page, params = {}) {
    APP.currentPage = page;
    const container = document.getElementById("app-content");
    container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

    switch (page) {
        case "login": renderLogin(container); break;
        case "register": renderRegister(container); break;
        case "parent-home": renderParentHome(container); break;
        case "add-child": renderAddChild(container); break;
        case "child-home": renderChildHome(container, params); break;
        case "training": renderTraining(container, params); break;
        case "task-detail": renderTaskDetail(container, params); break;
        case "prototypes": renderPrototypeLibrary(container, params); break;
        case "transforms": renderTransformLibrary(container, params); break;
        default: renderLogin(container);
    }
}

// ============================================================
// 页面渲染
// ============================================================

function renderLogin(container) {
    container.innerHTML = `
        <div class="page">
            <div style="text-align:center; padding:40px 0 30px;">
                <div style="font-size:3rem; margin-bottom:12px;">🎨</div>
                <h1 style="font-size:1.5rem; color:var(--primary-700);">绘创前程</h1>
                <p style="color:var(--gray-500); font-size:0.85rem; margin-top:4px;">没有原型就没有变形，没有变形就没有创造</p>
            </div>
            <div class="form-group">
                <label class="form-label">手机号</label>
                <input type="tel" id="login-phone" class="form-input" placeholder="请输入手机号" maxlength="11">
            </div>
            <div class="form-group">
                <label class="form-label">密码</label>
                <input type="password" id="login-password" class="form-input" placeholder="请输入密码">
            </div>
            <button class="btn btn-primary btn-large" onclick="doLogin()">登录</button>
            <div style="text-align:center; margin-top:16px;">
                <a href="javascript:navigate('register')" style="color:var(--primary-500); font-size:0.9rem;">还没有账号？立即注册</a>
            </div>
        </div>
    `;
}

function renderRegister(container) {
    container.innerHTML = `
        <div class="page">
            <div style="text-align:center; padding:30px 0 20px;">
                <h2 style="color:var(--primary-700);">家长注册</h2>
                <p style="color:var(--gray-500); font-size:0.85rem;">创建账号，开启孩子的创造力之旅</p>
            </div>
            <div class="form-group">
                <label class="form-label">手机号</label>
                <input type="tel" id="reg-phone" class="form-input" placeholder="请输入手机号" maxlength="11">
            </div>
            <div class="form-group">
                <label class="form-label">密码</label>
                <input type="password" id="reg-password" class="form-input" placeholder="至少6位">
            </div>
            <div class="form-group">
                <label class="form-label">昵称（选填）</label>
                <input type="text" id="reg-nickname" class="form-input" placeholder="如何称呼您">
            </div>
            <button class="btn btn-primary btn-large" onclick="doRegister()">注册</button>
            <div style="text-align:center; margin-top:16px;">
                <a href="javascript:navigate('login')" style="color:var(--primary-500); font-size:0.9rem;">已有账号？去登录</a>
            </div>
        </div>
    `;
}

async function renderParentHome(container) {
    try {
        const resp = await API.getChildren();
        const children = resp.children || [];

        container.innerHTML = `
            <div class="header">
                <h1>绘创前程</h1>
                <div class="header-subtitle">家长中心</div>
                <div class="header-actions">
                    <button onclick="doLogout()" style="background:none; border:none; color:#fff; font-size:0.85rem; cursor:pointer;">退出</button>
                </div>
            </div>
            <div class="page">
                <div class="welcome-section">
                    <div class="welcome-avatar">👨‍👩‍👧</div>
                    <div class="welcome-name">${escapeHtml(APP.user?.nickname || "家长")}</div>
                    <p style="color:var(--gray-500); font-size:0.85rem; margin-top:8px;">选择孩子，开始今天的创作之旅</p>
                </div>

                <div class="section-title">我的孩子</div>
                ${children.length > 0 ? children.map(child => `
                    <div class="card" onclick="selectChild(${child.id})" style="cursor:pointer;">
                        <div class="card-title">
                            <span style="font-size:1.5rem;">${child.gender === 'female' ? '👧' : '👦'}</span>
                            ${escapeHtml(child.nickname)}
                        </div>
                        <div class="card-subtitle">${child.age}岁 · ${levelName(child.level_grade)}</div>
                    </div>
                `).join("") : `
                    <div class="empty-state">
                        <div class="empty-state-icon">👶</div>
                        <p>还没有添加孩子</p>
                    </div>
                `}

                <button class="btn btn-outline btn-large" onclick="navigate('add-child')" style="margin-top:16px;">
                    + 添加孩子
                </button>
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
    }
}

function renderAddChild(container) {
    container.innerHTML = `
        <div class="header">
            <h1>添加孩子</h1>
            <div class="header-actions">
                <button onclick="navigate('parent-home')" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
            </div>
        </div>
        <div class="page">
            <div class="form-group">
                <label class="form-label">孩子昵称</label>
                <input type="text" id="child-name" class="form-input" placeholder="孩子的名字或昵称">
            </div>
            <div class="form-group">
                <label class="form-label">年龄</label>
                <select id="child-age" class="form-input">
                    ${[3,4,5,6,7,8,9,10,11,12].map(a => `<option value="${a}">${a}岁</option>`).join("")}
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">性别</label>
                <select id="child-gender" class="form-input">
                    <option value="male">男孩</option>
                    <option value="female">女孩</option>
                </select>
            </div>
            <button class="btn btn-primary btn-large" onclick="doAddChild()">确认添加</button>
        </div>
    `;
}

async function renderChildHome(container) {
    try {
        const todayResp = await API.getTodayTasks();
        const tasks = todayResp.tasks || [];
        const child = APP.currentChild;

        container.innerHTML = `
            <div class="header">
                <h1>${escapeHtml(child.nickname)}的创作空间</h1>
                <div class="header-subtitle">${levelName(child.level_grade)}</div>
                <div class="header-actions">
                    <button onclick="backToParent()" style="background:none; border:none; color:#fff; font-size:0.85rem; cursor:pointer;">切换</button>
                </div>
            </div>
            <div class="page">
                <div class="welcome-section" style="padding:20px 0;">
                    <div class="welcome-avatar">${child.gender === 'female' ? '👧' : '👦'}</div>
                    <div class="welcome-name">${escapeHtml(child.nickname)}</div>
                    <div class="welcome-level">${levelName(child.level_grade)} · ${child.age}岁</div>
                </div>

                <div class="section-title">今日训练</div>
                ${tasks.length > 0 ? tasks.map(t => renderTaskCard(t)).join("") : `
                    <div class="card" style="text-align:center; padding:30px;">
                        <p style="color:var(--gray-500); margin-bottom:16px;">今天还没有训练任务</p>
                        <button class="btn btn-primary" onclick="doGenerateTask()">开始今天的训练</button>
                    </div>
                `}

                <div style="margin-top:24px;">
                    <div class="section-title">探索</div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                        <div class="card" onclick="navigate('prototypes', {module:'A'})" style="text-align:center; cursor:pointer;">
                            <div style="font-size:2rem; margin-bottom:8px;">📐</div>
                            <div style="font-weight:600; font-size:0.9rem;">线条原型库</div>
                            <div style="font-size:0.75rem; color:var(--gray-500);">108种线条</div>
                        </div>
                        <div class="card" onclick="navigate('transforms')" style="text-align:center; cursor:pointer;">
                            <div style="font-size:2rem; margin-bottom:8px;">✨</div>
                            <div style="font-weight:600; font-size:0.9rem;">变形魔法库</div>
                            <div style="font-size:0.75rem; color:var(--gray-500);">30种变形</div>
                        </div>
                        <div class="card" onclick="navigate('prototypes', {module:'B'})" style="text-align:center; cursor:pointer;">
                            <div style="font-size:2rem; margin-bottom:8px;">🔷</div>
                            <div style="font-weight:600; font-size:0.9rem;">基础图形库</div>
                            <div style="font-size:0.75rem; color:var(--gray-500);">9种基础形</div>
                        </div>
                        <div class="card" style="text-align:center; opacity:0.5;">
                            <div style="font-size:2rem; margin-bottom:8px;">🖼️</div>
                            <div style="font-weight:600; font-size:0.9rem;">我的展馆</div>
                            <div style="font-size:0.75rem; color:var(--gray-500);">即将开放</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="tab-bar">
                <button class="tab-item active"><span class="tab-icon">🏠</span>首页</button>
                <button class="tab-item" onclick="doGenerateTask()"><span class="tab-icon">🎨</span>训练</button>
                <button class="tab-item"><span class="tab-icon">🖼️</span>展馆</button>
                <button class="tab-item"><span class="tab-icon">📊</span>成长</button>
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
    }
}

function renderTaskCard(task) {
    const moduleClass = task.module === "A" ? "module-a" : "module-b";
    const moduleName = task.module === "A" ? "原型组合" : "图形变形";
    const statusMap = { assigned: "待开始", in_progress: "进行中", submitted: "已提交", evaluated: "已评估" };

    return `
        <div class="card task-card ${moduleClass}" onclick="navigate('task-detail', {taskId: ${task.task_id}})">
            <span class="task-status ${task.status}">${statusMap[task.status] || task.status}</span>
            <div class="card-title">
                <span class="task-module-badge ${moduleClass}">${moduleName}</span>
                ${escapeHtml(task.task_type_name || task.title)}
            </div>
            <div class="card-subtitle">${escapeHtml(task.instruction || task.description)}</div>
            <div class="proto-tags">
                ${(task.prototypes || []).map(p => `<span class="proto-tag">${escapeHtml(p.name_zh)}</span>`).join("")}
                ${(task.transforms || []).map(t => `<span class="proto-tag">${t.icon || "✨"} ${escapeHtml(t.name_zh)}</span>`).join("")}
            </div>
            <div style="margin-top:10px; font-size:0.75rem; color:var(--gray-400);">
                预计 ${task.estimated_minutes || 15} 分钟 · ${task.icon || ""}
            </div>
        </div>
    `;
}

async function renderTaskDetail(container, params) {
    try {
        const task = await API.getTaskDetail(params.taskId);

        container.innerHTML = `
            <div class="header" style="background:${task.module === 'A' ? 'linear-gradient(135deg, var(--primary-500), var(--primary-400))' : 'linear-gradient(135deg, var(--accent-500), var(--accent-400))'};">
                <h1>${escapeHtml(task.task_type_name)}</h1>
                <div class="header-subtitle">${task.module === 'A' ? '模块A · 原型组合创意绘画' : '模块B · 图形变形与结构生成'}</div>
                <div class="header-actions">
                    <button onclick="navigate('child-home')" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                <div class="card">
                    <div class="card-title">${task.icon} ${escapeHtml(task.title)}</div>
                    <p style="color:var(--gray-600); font-size:0.9rem; line-height:1.7;">${escapeHtml(task.instruction)}</p>
                </div>

                ${task.prototypes.length > 0 ? `
                    <div class="section-title">${task.module === 'A' ? '本次使用的线条原型' : '本次使用的基础图形'}</div>
                    <div class="proto-grid">
                        ${task.prototypes.map(p => `
                            <div class="proto-cell selected">
                                <div class="proto-cell-icon">${task.module === 'A' ? '〰️' : '🔷'}</div>
                                <div class="proto-cell-name">${escapeHtml(p.name_zh)}</div>
                            </div>
                        `).join("")}
                    </div>
                ` : ""}

                ${task.transforms.length > 0 ? `
                    <div class="section-title">本次使用的变形魔法</div>
                    ${task.transforms.map(t => `
                        <div class="transform-card">
                            <div class="transform-icon" style="background:${t.color || '#f0f0f0'}22;">
                                ${t.icon || "✨"}
                            </div>
                            <div class="transform-info">
                                <div class="transform-name">${escapeHtml(t.name_zh)}</div>
                                <div class="transform-desc">${escapeHtml(t.description || "")}</div>
                            </div>
                        </div>
                    `).join("")}

                    ${task.requirement?.guiding_questions?.length ? `
                        <div class="card" style="background:var(--primary-50); border-color:var(--primary-200);">
                            <div class="card-title">💡 引导问题</div>
                            ${task.requirement.guiding_questions.map(q => `
                                <p style="font-size:0.9rem; color:var(--primary-700); margin-top:8px;">${escapeHtml(q)}</p>
                            `).join("")}
                        </div>
                    ` : ""}

                    ${task.requirement?.hints?.length ? `
                        <div class="card" style="background:var(--accent-50); border-color:var(--accent-200);">
                            <div class="card-title">🌟 小提示</div>
                            <ul style="padding-left:20px; margin-top:8px;">
                                ${task.requirement.hints.slice(0, 3).map(h => `
                                    <li style="font-size:0.85rem; color:var(--accent-700); margin-bottom:4px;">${escapeHtml(h)}</li>
                                `).join("")}
                            </ul>
                        </div>
                    ` : ""}
                ` : ""}

                <div class="demo-area">
                    <div style="font-size:3rem; margin-bottom:8px;">🖍️</div>
                    <div class="demo-instruction">
                        拿出纸和笔，开始你的创作吧！<br>
                        完成后拍照上传
                    </div>
                </div>

                ${task.status === "assigned" ? `
                    <button class="btn btn-primary btn-large" onclick="startTask(${task.task_id})">
                        开始创作
                    </button>
                ` : task.status === "in_progress" ? `
                    <button class="btn btn-accent btn-large" onclick="showToast('拍照上传功能即将开放', 'info')">
                        📷 拍照上传作品
                    </button>
                ` : `
                    <button class="btn btn-primary btn-large btn-disabled">已完成</button>
                `}
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
        navigate("child-home");
    }
}

async function renderPrototypeLibrary(container, params) {
    try {
        const module = params?.module || "A";
        const resp = await API.getPrototypes(`?module=${module}`);
        const protos = resp.prototypes || [];

        // 按类别分组
        const groups = {};
        protos.forEach(p => {
            const cat = p.category_name_zh || p.category;
            if (!groups[cat]) groups[cat] = [];
            groups[cat].push(p);
        });

        container.innerHTML = `
            <div class="header">
                <h1>${module === "A" ? "线条原型库" : "基础图形库"}</h1>
                <div class="header-subtitle">${module === "A" ? "9大类 · 108种线条" : "9种基础图形"}</div>
                <div class="header-actions">
                    <button onclick="navigate('child-home')" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                <p style="color:var(--gray-500); font-size:0.85rem; margin-bottom:16px;">
                    这些是创作的基础元素。认识它们，学会组合它们，就能创造无限可能。
                </p>
                ${Object.entries(groups).map(([cat, items]) => `
                    <div class="section-title">${escapeHtml(cat)}（${items.length}种）</div>
                    <div class="proto-grid">
                        ${items.map(p => `
                            <div class="proto-cell">
                                <div class="proto-cell-icon">${module === "A" ? "〰️" : "🔷"}</div>
                                <div class="proto-cell-name">${escapeHtml(p.name_zh)}</div>
                            </div>
                        `).join("")}
                    </div>
                `).join("")}
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
    }
}

async function renderTransformLibrary(container) {
    try {
        const resp = await API.getTransforms();
        const transforms = resp.transforms || [];

        // 按母类分组
        const groups = {};
        transforms.forEach(t => {
            if (!groups[t.category]) groups[t.category] = [];
            groups[t.category].push(t);
        });

        const catNames = {
            scale_form: "尺度与形态", structure: "结构变形", spatial: "空间变形",
            state: "状态变形", relation: "关系变形", creative: "创意变形"
        };

        container.innerHTML = `
            <div class="header" style="background:linear-gradient(135deg, var(--accent-500), var(--accent-400));">
                <h1>变形魔法库</h1>
                <div class="header-subtitle">7大母类 · 30种变形方法</div>
                <div class="header-actions">
                    <button onclick="navigate('child-home')" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                <p style="color:var(--gray-500); font-size:0.85rem; margin-bottom:16px;">
                    任意对象 x 任意变形 = 无限创造。掌握这些变形魔法，你就是小小创造家！
                </p>
                ${Object.entries(groups).map(([cat, items]) => `
                    <div class="section-title">${catNames[cat] || cat}（${items.length}种）</div>
                    ${items.map(t => `
                        <div class="transform-card">
                            <div class="transform-icon" style="background:${t.color || '#f0f0f0'}22; font-size:1.5rem;">
                                ${t.icon}
                            </div>
                            <div class="transform-info">
                                <div class="transform-name">${escapeHtml(t.name_zh)} <span style="color:var(--gray-400); font-size:0.75rem;">${escapeHtml(t.name_en)}</span></div>
                                <div class="transform-desc">${escapeHtml(t.description)}</div>
                                <div style="font-size:0.7rem; color:var(--gray-400); margin-top:4px;">${t.min_age}岁+</div>
                            </div>
                        </div>
                    `).join("")}
                `).join("")}
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
    }
}

// ============================================================
// 操作函数
// ============================================================

async function doRegister() {
    const phone = document.getElementById("reg-phone")?.value?.trim();
    const password = document.getElementById("reg-password")?.value;
    const nickname = document.getElementById("reg-nickname")?.value?.trim();

    if (!phone || !password) return showToast("请填写手机号和密码", "error");

    try {
        const resp = await API.register({ phone, password, nickname });
        APP.token = resp.token;
        APP.user = resp;
        localStorage.setItem("hc_token", resp.token);
        localStorage.setItem("hc_user", JSON.stringify(resp));
        showToast("注册成功！", "success");
        navigate("parent-home");
    } catch (e) {
        showToast(e.message, "error");
    }
}

async function doLogin() {
    const phone = document.getElementById("login-phone")?.value?.trim();
    const password = document.getElementById("login-password")?.value;

    if (!phone || !password) return showToast("请填写手机号和密码", "error");

    try {
        const resp = await API.login({ phone, password });
        APP.token = resp.token;
        APP.user = resp;
        localStorage.setItem("hc_token", resp.token);
        localStorage.setItem("hc_user", JSON.stringify(resp));
        showToast("登录成功！", "success");
        navigate("parent-home");
    } catch (e) {
        showToast(e.message, "error");
    }
}

function doLogout() {
    APP.token = null;
    APP.user = null;
    APP.childToken = null;
    APP.currentChild = null;
    localStorage.removeItem("hc_token");
    localStorage.removeItem("hc_user");
    navigate("login");
}

async function doAddChild() {
    const nickname = document.getElementById("child-name")?.value?.trim();
    const age = parseInt(document.getElementById("child-age")?.value);
    const gender = document.getElementById("child-gender")?.value;

    if (!nickname) return showToast("请输入孩子昵称", "error");

    try {
        await API.addChild({ nickname, age, gender });
        showToast("添加成功！", "success");
        navigate("parent-home");
    } catch (e) {
        showToast(e.message, "error");
    }
}

async function selectChild(childId) {
    try {
        const resp = await API.switchChild(childId);
        APP.childToken = resp.token;
        APP.currentChild = resp;
        navigate("child-home");
    } catch (e) {
        showToast(e.message, "error");
    }
}

function backToParent() {
    APP.childToken = null;
    APP.currentChild = null;
    navigate("parent-home");
}

async function doGenerateTask() {
    try {
        const resp = await API.generateDailyTask();
        showToast("训练任务已生成！", "success");
        navigate("child-home");
    } catch (e) {
        showToast(e.message, "error");
    }
}

async function startTask(taskId) {
    try {
        await API.updateTaskStatus(taskId, "in_progress");
        navigate("task-detail", { taskId });
    } catch (e) {
        showToast(e.message, "error");
    }
}

// ============================================================
// 工具函数
// ============================================================

function escapeHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function levelName(grade) {
    const map = {
        prep: "准备级", beginner_upper: "初级上", beginner_lower: "初级下",
        mid_upper: "中级上", mid_lower: "中级下", adv_upper: "高级上",
        adv_lower: "高级下", super_upper: "超级上", super_lower: "超级下",
    };
    return map[grade] || grade || "准备级";
}

function showToast(msg, type = "info") {
    let toast = document.getElementById("app-toast");
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "app-toast";
        toast.className = "toast";
        document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.className = `toast ${type} show`;
    setTimeout(() => toast.classList.remove("show"), 2500);
}

// ============================================================
// 初始化
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
    // 恢复登录状态
    const savedToken = localStorage.getItem("hc_token");
    const savedUser = localStorage.getItem("hc_user");

    if (savedToken && savedUser) {
        APP.token = savedToken;
        APP.user = JSON.parse(savedUser);
        navigate("parent-home");
    } else {
        navigate("login");
    }
});
