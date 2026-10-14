# 伟大工程：真实参考图的图生图评估

本轮输入为 `assets/historical/` 根目录的 20 张图片。根配置
`generate_dds_icon_config.json` 的 `historical_images.images` 已逐张映射，
输出为 `assets/historical/processed/<中文工程名>_ai_cartoon.png`。

生成使用项目已有的 `scripts/generate_historical_images.py`，通过 Images
edits API 上传源图。最初四张输出作为首轮评审基线保留；目录现有输出已增至 9 张。
旧提示词与评估记录
已存入 `baseline_v1/`。当前 20 条逐图提示词为第二轮方案，见
`historical_image_prompts.json` 和中文边界说明 `historical_image_prompt_plan.md`。

第二轮保留主体的身份、标志性结构与真实比例，允许增删或重组非主体元素、
加入少量时代相符的尺度参照，并轻微改变机位、距离或角度。主体须完整且突出，
绘画须作出明确的构图与笔触处理。错题材素材仍需换源，不能靠扩充陪衬冒充正确主体。
`overwrite=false`，重跑会跳过同一目录中已存在的输出。

当前风格要求为油画质感的卡通插画：概括形状、大色块、分组明暗、选择性描边、
宽刷笔触与简化细节须在缩略图上可见。风格声明位于每条提示词开头；建筑比例保持可信。
本次风格调整前的提示词快照在 `composition_v2_before_style_revision/`。

使用项目指定的 Python 解释器：

```powershell
# 先预演四张基线对应的第二轮方案；省略 --dry-run 才会调用 API。
& 'C:\Users\Hades\anaconda3\envs\eu5\python.exe' scripts/generate_historical_images.py --source 北京皇家粮仓 --source 博洛尼亚大学 --source 埃奇米阿津主教座堂 --source 埃斯科里亚尔修道院 --output-dir assets/historical/processed/v2 --dry-run
# 第二轮独立对照页；尚无输出的条目会显示等待生成。
& 'C:\Users\Hades\anaconda3\envs\eu5\python.exe' scripts/evaluate_historical_images.py --images-dir assets/historical/processed/v2 --output-dir assets/historical/review/v2
# 四张现有基线的对照页。
& 'C:\Users\Hades\anaconda3\envs\eu5\python.exe' scripts/evaluate_historical_images.py
```

API 工具读取配置指定的凭据环境变量（当前为 `IMAGE_API_KEY`）。不要把密钥
写进评估报告或提交到版本控制。生成失败后可以重跑，已保存的图片会保留。

评估产物：

- `sources_contact_sheet.jpg`：20 张输入概览。
- `source_review.json`：逐张源图类型、主体匹配、现代元素和处理建议。
- `index.html`：源图 / 原有纯 AI / 本轮图生图交互对照，可搜索和筛选。
- `comparison_01.jpg` 至 `comparison_04.jpg`：每页五项的静态对照。
- `evaluation.json`：文件摘要、尺寸、宽高比变化及结构相似度诊断。
- `generation_prompt.txt`：当前配置的完整提示词，用于下一次生成；不是已有图片的生成溯源记录。

在尚无 AI 输出时，对照页会显示“等待生成”；这不能算完成生成或完成
输出效果评估。源图评估不等同于输出评估。

人工评估逐项检查：

1. **主体正确**：画面确实对应目标工程，不能将市政厅、寺院等错认成大学
   或使馆。源图错题材时，“忠实保留源图”反而会保留错误。
2. **结构保留**：建筑轮廓、层数、穹顶、倾角、地形或浮雕关系保持可识别，
   轻微视角变化下几何关系仍可信，无臆造的塔楼或重复构件。陪衬增减不算主体失真。
3. **时代可信**：现代高楼、路灯、游客服装、汽车、球场、通信装置等需要
   单独核对；老旧色调、纸纹和暖光不能替代年代考据。真实照片通常记录的是
   现状，画作和重建插画也需要核验作者、年代与出处。
4. **绘画质感**：油画笔触与卡通化造型在缩略图上均可辨认，形状概括、色块清楚、
   明暗成组、描边有选择；避免塑料感、摄影级细节、平滑喷绘、通篇粗描边或单纯纹理滤镜。
5. **游戏可读性**：对照实际 27:11 横幅比例，检查主体是否被截断、是否被
   背景淹没。预览使用居中裁剪压力测试，正式裁剪仍需手工取景。
6. **伟大感**：取景、环境层次、小人物与明暗组织是否强化主体的体量和庄严感；
   是否突破了照片的平铺构图，同时避免用虚构主体结构制造规模。

`evaluation.json` 的 SSIM 只描述源图和输出的视觉接近程度，不判定历史
真实性。图生图可能改变构图或宽高比，所以这里不沿用本地确定性滤镜流程的
0.60 通过阈值；低分需要检查，高分也不能证明题材和时代正确。原有纯 AI
图与新图应分别评价历史特征和游戏表现，再决定是否替换。
