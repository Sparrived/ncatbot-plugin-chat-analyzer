import uuid
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Tuple, Dict, Optional
import base64
from io import BytesIO
from dataclasses import dataclass, field
from ncatbot.utils import status
import sys

# 导入 get_qq_avatar_async 函数
try:
    from ...utils import get_qq_avatar_async
except ImportError:
    # 直接运行此文件时,添加父目录到路径
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from utils import get_qq_avatar_async

@dataclass
class RenderUserInfo:
    """用于渲染排行榜时存储用户信息的类"""
    group_id: str
    user_id: str
    rank: int
    count: str = field(default="Unknown")  # 统计数值的字符串表示
    nickname: str = field(default="")  # 用户群昵称
    avatar_base64: str = field(default="")  # 头像的 base64 字符串
    debug: bool = field(default=False)
    meta_info: Dict[str, str] = field(default_factory=dict)  # 其他元信息

    @classmethod
    async def create(
        cls,
        group_id: str,
        user_id: str,
        rank: int,
        count: str = "Unknown",
        debug: bool = False,
        meta_info: Optional[Dict[str, str]] = None
    ) -> "RenderUserInfo":
        """
        异步工厂方法,用于创建 RenderUserInfo 实例
        
        :param group_id: 群组ID
        :param user_id: 用户ID
        :param rank: 排名
        :param debug: 是否为调试模式
        :param meta_info: 元信息字典
        :return: 初始化完成的 RenderUserInfo 实例
        """
        if meta_info is None:
            meta_info = {}
        
        instance = cls(
            group_id=group_id,
            user_id=user_id,
            rank=rank,
            count=count,
            debug=debug,
            meta_info=meta_info
        )
        
        # 异步初始化
        await instance._async_init()
        return instance
    
    async def _async_init(self):
        """异步初始化方法,获取昵称和头像"""
        if not self.debug:
            member_info = await status.global_api.get_group_member_info(self.group_id, self.user_id)
            if not member_info:
                raise ValueError(f"无法获取用户信息: group_id={self.group_id}, user_id={self.user_id}")
            self.nickname = member_info.card if member_info.card else member_info.nickname
        else:
            self.nickname = self.meta_info.get("nickname", "测试用户")
        self.avatar_base64 = await get_qq_avatar_async(self.user_id)
    
    @classmethod
    def create_placeholder(cls, rank: int) -> "RenderUserInfo":
        """
        创建一个"暂无"占位符实例
        
        :param rank: 排名
        :return: 昵称为"暂无"的 RenderUserInfo 实例
        """
        # 创建一个128x128的纯白色图片并转换为base64
        white_img = Image.new("RGBA", (128, 128), (255, 255, 255, 255))
        img_buffer = BytesIO()
        white_img.save(img_buffer, format="PNG")
        white_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return cls(
            group_id="0",
            user_id="0",
            rank=rank,
            nickname="暂无",
            avatar_base64=white_base64,
            debug=False,
            meta_info={}
        )


