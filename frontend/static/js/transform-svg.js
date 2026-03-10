/**
 * 绘创前程 — 变形动作SVG可视化
 * 每种变形用"基础形 → 真实创作物"的方式直观展示
 * 展示的是孩子能创造的有趣东西：动物、植物、生活用品等
 */

const TransformSVG = {
    W: 220,
    H: 90,

    /**
     * 生成变形动作的"前→后"对比SVG（列表用）
     */
    generate(actionId) {
        const fn = this.visuals[actionId];
        if (!fn) return "";
        return `<svg viewBox="0 0 ${this.W} ${this.H}" width="100%" height="80" xmlns="http://www.w3.org/2000/svg" style="max-width:300px;">
            ${this._arrow()}
            ${fn()}
        </svg>`;
    },

    /**
     * 生成大尺寸演示SVG（任务详情页用）
     */
    generateLarge(actionId, shapeName) {
        const fn = this.details[actionId];
        if (!fn) return this.generate(actionId);
        return `<svg viewBox="0 0 280 130" width="100%" height="120" xmlns="http://www.w3.org/2000/svg" style="max-width:360px;">
            ${this._arrowLarge()}
            ${fn(shapeName)}
        </svg>`;
    },

    /**
     * 生成创意示例卡片SVG（展示可以创造什么）
     */
    generateExample(exampleId) {
        const fn = this.examples[exampleId];
        if (!fn) return "";
        return `<svg viewBox="0 0 80 80" width="70" height="70" xmlns="http://www.w3.org/2000/svg">
            ${fn()}
        </svg>`;
    },

    _arrow() {
        return `<defs><marker id="tArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#D98B5F"/></marker></defs>
        <path d="M82 45 L100 45" stroke="#D98B5F" stroke-width="2.5" fill="none" marker-end="url(#tArrow)"/>`;
    },

    _arrowLarge() {
        return `<defs><marker id="tArrowL" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#D98B5F"/></marker></defs>
        <path d="M105 65 L130 65" stroke="#D98B5F" stroke-width="2.5" fill="none" marker-end="url(#tArrowL)"/>`;
    },

    // ========================================
    // 列表页：基础形 → 有趣的真实物体
    // ========================================
    visuals: {
        // 拉长：圆 → 花瓶
        stretch() {
            return `
                <circle cx="45" cy="45" r="24" fill="#E8F5F1" stroke="#4E8D7C" stroke-width="2"/>
                <text x="45" y="49" text-anchor="middle" font-size="10" fill="#4E8D7C">圆</text>
                <!-- 花瓶 -->
                <path d="M145 20 Q135 20 132 30 Q128 45 138 55 L138 68 L162 68 L162 55 Q172 45 168 30 Q165 20 155 20 Z" fill="#FFF4EB" stroke="#D98B5F" stroke-width="2"/>
                <ellipse cx="150" cy="20" rx="10" ry="4" fill="#E8F5F1" stroke="#D98B5F" stroke-width="1.5"/>
                <path d="M142 35 Q150 30 158 35" fill="none" stroke="#4E8D7C" stroke-width="1" opacity="0.5"/>
                <path d="M140 45 Q150 40 160 45" fill="none" stroke="#4E8D7C" stroke-width="1" opacity="0.5"/>
                <text x="150" y="82" text-anchor="middle" font-size="8" fill="#D98B5F" font-weight="bold">花瓶!</text>
            `;
        },

        // 切分：方 → 巧克力块
        split() {
            return `
                <rect x="21" y="21" width="48" height="48" rx="4" fill="#E8F5F1" stroke="#4E8D7C" stroke-width="2"/>
                <text x="45" y="49" text-anchor="middle" font-size="10" fill="#4E8D7C">方</text>
                <!-- 巧克力块 -->
                <rect x="115" y="22" width="52" height="48" rx="4" fill="#8B6914" stroke="#5C4510" stroke-width="1.5"/>
                <line x1="132" y1="22" x2="132" y2="70" stroke="#5C4510" stroke-width="1"/>
                <line x1="150" y1="22" x2="150" y2="70" stroke="#5C4510" stroke-width="1"/>
                <line x1="115" y1="46" x2="167" y2="46" stroke="#5C4510" stroke-width="1"/>
                <rect x="118" y="25" width="11" height="18" rx="2" fill="#A07B20" opacity="0.4"/>
                <rect x="135" y="25" width="12" height="18" rx="2" fill="#A07B20" opacity="0.4"/>
                <rect x="153" y="25" width="11" height="18" rx="2" fill="#A07B20" opacity="0.4"/>
                <rect x="118" y="49" width="11" height="18" rx="2" fill="#A07B20" opacity="0.3"/>
                <rect x="135" y="49" width="12" height="18" rx="2" fill="#A07B20" opacity="0.3"/>
                <rect x="153" y="49" width="11" height="18" rx="2" fill="#A07B20" opacity="0.3"/>
                <text x="141" y="84" text-anchor="middle" font-size="8" fill="#D98B5F" font-weight="bold">巧克力!</text>
            `;
        },

        // 叠加：圆 → 雪人
        overlap() {
            return `
                <circle cx="35" cy="35" r="18" fill="#E8F5F1" stroke="#4E8D7C" stroke-width="2"/>
                <circle cx="58" cy="50" r="14" fill="none" stroke="#4E8D7C" stroke-width="2" stroke-dasharray="4 3"/>
                <text x="45" y="70" text-anchor="middle" font-size="8" fill="#616E7C">两个圆</text>
                <!-- 雪人 -->
                <circle cx="155" cy="55" r="20" fill="#F0F7FF" stroke="#89B4D4" stroke-width="2"/>
                <circle cx="155" cy="28" r="14" fill="#F0F7FF" stroke="#89B4D4" stroke-width="2"/>
                <circle cx="151" cy="25" r="2" fill="#2D2D2D"/>
                <circle cx="159" cy="25" r="2" fill="#2D2D2D"/>
                <path d="M152 31 L158 31" stroke="#D98B5F" stroke-width="1.5"/>
                <rect x="143" y="14" width="24" height="6" rx="3" fill="#D94444" stroke="#B33" stroke-width="1"/>
                <rect x="147" y="8" width="16" height="8" rx="2" fill="#D94444" stroke="#B33" stroke-width="1"/>
                <line x1="135" y1="55" x2="120" y2="48" stroke="#5C4510" stroke-width="2"/>
                <line x1="175" y1="55" x2="190" y2="48" stroke="#5C4510" stroke-width="2"/>
                <text x="155" y="82" text-anchor="middle" font-size="8" fill="#D98B5F" font-weight="bold">雪人!</text>
            `;
        },

        // 拼接：半圆+方 → 冰淇淋
        join() {
            return `
                <path d="M25 55 A18 18 0 0 1 61 55" fill="#E8F5F1" stroke="#4E8D7C" stroke-width="2"/>
                <polygon points="30,32 52,32 41,55" fill="none" stroke="#D98B5F" stroke-width="2"/>
                <text x="43" y="72" text-anchor="middle" font-size="7" fill="#616E7C">分开的</text>
                <!-- 冰淇淋 -->
                <path d="M135 40 A22 22 0 0 1 179 40" fill="#FFD4E8" stroke="#D98B5F" stroke-width="2"/>
                <path d="M135 40 A22 22 0 0 0 179 40" fill="#FFF4EB" stroke="#D98B5F" stroke-width="2"/>
                <circle cx="145" cy="30" r="8" fill="#FFE4CC" stroke="#D98B5F" stroke-width="1"/>
                <circle cx="157" cy="26" r="10" fill="#FFD4E8" stroke="#D98B5F" stroke-width="1"/>
                <circle cx="169" cy="30" r="8" fill="#E8F5F1" stroke="#4E8D7C" stroke-width="1"/>
                <polygon points="139,42 175,42 157,78" fill="#F5D080" stroke="#D98B5F" stroke-width="2"/>
                <line x1="143" y1="50" x2="157" y2="78" stroke="#E8C060" stroke-width="1"/>
                <line x1="171" y1="50" x2="157" y2="78" stroke="#E8C060" stroke-width="1"/>
                <text x="157" y="88" text-anchor="middle" font-size="8" fill="#D98B5F" font-weight="bold">冰淇淋!</text>
            `;
        },

        // 缺口与添加：圆 → 苹果（被咬了一口）
        notch_add() {
            return `
                <circle cx="45" cy="42" r="24" fill="#E8F5F1" stroke="#4E8D7C" stroke-width="2"/>
                <text x="45" y="46" text-anchor="middle" font-size="10" fill="#4E8D7C">圆</text>
                <!-- 苹果被咬一口 -->
                <path d="M155 22 A24 24 0 1 1 155 68 Q155 55 142 45 Q155 35 155 22 Z" fill="#FF6B6B" stroke="#CC4444" stroke-width="2"/>
                <path d="M153 22 Q158 10 165 18" fill="none" stroke="#4E8D7C" stroke-width="2"/>
                <ellipse cx="155" cy="15" rx="6" ry="4" fill="#4E8D7C" opacity="0.6"/>
                <path d="M140 40 Q138 45 140 50" fill="none" stroke="#FFF" stroke-width="1" opacity="0.4"/>
                <text x="155" y="82" text-anchor="middle" font-size="8" fill="#D98B5F" font-weight="bold">咬一口!</text>
            `;
        },

        // 延展：圆 → 章鱼
        extend() {
            return `
                <circle cx="45" cy="42" r="22" fill="#E8F5F1" stroke="#4E8D7C" stroke-width="2"/>
                <text x="45" y="46" text-anchor="middle" font-size="10" fill="#4E8D7C">圆</text>
                <!-- 章鱼 -->
                <ellipse cx="155" cy="35" rx="22" ry="18" fill="#E8D4F5" stroke="#9B6DBF" stroke-width="2"/>
                <circle cx="148" cy="32" r="4" fill="#FFF" stroke="#333" stroke-width="1"/>
                <circle cx="148" cy="33" r="2" fill="#333"/>
                <circle cx="162" cy="32" r="4" fill="#FFF" stroke="#333" stroke-width="1"/>
                <circle cx="162" cy="33" r="2" fill="#333"/>
                <path d="M150 40 Q155 44 160 40" fill="none" stroke="#9B6DBF" stroke-width="1.5"/>
                <path d="M133 48 Q125 65 120 72" fill="none" stroke="#9B6DBF" stroke-width="2.5" stroke-linecap="round"/>
                <path d="M140 50 Q135 68 132 75" fill="none" stroke="#9B6DBF" stroke-width="2.5" stroke-linecap="round"/>
                <path d="M150 52 Q150 70 148 78" fill="none" stroke="#9B6DBF" stroke-width="2.5" stroke-linecap="round"/>
                <path d="M160 52 Q162 70 165 78" fill="none" stroke="#9B6DBF" stroke-width="2.5" stroke-linecap="round"/>
                <path d="M170 50 Q175 68 178 75" fill="none" stroke="#9B6DBF" stroke-width="2.5" stroke-linecap="round"/>
                <path d="M177 48 Q185 65 190 72" fill="none" stroke="#9B6DBF" stroke-width="2.5" stroke-linecap="round"/>
                <text x="155" y="88" text-anchor="middle" font-size="7" fill="#D98B5F" font-weight="bold">章鱼!</text>
            `;
        },

        // 增加：圆 → 猫咪脸
        increase() {
            return `
                <circle cx="45" cy="42" r="24" fill="#E8F5F1" stroke="#4E8D7C" stroke-width="2"/>
                <text x="45" y="46" text-anchor="middle" font-size="10" fill="#4E8D7C">圆</text>
                <!-- 猫咪 -->
                <circle cx="155" cy="45" r="24" fill="#FFE8CC" stroke="#D98B5F" stroke-width="2"/>
                <polygon points="133,28 138,10 148,25" fill="#FFE8CC" stroke="#D98B5F" stroke-width="2"/>
                <polygon points="177,28 172,10 162,25" fill="#FFE8CC" stroke="#D98B5F" stroke-width="2"/>
                <polygon points="135,27 139,14 146,24" fill="#FFB8B8" stroke="none"/>
                <polygon points="175,27 171,14 164,24" fill="#FFB8B8" stroke="none"/>
                <circle cx="146" cy="40" r="3.5" fill="#4E8D7C"/>
                <circle cx="164" cy="40" r="3.5" fill="#4E8D7C"/>
                <circle cx="147" cy="39" r="1.2" fill="#FFF"/>
                <circle cx="165" cy="39" r="1.2" fill="#FFF"/>
                <ellipse cx="155" cy="48" rx="3" ry="2" fill="#FFB8B8"/>
                <path d="M152 50 Q155 54 158 50" fill="none" stroke="#D98B5F" stroke-width="1.5"/>
                <line x1="131" y1="42" x2="118" y2="38" stroke="#D98B5F" stroke-width="1"/>
                <line x1="131" y1="46" x2="118" y2="46" stroke="#D98B5F" stroke-width="1"/>
                <line x1="131" y1="50" x2="118" y2="54" stroke="#D98B5F" stroke-width="1"/>
                <line x1="179" y1="42" x2="192" y2="38" stroke="#D98B5F" stroke-width="1"/>
                <line x1="179" y1="46" x2="192" y2="46" stroke="#D98B5F" stroke-width="1"/>
                <line x1="179" y1="50" x2="192" y2="54" stroke="#D98B5F" stroke-width="1"/>
                <text x="155" y="80" text-anchor="middle" font-size="8" fill="#D98B5F" font-weight="bold">小猫!</text>
            `;
        },
    },

    // ========================================
    // 任务详情页：大尺寸演示
    // ========================================
    details: {
        stretch() {
            return `
                <text x="10" y="15" font-size="10" fill="#616E7C">基础形</text>
                <text x="160" y="15" font-size="10" fill="#D98B5F">拉长变成...</text>
                <circle cx="55" cy="75" r="32" fill="#E8F5F1" stroke="#4E8D7C" stroke-width="2"/>
                <path d="M165 40 Q155 38 150 50 Q145 70 155 85 L155 100 L185 100 L185 85 Q195 70 190 50 Q185 38 175 40 Z" fill="#FFF4EB" stroke="#D98B5F" stroke-width="2"/>
                <ellipse cx="170" cy="40" rx="12" ry="5" fill="#E8F5F1" stroke="#D98B5F" stroke-width="1.5"/>
                <path d="M158 58 Q170 52 182 58" fill="none" stroke="#4E8D7C" stroke-width="1" opacity="0.5"/>
                <path d="M156 72 Q170 66 184 72" fill="none" stroke="#4E8D7C" stroke-width="1" opacity="0.5"/>
                <text x="170" y="118" text-anchor="middle" font-size="11" fill="#D98B5F" font-weight="bold">花瓶~</text>
            `;
        },
        split() {
            return `
                <text x="10" y="15" font-size="10" fill="#616E7C">一整块</text>
                <text x="160" y="15" font-size="10" fill="#D98B5F">切成好多块</text>
                <rect x="20" y="35" width="60" height="60" rx="4" fill="#E8F5F1" stroke="#4E8D7C" stroke-width="2"/>
                <rect x="140" y="30" width="65" height="55" rx="4" fill="#8B6914" stroke="#5C4510" stroke-width="2"/>
                <line x1="162" y1="30" x2="162" y2="85" stroke="#5C4510" stroke-width="1"/>
                <line x1="183" y1="30" x2="183" y2="85" stroke="#5C4510" stroke-width="1"/>
                <line x1="140" y1="57" x2="205" y2="57" stroke="#5C4510" stroke-width="1"/>
                <text x="172" y="118" text-anchor="middle" font-size="11" fill="#D98B5F" font-weight="bold">巧克力~</text>
            `;
        },
    },

    // ========================================
    // 创意示例小图标（用于展示"可以变成什么"）
    // ========================================
    examples: {
        // 拉长类
        vase() {
            return `<path d="M40 15 Q30 15 27 25 Q23 40 33 50 L33 65 L47 65 L47 50 Q57 40 53 25 Q50 15 40 15 Z" fill="#FFF4EB" stroke="#D98B5F" stroke-width="2"/><ellipse cx="40" cy="15" rx="10" ry="4" fill="#E8F5F1" stroke="#D98B5F" stroke-width="1.5"/>`;
        },
        giraffe() {
            return `<ellipse cx="40" cy="55" rx="16" ry="12" fill="#F5D080" stroke="#D98B5F" stroke-width="2"/><rect x="36" y="15" width="8" height="35" rx="3" fill="#F5D080" stroke="#D98B5F" stroke-width="2"/><circle cx="40" cy="14" r="8" fill="#F5D080" stroke="#D98B5F" stroke-width="2"/><circle cx="38" cy="12" r="1.5" fill="#333"/><circle cx="43" cy="12" r="1.5" fill="#333"/><line x1="38" y1="6" x2="36" y2="2" stroke="#D98B5F" stroke-width="1.5"/><line x1="42" y1="6" x2="44" y2="2" stroke="#D98B5F" stroke-width="1.5"/>`;
        },
        building() {
            return `<rect x="20" y="20" width="40" height="55" rx="2" fill="#E8F5F1" stroke="#4E8D7C" stroke-width="2"/><rect x="28" y="28" width="8" height="8" rx="1" fill="#FFF4EB" stroke="#D98B5F" stroke-width="1"/><rect x="44" y="28" width="8" height="8" rx="1" fill="#FFF4EB" stroke="#D98B5F" stroke-width="1"/><rect x="28" y="44" width="8" height="8" rx="1" fill="#FFF4EB" stroke="#D98B5F" stroke-width="1"/><rect x="44" y="44" width="8" height="8" rx="1" fill="#FFF4EB" stroke="#D98B5F" stroke-width="1"/><rect x="35" y="58" width="10" height="17" rx="1" fill="#D98B5F" stroke="#8B5A2B" stroke-width="1"/>`;
        },
        // 切分类
        pizza() {
            return `<circle cx="40" cy="40" r="28" fill="#F5D080" stroke="#D98B5F" stroke-width="2"/><line x1="40" y1="12" x2="40" y2="68" stroke="#CC8844" stroke-width="1.5"/><line x1="12" y1="40" x2="68" y2="40" stroke="#CC8844" stroke-width="1.5"/><circle cx="30" cy="30" r="3" fill="#CC4444"/><circle cx="50" cy="35" r="3" fill="#CC4444"/><circle cx="35" cy="52" r="3" fill="#CC4444"/><circle cx="52" cy="50" r="2.5" fill="#CC4444"/>`;
        },
        orange() {
            return `<circle cx="40" cy="40" r="26" fill="#FFA040" stroke="#CC7722" stroke-width="2"/><path d="M40 14 L40 66" stroke="#CC7722" stroke-width="1" opacity="0.5"/><path d="M14 40 L66 40" stroke="#CC7722" stroke-width="1" opacity="0.5"/><path d="M22 22 L58 58" stroke="#CC7722" stroke-width="1" opacity="0.5"/><path d="M58 22 L22 58" stroke="#CC7722" stroke-width="1" opacity="0.5"/><circle cx="40" cy="40" r="5" fill="#FFCC66"/>`;
        },
        // 叠加类
        snowman() {
            return `<circle cx="40" cy="55" r="18" fill="#F0F7FF" stroke="#89B4D4" stroke-width="2"/><circle cx="40" cy="30" r="12" fill="#F0F7FF" stroke="#89B4D4" stroke-width="2"/><circle cx="36" cy="28" r="2" fill="#333"/><circle cx="44" cy="28" r="2" fill="#333"/><path d="M37 34 L43 34" stroke="#D98B5F" stroke-width="1.5"/>`;
        },
        caterpillar() {
            return `<circle cx="18" cy="45" r="10" fill="#88CC66" stroke="#4E8D7C" stroke-width="2"/><circle cx="33" cy="40" r="10" fill="#88CC66" stroke="#4E8D7C" stroke-width="2"/><circle cx="48" cy="38" r="10" fill="#88CC66" stroke="#4E8D7C" stroke-width="2"/><circle cx="63" cy="40" r="12" fill="#AADD88" stroke="#4E8D7C" stroke-width="2"/><circle cx="59" cy="37" r="2.5" fill="#333"/><circle cx="67" cy="37" r="2.5" fill="#333"/><path d="M60 44 Q63 47 67 44" fill="none" stroke="#333" stroke-width="1.5"/><line x1="58" y1="28" x2="55" y2="20" stroke="#4E8D7C" stroke-width="1.5"/><line x1="68" y1="28" x2="71" y2="20" stroke="#4E8D7C" stroke-width="1.5"/>`;
        },
        // 拼接类
        icecream() {
            return `<circle cx="32" cy="22" r="10" fill="#FFD4E8" stroke="#D98B5F" stroke-width="1.5"/><circle cx="48" cy="22" r="10" fill="#FFF4EB" stroke="#D98B5F" stroke-width="1.5"/><circle cx="40" cy="15" r="10" fill="#E8F5F1" stroke="#4E8D7C" stroke-width="1.5"/><polygon points="28,28 52,28 40,70" fill="#F5D080" stroke="#D98B5F" stroke-width="2"/><line x1="32" y1="38" x2="40" y2="70" stroke="#E8C060" stroke-width="1"/><line x1="48" y1="38" x2="40" y2="70" stroke="#E8C060" stroke-width="1"/>`;
        },
        robot() {
            return `<rect x="25" y="15" width="30" height="25" rx="4" fill="#89B4D4" stroke="#5588AA" stroke-width="2"/><rect x="30" y="42" width="20" height="22" rx="2" fill="#89B4D4" stroke="#5588AA" stroke-width="2"/><rect x="18" y="42" width="8" height="16" rx="3" fill="#D98B5F" stroke="#8B5A2B" stroke-width="1.5"/><rect x="54" y="42" width="8" height="16" rx="3" fill="#D98B5F" stroke="#8B5A2B" stroke-width="1.5"/><circle cx="35" cy="25" r="4" fill="#FFF" stroke="#333" stroke-width="1"/><circle cx="45" cy="25" r="4" fill="#FFF" stroke="#333" stroke-width="1"/><circle cx="35" cy="26" r="2" fill="#333"/><circle cx="45" cy="26" r="2" fill="#333"/><rect x="34" y="33" width="12" height="3" rx="1" fill="#333"/>`;
        },
        // 缺口类
        apple() {
            return `<path d="M42 18 A22 22 0 1 1 42 64 Q42 50 32 40 Q42 30 42 18 Z" fill="#FF6B6B" stroke="#CC4444" stroke-width="2"/><path d="M40 18 Q44 8 50 14" fill="none" stroke="#4E8D7C" stroke-width="2"/><ellipse cx="43" cy="13" rx="5" ry="3" fill="#4E8D7C" opacity="0.6"/>`;
        },
        cup() {
            return `<rect x="18" y="20" width="38" height="40" rx="4" fill="#E8F5F1" stroke="#4E8D7C" stroke-width="2"/><path d="M56 28 Q70 28 70 40 Q70 52 56 52" fill="none" stroke="#4E8D7C" stroke-width="2"/><rect x="18" y="14" width="38" height="8" rx="3" fill="#FFF4EB" stroke="#D98B5F" stroke-width="1.5"/>`;
        },
        // 延展类
        octopus() {
            return `<ellipse cx="40" cy="28" rx="20" ry="16" fill="#E8D4F5" stroke="#9B6DBF" stroke-width="2"/><circle cx="34" cy="25" r="3.5" fill="#FFF" stroke="#333" stroke-width="1"/><circle cx="34" cy="26" r="1.8" fill="#333"/><circle cx="46" cy="25" r="3.5" fill="#FFF" stroke="#333" stroke-width="1"/><circle cx="46" cy="26" r="1.8" fill="#333"/><path d="M36 34 Q40 37 44 34" fill="none" stroke="#9B6DBF" stroke-width="1.5"/><path d="M22 40 Q15 55 12 62" fill="none" stroke="#9B6DBF" stroke-width="2.5" stroke-linecap="round"/><path d="M28 42 Q24 58 22 66" fill="none" stroke="#9B6DBF" stroke-width="2.5" stroke-linecap="round"/><path d="M40 44 Q40 60 40 68" fill="none" stroke="#9B6DBF" stroke-width="2.5" stroke-linecap="round"/><path d="M52 42 Q56 58 58 66" fill="none" stroke="#9B6DBF" stroke-width="2.5" stroke-linecap="round"/><path d="M58 40 Q65 55 68 62" fill="none" stroke="#9B6DBF" stroke-width="2.5" stroke-linecap="round"/>`;
        },
        sun() {
            return `<circle cx="40" cy="40" r="16" fill="#FFD060" stroke="#D98B5F" stroke-width="2"/><line x1="40" y1="20" x2="40" y2="8" stroke="#D98B5F" stroke-width="2.5"/><line x1="40" y1="60" x2="40" y2="72" stroke="#D98B5F" stroke-width="2.5"/><line x1="20" y1="40" x2="8" y2="40" stroke="#D98B5F" stroke-width="2.5"/><line x1="60" y1="40" x2="72" y2="40" stroke="#D98B5F" stroke-width="2.5"/><line x1="26" y1="26" x2="17" y2="17" stroke="#D98B5F" stroke-width="2"/><line x1="54" y1="26" x2="63" y2="17" stroke="#D98B5F" stroke-width="2"/><line x1="26" y1="54" x2="17" y2="63" stroke="#D98B5F" stroke-width="2"/><line x1="54" y1="54" x2="63" y2="63" stroke="#D98B5F" stroke-width="2"/>`;
        },
        flower() {
            return `<circle cx="40" cy="40" r="8" fill="#FFD060" stroke="#D98B5F" stroke-width="1.5"/><ellipse cx="40" cy="22" rx="8" ry="12" fill="#FFB8B8" stroke="#D98B5F" stroke-width="1.5"/><ellipse cx="40" cy="58" rx="8" ry="12" fill="#FFB8B8" stroke="#D98B5F" stroke-width="1.5"/><ellipse cx="22" cy="40" rx="12" ry="8" fill="#FFB8B8" stroke="#D98B5F" stroke-width="1.5"/><ellipse cx="58" cy="40" rx="12" ry="8" fill="#FFB8B8" stroke="#D98B5F" stroke-width="1.5"/><line x1="40" y1="70" x2="40" y2="78" stroke="#4E8D7C" stroke-width="2"/>`;
        },
        // 增加类
        cat() {
            return `<circle cx="40" cy="42" r="22" fill="#FFE8CC" stroke="#D98B5F" stroke-width="2"/><polygon points="20,26 25,6 34,22" fill="#FFE8CC" stroke="#D98B5F" stroke-width="2"/><polygon points="60,26 55,6 46,22" fill="#FFE8CC" stroke="#D98B5F" stroke-width="2"/><polygon points="22,25 26,10 32,21" fill="#FFB8B8" stroke="none"/><polygon points="58,25 54,10 48,21" fill="#FFB8B8" stroke="none"/><circle cx="33" cy="38" r="3.5" fill="#4E8D7C"/><circle cx="47" cy="38" r="3.5" fill="#4E8D7C"/><circle cx="34" cy="37" r="1.2" fill="#FFF"/><circle cx="48" cy="37" r="1.2" fill="#FFF"/><ellipse cx="40" cy="46" rx="3" ry="2" fill="#FFB8B8"/><path d="M37 48 Q40 52 43 48" fill="none" stroke="#D98B5F" stroke-width="1.5"/>`;
        },
        house() {
            return `<rect x="18" y="38" width="44" height="35" rx="2" fill="#FFF4EB" stroke="#D98B5F" stroke-width="2"/><polygon points="14,40 40,12 66,40" fill="#CC4444" stroke="#AA3333" stroke-width="2"/><rect x="33" y="52" width="14" height="21" rx="1" fill="#8B5A2B" stroke="#5C3A10" stroke-width="1.5"/><circle cx="44" cy="62" r="1.5" fill="#FFD060"/><rect x="24" y="44" width="8" height="8" rx="1" fill="#89B4D4" stroke="#5588AA" stroke-width="1"/><rect x="48" y="44" width="8" height="8" rx="1" fill="#89B4D4" stroke="#5588AA" stroke-width="1"/>`;
        },
        fish() {
            return `<ellipse cx="38" cy="40" rx="22" ry="14" fill="#89B4D4" stroke="#5588AA" stroke-width="2"/><polygon points="58,40 72,28 72,52" fill="#89B4D4" stroke="#5588AA" stroke-width="2"/><circle cx="28" cy="37" r="4" fill="#FFF" stroke="#333" stroke-width="1"/><circle cx="29" cy="37" r="2" fill="#333"/><path d="M20 48 Q30 52 40 48" fill="none" stroke="#5588AA" stroke-width="1.5"/><path d="M38 30 Q42 26 48 30" fill="none" stroke="#FFD060" stroke-width="1.5"/>`;
        },
    },
};

