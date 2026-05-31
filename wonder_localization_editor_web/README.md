# Wonder Localization Editor Web

`wonder_localization_editor_web/` 是 `wonder_localization_editor` 的 Web 化目录。它使用 `FastAPI + Uvicorn` 提供本地服务，前端采用原生 HTML/CSS/JS，主要读写 `data/wonder_localization.yaml` 这份奇观基础数据；仍保留的概念/工程部手工文件只负责它们尚未迁移的键，重生成脚本继续从这些底层文件出发。

## 安装依赖

建议直接装到项目当前使用的 `eu5` 环境里：

```powershell
conda run --no-capture-output -n eu5 python -m pip install -r wonder_localization_editor_web/requirements.txt
```

## 启动

兼容旧入口：

```powershell
conda run --no-capture-output -n eu5 python scripts/wonder_localization_editor.py
```

也可以直接运行包入口：

```powershell
conda run --no-capture-output -n eu5 python -m wonder_localization_editor_web
```

常用参数：

```powershell
conda run --no-capture-output -n eu5 python scripts/wonder_localization_editor.py --host 127.0.0.1 --port 8765 --no-browser
conda run --no-capture-output -n eu5 python scripts/wonder_localization_editor.py --check
```

## 目录

- `service.py`: 复用原编辑器的数据装配、保存与重新生成逻辑，优先操作 `data/wonder_localization.yaml`
- `server.py`: FastAPI 路由与静态资源挂载
- `static/`: Web 前端页面
- `__main__.py`: 启动入口
