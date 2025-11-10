from ncatbot.core import GroupMessageEvent
from typing import List
from collections import Counter
import re
from .base_analyzer import BaseAnalyzer, register_analyzer


@register_analyzer
class ImageAnalyzer(BaseAnalyzer):
    """图片分析器 - 统计发图次数"""
    
    def __init__(self, group_id: str):
        super().__init__(group_id) 
        self._name = "图片分享达人"
        self._unit = "张"
    
    def process_event(self, event: GroupMessageEvent):
        """处理单个消息事件,统计图片"""
        if '[CQ:image' in event.raw_message:
            # 计算该消息中的图片数量
            image_count = len(re.findall(r'\[CQ:image[^\]]*\]', event.raw_message))
            if image_count > 0:
                self._counter[str(event.user_id)] += image_count


@register_analyzer
class EmoticonAnalyzer(BaseAnalyzer):
    """表情包分析器 - 统计发送表情包(动画表情)次数"""

    def __init__(self, group_id: str):
        super().__init__(group_id) 
        self._name = "表情包大王"
        self._unit = "张"
    
    def process_event(self, event: GroupMessageEvent):
        """处理单个消息事件,统计表情包"""
        # 查找包含 summary=["动画表情"] 的图片 CQ 码
        emoticon_pattern = r'\[CQ:image[^\]]*summary=&#91;动画表情&#93;[^\]]*\]'
        emoticon_count = len(re.findall(emoticon_pattern, event.raw_message))
        
        if emoticon_count > 0:
            self._counter[str(event.user_id)] += emoticon_count