/**
 * 每种变形动作对应的"可以创造什么"列表
 * 用于在变形库页面展示丰富的创作可能性
 */
TransformSVG.creationMap = {
    stretch: [
        { id: "vase", name: "花瓶", desc: "把圆拉长变成优雅的花瓶" },
        { id: "giraffe", name: "长颈鹿", desc: "把方形拉高变成长脖子" },
        { id: "building", name: "高楼", desc: "把方形往上拉成大楼" },
    ],
    split: [
        { id: "pizza", name: "比萨饼", desc: "圆形切成好多片" },
        { id: "orange", name: "橙子", desc: "圆形切开看到瓣" },
    ],
    overlap: [
        { id: "snowman", name: "雪人", desc: "大圆小圆叠在一起" },
        { id: "caterpillar", name: "毛毛虫", desc: "好多圆叠成一排" },
    ],
    join: [
        { id: "icecream", name: "冰淇淋", desc: "圆+三角拼成甜筒" },
        { id: "robot", name: "机器人", desc: "方形拼成身体" },
    ],
    notch_add: [
        { id: "apple", name: "苹果", desc: "圆挖一口变苹果" },
        { id: "cup", name: "杯子", desc: "方形挖空+把手" },
    ],
    extend: [
        { id: "octopus", name: "章鱼", desc: "圆往外长出触手" },
        { id: "sun", name: "太阳", desc: "圆往外长出光芒" },
        { id: "flower", name: "花朵", desc: "圆往外长出花瓣" },
    ],
    increase: [
        { id: "cat", name: "小猫", desc: "圆+眼睛耳朵胡须" },
        { id: "house", name: "房子", desc: "方+门窗屋顶" },
        { id: "fish", name: "小鱼", desc: "椭圆+眼睛尾巴鳞片" },
    ],
};
