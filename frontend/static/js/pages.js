/**
 * 绘创前程 — 页面渲染模块
 * 所有 render* 函数集中管理
 *
 * XSS 安全策略：
 * - 显示文本统一使用 escapeHtml()
 * - 交互事件使用 data-nav / data-action 属性 + 事件委托（actions.js）
 * - 禁止在 onclick 中拼接用户可控字符串
 */

// ============================================================
// 认证页面
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
            <button class="btn btn-primary btn-large" data-action="login">登录</button>
            <div style="text-align:center; margin-top:16px;">
                <a href="#" data-nav="register" style="color:var(--primary-500); font-size:0.9rem;">还没有账号？立即注册</a>
            </div>
        </div>
    `;
}

function renderRegister(container, params = {}) {
    const prefillCode = params.inviteCode || "";
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
            <div class="form-group">
                <label class="form-label">邀请码（选填）</label>
                <input type="text" id="reg-invite-code" class="form-input" placeholder="有邀请码？填写可获30学币" maxlength="6" value="${escapeAttr(prefillCode)}" style="text-transform:uppercase; letter-spacing:3px;">
                <div id="invite-code-hint" style="font-size:0.75rem; margin-top:4px; min-height:18px;"></div>
            </div>
            <button class="btn btn-primary btn-large" data-action="register">注册</button>
            <div style="text-align:center; margin-top:16px;">
                <a href="#" data-nav="login" style="color:var(--primary-500); font-size:0.9rem;">已有账号？去登录</a>
            </div>
        </div>
    `;
    // 邀请码实时验证
    const codeInput = document.getElementById("reg-invite-code");
    const hint = document.getElementById("invite-code-hint");
    let timer = null;
    codeInput?.addEventListener("input", () => {
        clearTimeout(timer);
        const val = codeInput.value.trim().toUpperCase();
        codeInput.value = val;
        if (val.length < 6) { hint.textContent = ""; return; }
        timer = setTimeout(async () => {
            try {
                const resp = await API.validateInviteCode(val);
                if (resp.valid) {
                    hint.innerHTML = '<span style="color:var(--success-500);">✓ 来自 ' + escapeHtml(resp.inviter_nickname) + ' 的邀请，注册即得30学币</span>';
                } else {
                    hint.innerHTML = '<span style="color:var(--error-500);">邀请码无效</span>';
                }
            } catch { hint.textContent = ""; }
        }, 500);
    });
}

// ============================================================
// 家长页面
// ============================================================

