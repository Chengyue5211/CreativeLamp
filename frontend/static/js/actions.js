/**
 * 绘创前程 — 操作函数模块
 * 所有 doX() 用户交互操作集中管理
 */

async function doRegister() {
    const phone = document.getElementById("reg-phone")?.value?.trim();
    const password = document.getElementById("reg-password")?.value;
    const nickname = document.getElementById("reg-nickname")?.value?.trim();
    const invite_code = document.getElementById("reg-invite-code")?.value?.trim() || "";

    if (!phone || !password) return showToast("请填写手机号和密码", "error");

    try {
        const resp = await API.register({ phone, password, nickname, invite_code });
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

async function doLogout() {
    try {
        if (APP.token) {
            await fetch("/api/auth/logout", {
                method: "POST",
                headers: { "Authorization": "Bearer " + APP.token },
            }).catch(() => {});
        }
    } finally {
        APP.token = null;
        APP.user = null;
        APP.childToken = null;
        APP.currentChild = null;
        localStorage.removeItem("hc_token");
        localStorage.removeItem("hc_user");
        localStorage.removeItem("hc_child_token");
        localStorage.removeItem("hc_child");
        navigate("login");
    }
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
        localStorage.setItem("hc_child_token", resp.token);
        localStorage.setItem("hc_child", JSON.stringify(resp));
        navigate("child-home");
    } catch (e) {
        showToast(e.message, "error");
    }
}

function backToParent() {
    APP.childToken = null;
    APP.currentChild = null;
    localStorage.removeItem("hc_child_token");
    localStorage.removeItem("hc_child");
    navigate("parent-home");
}

async function doGenerateTask() {
    try {
        await API.generateDailyTask();
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

// 家长提交作品评价
async function doParentEvaluateWork(workId, childId, childName) {
    const originality = parseFloat(document.getElementById("p-score-originality")?.value || 7);
    const detail = parseFloat(document.getElementById("p-score-detail")?.value || 7);
    const composition = parseFloat(document.getElementById("p-score-composition")?.value || 7);
    const expression = parseFloat(document.getElementById("p-score-expression")?.value || 7);
    const feedback = document.getElementById("p-eval-feedback")?.value?.trim() || "";

    try {
        await API.request("POST", `/works/${workId}/evaluate`, { originality, detail, composition, expression, feedback });
        showToast("评价成功！", "success");
        navigate("parent-work-detail", { workId, childId, childName });
    } catch (e) {
        showToast(e.message, "error");
    }
}

// 提交作品评价
async function doEvaluateWork(workId) {
    const originality = parseFloat(document.getElementById("score-originality")?.value || 5);
    const detail = parseFloat(document.getElementById("score-detail")?.value || 5);
    const composition = parseFloat(document.getElementById("score-composition")?.value || 5);
    const expression = parseFloat(document.getElementById("score-expression")?.value || 5);
    const feedback = document.getElementById("eval-feedback")?.value?.trim() || "";

    try {
        await API.evaluateWork(workId, { originality, detail, composition, expression, feedback });
        showToast("评价成功！", "success");
        navigate("work-detail", { workId });
    } catch (e) {
        showToast(e.message, "error");
    }
}

// 打印份数调整
let _printCount = 1;
function changePrintCount(delta) {
    _printCount = Math.max(1, Math.min(10, _printCount + delta));
    const el = document.getElementById("print-count");
    if (el) el.textContent = _printCount;
}

// 下载打印轮廓图
function doPrintContour() {
    const printArea = document.getElementById("print-area");
    if (!printArea) return;

    const count = _printCount;
    const printWin = window.open("", "_blank");
    if (!printWin) {
        showToast("请允许弹出窗口以打印", "error");
        return;
    }

    let pages = "";
    for (let i = 0; i < count; i++) {
        pages += `<div class="print-page">${printArea.innerHTML}</div>`;
        if (i < count - 1) pages += `<div style="page-break-after: always;"></div>`;
    }

    printWin.document.write(`<!DOCTYPE html><html><head><meta charset="UTF-8"><title>绘创前程 · 打印底稿</title>
        <style>
            body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; }
            .print-page { max-width: 600px; margin: 20px auto; text-align: center; }
            svg, img { max-width: 100%; }
            @media print {
                body { padding: 0; }
                .print-page { max-width: none; margin: 0; padding: 40px; }
                .no-print { display: none; }
            }
        </style>
    </head><body>
        <div class="no-print" style="text-align:center; margin-bottom:20px;">
            <button onclick="window.print()" style="padding:12px 30px; font-size:1rem; background:#4E8D7C; color:#fff; border:none; border-radius:8px; cursor:pointer;">
                点击打印 (${count}张)
            </button>
        </div>
        ${pages}
    </body></html>`);
    printWin.document.close();
    showToast(`已打开打印预览 (${count}张)`, "success");
}

// 照片预览
function previewUploadPhoto(input) {
    if (!input.files || !input.files[0]) return;
    const file = input.files[0];
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById("upload-preview");
        if (preview) {
            const img = document.createElement("img");
            img.src = e.target.result;
            img.alt = "作品预览";
            img.style.cssText = "max-width:250px; max-height:250px; border-radius:12px; border:2px solid var(--primary-300);";

            const reselect = document.createElement("button");
            reselect.textContent = "重新选择";
            reselect.style.cssText = "background:none; border:none; color:var(--primary-500); font-size:0.85rem; cursor:pointer; margin-top:8px; display:block;";
            reselect.addEventListener("click", () => document.getElementById("photo-input").click());

            preview.innerHTML = "";
            preview.appendChild(img);
            preview.appendChild(reselect);
        }
    };
    reader.readAsDataURL(file);
}

// 上传作品
async function doUploadWork() {
    const fileInput = document.getElementById("photo-input");
    const title = document.getElementById("work-title")?.value?.trim();

    if (!fileInput?.files?.length) {
        return showToast("请先拍照或选择一张照片", "error");
    }
    const file = fileInput.files[0];
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        return showToast("只支持 JPG/PNG/WebP 图片格式", "error");
    }
    if (file.size > 10 * 1024 * 1024) {
        return showToast("图片大小不能超过10MB", "error");
    }
    if (!title) {
        return showToast("请给作品起个名字", "error");
    }

    const formData = new FormData();
    formData.append("image", file);
    formData.append("title", title);
    formData.append("description", document.getElementById("work-desc")?.value || "");

    const contourId = document.getElementById("work-contour-id")?.value;
    if (contourId) formData.append("contour_id", contourId);
    const taskId = document.getElementById("work-task-id")?.value;
    if (taskId) formData.append("task_id", taskId);

    try {
        const headers = {};
        const token = APP.childToken;
        if (token) headers["Authorization"] = `Bearer ${token}`;

        const resp = await fetch("/api/works/upload", {
            method: "POST",
            headers,
            body: formData,
        });

        let json;
        try { json = await resp.json(); } catch { json = {}; }

        if (!resp.ok) {
            throw new Error(json.detail || "上传失败，请重试");
        }

        showToast("作品上传成功！", "success");
        if (json.work_id) {
            navigate("work-detail", { workId: json.work_id });
        } else {
            navigate("gallery");
        }
    } catch (e) {
        showToast(e.message, "error");
    }
}

// ============================================================
// 事件委托：安全处理含用户数据的点击事件
// 用 data-* 属性替代 inline onclick 中的字符串拼接，防止 XSS
// ============================================================
document.getElementById("app").addEventListener("click", function(e) {
    // 导航事件：data-nav="page" data-params="json"
    const navEl = e.target.closest("[data-nav]");
    if (navEl) {
        e.preventDefault();
        e.stopPropagation();
        const page = navEl.dataset.nav;
        const params = {};
        // 从 data-* 属性收集参数
        for (const [key, val] of Object.entries(navEl.dataset)) {
            if (key === "nav") continue;
            // 将 data-child-id → childId, data-work-id → workId
            const camel = key.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
            // 尝试解析数字
            params[camel] = /^\d+$/.test(val) ? parseInt(val) : val;
        }
        navigate(page, params);
        return;
    }

    // 操作事件：data-action="fn" data-params="json"
    const actEl = e.target.closest("[data-action]");
    if (actEl) {
        e.preventDefault();
        e.stopPropagation();
        const action = actEl.dataset.action;
        const id = actEl.dataset.id ? parseInt(actEl.dataset.id) : null;

        switch (action) {
            case "select-child":
                selectChild(id);
                break;
            case "start-task":
                startTask(id);
                break;
            case "evaluate-work":
                doEvaluateWork(id);
                break;
            case "parent-evaluate": {
                const childId = parseInt(actEl.dataset.childId);
                const childName = actEl.dataset.childName || "";
                doParentEvaluateWork(id, childId, childName);
                break;
            }
            case "print":
                doPrintContour();
                break;
            case "logout":
                doLogout();
                break;
            case "generate-task":
                doGenerateTask();
                break;
            case "register":
                doRegister();
                break;
            case "login":
                doLogin();
                break;
            case "add-child":
                doAddChild();
                break;
            case "upload-work":
                doUploadWork();
                break;
            case "change-print":
                changePrintCount(parseInt(actEl.dataset.delta));
                break;
            case "copy-invite-code":
                navigator.clipboard?.writeText(actEl.dataset.code || "")
                    .then(() => showToast("邀请码已复制", "success"))
                    .catch(() => showToast("复制失败，请手动复制", "error"));
                break;
            case "copy-invite-link":
                navigator.clipboard?.writeText(actEl.dataset.link || "")
                    .then(() => showToast("邀请链接已复制", "success"))
                    .catch(() => showToast("复制失败，请手动复制", "error"));
                break;
            case "back-to-parent":
                backToParent();
                break;
            case "share-invite":
                if (navigator.share) {
                    navigator.share({
                        title: "绘创前程 — 儿童创造力成长平台",
                        text: `我在用绘创前程培养孩子的创造力，邀请你一起加入！邀请码: ${actEl.dataset.code}`,
                        url: actEl.dataset.link,
                    }).catch(() => {});
                }
                break;
        }
    }
});
