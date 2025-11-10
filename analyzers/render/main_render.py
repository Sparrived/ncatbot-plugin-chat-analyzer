from typing import Dict, List
from PIL import Image
import pillowmd
import asyncio
from pathlib import Path
from ncatbot.utils import get_log


try:
    from .rankings import save_ranking_with_avatars, RenderUserInfo
except ImportError:
    from rankings import save_ranking_with_avatars, RenderUserInfo

LOG = get_log("ChatAnalyzer")


async def render_analysis_result(
    results: Dict[str, tuple[RenderUserInfo]],
    title: str = "今日群聊信息总结",
    resources_path: Path = Path("data/ChatAnalyzer/resources")
) -> List[Image.Image]:
    """
    将分析结果渲染为图片,使用 pillowmd 渲染包含头像的 Markdown 文本
    
    :param results: 分析结果字典,格式为 {analyzer_name: [(user_id, count), ...], ...}
    :param title: 图片标题
    :param show_avatars: 是否在每个分析器下方显示头像
    :param resources_path: 资源文件夹路径(包含 mdstyle 文件夹)
    :return: 渲染后的图片帧列表(用于生成 GIF)
    """
    
    # 确保临时文件夹存在
    temp_dir = resources_path.parent / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    temp_pics: list[Path] = []

    pillowmd.Setting.QUICK_IMAGE_PATH = temp_dir
    # 构建 Markdown 文本
    markdown_parts = []
    markdown_parts.append(f"# {title}\n")
    
    # 遍历每个分析器的结果
    for analyzer_name, result_tuple in results.items():
        # 添加分析器名称作为二级标题
        markdown_parts.append(f"\n## {analyzer_name}\n")

        if result_tuple and len(result_tuple) > 0:
            # 获取前三名,不足的用占位符填充
            top_users = list(result_tuple[:3])
            while len(top_users) < 3:
                rank = len(top_users) + 1
                top_users.append(RenderUserInfo.create_placeholder(rank))
            
            avatar_img_path = save_ranking_with_avatars(
                champion_infos=(top_users[0], top_users[1], top_users[2]),
                resources_path=resources_path
            )
            temp_pics.append(avatar_img_path)
            
            # 在 Markdown 中添加图片引用
            markdown_parts.append(f"!sgm[{avatar_img_path.name}]")
        else:
            markdown_parts.append("\n*暂无数据*\n")
    # 组合完整的 Markdown 文本
    markdown_text = "\n".join(markdown_parts)
    
    style_path = resources_path / "mdstyle"
    style = pillowmd.LoadMarkdownStyles(str(style_path))
    result = await pillowmd.MdToImage(
        text=markdown_text,
        style=style,
        page=3,
        autoPage=True,
        sgm=True,
        sgexter=True
    )
    # 从渲染结果中获取图片
    if result.imageType == 'gif':
        base_images = result.images
    else:
        base_images = [result.image]
    # 删除临时图片文件
    for temp_pic in temp_pics:
        temp_pic.unlink(True)
    
    return base_images


if __name__ == "__main__":
    # 测试代码
    async def main():
        print("开始测试渲染...")
        
        # 创建测试用的 RenderUserInfo 对象
        test_results = {
            "💬 话痨之王": (
                await RenderUserInfo.create("1", "2837324789", 1, debug=True, meta_info={"nickname": "用户1"}),
                await RenderUserInfo.create("1", "1016813500", 2, debug=True, meta_info={"nickname": "用户2"}),
                await RenderUserInfo.create("1", "3223986962", 3, debug=True, meta_info={"nickname": "用户3"}),
            ),
            "📸 图片分享达人": (
                await RenderUserInfo.create("1", "1016813500", 1, debug=True, meta_info={"nickname": "图片王"}),
                await RenderUserInfo.create("1", "2837324789", 2, debug=True, meta_info={"nickname": "图片达人"}),
            ),
            "😂 表情包大王": (
                await RenderUserInfo.create("1", "3223986962", 1, debug=True, meta_info={"nickname": "表情包大师"}),
            )
        }
        
        # 带头像排行的渲染(每个分析器下方显示头像) - 保存为 PNG
        print("\n[测试] 带头像排行的渲染(每个分析器独立显示头像)...")
        result_images_with_avatars = await render_analysis_result(
            results=test_results
        )
        
        # 保存为 GIF 格式
        # output_path_avatars = "d:/Code/SiriusBot-Neko/test_analysis_result_with_avatars.gif"
        # print(f"渲染完成,GIF 帧数: {len(result_images_with_avatars)}, 尺寸: {result_images_with_avatars[0].size}")
        # result_images_with_avatars[0].save(
        #     output_path_avatars,
        #     save_all=True,
        #     append_images=result_images_with_avatars[1:],
        #     duration=100,
        #     loop=0,
        #     optimize=False
        # )
        output_path_avatars = "d:/Code/SiriusBot-Neko/test_analysis_result_with_avatars.png"
        result_images_with_avatars[0].save(output_path_avatars)
        print(f"测试图片已保存到: {output_path_avatars}")
        
        print("\n✅ 测试完成!")
        print(f"提示: 查看生成的图片,每个分析器下方都有对应的前三名头像排行")
    
    asyncio.run(main())
