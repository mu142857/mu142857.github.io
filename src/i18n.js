// Bilingual UI (English / 中文), driven by the `site-lang` localStorage key that Settings
// writes. English is the source of truth and lives in the HTML / JS call sites; this module
// holds ONLY the Chinese for it, in two dictionaries:
//
//   ZH — innerHTML per [data-i18n] key. applyTranslations() walks every element carrying a
//        data-i18n attribute (including inside <template>s), caches its original English
//        markup on first sight, then swaps zh in or restores the cached English.
//   UI — strings built in JS (canvas text, button labels), both languages, read via t(key).
//
// Translation intent, per the site owner: proper nouns stay in their real language — product
// and company names (Godot, AUAV, R&S Studio…) and English-born project names stay English;
// games use their official Chinese titles (直到经过, 8分钟, 信号分裂; Phage stays Phage).

export const LANG_STORAGE_KEY = 'site-lang';

export function getLang() {
  return localStorage.getItem(LANG_STORAGE_KEY) === 'zh' ? 'zh' : 'en';
}

export function setLang(lang) {
  localStorage.setItem(LANG_STORAGE_KEY, lang === 'zh' ? 'zh' : 'en');
  applyTranslations();
}

// ---------------------------------------------------------------------------
// DOM text (data-i18n keys). Keys are shared between index.html and classic.html wherever
// both show the same content — the per-element English cache makes that safe even when the
// two English wordings differ slightly.
const ZH = {
  'doc.titleIndex': '上官嘉木',
  'doc.titleClassic': '上官嘉木 — 作品集',

  // Interactive HUD + chrome
  'hud.classic': '标准版 ›',
  'hud.settings': '设置 ›',
  'hud.rotate': '请把手机横过来',

  // First-visit world picker
  'picker.name': '上官嘉木',
  'picker.sub': '个人网站 · 作品集 —— 选择一个世界开始探索',
  'picker.choose': '选择你的世界',
  'picker.forest': '森林',
  'picker.city': '城市',
  'picker.denied': '无访问权限',

  // Settings (both sites)
  'settings.title': '设置',
  'settings.music': '音乐',
  'settings.musicDesc': '主题音乐，每个世界各一首。',
  'settings.musicDescClassic': '交互版网站的主题音乐。',
  'settings.language': '语言',
  'settings.langDesc': '切换整站的显示语言。',
  'settings.clearTitle': '清除记录',
  'settings.clearDesc': '清除世界选择、音乐与语言设置以及跑酷最高分，然后刷新页面。',

  // Classic top bar / hero / footer
  'nav.brand': '上官嘉木',
  'nav.about': '关于',
  'nav.skills': '技能',
  'nav.experience': '经历',
  'nav.games': '游戏',
  'nav.projects': '项目',
  'nav.music': '音乐',
  'nav.contact': '联系',
  'nav.interactive': '交互版 ›',
  'nav.settings': '设置',
  'hero.name': '上官嘉木',
  'hero.role': '滑铁卢大学数学系 · 游戏开发者 · 作曲人',
  'hero.lead': '应用数学（科学计算与科学机器学习方向）大二学生。我用 Godot 开发游戏，也以键盘手的身份创作音乐。',
  'footer.copy': '© 2026 上官嘉木',
  'footer.blurb': '更喜欢像素？<a href="index.html">去交互版看看 ›</a>',

  // About
  'about.title': '关于我',
  'about.sub': '以应用数学为主线，创作实践并行。',
  'about.lead': '滑铁卢大学大二学生，就读于应用数学专业，科学计算与科学机器学习方向。',
  'about.body': '我用 Godot 开发游戏，也以键盘手的身份创作音乐——把数学的严谨带进创作，让和声理论与数论原理彼此交融。',
  'about.eduTitle': '教育经历',
  'about.eduBody': '<strong>滑铁卢大学</strong> — 数学学士（Co-op）<br /><span class="meta">2025 年 9 月至今 · 安大略省滑铁卢</span>',
  'about.eduLine': '<strong>滑铁卢大学</strong> — 数学学士（Co-op）',
  'about.eduMeta': '2025 年 9 月至今 · 安大略省滑铁卢',
  'about.eduMajor': '专业：应用数学，科学计算与科学机器学习方向（AM-SciML）。',
  'about.beyondTitle': '课业之外',
  'about.beyondBody': '十余年古典钢琴，原创作曲者；R&amp;S Studio 联合创始人。中文（母语）与英语流利。',
  'about.beyond1': '十余年古典钢琴，原创作曲者；R&amp;S Studio 联合创始人。',
  'about.beyond2': '我把数学的严谨带进创作，让和声理论与数论原理彼此交融。',
  'about.beyondMeta': '中文（母语）与英语流利。',

  // Skills — product names stay English; only concept chips translate
  'skills.title': '技术能力',
  'skills.lead': '我在 Web、创意与数据工作中常用的工具。',
  'skills.web': '前端与 Web',
  'skills.langs': '编程语言',
  'skills.tools': '工具与平台',
  'skills.ai': 'AI 与数据',
  'chip.responsive': '响应式设计',
  'chip.dataviz': '数据可视化',
  'chip.api': 'API 集成',
  'chip.deploy': 'Web 部署',

  // Experience
  'exp.title': '工作经历',
  'exp.sub': '数学与硬件相遇的地方。',
  'exp.role': 'AUAV — 技术实习生',
  'exp.meta': '无人机表演技术 · 卡尔加里 · 2024 年 7 月 – 8 月',
  'exp.b1': '使用 Python 与 Skybrush 模拟无人机集群编队，优化飞行路径，兼顾避障与视觉效果。',
  'exp.b2': '在 Blender 中制作 3D 预演资产，使技术飞行约束与艺术设计相互对齐。',
  'exp.b3': '执行自动化飞行测试并分析遥测数据，提升机群同步性与电池效率。',

  // Game projects
  'games.title': '游戏作品',
  'games.lead': '我用 Godot 做游戏——玩法、物理与状态机都用 GDScript 编写，像素美术也由我亲手绘制。',
  'games.sub': '玩法、物理与状态机用 GDScript 编写——像素美术亦为手绘。',
  'games.usp.title': '直到经过 <span class="badge">GMTK 2026</span>',
  'games.usp.meta': '叙事 / 艺术游戏 · 队长 · 设计与全部程序',
  'games.usp.results': '<span class="of">约 10,500 部作品 · 37,000+ 参赛者中：</span> <strong>音频全球第 53 · 叙事第 126 · 美术第 140</strong>',
  'games.usp.desc': '距离聚会还有五天。一款关于社交焦虑的短篇游戏，用 4 天为 GMTK Game Jam 2026（主题：Count Down）制作。三种玩法——行走、防守、躲避——每当有什么越过了你，你都会听到自己说出一句不太友善的话。我带领三人团队，负责设计并编写了全部代码。',
  'games.phage.title': 'Phage <span class="badge">开发中</span>',
  'games.phage.meta': '动作冒险 · 2D 像素横版',
  'games.phage.desc': '我的主项目：一款推向极致的手绘像素动作冒险——主角只有 8×4 像素，但每一帧都是手绘的。开发日志系列（还挺有意思的）在 bilibili 连载：目前累计 24 万+ 播放、约 6 万点赞。',
  'games.efl.title': '8分钟 <span class="badge">GMTK 2026</span>',
  'games.efl.meta': '解谜 / 策略 · 队长 · 设计与全部程序',
  'games.efl.results': '<span class="of">约 10,500 部作品 · 37,000+ 参赛者中：</span> <strong>叙事全球第 476 · 美术第 1,849 · 音频第 3,354</strong>',
  'games.efl.desc': '八分钟逃离一座水下设施。每个行动都会消耗倒计时，真正的谜题是决定去帮谁——你永远无法帮到所有人。同一届 Jam 的第二部作品：依然由我担任队长、负责设计并编写全部代码。',
  'games.ss.title': '信号分裂',
  'games.ss.meta': 'UW Game Jam · 队长 & 唯一程序员',
  'games.ss.desc': '72 小时内完成并打磨的 2D 平台跳跃游戏——总排名第 4，视觉单项第一。全部 GDScript（物理、状态机、关卡设计）与全部美术均由我完成。',
  'games.progress': 'bilibili 粉丝',
  'games.ctaItch': '在 itch.io 玩我的游戏',
  'games.ctaBili': '在 bilibili 关注我',

  // Other projects — names stay English except the physics sim
  'proj.title': '项目',
  'proj.lead': '黑客松获奖、公共科技与 Web 作品。',
  'proj.look.meta': '生活成本对比工具 · 队长',
  'proj.look.desc': '带领四人团队构建社区宜居度聚合工具，对比加拿大各城市的生活成本与住房指标。已在 Hack Canada 2026 上展示；正从 Web 迁移到移动端。',
  'proj.phys.title': '物理模拟 <span class="badge">第一名</span>',
  'proj.phys.meta': 'Claude Create-A-Thon · 数据可视化赛道',
  'proj.phys.desc': '在 30 支队伍中获得第一名——胡克定律与单摆能量转换的交互式模拟，带实时可视化。',
  'proj.sf.meta': 'uOttaHack 8 · 开发者',
  'proj.sf.desc': '基于 MediaPipe 的实时面部信号监测，配合 Streamlit 仪表盘；集成 OpenAI API 自动生成洞察，并通过 SurveyMonkey 分发问卷。',
  'proj.opg.meta': '公共科技开发者',
  'proj.opg.desc': '开源的市议会追踪工具：聚合公开听证会日程与决议，并用 AI 辅助流程对议程条目自动分类与摘要。',
  'proj.dt.meta': '公益科技 · 前端',
  'proj.dt.desc': '慈善透明化平台的前端原型，以清晰的界面呈现项目目标与功能。',

  // Music
  'musicSec.title': '音乐创作',
  'musicSec.lead': '十余年古典钢琴，原创作曲者。我联合创立了 R&amp;S Studio——一个展示原创作品的音乐制作项目。',
  'musicSec.body': '完整的曲目、发行与工作室主页都在 R&amp;S Studio。',
  'musicSec.sub': '十余年古典钢琴，原创作品经由 R&amp;S Studio 发布。',
  'musicSec.role': 'R&amp;S Studio — 联合创始人',
  'musicSec.meta': '音乐制作 · 原创作品',
  'musicSec.desc': '一个展示原创作品的音乐制作项目。完整的曲目与发行都在工作室主页。',
  'musicSec.cta': '访问 R&amp;S Studio',

  // Contact (classic only)
  'contact.title': '联系方式',
  'contact.sub': '欢迎 Co-op 机会、项目合作与 Game Jam 组队。',
};

