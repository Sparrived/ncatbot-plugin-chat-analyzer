from ncatbot.core import GroupMessageEvent
from ncatbot.utils import status
from typing import List, Dict, Any
from pathlib import Path

from .base_analyzer import BaseAnalyzer, get_all_analyzers


class ChatAnalysisEngine:
    """聊天分析引擎 - 协调多个分析器,一次遍历完成所有统计"""
    
    def __init__(self, resources_path: Path, group_id: str):
        """初始化分析引擎"""
        self._resources_path = resources_path
        self.analyzers = [cls(group_id) for cls in get_all_analyzers()]
    
    def register_analyzer(self, analyzer: BaseAnalyzer):
        """
        手动注册一个分析器实例
        
        :param analyzer: 分析器实例
        """
        self.analyzers.append(analyzer)
        return self
    
    def analyze(self, events: List[GroupMessageEvent]) -> Dict[str, Any]:
        """
        分析聊天记录,一次遍历完成所有统计
        
        :param events: GroupMessageEvent 对象列表
        :return: 包含所有分析结果的字典,key为分析器名称,value为分析结果
        """
        # 重置所有分析器
        for analyzer in self.analyzers:
            analyzer.reset()
        
        # 一次遍历,让所有分析器处理每个事件
        for event in events:
            for analyzer in self.analyzers:
                analyzer.process_event(event)
        
        # 收集所有分析结果
        results = {}
        for analyzer in self.analyzers:
            if analyzer.is_custom:
                results[analyzer.name] = analyzer.custom_image_getter(self._resources_path)  # type: ignore
            else:
                results[analyzer.name] = analyzer.get_result()
        
        return results
    
    def clear_analyzers(self):
        """清空所有注册的分析器"""
        self.analyzers.clear()
