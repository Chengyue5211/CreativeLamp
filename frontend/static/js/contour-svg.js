/**
 * 绘创前程 — 轮廓图形库
 * 丰富的动物、植物、生活用品等轮廓图
 * 用于：
 *   模块A — 轮廓装饰任务（孩子用线条原型装饰轮廓内部）
 *   模块B — 变形起点/目标参考
 *   打印底稿 — 下载打印后在纸上画
 */

const ContourSVG = {
    // 所有轮廓分类
    categories: {
        animals: { name: "动物", icon: "🐱", color: "#FFE8CC" },
        plants:  { name: "植物", icon: "🌸", color: "#E8F5F1" },
        objects: { name: "生活用品", icon: "🏠", color: "#F0F7FF" },
        food:    { name: "美食", icon: "🍰", color: "#FFF4EB" },
        fantasy: { name: "奇幻", icon: "🦄", color: "#E8D4F5" },
        vehicles:{ name: "交通工具", icon: "🚗", color: "#F0F7FF" },
    },

    /**
     * 获取所有轮廓图形列表
     */
    getAll() {
        return Object.entries(this.library).map(([id, item]) => ({
            id,
            ...item,
            categoryInfo: this.categories[item.category] || {},
        }));
    },

    /**
     * 按分类获取
     */
    getByCategory(cat) {
        return this.getAll().filter(c => c.category === cat);
    },

    /**
     * 生成轮廓SVG（用于列表展示，小尺寸）
     */
    generate(contourId) {
        const item = this.library[contourId];
        if (!item || !item.svg) return "";
        return `<svg viewBox="0 0 100 100" width="80" height="80" xmlns="http://www.w3.org/2000/svg" style="max-width:100px;">
            ${item.svg()}
        </svg>`;
    },

    /**
     * 生成打印用大尺寸轮廓（纯黑白，适合打印）
     */
    generatePrint(contourId) {
        const item = this.library[contourId];
        if (!item || !item.printSvg) {
            // 回退到普通SVG但放大
            if (!item || !item.svg) return "";
            return `<svg viewBox="0 0 100 100" width="400" height="400" xmlns="http://www.w3.org/2000/svg">
                ${item.svg()}
            </svg>`;
        }
        return `<svg viewBox="0 0 200 200" width="500" height="500" xmlns="http://www.w3.org/2000/svg">
            ${item.printSvg()}
        </svg>`;
    },

    // ========================================
    // 轮廓图形库
    // ========================================
    library: {
        // ============ 动物类 ============
        cat: {
            category: "animals",
            name: "小猫",
            difficulty: 1,
            description: "可爱的小猫咪轮廓，可以用各种线条装饰它的毛发和花纹",
            svg() {
                return `
                    <circle cx="50" cy="52" r="28" fill="none" stroke="#333" stroke-width="2"/>
                    <polygon points="24,30 30,8 40,26" fill="none" stroke="#333" stroke-width="2"/>
                    <polygon points="76,30 70,8 60,26" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="40" cy="46" r="4" fill="none" stroke="#333" stroke-width="1.5"/>
                    <circle cx="60" cy="46" r="4" fill="none" stroke="#333" stroke-width="1.5"/>
                    <ellipse cx="50" cy="56" rx="3" ry="2" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M47 58 Q50 62 53 58" fill="none" stroke="#333" stroke-width="1.5"/>
                    <line x1="22" y1="50" x2="8" y2="46" stroke="#333" stroke-width="1"/>
                    <line x1="22" y1="54" x2="8" y2="54" stroke="#333" stroke-width="1"/>
                    <line x1="22" y1="58" x2="8" y2="62" stroke="#333" stroke-width="1"/>
                    <line x1="78" y1="50" x2="92" y2="46" stroke="#333" stroke-width="1"/>
                    <line x1="78" y1="54" x2="92" y2="54" stroke="#333" stroke-width="1"/>
                    <line x1="78" y1="58" x2="92" y2="62" stroke="#333" stroke-width="1"/>
                `;
            },
        },

        butterfly: {
            category: "animals",
            name: "蝴蝶",
            difficulty: 2,
            description: "展翅的蝴蝶，翅膀里可以装饰各种花纹",
            svg() {
                return `
                    <path d="M50 30 Q25 10 15 35 Q10 55 35 55 Q45 55 50 50" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M50 30 Q75 10 85 35 Q90 55 65 55 Q55 55 50 50" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M50 50 Q35 60 30 75 Q28 85 42 80 Q48 76 50 65" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M50 50 Q65 60 70 75 Q72 85 58 80 Q52 76 50 65" fill="none" stroke="#333" stroke-width="2"/>
                    <line x1="50" y1="30" x2="50" y2="85" stroke="#333" stroke-width="2"/>
                    <circle cx="46" cy="26" r="2" fill="none" stroke="#333" stroke-width="1.5"/>
                    <circle cx="54" cy="26" r="2" fill="none" stroke="#333" stroke-width="1.5"/>
                    <line x1="46" y1="26" x2="42" y2="18" stroke="#333" stroke-width="1"/>
                    <line x1="54" y1="26" x2="58" y2="18" stroke="#333" stroke-width="1"/>
                `;
            },
        },

        fish: {
            category: "animals",
            name: "小鱼",
            difficulty: 1,
            description: "一条游动的小鱼，给它画上鳞片和花纹吧",
            svg() {
                return `
                    <ellipse cx="45" cy="50" rx="28" ry="18" fill="none" stroke="#333" stroke-width="2"/>
                    <polygon points="70,50 90,35 90,65" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="32" cy="46" r="4" fill="none" stroke="#333" stroke-width="1.5"/>
                    <circle cx="33" cy="45" r="1.5" fill="#333"/>
                    <path d="M25 58 Q35 64 50 58" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M45 32 Q50 26 56 32" fill="none" stroke="#333" stroke-width="1"/>
                    <line x1="55" y1="38" x2="55" y2="62" stroke="#333" stroke-width="1" stroke-dasharray="2 3"/>
                `;
            },
        },

        bird: {
            category: "animals",
            name: "小鸟",
            difficulty: 2,
            description: "一只可爱的小鸟，装饰它的羽毛",
            svg() {
                return `
                    <ellipse cx="50" cy="55" rx="22" ry="18" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="50" cy="32" r="14" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="45" cy="30" r="3" fill="none" stroke="#333" stroke-width="1.5"/>
                    <circle cx="45" cy="29" r="1.2" fill="#333"/>
                    <polygon points="58,30 72,28 62,34" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M28 55 Q15 48 10 60" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M72 55 Q85 48 90 60" fill="none" stroke="#333" stroke-width="2"/>
                    <line x1="42" y1="73" x2="42" y2="88" stroke="#333" stroke-width="2"/>
                    <line x1="58" y1="73" x2="58" y2="88" stroke="#333" stroke-width="2"/>
                    <path d="M36 88 L48 88" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M52 88 L64 88" fill="none" stroke="#333" stroke-width="2"/>
                `;
            },
        },

        elephant: {
            category: "animals",
            name: "大象",
            difficulty: 3,
            description: "一只大象的轮廓，大大的身体和长鼻子",
            svg() {
                return `
                    <ellipse cx="50" cy="50" rx="30" ry="24" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="28" cy="32" r="14" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M18 38 Q12 50 14 65 Q16 72 22 68" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="24" cy="30" r="3" fill="none" stroke="#333" stroke-width="1.5"/>
                    <circle cx="24" cy="29" r="1.2" fill="#333"/>
                    <path d="M16 25 Q8 20 6 30 Q4 38 14 36" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M40 25 Q48 18 56 22" fill="none" stroke="#333" stroke-width="1.5"/>
                    <line x1="35" y1="74" x2="35" y2="92" stroke="#333" stroke-width="2.5"/>
                    <line x1="50" y1="74" x2="50" y2="92" stroke="#333" stroke-width="2.5"/>
                    <line x1="65" y1="74" x2="65" y2="92" stroke="#333" stroke-width="2.5"/>
                    <path d="M72 45 Q82 42 78 52" fill="none" stroke="#333" stroke-width="1.5"/>
                `;
            },
        },

        turtle: {
            category: "animals",
            name: "乌龟",
            difficulty: 2,
            description: "一只小乌龟，龟壳上可以画出美丽的花纹",
            svg() {
                return `
                    <ellipse cx="50" cy="52" rx="28" ry="20" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M22 52 Q10 52 8 46 Q6 38 14 38" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="11" cy="40" r="2" fill="none" stroke="#333" stroke-width="1"/>
                    <path d="M28 68 L22 80" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M72 68 L78 80" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M78 52 Q86 52 84 60" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M36 52 L50 36 L64 52" fill="none" stroke="#333" stroke-width="1" stroke-dasharray="2 2"/>
                    <line x1="50" y1="52" x2="50" y2="72" stroke="#333" stroke-width="1" stroke-dasharray="2 2"/>
                    <line x1="30" y1="52" x2="70" y2="52" stroke="#333" stroke-width="1" stroke-dasharray="2 2"/>
                `;
            },
        },

        rabbit: {
            category: "animals",
            name: "兔子",
            difficulty: 1,
            description: "一只小兔子，大耳朵圆身体",
            svg() {
                return `
                    <ellipse cx="50" cy="58" rx="22" ry="20" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="50" cy="34" r="14" fill="none" stroke="#333" stroke-width="2"/>
                    <ellipse cx="42" cy="14" rx="5" ry="16" fill="none" stroke="#333" stroke-width="2"/>
                    <ellipse cx="58" cy="14" rx="5" ry="16" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="44" cy="32" r="3" fill="none" stroke="#333" stroke-width="1.5"/>
                    <circle cx="56" cy="32" r="3" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M48 38 L50 40 L52 38" fill="none" stroke="#333" stroke-width="1.5"/>
                    <circle cx="70" cy="60" r="5" fill="none" stroke="#333" stroke-width="1.5"/>
                `;
            },
        },

        snail: {
            category: "animals",
            name: "蜗牛",
            difficulty: 2,
            description: "一只蜗牛，螺旋形的壳特别适合装饰",
            svg() {
                return `
                    <path d="M20 70 Q30 60 50 60 Q70 60 75 70 Q80 80 50 82 Q20 84 20 70" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="55" cy="42" r="20" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M55 60 Q55 50 50 42 Q45 35 50 30 Q55 25 58 30 Q62 35 58 40" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M25 60 Q20 50 18 45" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="16" cy="42" r="3" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M32 60 Q28 52 30 45" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="31" cy="42" r="3" fill="none" stroke="#333" stroke-width="1.5"/>
                `;
            },
        },

        // ============ 植物类 ============
        flower_simple: {
            category: "plants",
            name: "花朵",
            difficulty: 1,
            description: "一朵五瓣花，每片花瓣都可以画不同的花纹",
            svg() {
                return `
                    <circle cx="50" cy="42" r="10" fill="none" stroke="#333" stroke-width="2"/>
                    <ellipse cx="50" cy="24" rx="10" ry="14" fill="none" stroke="#333" stroke-width="1.5"/>
                    <ellipse cx="50" cy="60" rx="10" ry="14" fill="none" stroke="#333" stroke-width="1.5"/>
                    <ellipse cx="33" cy="35" rx="14" ry="10" fill="none" stroke="#333" stroke-width="1.5"/>
                    <ellipse cx="67" cy="35" rx="14" ry="10" fill="none" stroke="#333" stroke-width="1.5"/>
                    <ellipse cx="36" cy="55" rx="12" ry="10" fill="none" stroke="#333" stroke-width="1.5" transform="rotate(-30,36,55)"/>
                    <ellipse cx="64" cy="55" rx="12" ry="10" fill="none" stroke="#333" stroke-width="1.5" transform="rotate(30,64,55)"/>
                    <line x1="50" y1="74" x2="50" y2="95" stroke="#333" stroke-width="2"/>
                    <path d="M50 80 Q40 76 35 82" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M50 86 Q60 82 65 88" fill="none" stroke="#333" stroke-width="1.5"/>
                `;
            },
        },

        tree: {
            category: "plants",
            name: "大树",
            difficulty: 2,
            description: "一棵大树，树冠里可以画出丰富的叶子纹理",
            svg() {
                return `
                    <path d="M20 65 Q15 30 50 15 Q85 30 80 65 Q65 70 50 68 Q35 70 20 65" fill="none" stroke="#333" stroke-width="2"/>
                    <rect x="42" y="65" width="16" height="28" rx="2" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M42 75 Q30 78 25 85" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M58 75 Q70 78 75 85" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M35 40 Q50 35 65 40" fill="none" stroke="#333" stroke-width="1" stroke-dasharray="3 3"/>
                    <path d="M28 52 Q50 46 72 52" fill="none" stroke="#333" stroke-width="1" stroke-dasharray="3 3"/>
                `;
            },
        },

        cactus: {
            category: "plants",
            name: "仙人掌",
            difficulty: 1,
            description: "一棵仙人掌，身上可以画刺和花纹",
            svg() {
                return `
                    <rect x="38" y="25" width="24" height="55" rx="12" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M38 50 Q28 48 24 38 Q20 28 28 28" fill="none" stroke="#333" stroke-width="2"/>
                    <rect x="22" y="26" width="10" height="26" rx="5" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M62 44 Q72 42 76 34 Q80 24 72 24" fill="none" stroke="#333" stroke-width="2"/>
                    <rect x="68" y="22" width="10" height="24" rx="5" fill="none" stroke="#333" stroke-width="2"/>
                    <ellipse cx="50" cy="22" rx="6" ry="5" fill="none" stroke="#333" stroke-width="1.5"/>
                    <line x1="38" y1="80" x2="62" y2="80" stroke="#333" stroke-width="2"/>
                `;
            },
        },

        leaf: {
            category: "plants",
            name: "树叶",
            difficulty: 1,
            description: "一片大树叶，叶脉上可以画各种线条",
            svg() {
                return `
                    <path d="M50 10 Q20 30 18 55 Q16 75 50 90 Q84 75 82 55 Q80 30 50 10" fill="none" stroke="#333" stroke-width="2"/>
                    <line x1="50" y1="15" x2="50" y2="88" stroke="#333" stroke-width="1.5"/>
                    <path d="M50 30 Q35 35 25 45" fill="none" stroke="#333" stroke-width="1"/>
                    <path d="M50 30 Q65 35 75 45" fill="none" stroke="#333" stroke-width="1"/>
                    <path d="M50 48 Q38 52 28 60" fill="none" stroke="#333" stroke-width="1"/>
                    <path d="M50 48 Q62 52 72 60" fill="none" stroke="#333" stroke-width="1"/>
                    <path d="M50 65 Q42 68 34 74" fill="none" stroke="#333" stroke-width="1"/>
                    <path d="M50 65 Q58 68 66 74" fill="none" stroke="#333" stroke-width="1"/>
                `;
            },
        },

        mushroom: {
            category: "plants",
            name: "蘑菇",
            difficulty: 1,
            description: "一个大蘑菇，伞盖上可以画圆点或花纹",
            svg() {
                return `
                    <path d="M15 55 Q15 20 50 15 Q85 20 85 55 Z" fill="none" stroke="#333" stroke-width="2"/>
                    <rect x="40" y="55" width="20" height="30" rx="3" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="35" cy="35" r="5" fill="none" stroke="#333" stroke-width="1.5"/>
                    <circle cx="55" cy="30" r="6" fill="none" stroke="#333" stroke-width="1.5"/>
                    <circle cx="65" cy="42" r="4" fill="none" stroke="#333" stroke-width="1.5"/>
                    <circle cx="42" cy="46" r="4" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M32 85 Q40 90 50 85 Q60 90 68 85" fill="none" stroke="#333" stroke-width="1"/>
                `;
            },
        },

        sunflower: {
            category: "plants",
            name: "向日葵",
            difficulty: 2,
            description: "一朵向日葵，圆形花盘和四周的花瓣",
            svg() {
                return `
                    <circle cx="50" cy="40" r="14" fill="none" stroke="#333" stroke-width="2"/>
                    <ellipse cx="50" cy="18" rx="7" ry="12" fill="none" stroke="#333" stroke-width="1.5"/>
                    <ellipse cx="50" cy="62" rx="7" ry="12" fill="none" stroke="#333" stroke-width="1.5"/>
                    <ellipse cx="28" cy="40" rx="12" ry="7" fill="none" stroke="#333" stroke-width="1.5"/>
                    <ellipse cx="72" cy="40" rx="12" ry="7" fill="none" stroke="#333" stroke-width="1.5"/>
                    <ellipse cx="34" cy="24" rx="10" ry="6" fill="none" stroke="#333" stroke-width="1.5" transform="rotate(-45,34,24)"/>
                    <ellipse cx="66" cy="24" rx="10" ry="6" fill="none" stroke="#333" stroke-width="1.5" transform="rotate(45,66,24)"/>
                    <ellipse cx="34" cy="56" rx="10" ry="6" fill="none" stroke="#333" stroke-width="1.5" transform="rotate(45,34,56)"/>
                    <ellipse cx="66" cy="56" rx="10" ry="6" fill="none" stroke="#333" stroke-width="1.5" transform="rotate(-45,66,56)"/>
                    <line x1="50" y1="74" x2="50" y2="95" stroke="#333" stroke-width="2.5"/>
                    <path d="M50 82 Q38 78 30 84" fill="none" stroke="#333" stroke-width="1.5"/>
                `;
            },
        },

        // ============ 生活用品类 ============
        house: {
            category: "objects",
            name: "房子",
            difficulty: 2,
            description: "一座小房子，墙壁和屋顶都可以装饰",
            svg() {
                return `
                    <rect x="18" y="45" width="64" height="42" rx="2" fill="none" stroke="#333" stroke-width="2"/>
                    <polygon points="10,47 50,15 90,47" fill="none" stroke="#333" stroke-width="2"/>
                    <rect x="40" y="60" width="16" height="27" rx="1" fill="none" stroke="#333" stroke-width="1.5"/>
                    <circle cx="53" cy="74" r="2" fill="none" stroke="#333" stroke-width="1"/>
                    <rect x="24" y="52" width="12" height="12" rx="1" fill="none" stroke="#333" stroke-width="1.5"/>
                    <line x1="30" y1="52" x2="30" y2="64" stroke="#333" stroke-width="1"/>
                    <line x1="24" y1="58" x2="36" y2="58" stroke="#333" stroke-width="1"/>
                    <rect x="60" y="52" width="12" height="12" rx="1" fill="none" stroke="#333" stroke-width="1.5"/>
                    <line x1="66" y1="52" x2="66" y2="64" stroke="#333" stroke-width="1"/>
                    <line x1="60" y1="58" x2="72" y2="58" stroke="#333" stroke-width="1"/>
                    <rect x="46" y="22" width="6" height="12" rx="1" fill="none" stroke="#333" stroke-width="1.5"/>
                `;
            },
        },

        vase: {
            category: "objects",
            name: "花瓶",
            difficulty: 2,
            description: "一个优美的花瓶，瓶身上可以画各种花纹",
            svg() {
                return `
                    <path d="M50 15 Q35 15 30 28 Q24 45 34 60 L34 78 L66 78 L66 60 Q76 45 70 28 Q65 15 50 15" fill="none" stroke="#333" stroke-width="2"/>
                    <ellipse cx="50" cy="15" rx="14" ry="5" fill="none" stroke="#333" stroke-width="2"/>
                    <ellipse cx="50" cy="78" rx="16" ry="4" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M36 35 Q50 30 64 35" fill="none" stroke="#333" stroke-width="1" stroke-dasharray="3 3"/>
                    <path d="M32 48 Q50 42 68 48" fill="none" stroke="#333" stroke-width="1" stroke-dasharray="3 3"/>
                    <path d="M36 62 Q50 56 64 62" fill="none" stroke="#333" stroke-width="1" stroke-dasharray="3 3"/>
                `;
            },
        },

        cup: {
            category: "objects",
            name: "杯子",
            difficulty: 1,
            description: "一个杯子，可以装饰杯身的花纹",
            svg() {
                return `
                    <rect x="22" y="25" width="46" height="50" rx="4" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M68 35 Q82 35 82 50 Q82 65 68 65" fill="none" stroke="#333" stroke-width="2"/>
                    <ellipse cx="45" cy="25" rx="23" ry="6" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M22 75 Q45 82 68 75" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M30 45 Q45 40 60 45" fill="none" stroke="#333" stroke-width="1" stroke-dasharray="2 2"/>
                    <path d="M30 58 Q45 53 60 58" fill="none" stroke="#333" stroke-width="1" stroke-dasharray="2 2"/>
                `;
            },
        },

        umbrella: {
            category: "objects",
            name: "雨伞",
            difficulty: 2,
            description: "一把漂亮的雨伞，伞面上可以画花纹",
            svg() {
                return `
                    <path d="M10 50 Q10 15 50 10 Q90 15 90 50" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M10 50 Q20 45 30 50 Q40 45 50 50 Q60 45 70 50 Q80 45 90 50" fill="none" stroke="#333" stroke-width="1.5"/>
                    <line x1="50" y1="10" x2="50" y2="80" stroke="#333" stroke-width="2"/>
                    <path d="M50 80 Q50 88 44 88 Q38 88 38 82" fill="none" stroke="#333" stroke-width="2"/>
                    <line x1="50" y1="10" x2="50" y2="5" stroke="#333" stroke-width="2"/>
                    <circle cx="50" cy="4" r="2" fill="none" stroke="#333" stroke-width="1.5"/>
                `;
            },
        },

        tshirt: {
            category: "objects",
            name: "T恤",
            difficulty: 2,
            description: "一件T恤衫，设计你喜欢的图案",
            svg() {
                return `
                    <path d="M30 20 L20 20 L5 40 L18 45 L25 30 L25 82 L75 82 L75 30 L82 45 L95 40 L80 20 L70 20 Q65 30 50 30 Q35 30 30 20" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M30 20 Q35 30 50 30 Q65 30 70 20" fill="none" stroke="#333" stroke-width="1.5" stroke-dasharray="3 3"/>
                `;
            },
        },

        kite: {
            category: "objects",
            name: "风筝",
            difficulty: 1,
            description: "一只菱形风筝，在上面画出美丽的图案",
            svg() {
                return `
                    <polygon points="50,10 80,45 50,80 20,45" fill="none" stroke="#333" stroke-width="2"/>
                    <line x1="20" y1="45" x2="80" y2="45" stroke="#333" stroke-width="1.5"/>
                    <line x1="50" y1="10" x2="50" y2="80" stroke="#333" stroke-width="1.5"/>
                    <path d="M50 80 Q52 88 48 92 Q52 95 48 98" fill="none" stroke="#333" stroke-width="1.5"/>
                `;
            },
        },

        // ============ 美食类 ============
        cake: {
            category: "food",
            name: "蛋糕",
            difficulty: 2,
            description: "一个双层蛋糕，装饰漂亮的花纹和图案",
            svg() {
                return `
                    <rect x="20" y="50" width="60" height="28" rx="4" fill="none" stroke="#333" stroke-width="2"/>
                    <rect x="28" y="28" width="44" height="24" rx="4" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M20 50 Q30 44 40 50 Q50 44 60 50 Q70 44 80 50" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M28 28 Q38 22 50 28 Q62 22 72 28" fill="none" stroke="#333" stroke-width="1.5"/>
                    <line x1="50" y1="20" x2="50" y2="12" stroke="#333" stroke-width="2"/>
                    <circle cx="50" cy="10" r="3" fill="none" stroke="#333" stroke-width="1.5"/>
                    <circle cx="35" cy="62" r="3" fill="none" stroke="#333" stroke-width="1"/>
                    <circle cx="50" cy="65" r="3" fill="none" stroke="#333" stroke-width="1"/>
                    <circle cx="65" cy="62" r="3" fill="none" stroke="#333" stroke-width="1"/>
                    <path d="M20 78 L80 78" stroke="#333" stroke-width="2"/>
                `;
            },
        },

        icecream: {
            category: "food",
            name: "冰淇淋",
            difficulty: 1,
            description: "一个冰淇淋甜筒",
            svg() {
                return `
                    <circle cx="38" cy="28" r="14" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="62" cy="28" r="14" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="50" cy="18" r="14" fill="none" stroke="#333" stroke-width="2"/>
                    <polygon points="30,38 70,38 50,90" fill="none" stroke="#333" stroke-width="2"/>
                    <line x1="34" y1="50" x2="50" y2="90" stroke="#333" stroke-width="1" stroke-dasharray="3 3"/>
                    <line x1="66" y1="50" x2="50" y2="90" stroke="#333" stroke-width="1" stroke-dasharray="3 3"/>
                `;
            },
        },

        pizza: {
            category: "food",
            name: "比萨饼",
            difficulty: 1,
            description: "一个圆形比萨，切成几块，每块画不同配料",
            svg() {
                return `
                    <circle cx="50" cy="50" r="35" fill="none" stroke="#333" stroke-width="2"/>
                    <line x1="50" y1="15" x2="50" y2="85" stroke="#333" stroke-width="1.5"/>
                    <line x1="15" y1="50" x2="85" y2="50" stroke="#333" stroke-width="1.5"/>
                    <circle cx="35" cy="35" r="4" fill="none" stroke="#333" stroke-width="1"/>
                    <circle cx="60" cy="38" r="5" fill="none" stroke="#333" stroke-width="1"/>
                    <circle cx="40" cy="62" r="4" fill="none" stroke="#333" stroke-width="1"/>
                    <circle cx="65" cy="60" r="3" fill="none" stroke="#333" stroke-width="1"/>
                    <ellipse cx="50" cy="50" rx="8" ry="6" fill="none" stroke="#333" stroke-width="1"/>
                `;
            },
        },

        // ============ 奇幻类 ============
        unicorn: {
            category: "fantasy",
            name: "独角兽",
            difficulty: 3,
            description: "一只独角兽的轮廓，给它画上美丽的装饰",
            svg() {
                return `
                    <ellipse cx="50" cy="55" rx="26" ry="20" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="35" cy="35" r="14" fill="none" stroke="#333" stroke-width="2"/>
                    <polygon points="35,21 30,2 40,2" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="30" cy="33" r="3" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M22 38 L16 40" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M42 46 Q55 42 60 35 Q65 28 58 24" fill="none" stroke="#333" stroke-width="1.5"/>
                    <line x1="32" y1="75" x2="32" y2="92" stroke="#333" stroke-width="2"/>
                    <line x1="45" y1="75" x2="45" y2="92" stroke="#333" stroke-width="2"/>
                    <line x1="58" y1="75" x2="58" y2="92" stroke="#333" stroke-width="2"/>
                    <line x1="68" y1="72" x2="68" y2="92" stroke="#333" stroke-width="2"/>
                    <path d="M74 50 Q85 48 88 55 Q92 62 82 60" fill="none" stroke="#333" stroke-width="1.5"/>
                `;
            },
        },

        rocket: {
            category: "fantasy",
            name: "火箭",
            difficulty: 2,
            description: "一枚飞向太空的火箭",
            svg() {
                return `
                    <path d="M50 8 Q40 25 38 45 L38 70 L62 70 L62 45 Q60 25 50 8" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M38 55 Q28 60 25 72 L38 68" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M62 55 Q72 60 75 72 L62 68" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="50" cy="40" r="6" fill="none" stroke="#333" stroke-width="1.5"/>
                    <rect x="44" y="55" width="12" height="8" rx="1" fill="none" stroke="#333" stroke-width="1"/>
                    <path d="M42 70 Q44 82 40 90" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M50 70 Q50 84 50 92" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M58 70 Q56 82 60 90" fill="none" stroke="#333" stroke-width="1.5"/>
                `;
            },
        },

        castle: {
            category: "fantasy",
            name: "城堡",
            difficulty: 3,
            description: "一座梦幻城堡，墙壁和塔楼可以画满花纹",
            svg() {
                return `
                    <rect x="25" y="40" width="50" height="48" rx="2" fill="none" stroke="#333" stroke-width="2"/>
                    <rect x="15" y="30" width="16" height="58" rx="1" fill="none" stroke="#333" stroke-width="2"/>
                    <rect x="69" y="30" width="16" height="58" rx="1" fill="none" stroke="#333" stroke-width="2"/>
                    <rect x="5" y="24" width="8" height="8" rx="0" fill="none" stroke="#333" stroke-width="1.5"/>
                    <rect x="19" y="24" width="8" height="8" rx="0" fill="none" stroke="#333" stroke-width="1.5"/>
                    <rect x="73" y="24" width="8" height="8" rx="0" fill="none" stroke="#333" stroke-width="1.5"/>
                    <rect x="87" y="24" width="8" height="8" rx="0" fill="none" stroke="#333" stroke-width="1.5"/>
                    <polygon points="40,40 50,20 60,40" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M43 88 Q43 78 50 78 Q57 78 57 88" fill="none" stroke="#333" stroke-width="2"/>
                    <rect x="32" y="50" width="8" height="10" rx="1" fill="none" stroke="#333" stroke-width="1"/>
                    <rect x="60" y="50" width="8" height="10" rx="1" fill="none" stroke="#333" stroke-width="1"/>
                    <circle cx="50" cy="28" r="3" fill="none" stroke="#333" stroke-width="1"/>
                `;
            },
        },

        dragon: {
            category: "fantasy",
            name: "小龙",
            difficulty: 3,
            description: "一条可爱的小龙，给它画上鳞片和花纹",
            svg() {
                return `
                    <ellipse cx="45" cy="50" rx="22" ry="18" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="30" cy="32" r="14" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="25" cy="30" r="3" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M36 38 L42 42" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M20 22 L16 12 L24 18" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M34 22 L38 12 L30 18" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M36 44 Q42 38 48 40" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M65 45 Q78 40 85 50 Q92 60 80 58 Q70 56 65 50" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M30 42 Q18 48 12 56 Q8 62 16 60" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M55 36 Q58 28 52 20" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M60 38 Q64 30 60 22" fill="none" stroke="#333" stroke-width="1.5"/>
                    <line x1="35" y1="68" x2="35" y2="82" stroke="#333" stroke-width="2"/>
                    <line x1="55" y1="68" x2="55" y2="82" stroke="#333" stroke-width="2"/>
                `;
            },
        },

        // ============ 交通工具类 ============
        car: {
            category: "vehicles",
            name: "小汽车",
            difficulty: 2,
            description: "一辆小汽车，车身上可以画各种装饰",
            svg() {
                return `
                    <path d="M15 55 L15 70 L85 70 L85 55 L72 55 L65 35 L35 35 L28 55 Z" fill="none" stroke="#333" stroke-width="2"/>
                    <line x1="35" y1="35" x2="65" y2="35" stroke="#333" stroke-width="2"/>
                    <line x1="50" y1="35" x2="50" y2="55" stroke="#333" stroke-width="1.5"/>
                    <circle cx="30" cy="70" r="10" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="30" cy="70" r="4" fill="none" stroke="#333" stroke-width="1"/>
                    <circle cx="70" cy="70" r="10" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="70" cy="70" r="4" fill="none" stroke="#333" stroke-width="1"/>
                    <rect x="18" y="55" width="8" height="6" rx="1" fill="none" stroke="#333" stroke-width="1"/>
                    <rect x="74" y="55" width="8" height="6" rx="1" fill="none" stroke="#333" stroke-width="1"/>
                `;
            },
        },

        boat: {
            category: "vehicles",
            name: "帆船",
            difficulty: 2,
            description: "一艘帆船，帆上可以画出各种花纹",
            svg() {
                return `
                    <path d="M15 65 Q30 58 50 55 Q70 58 85 65 L90 72 L10 72 Z" fill="none" stroke="#333" stroke-width="2"/>
                    <line x1="50" y1="55" x2="50" y2="12" stroke="#333" stroke-width="2"/>
                    <polygon points="50,15 50,52 78,52" fill="none" stroke="#333" stroke-width="2"/>
                    <polygon points="50,18 50,48 28,48" fill="none" stroke="#333" stroke-width="1.5"/>
                    <path d="M8 78 Q25 74 50 78 Q75 74 92 78" fill="none" stroke="#333" stroke-width="1" stroke-dasharray="3 3"/>
                `;
            },
        },

        airplane: {
            category: "vehicles",
            name: "飞机",
            difficulty: 2,
            description: "一架飞机，机身和机翼都可以装饰",
            svg() {
                return `
                    <ellipse cx="50" cy="50" rx="35" ry="10" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M35 50 L20 30 L55 44" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M35 50 L20 70 L55 56" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M75 46 L88 35 L85 50" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M75 54 L88 65 L85 50" fill="none" stroke="#333" stroke-width="2"/>
                    <circle cx="25" cy="48" r="4" fill="none" stroke="#333" stroke-width="1.5"/>
                    <line x1="40" y1="40" x2="60" y2="40" stroke="#333" stroke-width="1" stroke-dasharray="2 2"/>
                `;
            },
        },
    },
};
