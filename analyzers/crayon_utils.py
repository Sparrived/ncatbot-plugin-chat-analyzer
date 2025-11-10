"""蜡笔风格绘制工具"""
import random
from PIL import ImageDraw


def draw_crayon_rectangle(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    width: float,
    height: float,
    base_color: tuple,
    orientation: str = "auto"
):
    """
    绘制蜡笔风格的矩形色块
    
    :param draw: ImageDraw对象
    :param x: 左上角x坐标
    :param y: 左上角y坐标
    :param width: 宽度
    :param height: 高度
    :param base_color: 基础颜色(RGB)
    :param orientation: 方向 - "horizontal"(横向), "vertical"(竖向), "auto"(自动判断)
    """
    if width < 1 or height < 1:
        return
    
    # 自动判断方向
    if orientation == "auto":
        orientation = "horizontal" if width > height else "vertical"
    
    # 绘制基础色块（略微不规则的边缘）
    points = []
    
    if orientation == "horizontal":
        # 横向条形（宽>高）- 适合横向进度条等
        num_points_vertical = max(4, int(height / 3))  # 左右边缘的点数
        
        # 上边缘 - 添加随机波动
        for i in range(int(width / 10) + 1):
            px = x + min(i * 10, width)
            py = y + random.uniform(-1, 1)
            points.append((px, py))
        
        # 右边缘 - 添加随机波动
        for i in range(num_points_vertical + 1):
            px = x + width + random.uniform(-1, 1)
            py = y + (i / num_points_vertical) * height
            points.append((px, py))
        
        # 下边缘 - 添加随机波动
        for i in range(int(width / 10), -1, -1):
            px = x + min(i * 10, width)
            py = y + height + random.uniform(-1, 1)
            points.append((px, py))
        
        # 左边缘 - 添加随机波动
        for i in range(num_points_vertical, -1, -1):
            px = x + random.uniform(-1, 1)
            py = y + (i / num_points_vertical) * height
            points.append((px, py))
            
    else:  # vertical
        # 竖向色块（高>宽）- 适合竖向柱状图等
        num_points_horizontal = max(4, int(width / 5))  # 上下边缘的点数
        
        # 上边缘 - 添加随机波动
        for i in range(num_points_horizontal + 1):
            px = x + (i / num_points_horizontal) * width
            py = y + random.uniform(-1.5, 1.5)
            points.append((px, py))
        
        # 右边缘
        points.append((x + width + random.uniform(-0.5, 0.5), y + height / 2))
        
        # 下边缘 - 添加随机波动
        for i in range(num_points_horizontal, -1, -1):
            px = x + (i / num_points_horizontal) * width
            py = y + height + random.uniform(-1.5, 1.5)
            points.append((px, py))
        
        # 左边缘
        points.append((x + random.uniform(-0.5, 0.5), y + height / 2))
    
    # 绘制主色块（带透明度变化模拟蜡笔不均匀）
    draw.polygon(points, fill=base_color + (200,), outline=None)
    
    # 添加随机纹理点模拟蜡笔颗粒感
    min_size = 3 if orientation == "vertical" else 10
    if width > min_size and height > min_size:
        # 根据方向调整纹理密度
        density = 15 if orientation == "vertical" else 20
        num_texture_points = int(width * height / density)
        
        for _ in range(num_texture_points):
            tx = x + random.uniform(0, width)
            ty = y + random.uniform(0, height)
            
            # 随机颜色变化（更亮或更暗）
            color_variation = random.randint(-20, 25)
            texture_color = tuple(
                max(0, min(255, c + color_variation)) for c in base_color
            )
            
            # 绘制小点（模拟蜡笔颗粒）
            point_size = random.choice([1, 1, 1, 2])  # 大部分是1像素，偶尔2像素
            if point_size == 1:
                draw.point((tx, ty), fill=texture_color + (180,))
            else:
                draw.ellipse(
                    [(tx - 1, ty - 1), (tx + 1, ty + 1)],
                    fill=texture_color + (150,)
                )
    
    # 添加边缘高光（蜡笔特有的光泽感）
    if (orientation == "horizontal" and width > 20 and height > 10) or \
       (orientation == "vertical" and width > 5):
        highlight_color = tuple(min(255, c + 30) for c in base_color)
        # 上边缘高光
        highlight_points = int(width * 0.3) if orientation == "horizontal" else int(width)
        for i in range(highlight_points):
            hx = x + random.uniform(0, width)
            hy = y + random.uniform(0, 2)
            if random.random() < 0.3:  # 30%概率绘制高光点
                draw.point((hx, hy), fill=highlight_color + (100,))
