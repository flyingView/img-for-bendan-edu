<p align="center">
  <img src="assets/brand/banner.png" alt="傻瓜学术绘图" width="100%">
</p>

# img-for-bendan-edu · 傻瓜学术绘图

**让智能体读论文、学好图、反复改，再用软件精细重绘。**

适用于 **Codex、Claude Code、千问办公、Qoder**，同时提供 Qwen Code、QoderWork 安装入口。Skill、模板和部署文档使用英文，你仍可用中文交流，图中文字按论文需要决定。

## 1. 让智能体安装

把本项目的链接或文件夹交给智能体，直接说：

```text
请从 https://github.com/flyingView/img-for-bendan-edu 读取 INSTALL.md，
把 img-for-bendan-edu 安装到你当前使用的客户端，并检查是否能加载。
```

也可以在项目目录运行一条命令，将平台名换成 `codex`、`claude-code`、`qwen-work` 或 `qoder`：

```bash
python scripts/install.py --agent codex
```

安装后让客户端重新加载技能或新开会话。完整安装方式见 [INSTALL.md](INSTALL.md)。

卸载时通过客户端移除技能，或删除安装位置的整个 `img-for-bendan-edu` 文件夹；论文中的绘图成果仍会保留。

支持本地导入的客户端，也可以使用 [最新版 Skill 安装包](https://github.com/flyingView/img-for-bendan-edu/releases/latest/download/img-for-bendan-edu.zip)。

## 2. 给论文，说需求

**画指定的一张图：**

```text
使用 img-for-bendan-edu，阅读这篇论文，给方法章节画一张总体架构图。
重点讲清楚模块之间的关系，交付终稿和可编辑源文件。
```

**让智能体寻找配图位置：**

```text
使用 img-for-bendan-edu，通读这篇论文，在最值得用图解释的位置设计配图，并插入可编辑稿件。
```

新任务会先问两个数：**参考几篇论文、返工几轮**。推荐和未回答时的默认值是 **20 篇、5 轮**；也可以直接说“12 篇、3 轮”。生成草图数是 **返工轮数＋1**，之后再用软件重绘终稿。继续修改已有图片时沿用原设置。

## 3. 等它交付，再提修改

**理解论文 → 按优先级找参考 → 下载 PDF、提取图例 → 总结风格 → 生图 → 对照返工 → 软件重绘 → 交付。**

参考优先级：同领域同细方向经典论文 ＞ 同方向近1—3个月优质论文 ＞ 同领域其他细方向经典论文。

Skill 自带的脚本、模板和参考指南都装在客户端的同一个技能文件夹中。绘图时，每张图的资料集中放在论文项目的 `重型绘图任务/imgN/`。

交付后保留终稿、源码和必要数据，把参考 PDF、草图和返工记录压缩为 `process.zip`，核对完整后清理过程目录与临时缓存。后续直接说“修改 img1 的图例/配色/布局”即可；过程记录仍可从压缩包中查看。

图面要求：**不放小字说明，不写边界或防御性文案，不堆 AI 小图标；表达简洁，图例清晰，色调美观。** 最终版本由代码或绘图软件重绘。

绘图使用客户端已有的搜索、看图、生图和软件执行能力。本项目提供工作流，不绑定特定模型，也不要求安装其他 Skill。

[查看英文 Skill](SKILL.md) · [高星项目借鉴记录](docs/research-notes.md) · [MIT 许可证](LICENSE)
