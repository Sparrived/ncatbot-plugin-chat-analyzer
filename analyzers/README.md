# 聊天分析器使用说明

## 架构设计

这是一个可扩展的聊天分析系统,通过**一次遍历**完成所有统计任务。

### 核心组件

1. **BaseAnalyzer** - 分析器基类,定义统一接口
2. **具体分析器** - 实现特定的统计功能
   - `ImageAnalyzer` - 统计发图次数
   - `EmoticonAnalyzer` - 统计发送表情包次数
   - `ActiveSenderAnalyzer` - 统计发言次数
3. **ChatAnalysisEngine** - 分析引擎,协调所有分析器

## 使用方法

### 基础使用(自动注册)

```python
from .analyzers import ChatAnalysisEngine

# 创建分析引擎(自动注册所有已装饰的分析器)
engine = ChatAnalysisEngine()

# 获取聊天记录
chat_histories = await self._get_chat_history(str(event.group_id), "22:00")

# 一次遍历完成所有分析
results = engine.analyze(chat_histories)

# 获取结果
image_ranking = results["image_senders"]  # [(qq号, 次数), ...]
emoticon_ranking = results["emoticon_senders"]
active_ranking = results["active_senders"]

# 处理结果
if image_ranking:
    top_imager = image_ranking[0]
    await event.reply(f"发图冠军: {top_imager[0]}, 发了 {top_imager[1]} 张图喵~")
```

### 手动控制(不自动注册)

```python
from .analyzers import ChatAnalysisEngine, ImageAnalyzer, ActiveSenderAnalyzer

# 创建分析引擎,关闭自动注册
engine = ChatAnalysisEngine(auto_register=False)

# 手动注册需要的分析器
engine.register_analyzer(ImageAnalyzer())
engine.register_analyzer(ActiveSenderAnalyzer())

# 分析(只会运行已注册的分析器)
results = engine.analyze(chat_histories)
```

### 创建自定义分析器

**方式1: 使用装饰器自动注册(推荐)**

```python
# 在新文件 analyzers/link_analyzer.py 中
from .base_analyzer import BaseAnalyzer, register_analyzer
from collections import Counter

@register_analyzer  # 使用装饰器自动注册
class LinkAnalyzer(BaseAnalyzer):
    """链接分析器 - 统计发送链接的次数"""
    
    def reset(self):
        """重置统计数据"""
        self.link_counter = Counter()
    
    def process_event(self, event):
        """处理单个消息事件"""
        # 统计发送链接的次数
        if 'http://' in event.raw_message or 'https://' in event.raw_message:
            self.link_counter[str(event.user_id)] += 1
    
    def get_result(self):
        """返回分析结果"""
        if not self.link_counter:
            return []
        return self.link_counter.most_common()
    
    def get_name(self) -> str:
        """返回分析器名称(用作结果字典的key)"""
        return "link_senders"

# 在 __init__.py 中导入一次即可自动注册
from .link_analyzer import LinkAnalyzer

# 使用时无需手动注册,直接创建引擎即可
engine = ChatAnalysisEngine()  # LinkAnalyzer 已自动注册
results = engine.analyze(chat_histories)
link_ranking = results["link_senders"]
```

**方式2: 手动注册**

```python
# 不使用装饰器
class CustomAnalyzer(BaseAnalyzer):
    """自定义分析器"""
    # ... 实现各个方法 ...

# 手动注册
engine = ChatAnalysisEngine(auto_register=False)
engine.register_analyzer(CustomAnalyzer())
```

## 优势

1. **高效** - 只需一次遍历,O(n)时间复杂度
2. **可扩展** - 轻松添加新的分析器,无需修改现有代码
3. **灵活** - 可以动态注册/注销分析器
4. **解耦** - 各个分析器独立开发,互不干扰
5. **自动化** - 使用装饰器自动注册,无需手动管理分析器列表


## 添加新分析器的步骤

1. 创建新文件,例如 `analyzers/my_analyzer.py`
2. 定义类并使用 `@register_analyzer` 装饰
3. 实现必要方法
4. 在 `analyzers/__init__.py` 中导入你的类
