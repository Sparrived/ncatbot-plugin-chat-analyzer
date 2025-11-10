from ncatbot.core import GroupMessageEvent
from typing import List, Optional
from pathlib import Path
import re
import jieba
import uuid
from wordcloud import WordCloud
from PIL import Image
from .base_analyzer import BaseAnalyzer, register_analyzer


@register_analyzer
class WordCloudAnalyzer(BaseAnalyzer):
    """词云分析器 - 统计高频词汇并生成词云图片"""
    
    def __init__(self, group_id: str):
        super().__init__(group_id)
        self._name = "高频词云"
        self._stop_words = self._load_stop_words()
        self._custom_image_getter = self.generate_wordcloud_image
    
    def _load_stop_words(self) -> set:
        """加载停用词列表"""
        # 常见的中文停用词
        stop_words = {
            '的', '了', '是', '我', '你', '他', '她', '它', '们',
            '在', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '这', '那',
            '为', '吗', '啊', '吧', '呢', '吧', '嘛', '哦', '哈',
            '额', '嗯', '唔', '诶', '呀', '啦', '哟', '嘞',
            '什么', '怎么', '这个', '那个', '这样', '那样'
        }
        return stop_words
    
    def _extract_words(self, text: str) -> List[str]:
        """
        使用 jieba 从文本中提取词汇
        
        :param text: 原始文本
        :return: 词汇列表
        """
        
        # 移除特殊字符,保留中文、英文、数字和空格
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]+', '', text)
        
        if not text.strip():
            return []
        
        # 使用 jieba 分词
        words = jieba.cut(text)
        
        # 过滤停用词和短词
        filtered_words = [
            word.strip() for word in words 
            if len(word.strip()) >= 2 and word.lower() not in self._stop_words
        ]
        
        return filtered_words
    
    def process_event(self, event: GroupMessageEvent):
        """处理单个消息事件,提取并统计词汇"""
        if not event.raw_message:
            return
        texts = event.message.filter_text()
        all_text = ''.join([plain_text.text for plain_text in texts])
        words = self._extract_words(all_text)
        for word in words:
            self._counter[word] += 1
    
    def get_result(self):
        """
        获取高频词汇(返回前100个)
        
        :return: [(词汇, 出现次数), ...]
        """
        return self._counter.most_common(100)
    
    def generate_wordcloud_image(self, resources_path: Path) -> Path:
        """
        生成词云图片
        
        :return: 图片保存路径
        """
        
        # 尝试加载中文字体
        font_paths = [
        "C:/Windows/Fonts/STXINGKA.TTF",  # 华文行楷 - 可爱手写风格
        "C:/Windows/Fonts/STKAITI.TTF",   # 华文楷体 - 优雅可爱
        "C:/Windows/Fonts/simkai.ttf",    # 楷体 - 清秀可爱
        "C:/Windows/Fonts/STFANGSO.TTF",  # 华文仿宋 - 圆润风格
        "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑 - 备用
        ]
        
        font_path = None
        for path in font_paths:
            if Path(path).exists():
                font_path = path
                break
        
        # 创建词云
        wc = WordCloud(
            font_path=font_path,
            width=800,
            height=450,
            max_words=100,
            min_font_size=10,
            colormap='viridis'  # 可选: viridis, plasma, inferno, magma, rainbow
        )
        
        # 从词频字典生成词云
        word_freq = dict(self._counter.most_common())
        wc.generate_from_frequencies(word_freq)
        # 转换为 PIL Image
        wordcloud_image = wc.to_image()
        # 转换为 RGBA 模式
        wordcloud_image = wordcloud_image.convert("RGBA")
        bg_rgb = (0, 0, 0)
        # 使用 numpy 数组处理
        import numpy as np
        data = np.array(wordcloud_image)
        # 创建 alpha 通道
        # 找出接近背景色的像素
        r, g, b, _ = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
        mask = (np.abs(r - bg_rgb[0]) < 12) & \
                (np.abs(g - bg_rgb[1]) < 12) & \
                (np.abs(b - bg_rgb[2]) < 12)
        # 将背景色的 alpha 设为 0 (透明)
        data[mask, 3] = 0
        wordcloud_image = Image.fromarray(data, 'RGBA')

        output_path = resources_path.parent / f"wordcloud_{uuid.uuid4().hex}.png"        
        wordcloud_image.save(str(output_path), "PNG")
        return output_path
