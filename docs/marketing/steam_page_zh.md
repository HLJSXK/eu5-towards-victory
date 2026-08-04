[img]https://i.imgur.com/IUg6ek3.png[/img]
[i]本次更新重点是一些QoL改动，实现了一些小伙伴提出的要求[/i]
[list]
[*] 加入了2个新的通用奇观，并扩展了13处亚洲地区的历史独特奇观
[*] 现在可以拆除已有奇观，也可以通过关闭暂时禁用，作为价值观冲突问题的简易规避措施
[*] 工地在缺少投入品时会放慢进度
[*] 现在当你需要打开工程部页面做些什么时，右上方会有UI提醒
[*] 调整了一批明显存在问题的奇观增益，包括市场吸引力、粮仓等
[*] 使用 [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3692202776] Community Mod Framework (CMF) [/url] 的游戏内菜单功能，可以在一定程度上控制伟大工程的建造难度
[*] 模组现在内置 [b][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3601047146] Glorp UI [/url][/b] 版本的 location window，因此，在置于 GlorpUI（和[b][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3736668860] 建设管理器 [/url][/b]）下方时，将正确显示融合版UI
[/list]
[img]https://i.imgur.com/TnMdbwe.png[/img]
[h2][i]从构想到落成——六个阶段，一座国家级工程。[/i][/h2]

[img]https://i.imgur.com/GdMlBGy.png[/img]

原版 EU5 的奇观只是装饰——一段风味小知识，仅此而已。[b]伟大工程[/b] 把它变成一项真正的国家工程：一个专门负责统筹整个流程的组织、一套每个阶段都有真实代价的建造流程，以及最终揭幕时对全国生效的永久回报。

[img]https://i.imgur.com/cFeHvhv.png[/img]

[i]工程部面板——整个建造流程都在这里追踪。[/i]
[list]
[*] 一个独立的国际组织，[b]工程部[/b]，负责管理整个奇观建造流程
[*] [b]56 种通用奇观[/b]，任何国家均可建造；另有 [b]136 座历史独特奇观[/b]，绑定各自的真实历史地点——亚历山大的法罗斯灯塔、君士坦丁堡的圣索菲亚大教堂、库姆的波斯坎儿井等
[*] 完整的 [b]六阶段建造流程[/b]：构想 → 论证 → 勘测 → 建设 → 仪式 → 落成
[*] 专属的 [b]地图模式[/b]，为全世界已建成的奇观标色——既能规划自己的建造，也能借此侦察他国已建成的奇观、作为征服目标
[*] 配套的 [b]奇观图鉴网站[/b]，无需进入游戏即可在世界地图上浏览全部独特奇观
[/list]

[img]https://i.imgur.com/JKUnW0s.png[/img]

[i]建设——把建材投入奇观的四个组成部分：地基、主体、功能与饰面。[/i]
[olist]
[*] [b]构想[/b] —— 你的伟大工程师会根据国家现状同时提出三个方案，小/中/大型；你可以接受其中一个、重拟（花费声望），或拨款换取全新的一组方案
[*] [b]论证[/b] —— 在建设开始前，需要争取贵族、市民与教会的支持，积累国内支持度（0–200）
[*] [b]勘测[/b] —— 对选定地点评估规模、物流、组织度三项指标；结果会永久锁定奇观的最高等级，以及你此后能达到的最快建造速度
[*] [b]建设[/b] —— 建造配套设施，将建材投入奇观的四个组成部分
[*] [b]仪式[/b] —— 通用奇观可在 3 种风格中挑选；大多数独特奇观则会自动经历一套共通的8阶段仪式，只有法罗斯灯塔与圣索菲亚大教堂这两座拥有完全专属定制的仪式；这一步才真正决定了奇观的最终效果
[*] [b]落成[/b] —— 奇观正式建成，你会获得全国性的庆典增益，落成消息也会作为世界新闻公开播报
[/olist]

[img]https://i.imgur.com/WCc5gTr.png[/img]
[list]
[*] 本模组[b]需要[/b][b][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3692202776] Community Mod Framework (CMF) [/url][/b] 2.x——本模组依赖它提供的回调，在你每次读档时修复自身状态。
[*] [b]存档兼容[/b]：你可以用旧存档添加本mod继续游玩。
[*] [b]最大兼容[/b]：本模组的建造逻辑运行在自己的一套变量上，理论上应该与任何模组兼容。
[*] [b]UI 冲突[/b]：本模组修改了 location_window.gui 与 encyclopedia_lateralview.gui。同样修改这两个文件的其他模组会与本模组互相覆盖。维护中的兼容补丁见 [url=https://steamcommunity.com/workshop/filedetails/?id=3766879023] Great Project - Compatibility Submods [/url]。
[i]注：只影响UI显示。[/i]
[/list]

[img]https://i.imgur.com/9hS7MxD.png[/img]
[list]
[*] 本模组使用 AI 工作流生成海量内容。
[*] 特别感谢 Trinedy 的 [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3668193813] National Destinies [/url]。本项目"LLM 辅助模组制作流程"与"EU5 地图网站"的最初想法都来自于它。
[/list]

[img]https://i.imgur.com/8OwqW49.png[/img]
[list]
[*] [b][url=https://github.com/HLJSXK/eu5-towards-victory/wiki]GitHub wiki: [/url][/b]查看本模组的完整详情。
[*] [b][url=https://hljsxk.github.io/eu5-towards-victory]奇观图鉴网站: [/url][/b]无需进入游戏即可查看奇观数据。
[*] [b][url=https://discord.gg/Yy87G2hBHz]Discord: [/url][/b]欢迎在此服务器讨论与反馈。
[*] [b][url=https://qm.qq.com/q/MY89RweZcO]QQ: [/url][/b]1070041687
[/list]
