Tibetan spellchecker Resources
===

This repository provides resources to build Tibetan spellcheckers, and pointer to existing ones.

The resources are mainly the various [documents](doc/).

The [syllables](syllables) directory, containing resources for checking tibetan syllables, and pointer to applications built from it.

### 补充词典 Supplement

若发现常用音节被误判为错误，可编辑 `syllables/supplement.txt`，每行添加一个有效音节（以 `#` 开头为注释）。例如 བདེ（幸福）等由 NB 型词根构成的常见音节。

## 网页端服务 Web Service

本项目包含一个基于 FastAPI 的藏文拼写检查网页服务。

### 安装与运行

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

或直接运行 `run.bat`（Windows）。

### 访问

打开浏览器访问 http://localhost:8000 即可使用拼写检查界面。

### API 接口

- `POST /api/spellcheck` - 检查文本拼写，请求体 `{"text": "藏文文本"}`
- `GET /api/check/{syllable}` - 检查单个音节
- `GET /api/stats` - 获取词典统计信息

### 部署到 Netlify

1. 将项目推送到 GitHub
2. 在 [Netlify](https://app.netlify.com) 选择 "Add new site" → "Import an existing project"
3. 连接 GitHub 仓库，构建设置已由 `netlify.toml` 配置：
   - **Build command**: 无需（静态站点）
   - **Publish directory**: `static`
   - **Functions directory**: `netlify/functions`

4. 部署完成后，访问你的 Netlify 域名即可使用。

本地测试 Netlify 环境：`npx netlify dev`

## License

All files in this repository are under [Creative Commons CC0 license](http://creativecommons.org/publicdomain/zero/1.0/legalcode), see the [FAQ](http://wiki.creativecommons.org/CC0).
