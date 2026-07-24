# Towards Victory 编辑器 Web

把原先各自独立的三个 Web 工具——花费/奖励/Modifier/任务池编辑器、胜利之路节点位置规划器、
奇观本地化编辑器——合并成一个 FastAPI 应用、一个端口、一个页面。三个工具原来各自的服务层
（`CostRewardEditorService`/`VictoryTreePlannerService`/`WonderLocalizationService`）与前端
业务逻辑基本保持不变，迁移到本包下的 `services/` 与 `static/`；真正合并的是：

- **路由**：原来三个工具都各自定义 `/api/bootstrap`、`/static/*`（cost_reward 和 victory_tree
  还都定义了 `/api/save`），现在统一按工具前缀区分：`/api/cost-reward/*`、`/api/victory-tree/*`、
  `/api/wonder-localization/*`，图片静态资源仍是 `/tree-previews/*`、`/wonder-images/*`（本来就
  互不冲突）。
- **异常处理**：三个工具原来在每个路由里手写的
  `except KeyError: 404 / except ValueError: 400 / except RuntimeError: 500 / except Exception: 500`
  样板代码完全相同，现在提到 `server.py` 顶层用 FastAPI 的 `exception_handler` 统一注册一次，
  路由函数本身不再重复这段 try/except。
- **日志缓冲**：三个服务原来各自实现了几乎一样的"有上限的滚动日志列表"（`_log_lines`/
  `_append_log`、`_log_fragments`），现在共用 `services/common.py` 里的 `RollingLog`。
- **前端**：一个共享外壳页面 `static/index.html`（标签页 + 三个 `<section>`），三个工具原来的
  页面主体内容原样搬进各自的 `<section>`；三份 `app.js` 仍各自是独立的 ES module（`type="module"`
  意味着它们本来就不共享顶层作用域，不需要为此重写业务逻辑），只改了少量确实冲突的 DOM id
  （`cost_reward` 和 `victory_tree` 都用过的 `tabs`/`save-btn`/`reload-btn`/`log`，改成
  `cr-*`/`vt-*` 前缀）和 fetch 路径；三份 CSS 用 `@scope` 包裹后各自只在自己的 `<section>`
  内生效，不再互相覆盖 `body`/`button` 等通用选择器样式。

`wonder_localization` 服务在构造时会校验 `data/wonder_localization.yaml`
的本地化完整性，如果校验失败会在启动时被单独捕获——不会连带整个应用无法启动，只有奇观本地化
这一个标签页会显示 503 错误，另外两个工具仍可正常使用。

## 安装依赖

```powershell
conda run --no-capture-output -n eu5 python -m pip install -r towards_victory_editor_web/requirements.txt
```

## 启动

```powershell
conda run --no-capture-output -n eu5 python scripts/towards_victory_editor.py
# 或
conda run --no-capture-output -n eu5 python -m towards_victory_editor_web
```

默认监听 `127.0.0.1:8760`。常用参数：

```powershell
conda run --no-capture-output -n eu5 python scripts/towards_victory_editor.py --host 127.0.0.1 --port 8760 --no-browser
conda run --no-capture-output -n eu5 python scripts/towards_victory_editor.py --check
```

`--check` 依次运行三个工具各自的无头数据校验（`build_check_report()`），按工具名分组打印，
不启动服务器；某个工具校验失败不会中断其余工具的校验（见 `services/common.py` 的 `safe_check`）。

## 保存行为

与合并前完全一致：每个工具的保存逻辑、写入的 YAML 文件、校验规则都未改变，只是路由前缀和
异常处理位置变了。三个工具原有的独立启动方式（各自的端口 8765/8766/8767）已被本包完全取代，
不再保留。
