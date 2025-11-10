from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.utils import get_log

from functools import wraps
from typing import Callable, Literal, Optional
from PIL import Image
from io import BytesIO

import asyncio
import aiohttp
import base64


AVATARURL_TEMPLATE = "http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100"
LOG = get_log("ChatAnalyzer")


async def get_qq_avatar_async(
        user_id: str,
        max_retries: int = 3
) -> str:
    """
    异步获取 QQ 头像并转换为 base64
    
    :param user_id: QQ 号
    :param size: 头像大小
    :param max_retries: 最大重试次数
    :return: base64 编码的头像字符串,失败返回 None
    """
    url = AVATARURL_TEMPLATE.format(user_id=user_id)
    for attempt in range(max_retries):
        try:
            # 使用 aiohttp 异步获取头像
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        LOG.error(f"获取 QQ 头像失败 (user_id={user_id}): HTTP {response.status} (尝试 {attempt + 1}/{max_retries})")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(0.2)  # 重试前短暂延迟
                            continue
                        raise Exception(f"HTTP {response.status} error")
                    avatar_data = await response.read()
            # 验证是否为有效图片
            try:
                Image.open(BytesIO(avatar_data)).verify()
            except:
                LOG.error(f"QQ 头像验证失败 (user_id={user_id}) (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.2)
                    continue
                raise Exception("Invalid image data")
            # 转换为 base64
            return base64.b64encode(avatar_data).decode()
        except Exception as e:
            LOG.error(f"获取 QQ 头像失败 (user_id={user_id}): {e} (尝试 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.2)  # 重试前短暂延迟
                continue
    raise Exception(f"Failed to get QQ avatar for user_id={user_id} after {max_retries} attempts")


def subscribed_check(subscribed_groups: list, group_id: str) -> bool:
    """配置项基础检测"""
    if group_id not in subscribed_groups:
        return False
    return True

def require_subscription(func: Callable):
    """群组订阅判断装饰器函数"""
    @wraps(func)
    async def wrapper(self: NcatBotPlugin, event, *args, **kwargs):
        group_id = getattr(event, "group_id", None)
        if group_id is None:
            return await func(self, event, *args, **kwargs)
        if not subscribed_check(self.config["subscribed_groups"], str(group_id)):
            return None
        return await func(self, event, *args, **kwargs)

    return wrapper


def require_group_admin(role: Literal["admin", "owner"] = "admin", reply_message: str = "我不是该群的管理员，不能做这些喵……"):
    """群组管理员判断装饰器函数"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self: NcatBotPlugin, event, *args, **kwargs):
            group_id = getattr(event, "group_id", None)
            self_id = getattr(event, "self_id", None)
            if group_id is None or self_id is None:
                return await func(self, event, *args, **kwargs)
            self_info = await self.api.get_group_member_info(
                group_id=group_id, 
                user_id=self_id
            )
            if self_info.role == "owner":
                return await func(self, event, *args, **kwargs)
            if self_info.role != role:
                await event.reply(reply_message)
                return
            return await func(self, event, *args, **kwargs)

        return wrapper
    return decorator

def at_check_support(func: Callable):
    """支持 at 功能的装饰器函数"""
    @wraps(func)
    async def wrapper(self: NcatBotPlugin, event, *args, **kwargs):
        for i, arg in enumerate(args):
            if not isinstance(arg, str):
                continue
            if arg.startswith("At"):
                user_id = arg.split("=")[1].split('"')[1]
                args = list(args)
                args[i] = user_id
                args = tuple(args)
        return await func(self, event, *args, **kwargs)
    return wrapper