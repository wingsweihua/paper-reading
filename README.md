# Paper Sharing — 论文选读与已读记录

从 arXiv、Papers With Code、Hugging Face Daily Papers 浏览热文，一键加入你的 Google Sheet 已读列表。

## 项目结构

```
paper-sharing/
├── scripts/           # 拉取论文数据的 Python 脚本
├── data/              # 生成的 JSON（供网站使用）
├── web/               # 静态网站（可部署到 GitHub Pages）
├── apps-script/       # Google 表格「追加一行」脚本（需复制到 Apps Script）
├── .github/workflows/ # 每日自动更新数据的 GitHub Actions
└── README.md
```

## 1. 配置 Google Sheet 与 Apps Script

1. 打开你的 Google Sheet（新建或使用已有表格）。
2. **扩展程序 → Apps Script**，新建项目。
3. 将 `apps-script/Code.gs` 的内容粘贴进去并保存。
4. **部署 → 新建部署 → 类型选择「网络应用」**：
   - 执行身份：**以我的身份**
   - 谁可以访问：**所有人**（或「仅知道链接的用户」）
5. 部署后复制 **网络应用 URL**（形如 `https://script.google.com/macros/s/xxxxx/exec`）。
6. 在 `web/config.js` 里把 `SHEET_APPEND_URL` 改成这个 URL。

## 2. 本地生成数据并预览网站

```bash
cd ~/PycharmProjects/paper-sharing
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/fetch_all.py
```

用本地服务器预览（需先执行上一步生成 `data/*.json`）：

```bash
# 在项目根目录 paper-sharing 下
python -m http.server 8080
# 浏览器打开 http://localhost:8080/web/index.html
```

## 3. 部署到 GitHub Pages（免费公开访问）

1. 在 GitHub 新建仓库，把本项目推上去。
2. **Settings → Pages → Source** 选 **GitHub Actions**。
3. 推送后 workflow 会自动：拉取 arXiv/PWC/HF 数据 → 构建站点 → 发布到 gh-pages。完成后在 Settings → Pages 里看到站点地址（如 `https://<用户名>.github.io/<仓库名>/`）。
4. 每日定时（UTC 6:00）会重新拉数据并部署；也可在 Actions 页手动运行「Fetch papers and deploy site」。

## 4. 数据来源说明

- **arXiv**：官方 API，按 `cs.LG` 等分类取近期论文。
- **Papers With Code**：爬取 trending 页，可能随网站改版需微调。
- **Hugging Face Daily Papers**：请求社区接口或爬取 [huggingface.co/papers](https://huggingface.co/papers)，格式与脚本可能随 HF 更新需调整。

## 5. 「已读列表」表格列

与你的 Sheet 一致：**Date and time**, **Title**, **Authors and Affiliation**, **Takeaway**, **Paper link**。  
「加入我的列表」会写入日期、标题、作者、链接；Takeaway 留空，你可之后在表格里补。
