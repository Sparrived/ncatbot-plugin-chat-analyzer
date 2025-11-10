# 聊天分析渲染模块

## 概述

该模块使用 `pillowmd` 库将聊天分析结果渲染为美观的图片,支持独角兽 GIF 风格的渐变背景。

## 功能特性

- ✨ **独角兽渐变背景** - 彩虹色渐变效果,带星星装饰
- 📊 **表格化展示** - 清晰的排行榜表格
- 🏆 **勋章标识** - 前三名自动添加金银铜牌
- 👤 **QQ头像展示** - 自动获取前三名QQ头像并展示在排行榜上
- 🖼️ **头像框装饰** - 使用精美的金银铜头像框展示前三名
- 🎨 **可定制样式** - 支持自定义字体、颜色、间距等
- 📑 **分段显示** - 每个分析器结果独立展示,用分割线分隔

## 使用方法

### 1. 基本用法

```python
from plugins.chat_analyzer.render import render_analysis_result_sync

# 分析结果格式
results = {
    "最活跃成员": [
        ("12345678", 156),  # (用户ID, 次数)
        ("87654321", 142),
        ("11111111", 98),
    ],
    "最佳图片成员": [
        ("87654321", 89),
        ("12345678", 72),
    ],
}

# 渲染为图片
image = render_analysis_result_sync(
    results=results,
    title="群聊数据分析报告",
    use_gif=False,
    max_show_count=10
)

# 保存图片
image.save("analysis_result.png")
```

### 2. 异步用法

```python
from plugins.chat_analyzer.render import render_analysis_result

async def main():
    image = await render_analysis_result(
        results=results,
        title="群聊数据分析",
        use_gif=True,  # 生成 GIF 格式
        max_show_count=15
    )
    return image
```

### 3. 在插件中使用

```python
from .render import render_analysis_result_sync
from .analyzers import ChatAnalysisEngine

# 获取聊天记录
chat_histories = await self._get_chat_history(group_id, "22:00")

# 分析数据
engine = ChatAnalysisEngine()
results = engine.analyze(chat_histories)

# 渲染图片(带头像)
result_image = render_analysis_result_sync(
    results=results,
    title=f"群 {group_id} 数据分析",
    max_show_count=10,
    show_avatars=True  # 显示前三名头像
)

# 发送图片(转 base64)
from io import BytesIO
import base64

img_buffer = BytesIO()
result_image.save(img_buffer, format='PNG')
img_base64 = base64.b64encode(img_buffer.getvalue()).decode()

await event.reply(f"[CQ:image,file=base64://{img_base64}]")
```

### 4. 获取 QQ 头像

```python
from .render import get_qq_avatar, get_qq_avatar_async

# 同步方式
avatar_base64 = get_qq_avatar("12345678", size=100)

# 异步方式
avatar_base64 = await get_qq_avatar_async("12345678", size=100)

# 使用头像创建排行榜
from .render import render_top_users_with_avatars

top_users = [
    ("12345678", 156),
    ("87654321", 142),
    ("11111111", 98),
]

ranking_image = await render_top_users_with_avatars(
    top_users=top_users,
    analyzer_name="最活跃成员"
)
```

## 参数说明

### `render_analysis_result()` / `render_analysis_result_sync()`

| 参数             | 类型                             | 默认值         | 说明                         |
| ---------------- | -------------------------------- | -------------- | ---------------------------- |
| `results`        | Dict[str, List[Tuple[str, int]]] | 必填           | 分析结果字典,key为分析器名称 |
| `title`          | str                              | "群聊数据分析" | 图片主标题                   |
| `use_gif`        | bool                             | True           | 是否生成GIF格式              |
| `max_show_count` | int                              | 10             | 每个分析器最多显示的结果数量 |
| `show_avatars`   | bool                             | False          | 是否在顶部显示前三名头像     |

**返回值**: `PIL.Image.Image` - 渲染后的图片对象

