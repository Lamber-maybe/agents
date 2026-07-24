# agents

Lamber 的 Claude 技能（Skills）与智能体配置集合。

## Skills

### blog-seo-optimizer — 博客 SEO / GEO / AEO 优化

写完文章后一键优化，或对整站做 SEO 体检，目标是最大化内容曝光：

- **SEO**：传统搜索引擎（Google / Bing / 百度）的收录与排名
- **GEO**（Generative Engine Optimization）：被 ChatGPT、Perplexity、Claude、Google AI Overviews 等 AI 引擎**引用**
- **AEO**（Answer Engine Optimization）：精选摘要 / People-Also-Ask / 语音助手的直接答案

**三种用法：**

| 场景 | 说法示例 |
|---|---|
| 单篇文章优化 | "我刚写完 `posts/xxx.md`，帮我优化 SEO"|
| 全站体检 | "帮我的博客做一次全站 SEO / GEO / AEO 体检" |
| 曝光策略 | "怎么提高我博客的曝光度和被 AI 引用的概率？" |

**包含内容：**

```
skills/blog-seo-optimizer/
├── SKILL.md                        # 工作流：单篇优化 / 全站体检 / 曝光策略
├── references/
│   ├── article-checklist.md        # 单篇优化清单（标题/描述/答案先行/FAQ/证据密度…，含中文宽度标准）
│   ├── site-audit.md               # 全站技术体检（robots/AI爬虫/渲染/结构化数据/内链，含 Hugo+PaperMod 专项）
│   ├── structured-data.md          # JSON-LD 模板（BlogPosting/FAQPage/Person/HowTo…）
│   └── distribution.md             # 站外曝光手册（收录提交/IndexNow/AI引擎数据源/分发/中文生态）
└── scripts/
    └── seo_check.py                # 零依赖检测脚本：0-100 打分，支持中文宽度、批量目录、--json
```

**安装（任选其一）：**

```bash
# 个人级：所有项目可用
git clone https://github.com/Lamber-maybe/agents.git
cp -r agents/skills/blog-seo-optimizer ~/.claude/skills/

# 项目级：仅在博客仓库内可用
cp -r agents/skills/blog-seo-optimizer <你的博客仓库>/.claude/skills/
```

安装后在 Claude Code 里正常对话即可自动触发，也可以直接说"用 blog-seo-optimizer 优化这篇文章"。

**单独使用检测脚本（不经过 Claude）：**

```bash
python3 skills/blog-seo-optimizer/scripts/seo_check.py content/posts/my-post.md
python3 skills/blog-seo-optimizer/scripts/seo_check.py content/posts/ --json   # 全站批量
```
