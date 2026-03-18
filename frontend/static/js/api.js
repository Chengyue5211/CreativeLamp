/**
 * 绘创前程 — 状态管理 + API 封装
 */

const APP = {
    token: null,
    user: null,
    childToken: null,
    currentChild: null,
    currentPage: "login",
};

const API = {
    base: "/api",

    async request(method, path, data = null, useChildToken = false) {
        const headers = { "Content-Type": "application/json" };
        const token = useChildToken ? APP.childToken : APP.token;
        if (token) headers["Authorization"] = `Bearer ${token}`;

        const opts = { method, headers };
        if (data && method !== "GET") opts.body = JSON.stringify(data);

        const resp = await fetch(this.base + path, opts);

        let json;
        try {
            json = await resp.json();
        } catch {
            throw new Error(`服务器错误 (${resp.status})，请稍后再试`);
        }

        if (!resp.ok) {
            throw new Error(json.detail || `请求失败 (${resp.status})`);
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
    getTransforms: () => API.request("GET", "/training/transforms", null, true),
    getLevels: () => API.request("GET", "/training/levels", null, true),
    generateDailyTask: () => API.request("POST", "/training/daily-task", null, true),
    getTodayTasks: () => API.request("GET", "/training/today", null, true),
    getTaskDetail: (id) => API.request("GET", `/training/task/${id}`, null, true),
    updateTaskStatus: (id, status) => API.request("POST", `/training/task/${id}/status?status=${status}`, null, true),

    // 作品
    getWorkDetail: (id) => API.request("GET", `/works/${id}`, null, true),
    evaluateWork: (id, data) => API.request("POST", `/works/${id}/evaluate`, data, true),

    // 推广
    getMyInviteCode: () => API.request("GET", "/referral/my-code"),
    validateInviteCode: (code) => API.request("POST", "/referral/validate-code", { code }),
    getReferralDashboard: () => API.request("GET", "/referral/dashboard"),
    getReferralList: (page = 1) => API.request("GET", `/referral/referrals?page=${page}`),
    getCreditBalance: () => API.request("GET", "/referral/balance"),
    getRewardHistory: (page = 1) => API.request("GET", `/referral/rewards?page=${page}`),

    // 文创
    getMerchTypes: () => API.request("GET", "/merch/types"),
    createMerchOrder: (data) => API.request("POST", "/merch/order", data),
    getMerchOrders: () => API.request("GET", "/merch/orders"),
};
