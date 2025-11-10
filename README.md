<div align="center">
<h1>✨ncatbot - ChatAnalyzer 插件✨</h1>

一个功能强大的 NcatBot 群聊分析插件，提供多维度聊天数据统计、词云生成、活跃度分析等可视化能力。


[![License](https://img.shields.io/badge/License-MIT_License-green.svg)](https://github.com/Sparrived/ncatbot-plugin-chat-analyzer/blob/master/LICENSE)
[![ncatbot version](https://img.shields.io/badge/ncatbot->=4.3.0-blue.svg)](https://github.com/liyihao1110/ncatbot)
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)](https://github.com/Sparrived/ncatbot-plugin-chat-analyzer/releases)


</div>


---

## 🌟 功能亮点

- 📊 **话痨排行** - 统计群内发言次数最多的用户
- 💬 **字数统计** - 分析每位成员的发言字数
- 📸 **图片分享** - 统计群内图片分享最多的用户
- 😂 **表情包王** - 分析谁是群里的表情包大师
- ☁️ **词云生成** - 自动生成高频词汇词云图，直观展示聊天热词
- 📈 **词性分析** - 统计群聊中不同词性的使用频率（名词、动词、形容词等）
- ⏰ **小时活跃度** - 按时间段展示24小时聊天活跃度分布
- 🎨 **蜡笔风格** - 独特的手绘蜡笔风格图表，让数据更生动
- 📅 **自动推送** - 支持定时自动生成并推送每日/每周群聊总结

## ⚙️ 配置项

配置文件位于 `data/ChatAnalyzer/ChatAnalyzer.yaml`

| 配置键               | 类型        | 默认值          | 说明                                                     |
| -------------------- | ----------- | --------------- | -------------------------------------------------------- |
| `subscribed_groups`  | `List[str]` | `['123456789']` | 插件生效的群号白名单。只有在此列表中的群组才会处理命令。 |
| `auto_push.enabled`  | `bool`      | `false`         | 是否启用自动推送功能。                                   |
| `auto_push.time`     | `str`       | `"23:59"`       | 自动推送时间，格式为 `HH:MM`。                           |
| `auto_push.interval` | `str`       | `"daily"`       | 推送间隔，可选值：`daily`（每日）、`weekly`（每周）。    |

**配置示例:**
```yaml
subscribed_groups:
- '123456789'
- '987654321'
auto_push:
  enabled: true
  time: "23:59"
  interval: "daily"
```

> **提示:** 配置文件可通过 NcatBot 的统一配置机制进行覆盖。建议使用 `/ca subscribe` 命令动态添加群组，避免手动修改配置后需要重启机器人。

## 🚀 快速开始

### 依赖要求

- Python >= 3.8
- NcatBot >= 4.2.9
- 第三方依赖：
  - `jieba` - 中文分词
  - `wordcloud` - 词云生成
  - `pillow` - 图像处理
  - `pillowmd` - Markdown 渲染

### 使用 Git

```bash
git clone https://github.com/Sparrived/ncatbot-plugin-chat-analyzer.git
cd ncatbot-plugin-chat-analyzer
pip install -r plugins/chat_analyzer/requirements.txt
cp -r plugins/chat_analyzer /path/to/your/ncatbot/plugins/
```

> 请将 `/path/to/your/ncatbot/plugins/` 替换为机器人实际的插件目录。

### 自主下载

1. 将本插件目录置于 `plugins/chat_analyzer`。
2. 安装依赖：`pip install -r plugins/chat_analyzer/requirements.txt`
3. 根据实际需要调整 `subscribed_groups` 等配置项（建议在群内使用指令调整，手动调整config需要重启机器人）。
4. 重启 NcatBot，插件将自动加载。

### 插件指令

> **注意事项:**
> - 所有指令仅限 NcatBot 管理员用户使用（`admin_group_filter` 限制）
> - 分析功能需要先订阅群组才能生效
> - 首次使用建议订阅后等待一段时间收集聊天数据

| 指令                  | 参数                                     | 说明                                                       | 示例                              |
| --------------------- | ---------------------------------------- | ---------------------------------------------------------- | --------------------------------- |
| `/ca analyze [hours]` | `hours`：可选，统计时长（小时），默认 24 | 分析指定时间段内的群聊数据，生成包含多维度统计的可视化报告 | `/ca analyze`<br>`/ca analyze 48` |
| `/ca subscribe`       | 无                                       | 订阅当前群的聊天分析功能，开始收集聊天数据                 | `/ca subscribe`                   |
| `/ca unsubscribe`     | 无                                       | 取消当前群的订阅，停止收集聊天数据                         | `/ca unsubscribe`                 |
| `/ca help [command]`  | `command`：可选，指定命令名              | 显示所有可用指令或指定命令的详细说明                       | `/ca help`<br>`/ca help analyze`  |

## 📊 分析维度

### 用户行为分析
- **💬 话痨之王** - 发言次数统计，展示前三名活跃用户
- **📝 字数统计** - 发言总字数排行，分析谁最能"水"
- **📸 图片分享达人** - 图片发送次数统计
- **😂 表情包大王** - 表情包使用频率分析

### 内容分析
- **☁️ 高频词云** - 使用 jieba 分词生成词云图，透明背景设计，自动过滤停用词
- **📈 词性分布** - 分析群聊中名词、动词、形容词等词性的使用情况（前3名），蜡笔风格横向条形图

### 时间分析
- **⏰ 小时活跃度** - 24小时活跃度分布，蜡笔风格色块展示，按时间顺序排列，每2小时显示一个时间标签

## 🎨 视觉特色

### 蜡笔手绘风格
- 所有图表采用独特的蜡笔手绘风格
- 不规则边缘和随机纹理增加真实感
- 柔和的色彩搭配，观感舒适
- 透明背景设计，便于与其他元素组合

### Markdown 渲染
- 使用 pillowmd 库进行高质量 Markdown 渲染
- 支持自定义样式（mdstyle 文件夹）
- 头像、图表、文字完美融合
- 输出 PNG 格式图片，便于分享

## 🧠 运作逻辑

### 订阅机制
- 插件在执行命令前，会先检查群组是否在 `subscribed_groups` 配置列表中
- 对于未订阅的群组，插件会跳过处理，并提示先使用 `/ca subscribe` 订阅
- 使用 `/ca subscribe` 可快速将当前群添加到白名单，无需重启机器人

### 数据收集流程
- 通过 ncatbot 的历史聊天记录接口获取24小时内的所有聊天记录，并通过analyzer进行分析

### 分析流程
1. 接收到 `/ca analyze` 命令
2. 从数据库中读取指定时间段的聊天记录
3. 初始化所有注册的分析器（话痨、图片、词云等）
4. 一次遍历完成所有统计（高效处理）
5. 生成可视化图表
6. 使用 Markdown 渲染生成最终报告
7. 发送到群聊

### 性能优化
- **LRU 缓存**: jieba 分词结果使用 LRU 缓存，相同文本只处理一次
- **一次遍历**: 所有分析器共享同一次数据遍历，避免重复读取
- **懒加载**: 只在需要时才加载字体和生成图表
- **异步处理**: 图片生成和渲染使用异步方式，不阻塞主线程

## 🪵 日志与排错

插件使用 NcatBot 的统一日志系统，所有操作都会记录详细日志。

### 查看日志
```bash
# 日志文件位置
logs/bot.log.YYYY_MM_DD

# 筛选 ChatAnalyzer 相关日志
grep "ChatAnalyzer" logs/bot.log.2025_11_10
```

### 常见问题

**Q: 为什么指令没有响应？**
- 检查当前群是否已订阅（使用 `/ca subscribe`）
- 确认发送指令的用户是否在 NcatBot 的管理员列表中
- 查看日志确认是否有错误信息

**Q: 词云生成失败？**
- 确保已安装 `wordcloud` 库：`pip install wordcloud`
- 检查系统是否有中文字体（Windows: simkai.ttf 或 msyh.ttc）
- 确认有足够的聊天数据（至少需要一些包含文字的消息）

**Q: 分析结果为空？**
- 确认指定的时间段内有聊天记录
- 检查数据库文件是否正常（`data/ChatAnalyzer/chat_records.db`）
- 尝试增加分析时长（如 `/ca analyze 48`）

**Q: 图片渲染失败？**
- 确保已安装所有依赖：`pip install -r requirements.txt`
- 检查 `data/ChatAnalyzer/resources/mdstyle` 目录是否完整
- 查看日志中的详细错误信息

**Q: 自动推送不工作？**
- 检查 `auto_push.enabled` 配置是否为 `true`
- 确认 `auto_push.time` 格式正确（HH:MM）
- 检查日志确认定时任务是否正常启动

**Q: 小时活跃度时间显示不对？**
- 小时活跃度图会从当前统计开始时间展示连续24小时
- 时间标签每2小时显示一次（0, 2, 4, 6, ...）
- 色块按时间顺序从左到右排列，颜色深浅表示活跃程度

## 🤝 贡献

欢迎通过 Issue 或 Pull Request 分享改进建议、提交补丁！

### 贡献指南
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范
- 遵循 PEP 8 Python 代码风格
- 添加必要的注释和文档字符串
- 确保代码通过基本功能验证
- 新增分析器需要继承 `BaseAnalyzer` 类并使用 `@register_analyzer` 装饰器

### 添加新的分析器

如果想添加新的分析维度，可以参考以下步骤：

```python
from .base_analyzer import BaseAnalyzer, register_analyzer

@register_analyzer
class YourAnalyzer(BaseAnalyzer):
    """你的分析器说明"""
    
    def __init__(self, group_id: str):
        super().__init__(group_id)
        self._name = "分析器名称"
        self._unit = "单位"
    
    def process_event(self, event: GroupMessageEvent):
        """处理每条消息"""
        # 你的统计逻辑
        pass
    
    async def get_result(self):
        """返回分析结果"""
        # 返回 List[RenderUserInfo]
        pass
```

## 🙏 致谢

感谢以下项目和贡献者：

- [NcatBot](https://github.com/liyihao1110/ncatbot) - 提供稳定易用的 OneBot11 Python SDK
- [jieba](https://github.com/fxsjy/jieba) - 优秀的中文分词库
- [wordcloud](https://github.com/amueller/word_cloud) - 强大的词云生成工具
- [pillowmd](https://github.com/FlechazoPh/PillowMd) - Markdown 图像渲染库
- 社区测试者与维护者 - 提交 Issue、Pull Request 以及改进建议

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

<div align="center">

如果本插件帮助到了你，欢迎为项目点亮 ⭐ Star！

[报告问题](https://github.com/Sparrived/ncatbot-plugin-chat-analyzer/issues) · [功能建议](https://github.com/Sparrived/ncatbot-plugin-chat-analyzer/issues) · [查看发布](https://github.com/Sparrived/ncatbot-plugin-chat-analyzer/releases)

</div>
