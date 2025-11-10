from ncatbot.core import GroupMessageEvent
from ncatbot.utils import get_log
from typing import List, Dict
from pathlib import Path
import base64
from io import BytesIO

from .base_analyzer import BaseAnalyzer, get_all_analyzers
from .render import RenderUserInfo, render_analysis_result, RenderInfo

LOG = get_log("ChatAnalyzerEngine")

class ChatAnalysisEngine:
    """聊天分析引擎 - 协调多个分析器,一次遍历完成所有统计"""
    
    def __init__(self, resources_path: Path, group_id: str, render_info: RenderInfo):
        """初始化分析引擎"""
        self._resources_path = resources_path
        self.analyzers = [cls(group_id) for cls in get_all_analyzers()]
        self._render_info = render_info
    
    def register_analyzer(self, analyzer: BaseAnalyzer):
        """
        手动注册一个分析器实例
        
        :param analyzer: 分析器实例
        """
        self.analyzers.append(analyzer)
        return self
    
    async def analyze(self, events: List[GroupMessageEvent], retry: int = 0) -> str:
        """
        分析聊天记录,一次遍历完成所有统计
        
        :param events: GroupMessageEvent 对象列表
        :return: base64 字符串
        """
        if retry > 3:
            LOG.error("分析重试次数过多，终止分析")
            raise RuntimeError("分析重试次数过多，终止分析")
        # 重置所有分析器
        for analyzer in self.analyzers:
            analyzer.reset()
        
        # 一次遍历,让所有分析器处理每个事件
        for event in events:
            for analyzer in self.analyzers:
                analyzer.process_event(event)
        
        # 收集所有分析结果
        results: Dict[str, List[RenderUserInfo] | Path] = {}
        for analyzer in self.analyzers:
            if analyzer.is_custom:
                results[analyzer.name] = analyzer.custom_image_getter(self._resources_path)  # type: ignore
            else:
                results[analyzer.name] = await analyzer.get_result()

        images = await render_analysis_result(self._render_info, results, resources_path=self._resources_path)

        if not images:
            LOG.warning("分析结果图片生成失败，重试中...")
            return await self.analyze(events, retry=retry + 1)
        
        buffered = BytesIO()
        images[0].save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return img_str
    
    def clear_analyzers(self):
        """清空所有注册的分析器"""
        self.analyzers.clear()