def create_ranking_with_avatars(
    champion_infos: Tuple[RenderUserInfo, RenderUserInfo, RenderUserInfo],
    resources_path: Path = Path("data/ChatAnalyzer/resources"),
    gap: int = 24
) -> Image.Image:
    """
    创建带头像的排行榜图片
    
    :param champion_infos: 包含前三名用户信息的元组
    :param resources_path: 资源文件夹路径
    :param gap: 头像框之间的间隙(像素)
    :return: 完成的排行榜图片
    """
    # 固定的文字样式参数
    text_gap = 10  # 头像框和文字之间的间隙
    font_size = 32  # 昵称字体大小
    count_font_size = 24  # 统计数字的字体大小
    text_width_reduce = 48  # 文字区域比头像框总宽度短的像素数
    
    # 加载头像框
    img_1st = Image.open(resources_path / "1st.png").convert("RGBA")
    img_2nd = Image.open(resources_path / "2nd.png").convert("RGBA")
    img_3rd = Image.open(resources_path / "3rd.png").convert("RGBA")
    
    # 获取1st的原始尺寸
    width_1st, height_1st = img_1st.size
    
    # 计算2nd和3rd的尺寸
    width_2nd = int(width_1st * 0.95)
    height_2nd = int(height_1st * 0.95)
    img_2nd_resized = img_2nd.resize((width_2nd, height_2nd), Image.Resampling.LANCZOS)
    
    width_3rd = int(width_1st * 0.95)
    height_3rd = int(height_1st * 0.95)
    img_3rd_resized = img_3rd.resize((width_3rd, height_3rd), Image.Resampling.LANCZOS)
    
    # 计算画布尺寸(增加底部空间用于显示昵称和统计)
    frames_total_width = width_2nd + gap + width_1st + gap + width_3rd  # 头像框总宽度
    total_width = frames_total_width  # 画布总宽度与头像框相同
    text_height = font_size + count_font_size + text_gap * 2 + 10  # 昵称+统计+间隙+额外边距
    total_height = height_1st + text_height
    
    # 创建画布
    canvas = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))
    
    # 计算头像框位置
    x_2nd, y_2nd = 0, total_height - height_2nd - text_height
    x_1st, y_1st = width_2nd + gap, total_height - height_1st - text_height
    x_3rd, y_3rd = width_2nd + gap + width_1st + gap, total_height - height_3rd - text_height
    
    # 解码base64头像或创建白色填充
    def get_avatar(base64_str: Optional[str], size: int) -> Image.Image:
        """获取头像图片,如果base64为None则返回白色正方形"""
        if base64_str is None:
            # 创建白色正方形
            white_img = Image.new("RGBA", (size, size), (255, 255, 255, 255))
            return white_img
        else:
            # 解码base64
            avatar_data = base64.b64decode(base64_str)
            avatar_img = Image.open(BytesIO(avatar_data)).convert("RGBA")
            return avatar_img
    
    # 计算头像尺寸
    size_1st = int(min(width_1st, height_1st) * 0.8)
    size_2nd = int(min(width_2nd, height_2nd) * 0.8)
    size_3rd = int(min(width_3rd, height_3rd) * 0.8)
    
    avatar_1st = get_avatar(champion_infos[0].avatar_base64, size_1st)
    avatar_2nd = get_avatar(champion_infos[1].avatar_base64, size_2nd)
    avatar_3rd = get_avatar(champion_infos[2].avatar_base64, size_3rd)
    
    # 粘贴头像数据
    frame_data = [
        (avatar_2nd, x_2nd, y_2nd, width_2nd, height_2nd, size_2nd, champion_infos[1]),
        (avatar_1st, x_1st, y_1st, width_1st, height_1st, size_1st, champion_infos[0]),
        (avatar_3rd, x_3rd, y_3rd, width_3rd, height_3rd, size_3rd, champion_infos[2])
    ]
    
    # 先粘贴头像(在底层)
    for avatar, x, y, w, h, inner_size, user_info in frame_data:
        # 缩放头像以适应边框
        avatar_resized = avatar.resize((inner_size, inner_size), Image.Resampling.LANCZOS)
        
        # 计算居中位置
        offset_x = (w - inner_size) // 2
        offset_y = (h - inner_size) // 2
        
        # 粘贴头像(先粘贴,在底层)
        canvas.paste(avatar_resized, (x + offset_x, y + offset_y), avatar_resized)
    
    # 再粘贴头像框(在上层,覆盖头像)
    canvas.paste(img_2nd_resized, (x_2nd, y_2nd), img_2nd_resized)
    canvas.paste(img_1st, (x_1st, y_1st), img_1st)
    canvas.paste(img_3rd_resized, (x_3rd, y_3rd), img_3rd_resized)
    
    # 绘制昵称和统计文字
    draw = ImageDraw.Draw(canvas)
    
    # 尝试加载可爱的字体,如果失败则使用默认字体
    font_paths = [
        "C:/Windows/Fonts/STKAITI.TTF",   # 华文楷体
        "C:/Windows/Fonts/simkai.ttf",    # 楷体
        "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑 - 备用
    ]
    
    font = None
    count_font = None
    for font_path in font_paths:
        try:
            if font is None:
                font = ImageFont.truetype(font_path, font_size)
            if count_font is None:
                count_font = ImageFont.truetype(font_path, count_font_size)
            if font and count_font:
                break
        except:
            continue
    
    if font is None:
        font = ImageFont.load_default()
    if count_font is None:
        count_font = ImageFont.load_default()
    
    def truncate_text(text: str, max_width: int, font) -> str:
        """
        截断文字以适应最大宽度,超出部分用...代替
        
        :param text: 原始文字
        :param max_width: 最大宽度(像素)
        :param font: 字体对象
        :return: 截断后的文字
        """
        # 如果文字在宽度内,直接返回
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            return text
        
        # 文字超出宽度,需要截断
        ellipsis = "..."
        
        # 二分查找最合适的截断位置
        left, right = 0, len(text)
        result = ellipsis
        
        while left < right:
            mid = (left + right + 1) // 2
            test_text = text[:mid] + ellipsis
            test_bbox = draw.textbbox((0, 0), test_text, font=font)
            test_width = test_bbox[2] - test_bbox[0]
            
            if test_width <= max_width:
                result = test_text
                left = mid
            else:
                right = mid - 1
        
        return result
    
    # 绘制每个昵称和统计
    user_data = [
        (champion_infos[1], x_2nd, y_2nd + height_2nd, width_2nd),
        (champion_infos[0], x_1st, y_1st + height_1st, width_1st),
        (champion_infos[2], x_3rd, y_3rd + height_3rd, width_3rd)
    ]
    
    for user_info, x, y, w in user_data:
        # --- 绘制昵称 ---
        max_text_width = w - text_width_reduce
        truncated_nickname = truncate_text(user_info.nickname, max_text_width, font)
        
        nickname_bbox = draw.textbbox((0, 0), truncated_nickname, font=font)
        nickname_width = nickname_bbox[2] - nickname_bbox[0]
        nickname_x = x + (w - nickname_width) // 2
        nickname_y = y + text_gap
        
        draw.text((nickname_x, nickname_y), truncated_nickname, font=font, fill=(0, 0, 0, 255))
        
        # --- 绘制统计 ---
        count_text = user_info.count
        count_bbox = draw.textbbox((0, 0), count_text, font=count_font)
        count_width = count_bbox[2] - count_bbox[0]
        count_x = x + (w - count_width) // 2
        count_y = nickname_y + font_size  # 在昵称下方
        
        draw.text((count_x, count_y), count_text, font=count_font, fill=(80, 80, 80, 255))
    
    return canvas


