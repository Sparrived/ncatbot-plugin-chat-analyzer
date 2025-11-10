from ncatbot.core import GroupMessageEvent
from typing import Tuple
from pathlib import Path
import re
import jieba.posseg as pseg
import uuid
from functools import lru_cache
from wordcloud import WordCloud
from PIL import Image, ImageDraw, ImageFont
from .base_analyzer import BaseAnalyzer, register_analyzer
from .crayon_utils import draw_crayon_rectangle


# 停用词列表（两个分析器共享）
STOP_WORDS = {
    '一个', '什么', '怎么', '这个', '那个', '这样', '那样'
}


@lru_cache(maxsize=None)
def extract_words_with_pos(text: str) -> Tuple[Tuple[str, str], ...]:
    """
    使用 jieba 从文本中提取词汇和词性（两个分析器共享）
    使用 LRU 缓存避免重复计算相同文本
    maxsize=None 表示无限缓存，因为在单次分析会话中，每条消息只会被处理一次
    
    :param text: 原始文本
    :return: ((词汇, 词性), ...) 元组（用于缓存）
    """
    # 移除特殊字符,保留中文、英文、数字和空格
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]+', '', text)
    
    if not text.strip():
        return ()
    
    # 使用 jieba 进行词性标注（一次调用，返回词和词性）
    words_with_pos = pseg.cut(text)
    
    # 过滤停用词和短词
    filtered_results = tuple(
        (word.strip(), flag) for word, flag in words_with_pos
        if len(word.strip()) >= 2 and word.lower() not in STOP_WORDS
    )
    
    return filtered_results


