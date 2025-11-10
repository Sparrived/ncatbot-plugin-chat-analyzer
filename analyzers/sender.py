from ncatbot.core import GroupMessageEvent
from .base_analyzer import BaseAnalyzer, register_analyzer


@register_analyzer
class ActiveSenderAnalyzer(BaseAnalyzer):
    """发言活跃度分析器 - 统计发言次数"""
    
    def __init__(self, group_id: str):
        super().__init__(group_id) 
        self._name = "话痨之王"
        self._unit = "条"
    
    def process_event(self, event: GroupMessageEvent):
        """处理单个消息事件,统计发言"""
        self._counter[str(event.user_id)] += 1


@register_analyzer
class WordCountAnalyzer(BaseAnalyzer):
    """字数统计分析器 - 统计单条消息最长字数"""
    
    def __init__(self, group_id: str):
        super().__init__(group_id)
        self._name = "长文写手"
        self._unit = "字"
    
    def process_event(self, event: GroupMessageEvent):
        """处理单个消息事件,记录单条消息最长字数"""
        # 获取纯文本内容
        texts = event.message.filter_text()
        total_chars = sum(len(plain_text.text) for plain_text in texts)
        
        if total_chars > 0:
            user_id = str(event.user_id)
            # 只保留该用户发送过的最长的单条消息字数
            self._counter[user_id] = max(self._counter[user_id], total_chars)
    