async function renderParentHome(container) {
    try {
        const childResp = await API.getChildren();
        const children = childResp.children || [];

        let dashboard = null;
        try {
            dashboard = await API.request("GET", "/parent/dashboard");
        } catch (e) { /* 忽略 */ }
        const dashChildren = dashboard?.children || [];

        const childMap = {};
        dashChildren.forEach(dc => { childMap[dc.id] = dc; });

        container.innerHTML = `
            <div class="header">
                <h1>绘创前程</h1>
                <div class="header-subtitle">家长中心</div>
                <div class="header-actions">
                    <button data-action="logout" style="background:none; border:none; color:#fff; font-size:0.85rem; cursor:pointer;">退出</button>
                </div>
            </div>
            <div class="page">
                <div class="welcome-section">
                    <div class="welcome-avatar">👨‍👩‍👧</div>
                    <div class="welcome-name">${escapeHtml(APP.user?.nickname || "家长")}</div>
                    <p style="color:var(--gray-500); font-size:0.85rem; margin-top:8px;">选择孩子，进入创作空间</p>
                </div>

                <div class="section-title">我的孩子</div>
                ${children.length > 0 ? children.map(child => {
                    const dc = childMap[child.id] || {};
                    const stats = dc.stats || {};
                    return `
                    <div class="card" data-action="select-child" data-id="${child.id}" style="cursor:pointer;">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <div style="font-size:2.2rem;">${child.gender === 'female' ? '👧' : '👦'}</div>
                            <div style="flex:1;">
                                <div style="font-weight:700; font-size:1rem;">${escapeHtml(child.nickname)}</div>
                                <div style="font-size:0.8rem; color:var(--gray-500);">${child.age}岁 · ${levelName(child.level_grade)}</div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-size:0.75rem; color:var(--gray-400);">作品</div>
                                <div style="font-weight:700; font-size:1.2rem; color:var(--primary-600);">${stats.total_works || 0}</div>
                            </div>
                        </div>
                        ${stats.total_tasks > 0 ? `
                            <div style="margin-top:8px; display:flex; gap:12px; font-size:0.75rem; color:var(--gray-400);">
                                <span>任务 ${stats.total_tasks || 0}</span>
                                <span>完成 ${stats.completed_tasks || 0}</span>
                            </div>
                        ` : ''}
                        <button class="btn btn-primary" style="width:100%; margin-top:12px; padding:10px; font-size:0.95rem;">
                            进入创作空间
                        </button>
                        ${dc.latest_work ? `
                            <div style="margin-top:10px; padding-top:10px; border-top:1px solid var(--gray-100); display:flex; align-items:center; gap:10px;">
                                <div style="width:40px; height:40px; border-radius:8px; overflow:hidden; background:#F5F5F5; flex-shrink:0;">
                                    ${dc.latest_work.thumbnail_path ? `<img src="${escapeHtml(dc.latest_work.thumbnail_path)}" alt="作品缩略图" style="width:100%; height:100%; object-fit:cover;">` : ''}
                                </div>
                                <div style="flex:1; font-size:0.8rem; color:var(--gray-600);">最新: ${escapeHtml(dc.latest_work.title || '无题')}</div>
                                <button data-nav="parent-child-works" data-child-id="${child.id}" data-child-name="${escapeAttr(child.nickname)}" style="font-size:0.75rem; color:var(--primary-500); background:none; border:1px solid var(--primary-300); padding:3px 10px; border-radius:8px; cursor:pointer;">
                                    查看全部
                                </button>
                            </div>
                        ` : ''}
                    </div>
                    `;
                }).join("") : `
                    <div style="text-align:center; padding:30px;">
                        <div style="font-size:3rem; margin-bottom:12px;">👶</div>
                        <p style="color:var(--gray-500);">还没有添加孩子</p>
                        <p style="font-size:0.8rem; color:var(--gray-400); margin-top:4px;">添加孩子后，就可以开始创作之旅了</p>
                    </div>
                `}

                <button class="btn btn-outline btn-large" data-nav="add-child" style="margin-top:12px;">
                    + 添加孩子
                </button>

                <!-- 推广中心入口 -->
                <div class="card" style="margin-top:20px; cursor:pointer;" data-nav="referral-center">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <div style="font-size:1.8rem;">🎁</div>
                        <div style="flex:1;">
                            <div style="font-weight:700; font-size:0.95rem; color:var(--primary-700);">推广中心</div>
                            <div style="font-size:0.78rem; color:var(--gray-500);">邀请好友注册，双方获得学币奖励</div>
                        </div>
                        <div style="color:var(--gray-400); font-size:1.2rem;">›</div>
                    </div>
                </div>

                <!-- 文创商城入口 -->
                <div class="card" style="cursor:pointer;" data-nav="merch-shop">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <div style="font-size:1.8rem;">🎨</div>
                        <div style="flex:1;">
                            <div style="font-weight:700; font-size:0.95rem; color:var(--primary-700);">文创商城</div>
                            <div style="font-size:0.78rem; color:var(--gray-500);">孩子画作变成实体产品，学币可抵扣</div>
                        </div>
                        <div style="color:var(--gray-400); font-size:1.2rem;">›</div>
                    </div>
                </div>

                <div class="card" style="margin-top:16px; background:var(--gray-50); text-align:center; padding:16px;">
                    <p style="font-size:0.82rem; color:var(--gray-500); line-height:1.6;">
                        没有原型就没有变形<br>
                        没有变形就没有创造
                    </p>
                    <p style="font-size:0.7rem; color:var(--gray-400); margin-top:6px;">— 绘创前程教育理念</p>
                </div>
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
                <button data-nav="parent-home" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
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
            <button class="btn btn-primary btn-large" data-action="add-child">确认添加</button>
        </div>
    `;
}

async function renderParentChildWorks(container, params) {
    try {
        const childId = params.childId;
        const childName = params.childName || '';
        const resp = await API.request("GET", `/parent/child/${childId}/works`);
        const works = resp.works || [];

        container.innerHTML = `
            <div class="header">
                <h1>${escapeHtml(childName)}的作品</h1>
                <div class="header-subtitle">共 ${works.length} 件作品</div>
                <div class="header-actions">
                    <button data-nav="parent-home" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                ${works.length > 0 ? `
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                        ${works.map(w => `
                            <div class="card" style="padding:0; overflow:hidden; cursor:pointer;"
                                 data-nav="parent-work-detail" data-work-id="${w.id}" data-child-id="${childId}" data-child-name="${escapeAttr(childName)}">
                                <div style="height:130px; background:#F5F5F5; display:flex; align-items:center; justify-content:center;">
                                    ${w.thumbnail_path ? `<img src="${escapeHtml(w.thumbnail_path)}" alt="作品缩略图" style="width:100%; height:100%; object-fit:cover;">` : `<div style="font-size:2.5rem;">🎨</div>`}
                                </div>
                                <div style="padding:10px;">
                                    <div style="font-weight:600; font-size:0.85rem;">${escapeHtml(w.title || '无题')}</div>
                                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
                                        <span style="font-size:0.68rem; color:var(--gray-400);">${escapeHtml(w.created_at || '')}</span>
                                        ${w.ai_score !== null && w.ai_score !== undefined ? `
                                            <span style="font-size:0.72rem; background:#FFF4EB; color:#D98B5F; padding:1px 6px; border-radius:8px; font-weight:600;">${w.ai_score}</span>
                                        ` : `
                                            <span style="font-size:0.68rem; color:var(--primary-500);">待评价</span>
                                        `}
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : `
                    <div style="text-align:center; padding:40px;">
                        <div style="font-size:3rem; margin-bottom:12px;">🖼️</div>
                        <p style="color:var(--gray-500);">还没有作品</p>
                    </div>
                `}
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
        navigate("parent-home");
    }
}

async function renderParentWorkDetail(container, params) {
    try {
        const work = await API.request("GET", `/works/${params.workId}`);
        const childName = params.childName || '';
        const childId = params.childId;
        const hasEval = work.evaluation && work.evaluation.originality !== null;

        const dims = [
            { key: "originality", name: "原创性", icon: "💡", color: "#D98B5F" },
            { key: "detail", name: "细节丰富度", icon: "🔍", color: "#4E8D7C" },
            { key: "composition", name: "构图表现", icon: "📐", color: "#89B4D4" },
            { key: "expression", name: "创意表达", icon: "🎨", color: "#9B6DBF" },
        ];

        container.innerHTML = `
            <div class="header" style="background:linear-gradient(135deg, #4E8D7C, #6BAF9C);">
                <h1>${escapeHtml(work.title || '无题')}</h1>
                <div class="header-subtitle">${escapeHtml(childName)}的作品</div>
                <div class="header-actions">
                    <button data-nav="parent-child-works" data-child-id="${childId}" data-child-name="${escapeAttr(childName)}" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                <div class="card" style="padding:0; overflow:hidden; margin-bottom:16px;">
                    <div style="background:#F5F5F5; min-height:200px; display:flex; align-items:center; justify-content:center;">
                        ${work.image_path ? `<img src="${escapeHtml(work.image_path)}" alt="作品预览" style="width:100%; max-height:400px; object-fit:contain;">` : `<div style="font-size:4rem; padding:40px;">🎨</div>`}
                    </div>
                </div>

                <div class="card" style="margin-bottom:12px;">
                    <div style="font-weight:700; font-size:1.1rem;">${escapeHtml(work.title || '无题')}</div>
                    ${work.description ? `<p style="color:var(--gray-600); font-size:0.9rem; margin-top:6px;">${escapeHtml(work.description)}</p>` : ''}
                    <div style="font-size:0.75rem; color:var(--gray-400); margin-top:8px;">${escapeHtml(work.created_at || '')}</div>
                </div>

                ${hasEval ? `
                    <div class="card" style="background:linear-gradient(135deg, #FFF8F0, #FFF4EB); border-color:#E8C090;">
                        <div class="card-title">⭐ 评价结果</div>
                        ${dims.map(d => {
                            const score = work.evaluation[d.key] || 0;
                            return `
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                                <span style="font-size:0.85rem;">${d.icon} ${d.name}</span>
                                <span style="font-weight:700; color:${d.color};">${score}</span>
                            </div>`;
                        }).join('')}
                        ${work.evaluation.feedback ? `<div style="margin-top:8px; padding:8px; background:#fff; border-radius:8px; font-size:0.88rem; color:var(--gray-700);">💬 ${escapeHtml(work.evaluation.feedback)}</div>` : ''}
                    </div>
                ` : `
                    <div class="card" id="parent-eval-section">
                        <div class="card-title">⭐ 评价这幅作品</div>
                        <p style="font-size:0.82rem; color:var(--gray-500); margin-bottom:12px;">给${escapeHtml(childName)}的作品打分鼓励一下</p>
                        ${dims.map(d => `
                            <div style="margin-bottom:12px;">
                                <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                                    <span style="font-size:0.85rem; font-weight:600;">${d.icon} ${d.name}</span>
                                    <span><span id="p-score-label-${d.key}" style="font-weight:700; color:${d.color};">7</span><span style="font-size:0.75rem; color:var(--gray-400);">/10</span></span>
                                </div>
                                <input type="range" id="p-score-${d.key}" min="0" max="10" step="0.5" value="7"
                                    oninput="document.getElementById('p-score-label-${d.key}').textContent=this.value"
                                    style="width:100%; accent-color:${d.color};">
                            </div>
                        `).join('')}
                        <div class="form-group">
                            <label class="form-label">💬 写一句鼓励的话</label>
                            <textarea id="p-eval-feedback" class="form-input" rows="2" placeholder="宝贝画得真棒！" style="resize:none;"></textarea>
                        </div>
                        <button class="btn btn-primary btn-large" data-action="parent-evaluate" data-id="${work.id}" data-child-id="${childId}" data-child-name="${escapeAttr(childName)}">
                            提交评价
                        </button>
                    </div>
                `}
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
        navigate("parent-home");
    }
}

// ============================================================
// 孩子页面
// ============================================================

async function renderChildHome(container) {
    try {
        const todayResp = await API.getTodayTasks();
        const tasks = todayResp.tasks || [];
        const child = APP.currentChild;

        let worksCount = 0;
        let growthData = null;
        try {
            const [worksResp, growthResp] = await Promise.all([
                API.request("GET", "/works/my", null, true),
                API.request("GET", "/showcase/growth", null, true),
            ]);
            worksCount = worksResp.total || 0;
            growthData = growthResp;
        } catch (e) { /* ignore */ }

        const completedToday = tasks.filter(t => t.status === "submitted" || t.status === "evaluated").length;
        const totalToday = tasks.length;
        const radar = growthData?.ability_radar;

        container.innerHTML = `
            <div class="header">
                <h1>${escapeHtml(child.nickname)}的创作空间</h1>
                <div class="header-subtitle">${levelName(child.level_grade)} · ${child.age}岁</div>
                <div class="header-actions">
                    <button data-action="back-to-parent" style="background:none; border:none; color:#fff; font-size:0.85rem; cursor:pointer;">切换</button>
                </div>
            </div>
            <div class="page">
                <div style="display:flex; gap:8px; margin-bottom:16px;">
                    <div style="flex:1; text-align:center; background:var(--primary-50); border-radius:12px; padding:10px 4px;">
                        <div style="font-size:1.5rem; font-weight:800; color:var(--primary-600);">${worksCount}</div>
                        <div style="font-size:0.7rem; color:var(--gray-500);">作品</div>
                    </div>
                    <div style="flex:1; text-align:center; background:var(--accent-50); border-radius:12px; padding:10px 4px;">
                        <div style="font-size:1.5rem; font-weight:800; color:var(--accent-600);">${growthData?.stats?.completed_tasks || 0}</div>
                        <div style="font-size:0.7rem; color:var(--gray-500);">完成</div>
                    </div>
                    <div style="flex:1; text-align:center; background:#FFF4EB; border-radius:12px; padding:10px 4px;">
                        <div style="font-size:1.5rem; font-weight:800; color:#D98B5F;">${levelName(child.level_grade)}</div>
                        <div style="font-size:0.7rem; color:var(--gray-500);">等级</div>
                    </div>
                </div>

                <div class="section-title" style="display:flex; justify-content:space-between; align-items:center;">
                    <span>今日训练</span>
                    <div style="display:flex; gap:12px; align-items:center;">
                        ${totalToday > 0 ? `<span style="font-size:0.75rem; color:var(--primary-500);">${completedToday}/${totalToday}</span>` : ''}
                        <span data-nav="task-history" style="font-size:0.75rem; color:var(--gray-400); cursor:pointer;">历史 ›</span>
                    </div>
                </div>
                ${tasks.length > 0 ? tasks.map(t => renderTaskCard(t)).join("") : `
                    <div class="card" style="text-align:center; padding:30px;">
                        <div style="font-size:2.5rem; margin-bottom:12px;">🎯</div>
                        <p style="color:var(--gray-500); margin-bottom:16px;">今天还没有训练任务</p>
                        <button class="btn btn-primary" data-action="generate-task">开始今天的训练</button>
                    </div>
                `}

                <div style="margin-top:20px;">
                    <div class="section-title">快速创作</div>
                    <div class="card" style="display:flex; align-items:center; gap:12px; cursor:pointer; border-color:var(--primary-300); border-width:2px;" data-nav="upload-work">
                        <div style="font-size:2rem;">📷</div>
                        <div style="flex:1;">
                            <div style="font-weight:700; font-size:0.95rem;">直接上传作品</div>
                            <div style="font-size:0.78rem; color:var(--gray-500);">拍照上传你随时画的作品</div>
                        </div>
                        <div style="color:var(--gray-300); font-size:1.2rem;">›</div>
                    </div>
                </div>

                <div style="margin-top:20px;">
                    <div class="section-title">探索</div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                        <div class="card" data-nav="contours" style="text-align:center; cursor:pointer; border-color:#D98B5F; border-width:2px;">
                            <div style="font-size:2rem; margin-bottom:8px;">🎨</div>
                            <div style="font-weight:600; font-size:0.9rem;">图形库</div>
                            <div style="font-size:0.75rem; color:var(--gray-500);">动物·植物·物品</div>
                        </div>
                        <div class="card" data-nav="transforms" style="text-align:center; cursor:pointer; border-color:#9B6DBF; border-width:2px;">
                            <div style="font-size:2rem; margin-bottom:8px;">✨</div>
                            <div style="font-weight:600; font-size:0.9rem;">变形魔法</div>
                            <div style="font-size:0.75rem; color:var(--gray-500);">7种创造技法</div>
                        </div>
                        <div class="card" data-nav="prototypes" data-module="A" style="text-align:center; cursor:pointer;">
                            <div style="font-size:2rem; margin-bottom:8px;">📐</div>
                            <div style="font-weight:600; font-size:0.9rem;">线条原型库</div>
                            <div style="font-size:0.75rem; color:var(--gray-500);">108种线条</div>
                        </div>
                        <div class="card" data-nav="gallery" style="text-align:center; cursor:pointer; border-color:#4E8D7C; border-width:2px;">
                            <div style="font-size:2rem; margin-bottom:8px;">🖼️</div>
                            <div style="font-weight:600; font-size:0.9rem;">我的展馆</div>
                            <div style="font-size:0.75rem; color:var(--gray-500);">${worksCount}件作品</div>
                        </div>
                    </div>
                </div>

                ${radar ? `
                    <div style="margin-top:20px;">
                        <div class="section-title">创造力概览</div>
                        <div class="card" data-nav="growth" style="cursor:pointer;">
                            <div style="display:flex; justify-content:space-around;">
                                ${[
                                    {key:'originality', name:'原创', icon:'💡', color:'#D98B5F'},
                                    {key:'detail', name:'细节', icon:'🔍', color:'#4E8D7C'},
                                    {key:'composition', name:'构图', icon:'📐', color:'#89B4D4'},
                                    {key:'expression', name:'表达', icon:'🎨', color:'#9B6DBF'},
                                ].map(d => `
                                    <div style="text-align:center;">
                                        <div style="font-size:0.7rem; color:var(--gray-400);">${d.icon} ${d.name}</div>
                                        <div style="font-size:1.2rem; font-weight:800; color:${d.color};">${radar[d.key]}</div>
                                    </div>
                                `).join('')}
                            </div>
                            <div style="text-align:center; margin-top:8px; font-size:0.72rem; color:var(--gray-400);">点击查看完整成长档案 ›</div>
                        </div>
                    </div>
                ` : ''}
            </div>

            <div class="tab-bar">
                <button class="tab-item active" aria-label="首页"><span class="tab-icon">🏠</span>首页</button>
                <button class="tab-item" data-nav="contours" aria-label="图形库"><span class="tab-icon">🎨</span>图形库</button>
                <button class="tab-item" data-nav="gallery" aria-label="展馆"><span class="tab-icon">🖼️</span>展馆</button>
                <button class="tab-item" data-nav="growth" aria-label="成长"><span class="tab-icon">📊</span>成长</button>
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
        <div class="card task-card ${moduleClass}" data-nav="task-detail" data-task-id="${task.task_id}">
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
                    <button data-nav="child-home" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
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
                                <div class="proto-cell-icon">${
                                    task.module === 'A'
                                        ? (typeof LineSVG !== 'undefined' ? LineSVG.generate(p.category, p.variant_index || 1) : '〰️')
                                        : (typeof LineSVG !== 'undefined' ? LineSVG.generateShape(p.id) : '🔷')
                                }</div>
                                <div class="proto-cell-name">${escapeHtml(p.name_zh)}</div>
                            </div>
                        `).join("")}
                    </div>
                ` : ""}

                ${task.transforms.length > 0 ? `
                    <div class="section-title">本次使用的变形魔法</div>
                    ${task.transforms.map(t => `
                        <div class="card" style="margin-bottom:10px;">
                            <div style="font-weight:700; font-size:1rem; margin-bottom:6px;">${escapeHtml(t.name_zh)}</div>
                            <div style="font-size:0.85rem; color:var(--gray-600); margin-bottom:8px;">${escapeHtml(t.description || "")}</div>
                            <div style="background:var(--gray-50); border-radius:10px; padding:8px; text-align:center;">
                                ${typeof TransformSVG !== 'undefined' ? TransformSVG.generateLarge(t.id, '') : ''}
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

                ${task.requirement?.recommended_contour ? `
                    <div class="card" style="background:linear-gradient(135deg, #FFF8F0, #FFF4EB); border-color:#E8C090; text-align:center;">
                        <div class="card-title">📋 推荐的图形底稿</div>
                        <div style="background:#fff; border-radius:12px; padding:12px; margin:8px 0;">
                            <img src="/api/contours/image/${encodeURIComponent(task.requirement.recommended_contour.image || task.requirement.recommended_contour.id + '.png')}" alt="${escapeAttr(task.requirement.recommended_contour.name || '轮廓图形')}" style="max-width:200px; max-height:200px; object-fit:contain;" loading="lazy">
                        </div>
                        <div style="font-weight:700; font-size:1rem; margin:4px 0;">${escapeHtml(task.requirement.recommended_contour.name)}</div>
                        <button class="btn btn-primary" data-nav="print-preview" data-contour-id="${escapeAttr(task.requirement.recommended_contour.id)}" style="margin-top:8px;">
                            🖨️ 下载打印这个图形
                        </button>
                        <p style="font-size:0.75rem; color:var(--gray-400); margin-top:6px;">也可以去图形库选其他图形哦</p>
                    </div>
                ` : `
                    <div class="card" style="text-align:center; padding:20px; background:var(--gray-50);">
                        <div style="font-size:2.5rem; margin-bottom:8px;">🖍️</div>
                        <p style="color:var(--gray-600); font-size:0.9rem; margin-bottom:10px;">拿出纸和笔，开始你的创作吧！</p>
                        <button class="btn btn-outline" data-nav="contours" style="font-size:0.85rem;">去图形库选个图形打印</button>
                    </div>
                `}

                ${task.status === "assigned" ? `
                    <button class="btn btn-primary btn-large" data-action="start-task" data-id="${task.task_id}">开始创作</button>
                ` : task.status === "in_progress" ? `
                    <button class="btn btn-accent btn-large" data-nav="upload-work" data-task-id="${task.task_id}">📷 拍照上传作品</button>
                ` : task.status === "submitted" ? `
                    <div class="card" style="text-align:center; background:#E8F5F1; border-color:#4E8D7C;">
                        <div style="font-size:2rem;">✅</div>
                        <div style="font-weight:700; color:#4E8D7C; margin-top:4px;">作品已提交</div>
                        <p style="font-size:0.82rem; color:var(--gray-500); margin-top:4px;">等待评价中</p>
                    </div>
                    <button class="btn btn-outline btn-large" data-nav="upload-work" data-task-id="${task.task_id}" style="margin-top:8px;">📷 再画一幅</button>
                ` : `
                    <div class="card" style="text-align:center; background:#FFF8F0; border-color:#D98B5F;">
                        <div style="font-size:2rem;">🌟</div>
                        <div style="font-weight:700; color:#D98B5F; margin-top:4px;">已评价完成</div>
                    </div>
                `}
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
        navigate("child-home");
    }
}

// ============================================================
// 图形库 / 变形库 / 原型库
// ============================================================

async function renderPrototypeLibrary(container, params) {
    try {
        const module = params?.module || "A";
        const resp = await API.getPrototypes(`?module=${module}`);
        const protos = resp.prototypes || [];

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
                    <button data-nav="child-home" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
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
                                <div class="proto-cell-icon">${
                                    module === "A"
                                        ? (typeof LineSVG !== 'undefined' ? LineSVG.generate(p.category, p.variant_index || 1) : "〰️")
                                        : (typeof LineSVG !== 'undefined' ? LineSVG.generateShape(p.id) : "🔷")
                                }</div>
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
        const actions = resp.actions || [];

        const actionMeta = {
            stretch:   { emoji: "📏", label: "拉一拉", color: "#E8F5F1", border: "#4E8D7C" },
            split:     { emoji: "✂️", label: "切一切", color: "#FFF4EB", border: "#D98B5F" },
            overlap:   { emoji: "🔄", label: "叠一叠", color: "#F0F7FF", border: "#89B4D4" },
            join:      { emoji: "🧩", label: "拼一拼", color: "#FFF4EB", border: "#D98B5F" },
            notch_add: { emoji: "✨", label: "挖一挖", color: "#FFF0F0", border: "#CC4444" },
            extend:    { emoji: "🌱", label: "长一长", color: "#E8D4F5", border: "#9B6DBF" },
            increase:  { emoji: "🎨", label: "添一添", color: "#FFE8CC", border: "#D98B5F" },
        };

        container.innerHTML = `
            <div class="header" style="background:linear-gradient(135deg, #D98B5F, #E8A87C);">
                <h1>变形魔法工坊</h1>
                <div class="header-subtitle">看看基础形能变成什么有趣的东西！</div>
                <div class="header-actions">
                    <button data-nav="child-home" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                <div class="card" style="background:linear-gradient(135deg, #FFF8F0, #FFF4EB); border-color:#F0D4B8; margin-bottom:16px; text-align:center;">
                    <p style="font-size:1rem; color:#8B5A2B; line-height:1.8; font-weight:600;">
                        从简单的圆、方、三角出发<br>
                        用7种魔法变成各种有趣的东西！
                    </p>
                    <p style="font-size:0.8rem; color:#B88B60; margin-top:4px;">点开每种魔法，看看能创造什么</p>
                </div>

                ${actions.map(a => {
                    const meta = actionMeta[a.id] || { emoji: "✨", label: a.name_zh, color: "#F5F5F5", border: "#CCC" };
                    const creations = (typeof TransformSVG !== 'undefined' && TransformSVG.creationMap[a.id]) || [];

                    return `
                    <div class="card" style="margin-bottom:14px; border-color:${meta.border}; border-width:2px; overflow:hidden;">
                        <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                            <div style="font-size:1.8rem;">${meta.emoji}</div>
                            <div>
                                <div style="font-weight:700; font-size:1.1rem; color:${meta.border};">
                                    ${meta.label}
                                    <span style="font-size:0.75rem; color:var(--gray-400); font-weight:400; margin-left:4px;">${escapeHtml(a.name_zh)} · ${escapeHtml(a.name_en)}</span>
                                </div>
                                <div style="font-size:0.82rem; color:var(--gray-600); margin-top:2px;">${escapeHtml(a.instruction)}</div>
                            </div>
                        </div>

                        <div style="background:${meta.color}; border-radius:10px; padding:8px; margin-bottom:10px; text-align:center;">
                            ${typeof TransformSVG !== 'undefined' ? TransformSVG.generate(a.id) : ''}
                        </div>

                        ${creations.length > 0 ? `
                            <div style="font-size:0.78rem; color:var(--gray-500); font-weight:600; margin-bottom:6px;">用这个魔法可以创造：</div>
                            <div style="display:flex; gap:8px; overflow-x:auto; padding-bottom:4px;">
                                ${creations.map(c => `
                                    <div style="flex-shrink:0; text-align:center; background:${meta.color}; border-radius:10px; padding:6px 8px; min-width:80px;">
                                        ${typeof TransformSVG !== 'undefined' && TransformSVG.examples[c.id] ? TransformSVG.generateExample(c.id) : ''}
                                        <div style="font-size:0.85rem; font-weight:600; color:${meta.border}; margin-top:2px;">${escapeHtml(c.name)}</div>
                                        <div style="font-size:0.65rem; color:var(--gray-500);">${escapeHtml(c.desc)}</div>
                                    </div>
                                `).join("")}
                            </div>
                        ` : ''}
                    </div>
                    `;
                }).join("")}

                <div class="section-title" style="margin-top:20px;">"添一添"的5种玩法</div>
                <p style="font-size:0.8rem; color:var(--gray-500); margin-bottom:10px;">
                    "添一添"最自由——往图形里面添内容，想加什么就加什么！
                </p>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                    ${[
                        {name:'画表情', desc:'眼睛嘴巴 让它活起来', icon:'😊', color:'#FFF4EB'},
                        {name:'加线条', desc:'胡须光芒 让它更酷', icon:'✏️', color:'#E8F5F1'},
                        {name:'装零件', desc:'翅膀轮子 给它超能力', icon:'🔧', color:'#F0F7FF'},
                        {name:'变多多', desc:'复制窗户 排成一排', icon:'📋', color:'#FFF0F0'},
                        {name:'戴饰品', desc:'帽子围巾 打扮起来', icon:'🎀', color:'#E8D4F5'},
                    ].map(s => `
                        <div class="card" style="padding:12px; text-align:center; background:${s.color};">
                            <div style="font-size:1.5rem;">${s.icon}</div>
                            <div style="font-weight:700; font-size:0.85rem; margin-top:4px;">${s.name}</div>
                            <div style="font-size:0.7rem; color:var(--gray-500); margin-top:2px;">${s.desc}</div>
                        </div>
                    `).join("")}
                </div>
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
    }
}

async function renderContourLibrary(container) {
    let allContours = [];
    try {
        const resp = await API.request("GET", "/training/contours", null, true);
        allContours = resp.contours || [];
    } catch (e) {
        container.innerHTML = '<div class="page"><p>图形库加载失败，请刷新页面</p></div>';
        return;
    }

    const categoryMeta = {
        animals:  { icon: "🐾", name: "动物", color: "#FFF4EB" },
        plants:   { icon: "🌿", name: "植物果实", color: "#E8F5F1" },
        objects:  { icon: "🏠", name: "生活用品", color: "#F0F7FF" },
        clothing: { icon: "👗", name: "服饰", color: "#E8D4F5" },
        vehicles: { icon: "🚀", name: "交通工具", color: "#FFF0F0" },
        fantasy:  { icon: "🐉", name: "奇幻", color: "#FFE8CC" },
    };

    const catOrder = ["animals", "plants", "objects", "clothing", "vehicles", "fantasy"];
    let activeCategory = "animals";

    function render() {
        const items = allContours.filter(c => c.category === activeCategory);
        const catInfo = categoryMeta[activeCategory] || { icon: "📦", name: activeCategory, color: "#F5F5F5" };

        container.innerHTML = `
            <div class="header" style="background:linear-gradient(135deg, #D98B5F, #E8A87C);">
                <h1>图形库</h1>
                <div class="header-subtitle">${allContours.length}个原创线描图形，选一个打印出来画画吧！</div>
                <div class="header-actions">
                    <button data-nav="child-home" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                <div style="display:flex; gap:6px; overflow-x:auto; padding:4px 0 12px; -webkit-overflow-scrolling:touch;">
                    ${catOrder.filter(cid => allContours.some(c => c.category === cid)).map(catId => {
                        const cat = categoryMeta[catId] || {};
                        const count = allContours.filter(c => c.category === catId).length;
                        return `
                        <button onclick="switchContourCategory('${catId}')"
                            style="flex-shrink:0; padding:8px 14px; border-radius:20px; border:2px solid ${activeCategory === catId ? '#D98B5F' : '#E0E0E0'};
                            background:${activeCategory === catId ? cat.color : '#fff'}; font-size:0.82rem; cursor:pointer; font-weight:${activeCategory === catId ? '700' : '400'}; white-space:nowrap;">
                            ${cat.icon} ${cat.name}<span style="font-size:0.7rem; color:var(--gray-400); margin-left:2px;">${count}</span>
                        </button>`;
                    }).join("")}
                </div>

                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                    ${items.map(item => `
                        <div class="card" style="text-align:center; padding:8px; cursor:pointer; transition:all 0.2s;"
                             data-nav="print-preview" data-contour-id="${escapeAttr(item.id)}">
                            <div style="background:${catInfo.color}; border-radius:12px; padding:6px; margin-bottom:8px; min-height:120px; display:flex; align-items:center; justify-content:center;">
                                ${item.image_url
                                    ? `<img src="${escapeHtml(item.image_url)}" alt="${escapeAttr(item.name_zh || item.name || '轮廓图形')}" style="max-width:100%; max-height:140px; object-fit:contain;" loading="lazy">`
                                    : (typeof ContourSVG !== 'undefined' ? ContourSVG.generate(item.id) : `<div style="font-size:2rem;">🎨</div>`)}
                            </div>
                            <div style="font-weight:700; font-size:0.95rem;">${escapeHtml(item.name)}</div>
                            <div style="font-size:0.72rem; color:var(--gray-500); margin-top:2px;">${escapeHtml(item.description || '')}</div>
                            <div style="margin-top:6px;">
                                <span style="font-size:0.7rem; background:var(--primary-50); color:var(--primary-600); padding:2px 8px; border-radius:10px;">
                                    ${'⭐'.repeat(item.difficulty)}
                                </span>
                            </div>
                        </div>
                    `).join("")}
                </div>

                ${items.length === 0 ? `
                    <div class="empty-state">
                        <div class="empty-state-icon">${catInfo.icon}</div>
                        <p>这个分类正在准备中...</p>
                    </div>
                ` : ''}
            </div>

            <div class="tab-bar">
                <button class="tab-item" data-nav="child-home" aria-label="首页"><span class="tab-icon">🏠</span>首页</button>
                <button class="tab-item active" aria-label="图形库"><span class="tab-icon">🎨</span>图形库</button>
                <button class="tab-item" data-nav="gallery" aria-label="展馆"><span class="tab-icon">🖼️</span>展馆</button>
                <button class="tab-item" data-nav="growth" aria-label="成长"><span class="tab-icon">📊</span>成长</button>
            </div>
        `;
    }

    window.switchContourCategory = function(cat) {
        activeCategory = cat;
        render();
    };

    render();
}

async function renderPrintPreview(container, params) {
    const contourId = params?.contourId;
    if (!contourId) { navigate('contours'); return; }

    let item = null;
    try {
        const data = await API.request("GET", "/training/contours", null, true);
        const contours = data.contours || [];
        item = contours.find(c => c.id === contourId);
    } catch (e) {
        if (typeof ContourSVG !== 'undefined' && ContourSVG.library[contourId]) {
            item = ContourSVG.library[contourId];
        }
    }

    if (!item) { navigate('contours'); return; }

    const imageUrl = item.image_url || `/api/contours/image/${encodeURIComponent(contourId + '.png')}`;
    const child = APP.currentChild || {};
    const today = new Date().toLocaleDateString('zh-CN');

    container.innerHTML = `
        <div class="header" style="background:linear-gradient(135deg, var(--primary-500), var(--primary-400));">
            <h1>${escapeHtml(item.name)}</h1>
            <div class="header-subtitle">预览与下载打印</div>
            <div class="header-actions">
                <button data-nav="contours" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
            </div>
        </div>
        <div class="page">
            <div class="card" style="text-align:center; padding:20px;">
                <p style="font-size:0.85rem; color:var(--gray-600); margin-bottom:12px;">${escapeHtml(item.description || '')}</p>
                <div id="print-area" style="background:#fff; border:2px solid #E0E0E0; border-radius:8px; padding:20px; max-width:400px; margin:0 auto;">
                    <div style="text-align:center; font-size:0.8rem; color:#999; margin-bottom:10px;">
                        绘创前程 · ${escapeHtml(item.name)} · ${escapeHtml(child.nickname || '')}
                    </div>
                    <div style="display:flex; justify-content:center;">
                        <img src="${escapeHtml(imageUrl)}" alt="打印预览" style="max-width:100%; max-height:350px; object-fit:contain;" loading="lazy">
                    </div>
                    <div style="margin-top:12px; display:flex; justify-content:space-between; font-size:0.75rem; color:#BBB;">
                        <span>姓名：____________</span>
                        <span>日期：${today}</span>
                    </div>
                </div>
            </div>

            <div class="card" style="background:var(--accent-50); border-color:var(--accent-200);">
                <div class="card-title">打印份数</div>
                <p style="font-size:0.82rem; color:var(--gray-600); margin-bottom:10px;">同一个图形可以打印多张，用不同的风格来画！</p>
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                    <button data-action="change-print" data-delta="-1" style="width:44px; height:44px; border-radius:50%; border:2px solid var(--primary-300); background:var(--primary-50); font-size:1.2rem; cursor:pointer;">-</button>
                    <span id="print-count" style="font-size:1.5rem; font-weight:700; color:var(--primary-600); min-width:30px; text-align:center;">1</span>
                    <button data-action="change-print" data-delta="1" style="width:44px; height:44px; border-radius:50%; border:2px solid var(--primary-300); background:var(--primary-50); font-size:1.2rem; cursor:pointer;">+</button>
                    <span style="font-size:0.8rem; color:var(--gray-500);">张</span>
                </div>
            </div>

            <button class="btn btn-primary btn-large" data-action="print" style="margin-top:12px;">
                🖨️ 下载打印
            </button>

            <button class="btn btn-outline btn-large" data-nav="upload-work" data-contour-id="${escapeAttr(contourId)}" data-contour-name="${escapeAttr(item.name)}" style="margin-top:8px;">
                📷 画好了？上传作品
            </button>
        </div>
    `;
}

// ============================================================
// 作品 / 展馆 / 成长
// ============================================================

function renderUploadWork(container, params) {
    const contourId = params?.contourId || '';
    const taskId = params?.taskId || 0;
    const contourName = params?.contourName || '';

    container.innerHTML = `
        <div class="header" style="background:linear-gradient(135deg, #4E8D7C, #6BAF9C);">
            <h1>上传作品</h1>
            <div class="header-subtitle">${contourName ? '基于：' + escapeHtml(contourName) : '拍照上传你的创作'}</div>
            <div class="header-actions">
                <button data-nav="child-home" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
            </div>
        </div>
        <div class="page">
            <div class="card" style="text-align:center; padding:30px;">
                <div id="upload-preview" style="margin-bottom:16px;">
                    <div style="width:200px; height:200px; margin:0 auto; border:3px dashed #CCC; border-radius:16px; display:flex; align-items:center; justify-content:center; cursor:pointer;"
                         onclick="document.getElementById('photo-input').click()">
                        <div>
                            <div style="font-size:3rem;">📷</div>
                            <div style="font-size:0.85rem; color:var(--gray-500); margin-top:8px;">点击拍照或选择照片</div>
                        </div>
                    </div>
                </div>
                <input type="file" id="photo-input" accept="image/*" capture="camera" style="display:none;" onchange="previewUploadPhoto(this)">
            </div>

            <div class="form-group">
                <label class="form-label">作品名称</label>
                <input type="text" id="work-title" class="form-input" placeholder="给作品起个名字吧" value="${contourName ? '我的' + escapeHtml(contourName) : ''}">
            </div>

            <div class="form-group">
                <label class="form-label">想说点什么？（选填）</label>
                <textarea id="work-desc" class="form-input" rows="2" placeholder="比如：我用波浪线装饰了蝴蝶的翅膀" style="resize:none;"></textarea>
            </div>

            ${contourId ? `<input type="hidden" id="work-contour-id" value="${escapeAttr(contourId)}">` : ''}
            ${taskId ? `<input type="hidden" id="work-task-id" value="${taskId}">` : ''}

            <button class="btn btn-primary btn-large" data-action="upload-work">上传到我的展馆</button>
        </div>
    `;
}

async function renderGallery(container) {
    try {
        let works = [];
        try {
            const resp = await API.request("GET", "/works/my", null, true);
            works = resp.works || [];
        } catch (e) { /* API可能还没实现 */ }

        const child = APP.currentChild || {};

        container.innerHTML = `
            <div class="header" style="background:linear-gradient(135deg, #4E8D7C, #6BAF9C);">
                <h1>${escapeHtml(child.nickname || '')}的展馆</h1>
                <div class="header-subtitle">我的创作天地 · ${works.length} 件作品</div>
                <div class="header-actions">
                    <button data-nav="child-home" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                ${works.length > 0 ? `
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                        ${works.map(w => `
                            <div class="card" style="padding:0; overflow:hidden; cursor:pointer;" data-nav="work-detail" data-work-id="${w.id}">
                                <div style="height:140px; background:#F5F5F5; display:flex; align-items:center; justify-content:center;">
                                    ${w.thumbnail_path ? `<img src="${escapeHtml(w.thumbnail_path)}" alt="作品缩略图" style="width:100%; height:100%; object-fit:cover;" loading="lazy">` :
                                      `<div style="font-size:3rem;">🎨</div>`}
                                </div>
                                <div style="padding:10px;">
                                    <div style="font-weight:600; font-size:0.85rem;">${escapeHtml(w.title || '无题')}</div>
                                    <div style="font-size:0.7rem; color:var(--gray-400); margin-top:2px;">${escapeHtml(w.created_at || '')}</div>
                                    ${w.source_type === 'task' ? '<span style="font-size:0.65rem; background:#E8F5F1; color:#4E8D7C; padding:1px 6px; border-radius:8px;">任务作品</span>' : ''}
                                </div>
                            </div>
                        `).join("")}
                    </div>
                ` : `
                    <div style="text-align:center; padding:40px 20px;">
                        <div style="font-size:4rem; margin-bottom:16px;">🖼️</div>
                        <h3 style="color:var(--gray-600); margin-bottom:8px;">展馆还是空的</h3>
                        <p style="font-size:0.85rem; color:var(--gray-400); line-height:1.6; margin-bottom:20px;">
                            完成训练任务，或者从图形库选一个图形打印出来画画，<br>
                            然后拍照上传，你的作品就会出现在这里！
                        </p>
                        <div style="display:flex; gap:10px; justify-content:center; flex-wrap:wrap;">
                            <button class="btn btn-primary" data-nav="contours">去图形库选图</button>
                            <button class="btn btn-outline" data-nav="upload-work">直接上传作品</button>
                        </div>
                    </div>
                `}
            </div>

            <div class="tab-bar">
                <button class="tab-item" data-nav="child-home" aria-label="首页"><span class="tab-icon">🏠</span>首页</button>
                <button class="tab-item" data-nav="contours" aria-label="图形库"><span class="tab-icon">🎨</span>图形库</button>
                <button class="tab-item active" aria-label="展馆"><span class="tab-icon">🖼️</span>展馆</button>
                <button class="tab-item" data-nav="growth" aria-label="成长"><span class="tab-icon">📊</span>成长</button>
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
    }
}

async function renderGrowth(container) {
    try {
        let data = null;
        try { data = await API.request("GET", "/showcase/growth", null, true); } catch (e) {}

        const child = APP.currentChild || {};
        const stats = data?.stats || {};
        const recentWorks = data?.recent_works || [];
        const radar = data?.ability_radar;
        const bestWork = data?.best_work;
        const evalTrend = data?.eval_trend || [];

        const dims = [
            { key: "originality", name: "原创性", icon: "💡", color: "#D98B5F" },
            { key: "detail", name: "细节", icon: "🔍", color: "#4E8D7C" },
            { key: "composition", name: "构图", icon: "📐", color: "#89B4D4" },
            { key: "expression", name: "表达", icon: "🎨", color: "#9B6DBF" },
        ];

        container.innerHTML = `
            <div class="header" style="background:linear-gradient(135deg, #6BAF9C, #4E8D7C);">
                <h1>${escapeHtml(child.nickname || '')}的成长档案</h1>
                <div class="header-subtitle">${levelName(child.level_grade)} · ${child.age || ''}岁</div>
                <div class="header-actions">
                    <button data-nav="child-home" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin-bottom:16px;">
                    <div class="card" style="text-align:center; background:var(--primary-50); padding:14px 8px;">
                        <div style="font-size:1.6rem; font-weight:800; color:var(--primary-600);">${stats.total_works || 0}</div>
                        <div style="font-size:0.75rem; color:var(--gray-500);">件作品</div>
                    </div>
                    <div class="card" style="text-align:center; background:var(--accent-50); padding:14px 8px;">
                        <div style="font-size:1.6rem; font-weight:800; color:var(--accent-600);">${stats.completed_tasks || 0}</div>
                        <div style="font-size:0.75rem; color:var(--gray-500);">完成任务</div>
                    </div>
                    <div class="card" style="text-align:center; background:#FFF4EB; padding:14px 8px;">
                        <div style="font-size:1.6rem; font-weight:800; color:#D98B5F;">${stats.evaluated_works || 0}</div>
                        <div style="font-size:0.75rem; color:var(--gray-500);">已评价</div>
                    </div>
                </div>

                ${radar ? `
                    <div class="card" style="margin-bottom:14px; background:linear-gradient(135deg, #FAFCFB, #F5FAF8);">
                        <div class="card-title">🌟 创造力画像</div>
                        <div style="margin-top:12px;">
                            ${dims.map(d => {
                                const score = radar[d.key] || 0;
                                const pct = Math.round(score * 10);
                                return `
                                <div style="margin-bottom:10px;">
                                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                        <span style="font-size:0.85rem; font-weight:600;">${d.icon} ${d.name}</span>
                                        <span style="font-size:0.95rem; font-weight:700; color:${d.color};">${score}</span>
                                    </div>
                                    <div style="background:#E8E8E8; border-radius:6px; height:8px; overflow:hidden;">
                                        <div style="background:linear-gradient(90deg, ${d.color}88, ${d.color}); height:100%; width:${pct}%; border-radius:6px; transition:width 0.8s ease;"></div>
                                    </div>
                                </div>`;
                            }).join('')}
                            <div style="text-align:center; margin-top:14px; padding-top:12px; border-top:1px solid #E0E0E0;">
                                <span style="font-size:0.75rem; color:var(--gray-400);">基于 ${stats.evaluated_works} 件作品的综合评估</span>
                            </div>
                        </div>
                    </div>
                ` : ''}

                ${bestWork ? `
                    <div class="card" style="margin-bottom:14px; background:linear-gradient(135deg, #FFF8F0, #FFF4EB); border-color:#E8C090; cursor:pointer;" data-nav="work-detail" data-work-id="${bestWork.id}">
                        <div class="card-title">🏆 最佳作品</div>
                        <div style="display:flex; align-items:center; gap:12px; margin-top:8px;">
                            <div style="width:60px; height:60px; border-radius:10px; overflow:hidden; background:#F5F5F5; flex-shrink:0;">
                                ${bestWork.thumbnail_path ? `<img src="${escapeHtml(bestWork.thumbnail_path)}" alt="作品缩略图" style="width:100%; height:100%; object-fit:cover;">` : '<div style="display:flex;align-items:center;justify-content:center;height:100%;font-size:1.5rem;">🎨</div>'}
                            </div>
                            <div>
                                <div style="font-weight:700; font-size:1rem;">${escapeHtml(bestWork.title)}</div>
                                <div style="font-size:0.85rem; color:#D98B5F; font-weight:600;">综合评分 ${bestWork.avg_score}</div>
                            </div>
                        </div>
                    </div>
                ` : ''}

                ${evalTrend.length > 1 ? `
                    <div class="card" style="margin-bottom:14px;">
                        <div class="card-title">📈 进步趋势</div>
                        <div style="margin-top:8px;">
                            ${evalTrend.slice().reverse().map((e, i) => {
                                const avg = ((e.scores.originality + e.scores.detail + e.scores.composition + e.scores.expression) / 4).toFixed(1);
                                const pct = Math.round(avg * 10);
                                return `
                                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px; cursor:pointer;" data-nav="work-detail" data-work-id="${e.id}">
                                    <span style="font-size:0.72rem; color:var(--gray-400); min-width:18px;">${i + 1}</span>
                                    <div style="flex:1; background:#F0F0F0; border-radius:4px; height:20px; overflow:hidden; position:relative;">
                                        <div style="background:linear-gradient(90deg, #4E8D7C, #6BAF9C); height:100%; width:${pct}%; border-radius:4px; transition:width 0.5s;"></div>
                                        <span style="position:absolute; left:8px; top:2px; font-size:0.7rem; color:#333; font-weight:600;">${escapeHtml(e.title)}</span>
                                    </div>
                                    <span style="font-size:0.85rem; font-weight:700; color:#4E8D7C; min-width:30px; text-align:right;">${avg}</span>
                                </div>`;
                            }).join('')}
                        </div>
                    </div>
                ` : ''}

                <div class="card" style="margin-bottom:14px;">
                    <div class="card-title">🏅 训练等级</div>
                    <div style="display:flex; align-items:center; gap:10px; margin-top:8px;">
                        <div style="font-size:2rem;">🏅</div>
                        <div style="flex:1;">
                            <div style="font-weight:700; font-size:1.1rem; color:var(--primary-600);">${levelName(child.level_grade)}</div>
                            <div style="font-size:0.8rem; color:var(--gray-500);">${child.age || ''}岁</div>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:0.7rem; color:var(--gray-400);">模块A</span>
                            <span style="font-weight:700; color:#4E8D7C; margin-left:4px;">${stats.module_a_tasks || 0}</span>
                            <span style="font-size:0.7rem; color:var(--gray-400); margin-left:8px;">模块B</span>
                            <span style="font-weight:700; color:#D98B5F; margin-left:4px;">${stats.module_b_tasks || 0}</span>
                        </div>
                    </div>
                    <div style="margin-top:10px; background:var(--gray-100); border-radius:10px; height:8px; overflow:hidden;">
                        <div style="background:linear-gradient(90deg, var(--primary-400), var(--accent-400)); height:100%; width:${Math.min(100, (stats.completed_tasks || 0) * 10)}%; border-radius:10px; transition:width 0.5s;"></div>
                    </div>
                </div>

                ${recentWorks.length > 0 ? `
                    <div class="section-title">最近的作品</div>
                    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-bottom:16px;">
                        ${recentWorks.map(w => `
                            <div style="background:#F5F5F5; border-radius:10px; overflow:hidden; aspect-ratio:1; cursor:pointer;" data-nav="work-detail" data-work-id="${w.id}">
                                ${w.thumbnail_path ? `<img src="${escapeHtml(w.thumbnail_path)}" alt="作品缩略图" style="width:100%; height:100%; object-fit:cover;" loading="lazy">` :
                                  `<div style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; font-size:2rem;">🎨</div>`}
                            </div>
                        `).join("")}
                    </div>
                ` : ''}

                ${(stats.total_works || 0) === 0 ? `
                    <div class="card" style="text-align:center; background:linear-gradient(135deg, #FFF8F0, #FFF4EB); padding:24px;">
                        <div style="font-size:3rem; margin-bottom:12px;">🌟</div>
                        <h3 style="color:#8B5A2B;">开始你的创作之旅</h3>
                        <p style="font-size:0.85rem; color:#B88B60; margin:8px 0 16px;">
                            每一件作品都是成长的足迹<br>
                            从图形库选一个图形开始吧！
                        </p>
                        <button class="btn btn-primary" data-nav="contours">去图形库</button>
                    </div>
                ` : `
                    <div class="card" style="text-align:center;">
                        <p style="font-size:0.85rem; color:var(--gray-500);">
                            每一件作品都是成长的足迹。继续创作，让展馆越来越丰富！
                        </p>
                        <button class="btn btn-outline" data-nav="gallery" style="margin-top:8px; font-size:0.85rem;">查看全部作品</button>
                    </div>
                `}
            </div>

            <div class="tab-bar">
                <button class="tab-item" data-nav="child-home" aria-label="首页"><span class="tab-icon">🏠</span>首页</button>
                <button class="tab-item" data-nav="contours" aria-label="图形库"><span class="tab-icon">🎨</span>图形库</button>
                <button class="tab-item" data-nav="gallery" aria-label="展馆"><span class="tab-icon">🖼️</span>展馆</button>
                <button class="tab-item active" aria-label="成长"><span class="tab-icon">📊</span>成长</button>
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
    }
}

async function renderTaskHistory(container) {
    try {
        const resp = await API.request("GET", "/training/history", null, true);
        const tasks = resp.tasks || [];

        const statusMap = { assigned: "待开始", in_progress: "进行中", submitted: "已提交", evaluated: "已评价" };
        const statusColor = { assigned: "#8C99A5", in_progress: "#856404", submitted: "#0C5460", evaluated: "#155724" };
        const statusBg = { assigned: "#F0F0F0", in_progress: "#FFF3CD", submitted: "#D1ECF1", evaluated: "#D4EDDA" };

        container.innerHTML = `
            <div class="header">
                <h1>训练记录</h1>
                <div class="header-subtitle">共 ${resp.total} 个任务</div>
                <div class="header-actions">
                    <button data-nav="child-home" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                ${tasks.length > 0 ? tasks.map(t => `
                    <div class="card" style="border-left:4px solid ${t.module === 'A' ? 'var(--primary-500)' : 'var(--accent-500)'}; cursor:pointer;" data-nav="task-detail" data-task-id="${t.id}">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                            <div style="flex:1;">
                                <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px;">
                                    <span style="font-size:0.68rem; background:${t.module === 'A' ? 'var(--primary-50)' : 'var(--accent-50)'}; color:${t.module === 'A' ? 'var(--primary-600)' : 'var(--accent-600)'}; padding:1px 8px; border-radius:10px; font-weight:600;">
                                        ${t.module === 'A' ? '原型组合' : '图形变形'}
                                    </span>
                                    <span style="font-size:0.68rem; background:${statusBg[t.status]}; color:${statusColor[t.status]}; padding:1px 8px; border-radius:10px;">
                                        ${statusMap[t.status]}
                                    </span>
                                </div>
                                <div style="font-weight:700; font-size:0.95rem;">${escapeHtml(t.title)}</div>
                                <div style="font-size:0.78rem; color:var(--gray-500); margin-top:2px;">${escapeHtml(t.description || '').slice(0, 50)}${(t.description || '').length > 50 ? '...' : ''}</div>
                                <div style="font-size:0.7rem; color:var(--gray-400); margin-top:4px;">${escapeHtml(t.assigned_at || '')}</div>
                            </div>
                            ${t.works.length > 0 ? `
                                <div style="flex-shrink:0; margin-left:10px;">
                                    <div style="width:50px; height:50px; border-radius:8px; overflow:hidden; background:#F5F5F5;">
                                        ${t.works[0].thumbnail_path ? `<img src="${escapeHtml(t.works[0].thumbnail_path)}" alt="作品缩略图" style="width:100%; height:100%; object-fit:cover;">` : ''}
                                    </div>
                                    ${t.works.length > 1 ? `<div style="font-size:0.65rem; color:var(--gray-400); text-align:center; margin-top:2px;">+${t.works.length}</div>` : ''}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `).join('') : `
                    <div style="text-align:center; padding:40px;">
                        <div style="font-size:3rem; margin-bottom:12px;">📝</div>
                        <p style="color:var(--gray-500);">还没有训练记录</p>
                        <button class="btn btn-primary" data-nav="child-home" style="margin-top:16px;">去开始训练</button>
                    </div>
                `}
            </div>

            <div class="tab-bar">
                <button class="tab-item" data-nav="child-home" aria-label="首页"><span class="tab-icon">🏠</span>首页</button>
                <button class="tab-item" data-nav="contours" aria-label="图形库"><span class="tab-icon">🎨</span>图形库</button>
                <button class="tab-item" data-nav="gallery" aria-label="展馆"><span class="tab-icon">🖼️</span>展馆</button>
                <button class="tab-item" data-nav="growth" aria-label="成长"><span class="tab-icon">📊</span>成长</button>
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
    }
}

async function renderWorkDetail(container, params) {
    try {
        const work = await API.getWorkDetail(params.workId);
        const child = APP.currentChild || {};
        const hasEval = work.evaluation && work.evaluation.originality !== null;

        const dims = [
            { key: "originality", name: "原创性", icon: "💡", desc: "是否有自己的想法", color: "#D98B5F" },
            { key: "detail", name: "细节丰富度", icon: "🔍", desc: "细节是否丰富多样", color: "#4E8D7C" },
            { key: "composition", name: "构图表现", icon: "📐", desc: "画面布局是否协调", color: "#89B4D4" },
            { key: "expression", name: "创意表达", icon: "🎨", desc: "是否传达出想法和情感", color: "#9B6DBF" },
        ];

        container.innerHTML = `
            <div class="header" style="background:linear-gradient(135deg, #4E8D7C, #6BAF9C);">
                <h1>${escapeHtml(work.title || '无题')}</h1>
                <div class="header-subtitle">${escapeHtml(child.nickname || '')}的作品</div>
                <div class="header-actions">
                    <button data-nav="gallery" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                <div class="card" style="padding:0; overflow:hidden; margin-bottom:16px;">
                    <div style="background:#F5F5F5; min-height:200px; display:flex; align-items:center; justify-content:center;">
                        ${work.image_path
                            ? `<img src="${escapeHtml(work.image_path)}" alt="作品预览" style="width:100%; max-height:400px; object-fit:contain;">`
                            : `<div style="font-size:4rem; padding:40px;">🎨</div>`}
                    </div>
                </div>

                <div class="card" style="margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <div style="font-weight:700; font-size:1.1rem;">${escapeHtml(work.title || '无题')}</div>
                        <span style="font-size:0.7rem; background:${work.source_type === 'task' ? '#E8F5F1' : '#FFF4EB'}; color:${work.source_type === 'task' ? '#4E8D7C' : '#D98B5F'}; padding:3px 10px; border-radius:12px;">
                            ${work.source_type === 'task' ? '训练作品' : '自由创作'}
                        </span>
                    </div>
                    ${work.description ? `<p style="color:var(--gray-600); font-size:0.9rem; line-height:1.6;">${escapeHtml(work.description)}</p>` : ''}
                    <div style="font-size:0.75rem; color:var(--gray-400); margin-top:8px;">${escapeHtml(work.created_at || '')}</div>
                </div>

                ${work.task ? `
                    <div class="card" style="background:var(--primary-50); border-color:var(--primary-200); margin-bottom:12px;">
                        <div class="card-title">📋 来自训练任务</div>
                        <div style="font-weight:600; font-size:0.9rem; margin-top:4px;">${escapeHtml(work.task.title)}</div>
                        <div style="font-size:0.8rem; color:var(--gray-500); margin-top:2px;">
                            ${work.task.module === 'A' ? '模块A · 原型组合' : '模块B · 图形变形'} · ${escapeHtml(work.task.task_type)}
                        </div>
                        ${work.task.instruction ? `<p style="font-size:0.82rem; color:var(--primary-700); margin-top:6px;">${escapeHtml(work.task.instruction)}</p>` : ''}
                    </div>
                ` : ''}

                ${(work.prototype_tags?.length || work.transform_tags?.length) ? `
                    <div class="card" style="margin-bottom:12px;">
                        <div class="card-title">🏷️ 创作元素</div>
                        <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:8px;">
                            ${(work.prototype_tags || []).map(t => `<span style="font-size:0.8rem; background:var(--primary-50); color:var(--primary-600); padding:3px 10px; border-radius:12px;">${escapeHtml(typeof t === 'string' ? t : t.name || t)}</span>`).join('')}
                            ${(work.transform_tags || []).map(t => `<span style="font-size:0.8rem; background:var(--accent-50); color:var(--accent-600); padding:3px 10px; border-radius:12px;">✨ ${escapeHtml(typeof t === 'string' ? t : t.name || t)}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}

                ${hasEval ? `
                    <div class="card" style="background:linear-gradient(135deg, #FFF8F0, #FFF4EB); border-color:#E8C090; margin-bottom:12px;">
                        <div class="card-title">⭐ 作品评价</div>
                        <div style="margin-top:12px;">
                            ${dims.map(d => {
                                const score = work.evaluation[d.key] || 0;
                                const pct = Math.round(score * 10);
                                return `
                                <div style="margin-bottom:10px;">
                                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                        <span style="font-size:0.85rem; font-weight:600;">${d.icon} ${d.name}</span>
                                        <span style="font-size:0.9rem; font-weight:700; color:${d.color};">${score}</span>
                                    </div>
                                    <div style="background:#E0E0E0; border-radius:6px; height:6px; overflow:hidden;">
                                        <div style="background:${d.color}; height:100%; width:${pct}%; border-radius:6px; transition:width 0.5s;"></div>
                                    </div>
                                </div>`;
                            }).join('')}
                        </div>
                        <div style="text-align:center; margin-top:12px; padding-top:12px; border-top:1px solid #E8D4B8;">
                            <div style="font-size:2rem; font-weight:800; color:#D98B5F;">
                                ${((work.evaluation.originality + work.evaluation.detail + work.evaluation.composition + work.evaluation.expression) / 4).toFixed(1)}
                            </div>
                            <div style="font-size:0.75rem; color:#B88B60;">综合评分</div>
                        </div>
                        ${work.evaluation.feedback ? `
                            <div style="margin-top:12px; padding:10px; background:#fff; border-radius:10px; font-size:0.88rem; color:var(--gray-700); line-height:1.6;">
                                💬 ${escapeHtml(work.evaluation.feedback)}
                            </div>
                        ` : ''}
                    </div>
                ` : `
                    <div class="card" style="margin-bottom:12px;" id="eval-section">
                        <div class="card-title">⭐ 给作品打分</div>
                        <p style="font-size:0.82rem; color:var(--gray-500); margin-bottom:12px;">从4个维度为这幅作品打分（0-10分）</p>
                        ${dims.map(d => `
                            <div style="margin-bottom:14px;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                                    <div>
                                        <span style="font-weight:600; font-size:0.9rem;">${d.icon} ${d.name}</span>
                                        <span style="font-size:0.72rem; color:var(--gray-400); margin-left:4px;">${d.desc}</span>
                                    </div>
                                    <span><span id="score-label-${d.key}" style="font-size:1rem; font-weight:700; color:${d.color};">5</span><span style="font-size:0.75rem; color:var(--gray-400);">/10</span></span>
                                </div>
                                <input type="range" id="score-${d.key}" min="0" max="10" step="0.5" value="5"
                                    oninput="document.getElementById('score-label-${d.key}').textContent = this.value"
                                    style="width:100%; accent-color:${d.color};">
                            </div>
                        `).join('')}
                        <div class="form-group" style="margin-top:8px;">
                            <label class="form-label">💬 评语（选填）</label>
                            <textarea id="eval-feedback" class="form-input" rows="2" placeholder="写一句鼓励的话" style="resize:none;"></textarea>
                        </div>
                        <button class="btn btn-primary btn-large" data-action="evaluate-work" data-id="${work.id}">提交评价</button>
                    </div>
                `}

                <div style="display:flex; gap:10px; margin-top:12px;">
                    <button class="btn btn-outline" data-nav="upload-work" data-task-id="${work.task?.id || 0}" style="flex:1; font-size:0.85rem;">📷 再画一幅</button>
                    <button class="btn btn-outline" data-nav="gallery" style="flex:1; font-size:0.85rem;">🖼️ 回到展馆</button>
                </div>
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
        navigate("gallery");
    }
}

// ============================================================
// 推广中心
// ============================================================

const TX_TYPE_LABELS = {
    referral_signup: "推荐注册奖励",
    referral_l2_signup: "二级推荐奖励",
    welcome_bonus: "欢迎奖励",
    milestone_bonus: "里程碑奖励",
    admin_adjustment: "系统调整",
    course_purchase: "课程消费",
    merch_purchase: "文创消费",
    withdrawal: "提现",
};

async function renderReferralCenter(container) {
    try {
        const dash = await API.getReferralDashboard();
        const shareUrl = location.origin + "/?invite=" + dash.invite_code;

        container.innerHTML = `
            <div class="header">
                <h1>推广中心</h1>
                <div class="header-actions">
                    <button data-nav="parent-home" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                <!-- 学币余额卡片 -->
                <div class="card" style="background:linear-gradient(135deg, var(--primary-600), var(--primary-400)); color:#fff; text-align:center; padding:24px;">
                    <div style="font-size:0.8rem; opacity:0.85;">我的学币</div>
                    <div style="font-size:2.5rem; font-weight:800; margin:6px 0;">${dash.credit_balance}</div>
                    <div style="font-size:0.75rem; opacity:0.7;">累计获得 ${dash.total_earned} 学币</div>
                </div>

                <!-- 邀请码 -->
                <div class="card" style="text-align:center;">
                    <div style="font-size:0.85rem; color:var(--gray-500); margin-bottom:8px;">我的邀请码</div>
                    <div id="invite-code-display" style="font-size:2rem; font-weight:800; letter-spacing:6px; color:var(--primary-700); font-family:monospace; user-select:all; cursor:pointer;">${escapeHtml(dash.invite_code)}</div>
                    <div style="font-size:0.7rem; color:var(--gray-400); margin-top:4px;">点击复制</div>

                    <div style="margin-top:16px; display:flex; gap:10px; justify-content:center;">
                        <button data-action="copy-invite-code" data-code="${escapeAttr(dash.invite_code)}" class="btn btn-primary" style="font-size:0.85rem; padding:8px 20px;">
                            复制邀请码
                        </button>
                        <button data-action="copy-invite-link" data-link="${escapeAttr(shareUrl)}" class="btn btn-outline" style="font-size:0.85rem; padding:8px 20px;">
                            复制链接
                        </button>
                    </div>

                    ${navigator.share ? `
                        <button data-action="share-invite" data-code="${escapeAttr(dash.invite_code)}" data-link="${escapeAttr(shareUrl)}" class="btn btn-outline btn-large" style="margin-top:12px; font-size:0.85rem;">
                            分享给好友
                        </button>
                    ` : ""}
                </div>

                <!-- 推广数据 -->
                <div class="section-title">推广数据</div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                    <div class="card" style="text-align:center; padding:16px;">
                        <div style="font-size:1.5rem; font-weight:700; color:var(--primary-600);">${dash.total_referrals}</div>
                        <div style="font-size:0.75rem; color:var(--gray-500);">累计推荐</div>
                    </div>
                    <div class="card" style="text-align:center; padding:16px;">
                        <div style="font-size:1.5rem; font-weight:700; color:var(--accent-500);">${dash.monthly_referrals}</div>
                        <div style="font-size:0.75rem; color:var(--gray-500);">本月推荐</div>
                    </div>
                </div>

                ${dash.next_milestone ? `
                <div class="card" style="padding:14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size:0.85rem; font-weight:600;">下一个里程碑</span>
                        <span style="font-size:0.75rem; color:var(--accent-500);">+${dash.next_milestone.reward}学币</span>
                    </div>
                    <div style="background:var(--gray-100); border-radius:6px; height:8px; overflow:hidden;">
                        <div style="background:var(--primary-500); height:100%; width:${Math.round(dash.next_milestone.current / dash.next_milestone.target * 100)}%; border-radius:6px; transition:width 0.3s;"></div>
                    </div>
                    <div style="font-size:0.7rem; color:var(--gray-400); margin-top:4px;">已推荐 ${dash.next_milestone.current}/${dash.next_milestone.target} 人</div>
                </div>
                ` : ""}

                <!-- 快捷入口 -->
                <div style="display:flex; gap:10px; margin-top:8px;">
                    <button class="btn btn-outline" data-nav="referral-list" style="flex:1; font-size:0.85rem;">推荐记录</button>
                    <button class="btn btn-outline" data-nav="reward-history" style="flex:1; font-size:0.85rem;">学币明细</button>
                </div>

                <!-- 奖励说明 -->
                <div class="card" style="margin-top:16px; background:var(--gray-50);">
                    <div style="font-size:0.85rem; font-weight:600; margin-bottom:10px;">奖励规则</div>
                    <div style="font-size:0.78rem; color:var(--gray-600); line-height:1.8;">
                        <div>1. 邀请好友注册，您获得 <b>50学币</b>，好友获得 <b>30学币</b></div>
                        <div>2. 好友再邀请新用户，您额外获得 <b>10学币</b>（二级奖励）</div>
                        <div>3. 推荐达到5/10/25/50人可获里程碑奖励</div>
                        <div>4. 学币可用于兑换课程和文创产品</div>
                    </div>
                </div>
            </div>
        `;

        // 点击邀请码复制
        document.getElementById("invite-code-display")?.addEventListener("click", () => {
            navigator.clipboard?.writeText(dash.invite_code).then(() => showToast("邀请码已复制", "success"));
        });

    } catch (e) {
        showToast(e.message, "error");
        navigate("parent-home");
    }
}

async function renderReferralList(container) {
    try {
        const data = await API.getReferralList();
        container.innerHTML = `
            <div class="header">
                <h1>推荐记录</h1>
                <div class="header-actions">
                    <button data-nav="referral-center" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                ${data.items.length > 0 ? `
                    <div style="font-size:0.8rem; color:var(--gray-400); margin-bottom:12px;">共 ${data.total} 条记录</div>
                    ${data.items.map(r => `
                        <div class="card" style="padding:12px; display:flex; align-items:center; gap:12px;">
                            <div style="width:36px; height:36px; border-radius:50%; background:var(--primary-100); display:flex; align-items:center; justify-content:center; font-size:1rem;">👤</div>
                            <div style="flex:1;">
                                <div style="font-weight:600; font-size:0.9rem;">${escapeHtml(r.nickname || "用户")}</div>
                                <div style="font-size:0.7rem; color:var(--gray-400);">${escapeHtml(r.created_at || "").slice(0, 10)}</div>
                            </div>
                            <div style="font-size:0.75rem; color:var(--success-500);">+50学币</div>
                        </div>
                    `).join("")}
                ` : `
                    <div style="text-align:center; padding:40px;">
                        <div style="font-size:2.5rem; margin-bottom:12px;">📢</div>
                        <p style="color:var(--gray-500);">还没有推荐记录</p>
                        <p style="font-size:0.8rem; color:var(--gray-400); margin-top:4px;">分享邀请码给好友，一起加入绘创前程</p>
                    </div>
                `}
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
        navigate("referral-center");
    }
}

async function renderRewardHistory(container) {
    try {
        const balResp = await API.getCreditBalance();
        const data = await API.getRewardHistory();
        container.innerHTML = `
            <div class="header">
                <h1>学币明细</h1>
                <div class="header-subtitle">余额: ${balResp.credit_balance} 学币</div>
                <div class="header-actions">
                    <button data-nav="referral-center" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                ${data.items.length > 0 ? data.items.map(tx => `
                    <div class="card" style="padding:12px; display:flex; align-items:center; gap:12px;">
                        <div style="flex:1;">
                            <div style="font-size:0.85rem; font-weight:500;">${escapeHtml(tx.description || TX_TYPE_LABELS[tx.tx_type] || tx.tx_type)}</div>
                            <div style="font-size:0.7rem; color:var(--gray-400);">${escapeHtml(tx.created_at || "").slice(0, 16).replace("T", " ")}</div>
                        </div>
                        <div style="font-size:1rem; font-weight:700; color:${tx.amount > 0 ? 'var(--success-500)' : 'var(--error-500)'};">
                            ${tx.amount > 0 ? "+" : ""}${tx.amount}
                        </div>
                    </div>
                `).join("") : `
                    <div style="text-align:center; padding:40px;">
                        <div style="font-size:2.5rem; margin-bottom:12px;">💰</div>
                        <p style="color:var(--gray-500);">暂无学币记录</p>
                    </div>
                `}
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
        navigate("referral-center");
    }
}

// ============================================================
// 文创商城
// ============================================================

const MERCH_ICONS = {
    postcard: "💌", sticker: "🏷️", photobook: "📖",
    tshirt: "👕", mug: "☕", canvas: "🖼️", tote_bag: "👜",
};

async function renderMerchShop(container) {
    try {
        const resp = await API.getMerchTypes();
        const types = resp.merch_types || [];
        const balResp = await API.getCreditBalance();
        const balance = balResp.credit_balance || 0;

        container.innerHTML = `
            <div class="header">
                <h1>文创商城</h1>
                <div class="header-subtitle">学币余额: ${balance}</div>
                <div class="header-actions">
                    <button data-nav="parent-home" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                <div style="font-size:0.85rem; color:var(--gray-500); margin-bottom:16px;">
                    用孩子的画作定制专属文创产品，学币可抵扣
                </div>

                ${types.map(t => `
                    <div class="card" style="cursor:pointer;" data-nav="merch-detail" data-merch-id="${escapeAttr(t.id)}" data-merch-name="${escapeAttr(t.name_zh)}" data-merch-price="${t.base_price}">
                        <div style="display:flex; align-items:center; gap:14px;">
                            <div style="font-size:2.2rem;">${MERCH_ICONS[t.id] || "🎁"}</div>
                            <div style="flex:1;">
                                <div style="font-weight:700; font-size:1rem;">${escapeHtml(t.name_zh)}</div>
                                <div style="font-size:0.78rem; color:var(--gray-500); margin-top:2px;">${escapeHtml(t.description || "")}</div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-weight:700; color:var(--primary-600);">${escapeHtml(t.price_display)}</div>
                                <div style="font-size:0.65rem; color:var(--gray-400);">${t.base_price}学币可全额抵</div>
                            </div>
                        </div>
                    </div>
                `).join("")}

                <button class="btn btn-outline btn-large" data-nav="merch-orders" style="margin-top:16px;">
                    我的订单
                </button>
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
        navigate("parent-home");
    }
}

async function renderMerchDetail(container, params = {}) {
    const merchId = params.merchId || "";
    const merchName = params.merchName || "";
    const merchPrice = parseInt(params.merchPrice) || 0;
    const icon = MERCH_ICONS[merchId] || "🎁";

    try {
        // 获取家长的所有孩子
        const childResp = await API.getChildren();
        const children = childResp.children || [];
        const balResp = await API.getCreditBalance();
        const balance = balResp.credit_balance || 0;

        // 加载第一个孩子的作品（默认）
        let works = [];
        let selectedChildId = children.length > 0 ? children[0].id : null;
        if (selectedChildId) {
            const wResp = await API.request("GET", `/parent/child/${selectedChildId}/works?limit=50`);
            works = wResp.works || [];
        }

        const priceDisplay = merchPrice >= 100 ? `¥${(merchPrice / 100).toFixed(0)}` : `¥${(merchPrice / 100).toFixed(2)}`;

        container.innerHTML = `
            <div class="header">
                <h1>${icon} ${escapeHtml(merchName)}</h1>
                <div class="header-actions">
                    <button data-nav="merch-shop" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                <div class="card" style="margin-bottom:16px;">
                    <div style="font-size:1.1rem; font-weight:700; margin-bottom:8px;">${escapeHtml(merchName)}</div>
                    <div style="font-size:0.85rem; color:var(--gray-500); margin-bottom:8px;">价格: <strong style="color:var(--primary-600);">${priceDisplay}</strong></div>
                    <div style="font-size:0.78rem; color:var(--gray-400);">学币余额: ${balance}（可全额抵扣）</div>
                </div>

                ${children.length > 1 ? `
                    <div style="margin-bottom:16px;">
                        <label style="font-size:0.85rem; font-weight:600; display:block; margin-bottom:6px;">选择孩子</label>
                        <select id="merch-child-select" style="width:100%; padding:10px; border:1px solid var(--gray-300); border-radius:8px; font-size:0.9rem;">
                            ${children.map(c => `<option value="${c.id}" ${c.id === selectedChildId ? "selected" : ""}>${escapeHtml(c.nickname)}</option>`).join("")}
                        </select>
                    </div>
                ` : ""}

                <div style="font-size:0.9rem; font-weight:600; margin-bottom:10px;">选择作品（点击选中）</div>
                <div id="merch-works-grid" style="display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; margin-bottom:16px;">
                    ${works.length > 0 ? works.map(w => `
                        <div class="merch-work-item" data-work-id="${w.id}" style="cursor:pointer; border:2px solid var(--gray-200); border-radius:10px; overflow:hidden; position:relative;">
                            <img src="/api/works/image/${escapeAttr(w.image_url || '')}" alt="${escapeAttr(w.title || '')}" style="width:100%; aspect-ratio:1; object-fit:cover;">
                            <div style="font-size:0.7rem; padding:4px; text-align:center; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escapeHtml(w.title || "无标题")}</div>
                        </div>
                    `).join("") : '<div style="grid-column:1/-1; text-align:center; color:var(--gray-400); padding:20px;">暂无作品</div>'}
                </div>

                <div style="margin-bottom:16px;">
                    <label style="font-size:0.85rem; font-weight:600; display:block; margin-bottom:6px;">收货地址（选填）</label>
                    <input type="text" id="merch-address" class="form-input" placeholder="请输入收货地址" maxlength="200">
                </div>

                <div style="display:flex; align-items:center; gap:10px; margin-bottom:16px;">
                    <label style="font-size:0.85rem; font-weight:600;">使用学币抵扣</label>
                    <input type="number" id="merch-credits" class="form-input" style="width:100px;" value="0" min="0" max="${Math.min(balance, merchPrice)}">
                </div>

                <button id="merch-order-btn" class="btn btn-primary btn-large" style="width:100%;" disabled>
                    请先选择作品
                </button>
            </div>
        `;

        // 作品选中逻辑
        const selectedWorks = new Set();
        const grid = document.getElementById("merch-works-grid");
        const orderBtn = document.getElementById("merch-order-btn");

        grid?.addEventListener("click", (e) => {
            const item = e.target.closest(".merch-work-item");
            if (!item) return;
            const wid = parseInt(item.dataset.workId);
            if (selectedWorks.has(wid)) {
                selectedWorks.delete(wid);
                item.style.borderColor = "var(--gray-200)";
                item.querySelector("div[style*='position:absolute']")?.remove();
            } else {
                selectedWorks.add(wid);
                item.style.borderColor = "var(--primary-500)";
                const check = document.createElement("div");
                check.style.cssText = "position:absolute; top:4px; right:4px; background:var(--primary-500); color:#fff; border-radius:50%; width:22px; height:22px; display:flex; align-items:center; justify-content:center; font-size:0.75rem;";
                check.textContent = "✓";
                item.appendChild(check);
            }
            orderBtn.disabled = selectedWorks.size === 0;
            orderBtn.textContent = selectedWorks.size > 0 ? `立即定制（${selectedWorks.size}件作品）` : "请先选择作品";
        });

        // 切换孩子时重新加载作品
        document.getElementById("merch-child-select")?.addEventListener("change", async (e) => {
            const cid = parseInt(e.target.value);
            try {
                const wResp = await API.request("GET", `/parent/child/${cid}/works?limit=50`);
                const newWorks = wResp.works || [];
                selectedWorks.clear();
                orderBtn.disabled = true;
                orderBtn.textContent = "请先选择作品";
                grid.innerHTML = newWorks.length > 0 ? newWorks.map(w => `
                    <div class="merch-work-item" data-work-id="${w.id}" style="cursor:pointer; border:2px solid var(--gray-200); border-radius:10px; overflow:hidden; position:relative;">
                        <img src="/api/works/image/${escapeAttr(w.image_url || '')}" alt="${escapeAttr(w.title || '')}" style="width:100%; aspect-ratio:1; object-fit:cover;">
                        <div style="font-size:0.7rem; padding:4px; text-align:center; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escapeHtml(w.title || "无标题")}</div>
                    </div>
                `).join("") : '<div style="grid-column:1/-1; text-align:center; color:var(--gray-400); padding:20px;">暂无作品</div>';
            } catch (err) {
                showToast(err.message, "error");
            }
        });

        // 下单
        orderBtn?.addEventListener("click", async () => {
            if (selectedWorks.size === 0) return;
            orderBtn.disabled = true;
            orderBtn.textContent = "提交中...";
            try {
                const credits = parseInt(document.getElementById("merch-credits")?.value) || 0;
                const address = document.getElementById("merch-address")?.value?.trim() || "";
                const resp = await API.createMerchOrder({
                    merch_type_id: merchId,
                    work_ids: Array.from(selectedWorks),
                    use_credits: credits,
                    shipping_address: address,
                });
                showToast(`下单成功！${resp.amount_display}`, "success");
                navigate("merch-orders");
            } catch (err) {
                showToast(err.message, "error");
                orderBtn.disabled = false;
                orderBtn.textContent = `立即定制（${selectedWorks.size}件作品）`;
            }
        });

    } catch (e) {
        showToast(e.message, "error");
        navigate("merch-shop");
    }
}

async function renderMerchOrders(container) {
    try {
        const resp = await API.getMerchOrders();
        const orders = resp.orders || [];

        const statusLabels = {
            preview: "预览中", confirmed: "已确认", paid: "已支付",
            producing: "制作中", shipped: "已发货", completed: "已完成", cancelled: "已取消",
        };

        container.innerHTML = `
            <div class="header">
                <h1>我的订单</h1>
                <div class="header-actions">
                    <button data-nav="merch-shop" style="background:none; border:none; color:#fff; cursor:pointer;">返回</button>
                </div>
            </div>
            <div class="page">
                ${orders.length > 0 ? orders.map(o => `
                    <div class="card" style="padding:14px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <div style="font-weight:600;">${MERCH_ICONS[o.id] || "🎁"} ${escapeHtml(o.name_zh)}</div>
                                <div style="font-size:0.75rem; color:var(--gray-400); margin-top:4px;">${escapeHtml(o.created_at || "").slice(0, 10)}</div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-weight:700; color:var(--primary-600);">${escapeHtml(o.price_display)}</div>
                                <div style="font-size:0.75rem; color:var(--accent-500);">${statusLabels[o.status] || o.status}</div>
                            </div>
                        </div>
                    </div>
                `).join("") : `
                    <div style="text-align:center; padding:40px;">
                        <div style="font-size:2.5rem; margin-bottom:12px;">📦</div>
                        <p style="color:var(--gray-500);">还没有订单</p>
                        <button class="btn btn-primary" data-nav="merch-shop" style="margin-top:16px;">去逛逛</button>
                    </div>
                `}
            </div>
        `;
    } catch (e) {
        showToast(e.message, "error");
        navigate("merch-shop");
    }
}