@register_analyzer
class PartOfSpeechAnalyzer(BaseAnalyzer):
    """词性分析器 - 统计不同词性的使用频率"""
    
    # 词性中文映射
    POS_NAMES = {
        'n': '名词',
        'v': '动词',
        'a': '形容词',
        'd': '副词',
        'p': '介词',
        'c': '连词',
        'u': '助词',
        'm': '数词',
        'q': '量词',
        'r': '代词',
        'e': '叹词',
        'o': '拟声词',
        'i': '成语',
        'j': '简称',
        'l': '习语',
        'x': '其他',
    }
    
    def __init__(self, group_id: str):
        super().__init__(group_id)
        self._name = "词性分布"
        self._unit = "次"
        self._custom_image_getter = self._generate_pos_chart
    
    def process_event(self, event: GroupMessageEvent):
        """处理单个消息事件，提取并统计词性"""
        if not event.raw_message:
            return
        
        texts = event.message.filter_text()
        all_text = ""
        for plain_text in texts:
            if plain_text.text.startswith('/'):
                continue  # 忽略命令消息
            all_text += plain_text.text + " "
        
        # 使用共享的文本处理函数（只调用一次jieba）
        words_with_pos = extract_words_with_pos(all_text)
        
        for _, flag in words_with_pos:  # 只使用词性，忽略词
            # 提取词性的首字母（jieba的词性标注可能有子类）
            pos = flag[0] if flag else 'x'
            pos_name = self.POS_NAMES.get(pos, '其他')
            self._counter[pos_name] += 1
    
    
    def _generate_pos_chart(self, resources_path: Path) -> Path:
        """
        生成词性分布条形图
        
        :param resources_path: 资源文件夹路径
        :return: 生成的图片路径
        """
        # 图表配置
        width = 960
        height = 240
        padding_x = 100
        padding_y = 40
        bar_spacing = 15
        
        # 获取前3个词性
        top_pos = self._counter.most_common(3)
        if not top_pos:
            # 如果没有数据，创建一个空白图片
            img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            output_path = resources_path.parent / "temp" / f"pos_chart_{uuid.uuid4().hex}.png"
            img.save(output_path, "PNG")
            return output_path
        
        # 创建画布
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 加载字体
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
        ]
        
        font = None
        font_large = None
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 14)
                font_large = ImageFont.truetype(font_path, 16)
                break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
            font_large = font
        
        # 计算最大值用于缩放
        max_count = max(count for _, count in top_pos)
        
        # 计算条形图区域
        chart_height = height - 2 * padding_y
        bar_height = (chart_height - (len(top_pos) - 1) * bar_spacing) / len(top_pos)
        max_bar_width = width - 2 * padding_x - 100  # 留出标签空间
        
        # 颜色方案（蜡笔色系 - 柔和的颜色）
        colors = [
            (255, 138, 128),  # 珊瑚红
            (255, 179, 128),  # 桃色
            (255, 218, 128),  # 杏色
            (240, 230, 140),  # 卡其黄
            (189, 252, 201),  # 薄荷绿
            (144, 238, 144),  # 浅绿
            (135, 206, 235),  # 天蓝
            (173, 216, 230),  # 浅蓝
            (176, 196, 222),  # 浅钢蓝
            (221, 160, 221),  # 梅红
        ]
        
        # 绘制条形图（蜡笔风格）
        y = padding_y
        for idx, (pos_name, count) in enumerate(top_pos):
            # 计算条形宽度
            bar_width = (count / max_count) * max_bar_width if max_count > 0 else 0
            
            # 选择颜色（使用柔和的蜡笔色系）
            color = colors[idx % len(colors)]
            
            # 绘制蜡笔风格的条形
            if bar_width > 1:
                draw_crayon_rectangle(
                    draw,
                    x=padding_x,
                    y=y,
                    width=bar_width,
                    height=bar_height,
                    base_color=color,
                    orientation="horizontal"
                )
            
            # 绘制词性名称（左侧）
            text_bbox = draw.textbbox((0, 0), pos_name, font=font_large)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = padding_x - text_width - 15
            text_y = y + (bar_height - text_height) / 2
            draw.text((text_x, text_y), pos_name, font=font_large, fill=(80, 80, 80, 255))
            
            # 绘制数量（条形右侧）
            count_text = str(count)
            count_bbox = draw.textbbox((0, 0), count_text, font=font)
            count_width = count_bbox[2] - count_bbox[0]
            count_height = count_bbox[3] - count_bbox[1]
            
            if bar_width > count_width + 30:
                # 如果条形足够宽，显示在内部右侧
                count_x = padding_x + bar_width - count_width - 10
                count_color = (255, 255, 255, 255)
            else:
                # 否则显示在条形右侧
                count_x = padding_x + bar_width + 8
                count_color = (80, 80, 80, 255)
            
            count_y = y + (bar_height - count_height) / 2
            draw.text((count_x, count_y), count_text, font=font, fill=count_color)
            
            y += bar_height + bar_spacing
        
        # 保存图片
        temp_dir = resources_path.parent / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        output_path = temp_dir / f"pos_chart_{uuid.uuid4().hex}.png"
        img.save(output_path, "PNG")
        
        return output_path


@register_analyzer
class WordCloudAnalyzer(BaseAnalyzer):
    """词云分析器 - 统计高频词汇并生成词云图片"""
    
    def __init__(self, group_id: str):
        super().__init__(group_id)
        self._name = "高频词云"
        self._custom_image_getter = self.generate_wordcloud_image
    
    def process_event(self, event: GroupMessageEvent):
        """处理单个消息事件,提取并统计词汇"""
        if not event.raw_message:
            return
        texts = event.message.filter_text()
        all_text = ""
        for plain_text in texts:
            if plain_text.text.startswith('/'):
                continue  # 忽略命令消息
            all_text += plain_text.text + " "
        
        words_with_pos = extract_words_with_pos(all_text)
        for word, _ in words_with_pos:  # 只使用词，忽略词性
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
        "C:/Windows/Fonts/simkai.ttf",    # 楷体
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
            height=600,
            max_words=100,
            min_font_size=10,
            colormap='viridis'
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

        output_path = resources_path.parent / "temp" / f"wordcloud_{uuid.uuid4().hex}.png"        
        wordcloud_image.save(str(output_path), "PNG")
        return output_path