def save_ranking_with_avatars(
    champion_infos: tuple[RenderUserInfo, RenderUserInfo, RenderUserInfo],
    resources_path: Path = Path("data/ChatAnalyzer/resources"),
    gap: int = 24,
) -> Path:
    """
    生成并保存带头像的排行榜图片
    
    :param champion_infos: 包含前三名用户信息的元组
    :param resources_path: 资源文件夹路径
    :param gap: 头像框之间的间隙(像素)
    :return: 输出文件路径
    """
    image = create_ranking_with_avatars(
        champion_infos,
        resources_path,
        gap
    )
    random_name = uuid.uuid4().hex
    output_path = resources_path.parent / "temp" / f"ranking_{random_name}.png"
    image.save(output_path, "PNG")
    return output_path


if __name__ == "__main__":
    import asyncio
    
    async def main():
        # 测试1: 使用异步工厂方法创建实例
        user_1st = await RenderUserInfo.create("1", "2388389247", 1, debug=True, meta_info={"nickname": "用户100000000000041241241241242140"})
        user_2nd = await RenderUserInfo.create("2", "2372447549", 2, debug=True, meta_info={"nickname": "用户2"})
        user_3rd = RenderUserInfo.create_placeholder(3)

        create_ranking_with_avatars((user_1st, user_2nd, user_3rd)).show()

    
    asyncio.run(main())