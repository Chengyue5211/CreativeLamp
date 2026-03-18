/**
 * 绘创前程 — 路由 + 初始化
 *
 * 模块加载顺序: utils.js → api.js → pages.js → actions.js → app.js
 *
 * 安全说明:
 * - 所有用户可控字符串通过 data-* 属性传递，由 actions.js 事件委托处理
 * - 不再使用 escapeJsString() 拼接 onclick 内容
 * - 显示文本统一使用 escapeHtml() / escapeAttr()
 */

// ============================================================
// 路由
// ============================================================
function navigate(page, params = {}) {
    APP.currentPage = page;
    const container = document.getElementById("app-content");
    container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

    switch (page) {
        case "login": renderLogin(container); break;
        case "register": renderRegister(container, params); break;
        case "parent-home": renderParentHome(container); break;
        case "add-child": renderAddChild(container); break;
        case "child-home": renderChildHome(container, params); break;
        case "training": renderChildHome(container, params); break;
        case "task-detail": renderTaskDetail(container, params); break;
        case "prototypes": renderPrototypeLibrary(container, params); break;
        case "transforms": renderTransformLibrary(container, params); break;
        case "contours": renderContourLibrary(container, params); break;
        case "gallery": renderGallery(container, params); break;
        case "print-preview": renderPrintPreview(container, params); break;
        case "upload-work": renderUploadWork(container, params); break;
        case "growth": renderGrowth(container, params); break;
        case "work-detail": renderWorkDetail(container, params); break;
        case "task-history": renderTaskHistory(container, params); break;
        case "parent-child-works": renderParentChildWorks(container, params); break;
        case "parent-work-detail": renderParentWorkDetail(container, params); break;
        case "referral-center": renderReferralCenter(container); break;
        case "referral-list": renderReferralList(container); break;
        case "reward-history": renderRewardHistory(container); break;
        case "merch-shop": renderMerchShop(container); break;
        case "merch-detail": renderMerchDetail(container, params); break;
        case "merch-orders": renderMerchOrders(container); break;
        default: renderLogin(container);
    }
}

// ============================================================
// 初始化
// ============================================================
// Service Worker：注销旧版本并清除缓存，再注册新版本
if ("serviceWorker" in navigator) {
    navigator.serviceWorker.getRegistrations().then(regs => {
        regs.forEach(r => r.unregister());
    });
    caches.keys().then(keys => {
        keys.forEach(k => caches.delete(k));
    });
    navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch(() => {});
}

document.addEventListener("DOMContentLoaded", () => {
    const savedToken = sessionStorage.getItem("hc_token");
    const savedUser = sessionStorage.getItem("hc_user");

    // 检查 URL 中的邀请码参数
    const urlParams = new URLSearchParams(location.search);
    const inviteCode = urlParams.get("invite") || "";

    if (savedToken && savedUser) {
        try {
            APP.token = savedToken;
            APP.user = JSON.parse(savedUser);
            navigate("parent-home");
        } catch {
            navigate(inviteCode ? "register" : "login", { inviteCode });
        }
    } else {
        // 有邀请码则直接进注册页
        if (inviteCode) {
            navigate("register", { inviteCode });
        } else {
            navigate("login");
        }
    }
});
