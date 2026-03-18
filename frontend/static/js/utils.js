/**
 * 绘创前程 — 工具函数模块
 */

function escapeHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function escapeAttr(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
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
    setTimeout(() => toast.classList.remove("show"), 4000);
}
