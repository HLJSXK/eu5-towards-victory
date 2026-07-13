# Victory Tree Node Planner Web

一个独立的本地 Web 工具，用于规划 6 条胜利之路（conquest / prosperity / trade / diplomatic /
cultural / science）在其树形背景图（`src/main_menu/gfx/interface/icons/towards_victory/victory_trees/`，
2048×1152）上的奖励节点摆放位置。

节点结构对应 `docs/design/Victory_Path_Tree_Variant_Design.md` 记录的树状奖励重构方案
（**尚未实现**，用于取代现行 `data/victory_paths.yaml` 的线性五里程碑/每层三选一奖励模型）：每条路径
一条 5 节点主干，外加 5 条支线，每条支线从主干某个节点分叉后再延伸自己的一串节点（长度 2–4 不等）。
节点数据（主干、支线、`attach_after` 分叉点、每个节点的效果名与数值）读取自结构化转录文件
`data/victory_path_tree_variant.yaml`；该文件与仍在使用的 `data/victory_paths.yaml` 相互独立，互不引用。

摆放结果保存到独立的 `data/victory_tree_node_positions.yaml`：按路径存一个 `节点 id -> {x, y}`
的映射，坐标为背景图的归一化比例（0–1），与最终 GUI 渲染尺寸无关，可直接换算进
`src/in_game/gui/panels/situation/tv_victory_situation.gui` 中节点 widget 的 `position`
（该重构一旦实现）。

工具启动时会自动把 6 张 `.dds` 树背景解码为 PNG，缓存到 `data/generated_tree_previews/`
（按源文件 mtime 判断是否需要重新解码），无需手动转换。

## 安装依赖

```powershell
conda run --no-capture-output -n eu5 python -m pip install -r victory_tree_planner_web/requirements.txt
```

## 启动

```powershell
conda run --no-capture-output -n eu5 python scripts/victory_tree_planner.py
# 或
conda run --no-capture-output -n eu5 python -m victory_tree_planner_web
```

默认监听 `127.0.0.1:8767`（wonder 编辑器 `8765`、cost/reward 编辑器 `8766` 之后的下一个端口）。
常用参数：

```powershell
conda run --no-capture-output -n eu5 python scripts/victory_tree_planner.py --host 127.0.0.1 --port 8767 --no-browser
conda run --no-capture-output -n eu5 python scripts/victory_tree_planner.py --check
```

`--check` 只做无头数据校验，不启动服务器：先校验 `data/victory_path_tree_variant.yaml` 每条路径的
`attach_after` 都指向该路径自己的主干节点，再校验 `data/victory_tree_node_positions.yaml`
（若尚不存在则视为正常，规划器会使用默认布局直到第一次保存）——若已存在则要求每条路径保存的节点
id 集合与主干+支线节点 id 集合完全一致，且每个节点的 `x`/`y` 落在 0..1 范围内。

## 界面

- 顶部标签页切换 6 条路径，画布按背景图原始比例显示（可缩放）
- 每个节点是可拖拽的圆形按钮：金色=主干节点，其余 5 种颜色分别对应 5 条支线；悬浮/常显标签展示
  该节点的效果名与数值
- 节点之间用虚线连接，按节点的前置关系绘制——主干链依次相连，每条支线从其分叉点开始沿自己的
  节点链延伸——直观体现真实的树状结构，而非简单的顺序排列
- 右侧节点列表分组显示："主干"一组（5 个节点），随后是"分支 1"–"分支 5"五组，每组只列出该支线
  自己新增的节点（与主干共享的分叉前置节点不重复列出，因为它已经作为主干节点单独存在一次）
- 列表支持直接输入精确的 x/y 数值；也可以先在列表中点选某个节点，再点击画布空白处把它移动到该位置
- "重置当前路径" 会把当前路径的所有节点恢复为内置的默认布局（主干沿上升曲线排列，各支线从其分叉点
  向图像边缘方向扇形展开，交替分布在主干两侧以避免重叠；不会立即保存，需要再次点击"保存"）

## 保存行为

点击"保存"会把当前内存中全部 6 条路径的节点位置整体写入
`data/victory_tree_node_positions.yaml`（保留文件顶部的说明注释）。保存前会校验每条路径保存的节点
id 集合与 `victory_path_tree_variant.yaml` 推导出的主干+支线节点 id 集合完全一致、且所有坐标落在
0..1 范围内，任一路径校验失败则整体不写盘（返回 400 并说明具体缺失/多余的节点 id）。保存后不会
自动改写任何 `.gui` 文件——把规划好的坐标接入实际 GUI 节点 `position` 仍需手动编辑（或在该重构
正式实现时新增一个消费这两个数据文件的生成脚本）。
