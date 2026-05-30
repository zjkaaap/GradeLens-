<div align="center">

# 📝 GradeLens 智阅

**上传一张学生作答照片，AI 自动识别手写内容、对照标准答案打分并给出扣分点与评语。**

基于多模态大模型的端到端自动阅卷应用，无需 OCR 预处理，直接「看图—理解—评分」一步到位。

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![uni-app](https://img.shields.io/badge/uni--app-Vue-42b883?logo=vue.js&logoColor=white)](https://uniapp.dcloud.net.cn/)
[![Qwen](https://img.shields.io/badge/Model-qwen3.6--plus-FF6A00)](https://dashscope.console.aliyun.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](#-许可证)

</div>

---

## 📖 简介

**GradeLens（智阅）** 是一个端到端的 AI 自动阅卷应用。教师上传 `.docx` 试卷后，系统自动解析出每道题的题干、标准答案与分值；学生作答只需拍照上传，多模态大模型 `qwen3.6-plus` 便直接「看图—理解手写—对照评分」一步到位，输出结构化的得分、扣分点与评语。

与传统「OCR + 文本大模型」的两段式方案不同，GradeLens 让模型直接读取原始作答图片，避免了手写公式在 OCR 环节的识别损失，对数学等含大量公式的学科尤其友好。前端基于 uni-app，一套代码即可运行于 H5、Android 与小程序。

---

## ✨ 功能特性

- 📄 **试卷智能解析** —— 上传 `.docx` 试卷，自动拆分出每道题的题干 / 标准答案 / 解析 / 分值并入库
- 🖼️ **手写作答识别** —— 学生作答拍照上传，多模态模型直接读图，无需独立 OCR 引擎，避免手写识别损失
- 🎯 **逐题精准评分** —— 对照标准答案输出 `得分 / 满分 / 扣分点 / 评语`，结构化 JSON 返回
- 📚 **整卷一次评分** —— 一次上传多张作答图片，整卷题目批量评分（`/api/grade_paper`）
- 🧮 **数学公式渲染** —— 前端 KaTeX 渲染 LaTeX，作答与评语中的公式正常显示
- 📱 **跨端运行** —— 一套 uni-app 代码可跑 H5 / Android APK / 小程序
- 🗂️ **历史记录** —— 评分结果落入 SQLite，可随时回查

---

## 🧠 工作原理

```
教师端                          后端 (FastAPI)                     阿里云百炼
  │                                 │                                 │
  │  1. 上传 .docx 试卷              │                                 │
  ├────────────────────────────────►│  python-docx 解析 +             │
  │                                 │  qwen3.6-plus 兜底结构化  ──────►│
  │                                 │◄─── 题目列表入库 (SQLite) ◄──────┤
  │                                 │                                 │
  │  2. 上传学生作答图片 (题号/整卷)  │                                 │
  ├────────────────────────────────►│  图片 → base64 data URL         │
  │                                 │  + 标准答案 拼成多模态消息  ─────►│
  │                                 │                                 │ qwen3.6-plus
  │                                 │                                 │ 看图+理解+评分
  │   3. 得分/扣分点/评语 (JSON)      │◄──── 结构化 JSON ◄──────────────┤
  │◄────────────────────────────────┤  规整 + 入库                    │
```

> **关键设计：单模型、直接多模态。** 全流程只用 `qwen3.6-plus` 一个模型，学生作答图片**直接**作为 `image_url` 送入对话，由模型一次性完成「视觉理解 + 转录 + 打分」，**不是** OCR + 文本大模型的两段式方案，避免了手写公式在 OCR 环节的识别损失。

---

## 🛠️ 技术栈

| 层 | 技术 |
|---|---|
| 前端 | uni-app (Vue 2)、HBuilderX、KaTeX |
| 后端 | FastAPI、Uvicorn、SQLAlchemy 2.x、Pydantic v2 |
| 数据库 | SQLite |
| 大模型 | 阿里云百炼 `qwen3.6-plus`（OpenAI 兼容模式） |
| 文档解析 | python-docx + LLM 兜底 |
| 图像处理 | Pillow（压缩 / base64） |

---

## 📁 目录结构

```
AI试卷评分系统/
├── backend/                       后端（FastAPI）
│   ├── main.py                    应用入口、CORS、路由注册、/health
│   ├── config.py                  配置加载（读取 .env）
│   ├── database.py                SQLite + SQLAlchemy 会话
│   ├── models.py                  ORM：Paper / Question / GradingRecord
│   ├── schemas.py                 Pydantic 请求/响应模型
│   ├── routers/
│   │   ├── paper.py               试卷上传、列表、详情、删除
│   │   └── grade.py               单题评分、整卷评分、记录查询
│   ├── services/
│   │   ├── docx_parser.py         docx → 题目结构化
│   │   ├── grading_service.py     多模态评分核心逻辑
│   │   ├── matcher.py             按题号/关键字匹配题目
│   │   └── llm_client.py          百炼客户端（OpenAI SDK）
│   ├── utils/
│   │   ├── image_utils.py         图片压缩 + base64 data URL
│   │   └── prompt_templates.py    系统/用户 Prompt 模板
│   ├── storage/                   运行时生成：docx / 学生图片 / app.db
│   ├── requirements.txt
│   └── .env.example               配置模板（复制为 .env 后填 Key）
├── frontend/                      前端（uni-app，用 HBuilderX 打开）
│   ├── manifest.json / pages.json / App.vue / main.js
│   ├── api/index.js               请求封装，含 BASE_URL 配置
│   ├── components/math-text/      KaTeX 公式渲染组件
│   └── pages/                     首页 / 试卷上传·列表·详情 / 评分·结果
├── 5月23日解析（B卷）.docx          端到端测试用试卷
└── 学生试卷题目1.png / 2.png        端到端测试用作答图片
```

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- [HBuilderX](https://www.dcloud.io/hbuilderx.html)（前端开发 / APK 打包）
- 阿里云百炼 API Key —— [前往申请](https://dashscope.console.aliyun.com/) 并开通 `qwen3.6-plus`

### 1️⃣ 启动后端

```bash
cd backend

# 创建并激活虚拟环境
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate      # macOS / Linux

# 安装依赖
pip install -r requirements.txt

# 配置 API Key
cp .env.example .env             # Windows: copy .env.example .env
# 编辑 .env，把 DASHSCOPE_API_KEY 改成你的真实 Key

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

打开 `http://127.0.0.1:8000/docs` 用 Swagger 自测：

1. `POST /api/paper/upload` 上传 `5月23日解析（B卷）.docx`
2. `POST /api/grade` 上传 `学生试卷题目1.png`，填 `paper_id=1` 及对应 `question_no`

### 2️⃣ 启动前端（H5 调试）

1. 用 HBuilderX 打开 `frontend/` 目录
2. 工具栏 **运行 → 运行到浏览器 → Chrome**
3. 浏览器访问 `http://localhost:8080`
4. 首页底部「后端地址」默认 `http://127.0.0.1:8000`，如后端在别处可在此修改

### 3️⃣ 打包 Android APK

1. HBuilderX 打开 `frontend/manifest.json`，在「基础配置」重新生成 AppID（首次需登录 DCloud 账号）
2. **关键**：APK 内的 `127.0.0.1` 指向手机本身。需把后端部署到电脑内网 IP（如 `http://192.168.1.10:8000`），并在 App 首页「后端地址」或 `frontend/api/index.js` 的 `DEFAULT_BASE_URL` 中填写
3. 后端 `.env` 的 `ALLOWED_ORIGINS` 加入对应来源（或填 `*`）
4. 菜单 **发行 → 原生 App-云打包 → Android**，选「使用公共测试证书」，等待 5–10 分钟
5. 下载 APK 安装到手机（手机需与电脑同一 WiFi）

---

## ⚙️ 配置项

`backend/.env`：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `DASHSCOPE_API_KEY` | *(必填)* | 阿里云百炼 API Key |
| `DASHSCOPE_BASE_URL` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | OpenAI 兼容入口 |
| `MODEL_NAME` | `qwen3.6-plus` | 统一模型：解析兜底 / 视觉识别 / 评分 |
| `MAX_UPLOAD_MB` | `20` | 单文件上传大小上限 |
| `ALLOWED_ORIGINS` | `http://localhost:8080,...` | CORS 白名单，逗号分隔，`*` 表示全部 |

---

## 📡 API 速览

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/health` | 健康检查，返回当前模型名 |
| `POST` | `/api/paper/upload` | 上传 docx，解析题目入库 |
| `GET` | `/api/paper/list` | 试卷列表 |
| `GET` | `/api/paper/{id}` | 试卷详情（含全部题目） |
| `DELETE` | `/api/paper/{id}` | 删除试卷（级联删除题目与记录） |
| `POST` | `/api/grade` | 上传单张图片，按题号评分 |
| `POST` | `/api/grade_paper` | 上传多张图片，整卷批量评分 |
| `GET` | `/api/grade/{record_id}` | 查询历史评分记录 |

`/api/grade` 响应字段：`record_id, matched_question, student_answer_ocr, score_obtained, full_score, deductions[], deduction_reason, ai_comment`

> 注：响应字段 `student_answer_ocr` 与数据库列 `student_ocr` 仅为命名，存储的是**模型转录的作答文本**（`transcribed_answer`），并非独立 OCR 引擎输出。

---

## 🗄️ 数据存储

SQLite 数据库 `backend/storage/app.db`：

- `papers (id, name, file_path, created_at)`
- `questions (id, paper_id, qno, stem, answer, explanation, score)`
- `grading_records (id, paper_id, question_id, image_path, student_ocr, score_obtained, full_score, deduction_reason, ai_comment, created_at)`

上传的 docx 存于 `backend/storage/papers/`，学生图片存于 `backend/storage/student_imgs/`。

---

## 🩺 故障排查

| 现象 | 排查方向 |
|---|---|
| 后端起不来 / `/health` 不通 | 确认 `.venv` 已激活、8000 端口未被占用 |
| 上传 docx 后题数为 0 | 试卷格式过于非典型，解析器期望「一、单选题」等章节头；可在 docx 中补上标题 |
| 前端调后端报 CORS | 检查 `.env` 的 `ALLOWED_ORIGINS` 是否包含 H5 端口（默认 8080） |
| APK 中 `Failed to fetch` | APK 无法访问 127.0.0.1，须改电脑内网 IP，且手机与电脑同一 WiFi |
| 模型报 400 / 401 | 核对 `DASHSCOPE_API_KEY`，确认百炼控制台已开通 `qwen3.6-plus` |
| 图片过大被拒 | 调高 `MAX_UPLOAD_MB`，或拍照时启用压缩 |
| 评分返回非 JSON | 服务已有正则兜底；如频繁出现可把 `grading_service.py` 的 `temperature` 调为 0 |

---


## 🧭 已知问题与路线图

- ⚠️ **整卷评分的题目归属幻觉**：当 `/api/grade_paper` 一次性整卷评分、而上传图片实为另一份试卷的作答（如题干「四棱锥 P-ABCD」对作答「正方体 ABCD-A₁B₁C₁D₁」）时，模型有时会忽略对象不一致而按推理严谨度给高分。已在 Prompt 加入对象一致性硬约束并要求输出 `belongs_to_this_question` 做兜底清零，但模型仍可能自报 `true` 绕过。
  *正确用法：上传图片应与所选试卷对应。后续可对每道 `score>0` 的题再发一次纯文本归属判定调用，结果为 false 时清零。*
- ✅ **LaTeX 控制字符已修复**：`grading_service.py` 的 `_restore_latex` 将模型在 JSON 字符串里写单反斜杠时被吞掉的 `\t \b \f \r \v` 还原为字面反斜杠，前端 KaTeX 可正常渲染。

---
=======


## 🤝 贡献

欢迎提交 Issue 与 Pull Request。提交 PR 前请确保后端可正常启动、相关接口自测通过。

---



---

<div align="center">
<sub>Built with FastAPI · uni-app · 阿里云百炼 qwen3.6-plus</sub>
</div>
