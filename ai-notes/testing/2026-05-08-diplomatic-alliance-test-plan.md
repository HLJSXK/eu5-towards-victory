# 测试清单：外交联盟系统

测试者：请在 EU5 游戏内进行以下验证。
日期：2026-05-08
分支：main（待合入的 commit）

---

## 测试前准备

1. 使用控制台积累 DVP（如有控制台命令，或编辑存档将 `tv_diplomatic_victory_points` 设为 50+）
2. 建议使用外交声誉较高的国家开局（如教皇国、法兰西）
3. 确认 mod 加载无报错（检查 `error.log` 中无 `tv_diplomatic_alliance` / `tv_seek_diplomatic_support` 相关错误）

---

## 测试用例

### T1: 基础加载验证

- [ ] 游戏启动无崩溃
- [ ] `error.log` 中无 `tv_` 前缀的报错（允许 warning，记录下来）
- [ ] 胜利情境面板 (Towards Victory) 正常显示 6 条路径

### T2: 外交支持互动出现

- [ ] 当 `tv_diplomatic_victory_points >= 50` 时，外交操作菜单中出现"Seek Diplomatic Support"（寻求外交支持）
- [ ] 该操作分类在友善行动 (CATEGORY_FRIENDLY_ACTIONS) 中
- [ ] 对已经是附庸的国家，该操作不可见
- [ ] 对已经支持过其他国家的国家，该操作不可见

### T3: AI 接受概率

- [ ] 对 200 好感的同文化、同宗教国家，接受概率应接近 100%（-200 + 100 + 50 + 50 + 声誉×5）
- [ ] 对好感为 0 的异文化、异宗教国家，接受概率极低（-200 - 50）
- [ ] 验证鼠标悬浮时 tooltip 正确显示各项加成/减成理由

### T4: 支持计数与事件

- [ ] 成功获得支持后，控制台检查 `tv_diplomatic_support_count` 递增
- [ ] 被支持国身上存在 `tv_diplomatic_supporter_of` 变量
- [ ] 当 DVP ≥ 50 且支持 < 10 时，触发通知事件 `tv_diplo_alliance.1`（"外交之路开启"）
- [ ] 当支持 ≥ 10 时，触发通知事件 `tv_diplo_alliance.2`（"联盟雏形初现"）

### T5: M1 里程碑与 IO 创建

- [ ] 同时满足 DVP ≥ 50 + 支持 ≥ 10 时，外交胜利 M1 里程碑事件触发
- [ ] 事件选项点击后：
  - [ ] 获得 `tv_diplomatic_m1_bonus` 永久修正
  - [ ] 国际组织 `tv_diplomatic_alliance` 被创建
  - [ ] 玩家成为组织领导者
  - [ ] 之前的 10 个支持国全部自动加入组织
- [ ] 外交地图模式中可见该组织

### T6: 支持国消亡

- [ ] 吞并一个支持国后，`tv_diplomatic_support_count` 减少 1
- [ ] 被吞并国从 IO 成员列表消失（如果 IO 已创建）

### T7: 法律系统

- [ ] 打开国际组织界面，5 个法律类别可见
- [ ] 所有法律初始为 Level 1 政策（无效果）
- [ ] 尝试提议 Level 2 政策：
  - [ ] 如果凝聚力 < 25，是否被 `allow` 阻止？
  - [ ] 如果凝聚力 ≥ 25，是否可以发起投票？
- [ ] 投票通过后：
  - [ ] 凝聚力扣除相应数值（25/50/75）
  - [ ] `tv_alliance_tier` 递增 1
  - [ ] 成员国获得对应 modifier
- [ ] `has_levels = yes` 是否阻止跳级（不能从 L1 直接到 L3）

### T8: 凝聚力增长

- [ ] 每月 `tv_alliance_cohesion` 增长 ≥ 0.1
- [ ] 拥有 10 点外交声誉的领导者，月增长应为 0.1 + 10×0.05 = 0.6
- [ ] 使用控制台 `set_variable tv_alliance_cohesion 24`，等 1 个月后确认超过 25

### T9: M2–M5 联盟等级门控

- [ ] M2 需要 DVP ≥ 120 且 `tv_alliance_tier >= 3`
- [ ] 使用控制台将 `tv_alliance_tier` 设为 3 并将 DVP 设为 120，确认 M2 触发
- [ ] 类似测试 M3(tier≥6)、M4(tier≥9)、M5(tier≥12)

### T10: 多玩家竞争（边界情况）

- [ ] 确认 IO 创建后，非领导国家无法使用"寻求外交支持"
- [ ] 确认 IO 是 `unique = yes`，不会被第二个国家重复创建

---

## 已知需关注的风险点

| 风险 | 如何验证 | 回退方案 |
|------|---------|---------|
| `has_levels = yes` 对自定义 IO 法律无效 | T7 跳级测试 | 改为纯 `allow` 门控（已有） |
| policy `allow` 中的变量检查 scope 不正确 | T7 凝聚力门控测试 | 将检查移入 `wants_propose_policy` 并加大 AI 惩罚 |
| `scope:recipient.leader_country` 解析失败 | T5 支持国加入验证 | 回退到 scope 嵌套写法 |
| `prev.var:tv_rep_bonus` 跨 scope 失败 | T8 凝聚力增长测试 | 改为硬编码固定增长值 |

---

## 报告格式

测试完成后请在 `ai-notes/testing/` 下新建结果文件，记录：
- 通过的用例打 ✅
- 失败的用例打 ❌ 并附 `error.log` 相关片段
- 任何意外的 warning 或行为

感谢测试！