### `get_qq_avatar()` / `get_qq_avatar_async()`

| 参数      | 类型 | 默认值 | 说明                  |
| --------- | ---- | ------ | --------------------- |
| `user_id` | str  | 必填   | QQ 号                 |
| `size`    | int  | 100    | 头像大小 (40/100/140) |

**返回值**: `Optional[str]` - base64 编码的头像字符串,失败返回 None

**QQ头像API**: `http://q1.qlogo.cn/g?b=qq&nk={user_id}&s={size}`

### `render_top_users_with_avatars()`

| 参数             | 类型                  | 默认值                        | 说明                              |
| ---------------- | --------------------- | ----------------------------- | --------------------------------- |
| `top_users`      | List[Tuple[str, int]] | 必填                          | 前三名用户列表 [(user_id, count)] |
| `analyzer_name`  | str                   | "排行榜"                      | 分析器名称                        |
| `resources_path` | str                   | "data/ChatAnalyzer/resources" | 资源文件夹路径                    |
| `gap`            | int                   | 24                            | 头像框之间的间隙                  |

**返回值**: `PIL.Image.Image` - 排行榜图片(仅前三名头像框)

## 样式定制

### 独角兽渐变背景

`create_unicorn_gradient_background()` 函数创建彩虹渐变背景:

```python
from plugins.chat_analyzer.render import create_unicorn_gradient_background

# 创建背景
background = create_unicorn_gradient_background(
    xs=800,    # 宽度
    ys=1200,   # 高度
    frame=0    # 动画帧(用于GIF)
)
```

### 自定义样式

可以修改 `main_render.py` 中的 `custom_style` 来定制样式:

```python
custom_style = MdStyle(
    **{
        **DEFAULT_STYLE.__dict__,
        'fontSize': 28,              # 正文字体大小
        'title1FontSize': 75,        # 一级标题大小
        'title2FontSize': 50,        # 二级标题大小
        'textColor': (255, 255, 255), # 文字颜色
        'xSizeMax': 900,             # 最大宽度
        'rd': 40,                    # 右边距
        'ld': 40,                    # 左边距
        'ud': 40,                    # 上边距
        'dd': 40,                    # 下边距
        'formLineColor': (150, 200, 255),  # 表格线颜色
        'formTextColor': (255, 255, 255),  # 表格文字颜色
        'backGroundDrawFunc': create_unicorn_gradient_background,
    }
)
```

## 输出示例

### 图片结构

```
┌────────────────────────────────┐
│    # 群聊数据分析报告          │
│                                │
│    ## 最活跃成员               │
│    ┌─────┬────────┬──────┐    │
│    │排名 │ 用户ID │ 次数 │    │
│    ├─────┼────────┼──────┤    │
│    │🥇 1 │12345678│ 156  │    │
│    │🥈 2 │87654321│ 142  │    │
│    │🥉 3 │11111111│  98  │    │
│    └─────┴────────┴──────┘    │
│                                │
│    ───────────────────────     │
│                                │
│    ## 最佳图片成员             │
│    ┌─────┬────────┬──────┐    │
│    │ ... │  ...   │ ...  │    │
│    └─────┴────────┴──────┘    │
└────────────────────────────────┘
```

## 依赖项

- `pillowmd >= 0.7.2` - Markdown 渲染引擎
- `Pillow` - 图像处理库

## 注意事项

1. **字体文件**: pillowmd 需要字体文件支持,默认使用 `smSans.ttf`
2. **性能**: 渲染大量数据可能需要几秒钟
3. **内存**: 生成的图片会占用内存,使用后及时释放
4. **GIF支持**: 目前暂不支持真正的 GIF 动画,仅支持静态图片

## 未来计划

- [ ] 支持真正的 GIF 动画效果
- [ ] 集成头像排名图(rankings.py)
- [ ] 支持更多图表类型(饼图、折线图等)
- [ ] 支持自定义主题切换
- [ ] 支持导出 PDF 格式
