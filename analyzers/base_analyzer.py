from abc import ABC, abstractmethod
from collections import Counter
from pathlib import Path
from ncatbot.core import GroupMessageEvent
from typing import Callable, List, Optional, Type

from .render import RenderUserInfo


# 全局分析器注册表
_ANALYZER_REGISTRY: List[Type['BaseAnalyzer']] = []


def register_analyzer(cls: Type['BaseAnalyzer']) -> Type['BaseAnalyzer']:
    """
    装饰器:注册分析器类到全局注册表
    
    使用方法:
    @register_analyzer
    class MyAnalyzer(BaseAnalyzer):
        ...
    
    :param cls: 分析器类
    :return: 原始类(不改变类本身)
    """
    if cls not in _ANALYZER_REGISTRY:
        _ANALYZER_REGISTRY.append(cls)
    return cls


def get_all_analyzers() -> List[Type['BaseAnalyzer']]:
    """
    获取所有已注册的分析器类
    
    :return: 分析器类列表
    """
    return _ANALYZER_REGISTRY.copy()


def clear_registry():
    """清空分析器注册表(主要用于测试)"""
    _ANALYZER_REGISTRY.clear()


class BaseAnalyzer(ABC):
    """分析器基类"""

    _name : str
    _counter : Counter
    _unit: str = "个"
    _custom_image_getter: Optional[Callable[[Path], Path]] = None

    def __init__(self, group_id: str):
        """初始化分析器"""
        self._counter = Counter()
        self._group_id = group_id
    
    def reset(self):
        """重置分析器的统计数据"""
        self._counter.clear()
    
    @abstractmethod
    def process_event(self, event: GroupMessageEvent):
        """
        处理单个消息事件
        
        :param event: 群消息事件
        """
        pass
    
    async def get_result(self) -> List[RenderUserInfo]:
        """
        获取分析结果
        
        :return: 分析结果
        """
        result = self._counter.most_common()
        rui_lst = []
        for count, (uid, time) in enumerate(result):
            rui_lst.append(
                await RenderUserInfo.create(
                    group_id=self._group_id,
                    user_id=uid,
                    rank=count + 1,
                    count=f"{time} {self._unit}"
                )
            )
        return rui_lst
    

    # ======== 属性 ========
    @property
    def name(self) -> str:
        """获取分析器名称"""
        return self._name

    @property
    def is_custom(self) -> bool:
        """是否有自定义图片生成函数"""
        return self._custom_image_getter is not None
    
    @property
    def custom_image_getter(self) -> Optional[Callable[[Path], Path]]:
        """获取自定义图片生成函数"""
        return self._custom_image_getter