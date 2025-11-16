<div align="center">
<h1>✨ncatbot - ChatAnalyzer 插件✨</h1>

一个功能强大的 NcatBot 群聊分析插件，提供多维度聊天数据统计、词云生成、活跃度分析等可视化能力。


[![License](https://img.shields.io/badge/License-MIT_License-green.svg)](https://github.com/Sparrived/ncatbot-plugin-chat-analyzer/blob/master/LICENSE)
[![ncatbot version](https://img.shields.io/badge/ncatbot->=4.3.0-blue.svg)](https://github.com/liyihao1110/ncatbot)
[![Version](https://img.shields.io/badge/version-1.0.6-orange.svg)](https://github.com/Sparrived/ncatbot-plugin-chat-analyzer/releases)


</div>


---

## 🌟 功能亮点

- 📊 **话痨排行** - 统计群内发言次数最多的用户
- 💬 **字数统计** - 分析每位成员的发言字数
- 📸 **图片分享** - 统计群内图片分享最多的用户
- 😂 **表情包王** - 分析谁是群里的表情包大师
- ☁️ **词云生成** - 自动生成高频词汇词云图，直观展示聊天热词
- 📈 **词性分析** - 统计群聊中不同词性的使用频率（名词、动词、形容词等）
- ⏰ **小时活跃度** - 按时间段展示聊天活跃度分布
- 🎨 **蜡笔风格** - 独特的手绘蜡笔风格图表，让数据更生动
- 📅 **自动推送** - 支持定时自动生成并推送群聊总结，可配置多个时间点

## ⚙️ 配置项

配置文件位于 `data/ChatAnalyzer/ChatAnalyzer.yaml`

| 配置键                  | 类型        | 默认值          | 说明                                                     |
| ----------------------- | ----------- | --------------- | -------------------------------------------------------- |
| `subscribed_groups`     | `List[str]` | `['123456789']` | 插件生效的群号白名单。只有在此列表中的群组才会处理命令。 |
| `analysis_time`         | `List[str]` | `['22:00']`     | 自动分析时间点列表，格式为 `HH:MM`，支持多个时间点。     |
| `analysis_duration`     | `int`       | `1440`          | 分析时长（分钟），默认 1440 分钟（24 小时）。            |
| `minimum_message_count` | `int`       | `10`            | 进行分析所需的最小消息数量。                             |

**配置示例:**
```yaml
subscribed_groups:
  - '123456789'
  - '987654321'
analysis_time:
  - "22:00"
  - "23:59"
analysis_duration: 1440
minimum_message_count: 10
```

> **提示:** 
> - 配置文件可通过 NcatBot 的统一配置机制进行覆盖
> - 建议使用 `/ca subscribe` 命令动态添加群组，避免手动修改配置后需要重启机器人
> - `analysis_time` 支持配置多个时间点，插件会在每个时间点自动发送分析报告
> - `analysis_duration` 为分析的时长，从指定时间点往前推算

## 🚀 快速开始

### 依赖要求

- Python >= 3.8
- NcatBot >= 4.3.0
- 第三方依赖：
  - `pillowmd` - Markdown 渲染
  - `aiohttp` - 异步 HTTP 请求
  - `wordcloud` - 词云生成
  - `jieba` - 中文分词

### 使用 Git

```bash
git clone https://github.com/Sparrived/ncatbot-plugin-chat-analyzer.git
cd ncatbot-plugin-chat-analyzer
pip install -r plugins/chat_analyzer/requirements.txt
cp -r plugins/chat_analyzer /path/to/your/ncatbot/plugins/
```
**⚠️ 重要：将 `resources.zip` 解压到 `data/ChatAnalyzer/` 目录下**（解压后应该有 `data/ChatAnalyzer/resources/` 文件夹）

> 请将 `/path/to/your/ncatbot/plugins/` 替换为机器人实际的插件目录。

### 自主下载

1. 将本插件目录置于 `plugins/chat_analyzer`。
2. 安装依赖：`pip install -r plugins/chat_analyzer/requirements.txt`
3. **⚠️ 重要：将 `resources.zip` 解压到 `data/ChatAnalyzer/` 目录下**（解压后应该有 `data/ChatAnalyzer/resources/` 文件夹）
4. 根据实际需要调整 `subscribed_groups` 等配置项（建议在群内使用指令调整，手动调整config需要重启机器人）。
5. 重启 NcatBot，插件将自动加载。

### 插件指令

> **注意事项:**
> - 所有指令仅限 NcatBot 管理员用户使用（`admin_group_filter` 限制）
> - 分析功能需要先订阅群组才能生效
> - 插件会自动从 OneBot11 API 获取历史聊天记录，无需手动收集数据

| 指令                            | 参数                                                                                           | 说明                                                       | 示例                                                              |
| ------------------------------- | ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------- |
| `/ca analyze [time] [duration]` | `time`：可选，分析时间点(HH:MM)，默认当前时间<br>`duration`：可选，分析时长（分钟），默认 1440 | 分析指定时间段内的群聊数据，生成包含多维度统计的可视化报告 | `/ca analyze`<br>`/ca analyze 22:00 1440`<br>`/ca analyze "" 720` |
| `/ca subscribe`                 | 无                                                                                             | 订阅当前群的聊天分析功能，加入自动推送白名单               | `/ca subscribe`                                                   |
| `/ca unsubscribe`               | 无                                                                                             | 取消当前群的订阅，移出自动推送白名单                       | `/ca unsubscribe`                                                 |
| `/ca help [command]`            | `command`：可选，指定命令名                                                                    | 显示所有可用指令或指定命令的详细说明                       | `/ca help`<br>`/ca help analyze`                                  |

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
- 订阅的群组会在配置的 `analysis_time` 时间点自动接收分析报告

### 数据收集流程
- 通过 ncatbot API 的 `get_group_msg_history` 接口实时获取历史聊天记录
- 支持自定义时间范围，从指定时间点往前推算指定时长的聊天记录
- 采用智能递归获取策略，自动处理分页，确保获取到完整的时间范围内的所有消息
- 使用二分查找算法快速定位目标时间范围，提高查询效率

### 分析流程
1. 接收到 `/ca analyze` 命令或触发自动推送任务
2. 通过 ncatbot API 获取指定时间段的聊天记录
3. 验证消息数量是否满足最小要求（`minimum_message_count`）
4. 初始化所有注册的分析器（话痨、图片、词云、词性、时间等）
5. 一次遍历完成所有统计（高效处理）
6. 生成可视化图表（词云、词性分布、小时活跃度）
7. 使用 Markdown 渲染生成最终报告
8. 转换为 Base64 图片并发送到群聊

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

**Q: 提示"未能获取到聊天记录"？**
- 检查机器人是否有获取群聊天记录的权限
- 尝试减少分析时长或调整时间点
- 查看日志确认 API 调用是否成功

**Q: 提示"聊天记录数量不足"？**
- 默认需要至少 10 条消息才能进行分析
- 可以通过修改 `minimum_message_count` 配置项调整阈值
- 尝试增加分析时长以获取更多消息

**Q: 词云生成失败？**
- 确保已安装 `wordcloud` 库：`pip install wordcloud`
- 检查系统是否有中文字体（Windows: simkai.ttf 或 msyh.ttc）
- 确认有足够的文字消息（纯图片/表情包无法生成词云）

**Q: 图片渲染失败？**
- 确保已安装所有依赖：`pip install -r requirements.txt`
- 检查 `data/ChatAnalyzer/resources/mdstyle` 目录是否完整
- 查看日志中的详细错误信息

**Q: 自动推送不工作？**
- 检查 `analysis_time` 配置是否正确（格式：HH:MM）
- 确认目标群组是否在 `subscribed_groups` 列表中
- 查看日志确认定时任务是否正常注册和触发
- 注意：修改配置后需要重启机器人

**Q: 小时活跃度时间显示不对？**
- 小时活跃度图会从指定时间点往前推算显示连续时间段
- 时间标签每2小时显示一次
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
- [pillowmd](https://github.com/Monody-S/CustomMarkdownImage) - Markdown 图像渲染库
- 社区测试者与维护者 - 提交 Issue、Pull Request 以及改进建议

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

<div align="center">

如果本插件帮助到了你，欢迎为项目点亮 ⭐ Star！

[报告问题](https://github.com/Sparrived/ncatbot-plugin-chat-analyzer/issues) · [功能建议](https://github.com/Sparrived/ncatbot-plugin-chat-analyzer/issues) · [查看发布](https://github.com/Sparrived/ncatbot-plugin-chat-analyzer/releases)

</div>
