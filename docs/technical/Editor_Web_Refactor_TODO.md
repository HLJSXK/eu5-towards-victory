# Editor/Web 重构待办与处理决定

状态入口：[Editor_Web_Refactor_Status.md](Editor_Web_Refactor_Status.md)。选题、分工与验收标准见
[Editor/Web 改进分工工作文档](Editor_Web_Work_Plan.md)；以下待议项需用户指定。

## 待议事项（保留原文）

- `missing_outputs` 只能发现首次生成的必需输出缺失：staging 预填已有产物，handler 未重写既有输出时仍报成功（`changed: false`）。
- cost/reward 的 preview 对派生 `unique_wonders.yaml` 只返回文件 SHA-256 差异，没有字段级 diff；本切片标注为文件摘要，是否细化后端报告另行决定。
- 中断后的 staging/备份启动恢复与清理尚未实现；本轮按确认的 A 准确提示人工核对，另行决定自动恢复。
- 2026-10-11 审计：`JobManager._run` 的执行闭包（`services/tooling.py`，约 130 行）把暂存、校验、发布与回滚交织在一起，是后端最密的代码；新增 handler 或修改发布逻辑前是否拆分待定。

## 收尾整合关闭的待办（2026-10-12）

- cost/reward → Wonder 同步：保留草稿刷新；冲突列出旧/新原值，刷新失败保留旧页面；完成。
- Wonder reload：当前奇观删除时回落 initial_wonder_id；完成。
- ritual specs：删除不读取的 Prompt 输入声明，生成计划与清单一致；完成。
- Code State：字符串数字加引号；交叉核对发现结构行 yes/no 原先依赖 YAML 隐式转型，现显式匹配后端布尔规范化；完成。
- on_error 异常：原始错误仍抛给调用方，回调错误写入操作事件与异常 notes；完成。
- 提交审计文案/日志：首次加载、保存后渲染、取消后渲染、cropper 顺序和媒体失败日志已修复。
- Node api/resource_state/media_job_polling 使用原生模块；cropper 页面 VM 保留并注明，真实接线由 Chrome 覆盖。
- 旧 Playwright 场景全部并入 Chrome：首次详情失败/重试、目录复用、仪式草稿往返后选项保留、目录与详情重试、Prompt 焦点、旧响应隔离和窄屏；删除旧入口。
- 审计 8 的 console.error/复制按钮：关闭；复制只读，诊断已可复制，不恢复额外忙碌处理。
- 整份 draft 复制/脏页统计：按确认结论关闭优化项，现有规模可用。
- JobManager 轮询复制全部内存快照：按确认结论关闭优化项。
- 未声明正式路径写入检测：按确认结论关闭，现有声明文件校验继续生效。
- formalize_json_paths 仅替换整值路径：按确认结论关闭，README handler 说明已注明目录/内嵌路径须使用正式路径。
- 媒体 stdout/stderr 重定向进程全局流：按确认结论关闭诊断归属优化项。
- 同步提交与异步调度统一：已并入后续任务 3。

上述关闭决定单列于此，遵循本次用户“不往明确边界新增条目”的要求；状态文档的已接受限制未增加条目。