// ---------------------------------------------------------------------------
// JS-built strings (canvas text and button labels), both languages.
const UI = {
  'ui.on': { en: 'On', zh: '开' },
  'ui.off': { en: 'Off', zh: '关' },
  'ui.clear': { en: 'Clear', zh: '清除' },
  'ui.confirm': { en: 'Confirm?', zh: '确认清除？' },

  'style.rustCity': { en: 'City Style ›', zh: '城市风格 ›' },
  'style.silvaron': { en: 'Forest Style ›', zh: '森林风格 ›' },

  'game.hi': { en: 'Hi, I am', zh: '你好，我是' },
  'game.name': { en: 'Jiamu Shangguan', zh: '上官嘉木' },
  'game.keyControls': {
    en: 'Walk A / D    Sprint Shift    Jump Space x2    Enter Up / Click',
    zh: '移动 A/D    冲刺 Shift    跳跃 空格×2    进入 ↑/点击',
  },
  'game.touchControls': {
    en: 'Buttons to walk and jump    Tap jump twice in the air    Tap a building to enter',
    zh: '用按钮行走和跳跃    空中再按一次跳跃可二段跳    点击建筑进入',
  },
  'game.enterGame': { en: 'ENTER GAME', zh: '进入游戏' },
  'game.enter': { en: 'ENTER', zh: '进入' },
  'game.back': { en: 'BACK', zh: '返回' },

  'building.gameProjects': { en: 'Game Projects', zh: '游戏作品' },
  'building.projects': { en: 'Projects', zh: '项目' },
  'building.music': { en: 'Music Composing', zh: '音乐创作' },
  'building.about': { en: 'About Me', zh: '关于我' },
  'building.skills': { en: 'Technical Skills', zh: '技术能力' },
  'building.experience': { en: 'Work Experience', zh: '工作经历' },

  'run.hi': { en: 'HI', zh: '最高' },
  'run.gameOver': { en: 'GAME OVER', zh: '游戏结束' },
  'run.score': { en: 'SCORE', zh: '得分' },
  'run.best': { en: 'BEST', zh: '最高' },
  'run.retryKey': {
    en: 'SPACE  retry        ENTER  back to the city',
    zh: '空格  重试        回车  回到城市',
  },
  'run.retryTouch': {
    en: 'JUMP  retry        BACK  to the city',
    zh: '跳跃  重试        返回  回到城市',
  },
};

export function t(key) {
  const entry = UI[key];
  return entry ? entry[getLang()] : key;
}

// ---------------------------------------------------------------------------
// [data-i18n] application. English markup is cached per element on first sight, so toggling
// back restores exactly what the HTML shipped with — the dictionary never needs English.
const enCache = new WeakMap();

function applyTo(root, zh) {
  for (const el of root.querySelectorAll('[data-i18n]')) {
    if (!enCache.has(el)) enCache.set(el, el.innerHTML);
    const key = el.dataset.i18n;
    el.innerHTML = zh && ZH[key] != null ? ZH[key] : enCache.get(el);
  }
}

export function applyTranslations() {
  const zh = getLang() === 'zh';
  applyTo(document, zh);
  // Template content is inert but translatable in place; overlay clones then inherit the
  // current language automatically.
  for (const tpl of document.querySelectorAll('template')) applyTo(tpl.content, zh);
  document.documentElement.lang = zh ? 'zh-CN' : 'en';
}
