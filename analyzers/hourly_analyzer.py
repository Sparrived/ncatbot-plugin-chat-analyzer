from ncatbot.core import GroupMessageEvent
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import uuid
from .base_analyzer import BaseAnalyzer, register_analyzer
from .crayon_utils import draw_crayon_rectangle


@register_analyzer
class HourlyActivityAnalyzer(BaseAnalyzer):
    """每小时活跃度分析器 - 统计每个小时内的聊天记录数量"""
    
    def __init__(self, group_id: str):
        super().__init__(group_id) 
        self._name = "小时活跃度"
        self._unit = "条"
        self._start_hour: int = -1
        self._custom_image_getter = self._generate_hourly_chart
    
    def reset(self):
        """重置分析器的统计数据"""
        super().reset()
        self._start_hour = -1
    
    def process_event(self, event: GroupMessageEvent):
        """处理单个消息事件,按小时统计消息数量"""
        # 获取消息的时间戳并转换为小时
        timestamp = event.time
        dt = datetime.fromtimestamp(timestamp)
        hour = dt.hour  # 0-23
        if self._start_hour == -1:
            self._start_hour = hour
        
        # 统计该小时的消息数量
        self._counter[hour] += 1
    
    def _generate_hourly_chart(self, resources_path: Path) -> Path:
        """
        生成24小时活跃度条（一条横线，色块长度表示活跃度）
        按热度从高到低排序显示
        
        :param resources_path: 资源文件夹路径
        :return: 生成的图片路径
        """
        # 图表配置
        width = 960
        height = 120
        padding_x = 80   # 左右边距
        padding_y = 30   # 上下边距
        bar_height = 48  # 条的高度
        
        # 创建画布（透明背景）
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 加载字体
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",    # 黑体
            "C:/Windows/Fonts/STKAITI.TTF",   # 华文楷体
        ]
        
        font = None
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 12)
                break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
        
        # 准备数据 - 从start_hour开始的24小时
        start_hour = self._start_hour if self._start_hour != -1 else 0
        hourly_data = []
        total_count = 0
        
        # 生成从start_hour开始的24小时数据（按时间顺序）
        for i in range(24):
            hour = (start_hour + i) % 24
            count = self._counter.get(hour, 0)
            hourly_data.append((hour, count))
            total_count += count
        
        # 如果总数为0，避免除以0
        if total_count == 0:
            total_count = 1
        
        # 计算活跃度条的位置和总宽度
        bar_y = padding_y
        total_bar_width = width - 2 * padding_x
        block_width = total_bar_width / 24  # 每个色块均分宽度
        
        # 计算最大值用于颜色分级
        max_count = max(count for _, count in hourly_data) if hourly_data else 1
        if max_count == 0:
            max_count = 1
        
        # 绘制24个色块，每个色块宽度相同，按时间顺序（蜡笔手绘风格）
        current_x = padding_x
        block_positions = []  # 记录每个色块的位置和对应的小时
        
        for hour, count in hourly_data:
            # 根据该时段在排序中的位置来着色（热度越高颜色越深）
            if count == 0:
                base_color = (230, 230, 230)  # 浅灰色
            else:
                # 根据消息数相对于最大值的比例来着色
                ratio = count / max_count if max_count > 0 else 0
                if ratio >= 0.8:
                    # 很高 - 深蓝紫
                    base_color = (30, 80, 200)
                elif ratio >= 0.6:
                    # 高 - 深蓝
                    base_color = (50, 110, 230)
                elif ratio >= 0.4:
                    # 中等 - 中蓝
                    base_color = (100, 150, 255)
                elif ratio >= 0.2:
                    # 低 - 浅蓝
                    base_color = (160, 190, 255)
                else:
                    # 很低 - 非常浅的蓝
                    base_color = (200, 220, 255)
            
            # 绘制蜡笔风格的色块
            draw_crayon_rectangle(
                draw, 
                current_x, 
                bar_y, 
                block_width, 
                bar_height, 
                base_color,
                orientation="vertical"
            )
            # 记录色块中心位置和对应的小时
            block_positions.append((current_x + block_width / 2, hour))
            
            current_x += block_width
        
        # 绘制时间标签（每2小时显示一次）
        label_y = bar_y + bar_height + 8
        
        # 每隔2小时显示一个标签（0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22）
        for i in range(0, 24, 2):
            # 由于是按时间顺序，第i个位置就是第i个小时
            if i < len(block_positions):
                x_position, hour = block_positions[i]
                
                # 显示实际的小时数
                hour_text = f"{hour:02d}"
                hour_bbox = draw.textbbox((0, 0), hour_text, font=font)
                hour_width = hour_bbox[2] - hour_bbox[0]
                
                # 居中对齐标签
                label_x = x_position - hour_width // 2
                
                # 边界限制，避免标签超出
                label_x = max(5, min(label_x, width - hour_width - 5))
                
                draw.text((label_x, label_y), hour_text, font=font, fill=(100, 100, 100, 255))
        
        # 保存图片
        temp_dir = resources_path.parent / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        random_name = uuid.uuid4().hex
        output_path = temp_dir / f"hourly_chart_{random_name}.png"
        img.save(output_path, "PNG")
        
        return output_path
    
