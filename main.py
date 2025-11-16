from ncatbot.plugin_system import NcatBotPlugin, admin_group_filter, command_registry, option, param, root_filter
from ncatbot.utils import get_log
from ncatbot.core import GroupMessageEvent
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry.help_system import HelpGenerator

from .utils import require_subscription
from .analyzers import ChatAnalysisEngine, RenderInfo

from datetime import datetime

import asyncio

class ChatAnalyzer(NcatBotPlugin):
    name = "ChatAnalyzer"
    version = "1.0.6"
    author = "Sparrived"
    description = "一个在某一时段内分析群聊活跃度的插件。"
    log = get_log(name)

    def init_config(self):
        """注册配置项"""
        self.register_config(
            "analysis_time",
            ["22:00"],
            "分析时间",
            list
        )
        self.register_config(
            "analysis_duration",
            60 * 24,
            "分析时长（分钟）",
            int
        )
        self.register_config(
            "minimum_message_count",
            10,
            "分析要求的最小消息数",
            int
        )
        self.register_config(
            "subscribed_groups",
            ["123456789"],  # 示例群号
            "需要订阅的群组列表",
            list
        )

    def init_scheduler(self):
        """初始化定时任务"""
        for time in self.config["analysis_time"]:
            self.add_scheduled_task(
                job_func=self._auto_send_analysis,
                name="auto_send_analysis",
                interval=time,
                kwargs={"time": time}
            )
            self.log.info(f"已注册自动发送分析任务， {time} 触发。")

    # ======== 初始化插件 ========
    async def on_load(self):
        self.init_config()
        self.init_scheduler()

    # ======== 注册指令 ========
    ca_group = command_registry.group("ca", description="聊天分析指令")
    
    @admin_group_filter
    @ca_group.command("analyze", description="分析群聊数据并生成图片报告")
    @param("time", default="", help="分析时间点(格式: HH:MM)", required=False)
    @param("duration", default=1440, help="分析时长(分钟)", required=False)
    @require_subscription
    async def cmd_analyze(self, event: GroupMessageEvent, time: str="", duration: int=1440):
        """分析群聊数据并生成图片报告"""
        if not time:
            time = datetime.now().strftime("%H:%M")
        # 校验时间格式
        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            await event.reply("时间格式错误喵~请使用 HH:MM 格式")
            return
        try:
            await event.reply("开始分析群聊数据喵~请稍等...")
            await self._post_analyze_img(event.group_id, time, duration)
        except Exception as e:
            self.log.error(f"分析失败: {e}", exc_info=True)
            await event.reply(f"分析失败喵~错误信息: {str(e)}")
    
    @root_filter
    @ca_group.command("test", description="测试指令")
    async def cmd_test(self, event: GroupMessageEvent):
        """这条指令用于测试获取聊天记录功能，仅root用户可用"""
        await event.reply("测试指令响应成功喵~")
        chat_histories = await self._get_chat_history(str(event.group_id), "22:00", self.config["analysis_duration"])
        earliest_chat = chat_histories[0]
        if earliest_chat:
            await self.api.post_group_msg(event.group_id, f"获取到了{len(chat_histories)}条聊天记录喵~最早一条聊天记录是: {earliest_chat.raw_message}，时间是{datetime.fromtimestamp(earliest_chat.time).strftime('%Y-%m-%d %H:%M:%S')}")

    # ======== 私有方法 ========
    async def _post_analyze_img(self, group_id: str, time: str, duration:int):
        # 获取聊天记录
        chat_histories = await self._get_chat_history(group_id, time, duration)
        if not chat_histories:
            raise ValueError("未能获取到聊天记录喵~")
        if len(chat_histories) < self.config["minimum_message_count"]:
            raise ValueError("聊天记录数量不足，无法进行分析喵~")
        
        self.log.info(f"从群 {group_id} 获取到 {len(chat_histories)} 条聊天记录")
        group_info = await self.api.get_group_info(group_id)
        # 使用分析引擎进行分析
        render_info = RenderInfo(
            current_time=datetime.now(),
            analysis_duration=duration,
            group_name_and_id=f"{group_info.group_name}({group_id})",
            plugin_version=self.version
        )
        engine = ChatAnalysisEngine(self.workspace / "resources", group_id, render_info)
        img_b64 = await engine.analyze(chat_histories)
        # 发送图片
        await self.api.post_group_msg(group_id, "大人们，这是你们今天的聊天分析报告，请注意查收喵~")
        await self.api.post_group_msg(group_id, image=f"base64://{img_b64}")

    async def _get_chat_history(self, group_id: str, time: str, duration:int, count: int = 101):
        """
        获取指定时间范围内的聊天记录

        :param group_id: 群组ID
        :param time: 目标时间点(格式: "HH:MM")
        :param duration: 分析时长(分钟)
        :param count: 每次获取的记录数量
        :param index: 已处理的记录数量(用于避免重复查询)
        :return: 时间范围内的聊天记录列表
        """
        # 校验时间格式
        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            raise ValueError("时间格式错误")
        
        # 获取聊天记录
        chat_histories = await self.api.get_group_msg_history(
            group_id=group_id,
            count=count
        )
        # API返回的第一个元素是最早的聊天记录
        earliest_chat_history = chat_histories[0]
        # 将时间字符串(如"22:00")转换为当天该时间点的timestamp
        hour, minute = map(int, time.split(':'))
        today = datetime.now().date()
        target_time = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
        target_timestamp = int(target_time.timestamp())
        earliest_timestamp = earliest_chat_history.time
        start_timestamp = target_timestamp - duration * 60
        # 判断最早的记录是否在我们需要的时间范围之前(或等于)
        if earliest_timestamp <= start_timestamp:
            # 已经获取到足够早的记录,进行二分查找
            # chat_histories 按时间升序排列(最早在前,最新在后)
            # 找到第一个 >= start_timestamp 的索引
            left, right = 0, len(chat_histories) - 1
            start_idx = len(chat_histories)  # 默认找不到
            while left <= right:
                mid = (left + right) // 2
                if chat_histories[mid].time >= start_timestamp:
                    start_idx = mid
                    right = mid - 1  # 继续向左找更早满足条件的
                else:
                    left = mid + 1
            # 找到最后一个 <= target_timestamp 的索引
            left, right = 0, len(chat_histories) - 1
            end_idx = -1  # 默认找不到
            while left <= right:
                mid = (left + right) // 2
                if chat_histories[mid].time <= target_timestamp:
                    end_idx = mid
                    left = mid + 1  # 继续向右找更晚满足条件的
                else:
                    right = mid - 1
            # 获取时间范围内的聊天记录
            if start_idx < len(chat_histories) and end_idx >= 0 and start_idx <= end_idx:
                filtered_histories = chat_histories[start_idx:end_idx + 1]
                return filtered_histories
            else:
                return []
        else:
            # 需要获取更早的聊天记录
            # 递归调用,增加count以获取更多历史记录
            return await self._get_chat_history(
                group_id=group_id, 
                time=time, 
                duration=duration, 
                count=count + 101
            )
    
    async def _auto_send_analysis(self, time: str):
        """自动发送分析报告的任务"""
        subscribed_groups = self.config["subscribed_groups"]
        self.log.info(f"触发时间点：{time}，即将向 {'、'.join(subscribed_groups)} 发送聊天分析报告")
        async def task(group_id: str):
            try:
                await self._post_analyze_img(group_id, time, self.config["analysis_duration"])
                self.log.info(f"成功向 {group_id} 发送聊天分析报告")
            except Exception as e:
                self.log.error(f"向 {group_id} 发送聊天分析报告失败：{e}")
                await self.api.post_group_msg(group_id, f"这个时间应该给你们总结近段时间的聊天记录的，结果因为 {e} 没能成功喵……")
        tasks = []
        for group_id in subscribed_groups:
            tasks.append(asyncio.create_task(task(group_id)))
        await asyncio.gather(*tasks)



    # ======== 订阅功能 ========
    @admin_group_filter
    @ca_group.command("subscribe", description="订阅聊天分析功能")
    async def cmd_subscribe(self, event: GroupMessageEvent):
        """订阅聊天分析功能"""
        subscribed_groups = self.config["subscribed_groups"]
        if str(event.group_id) in subscribed_groups:
            await event.reply("本群组已订阅聊天分析功能喵~")
            return
        self.config["subscribed_groups"].append(str(event.group_id))
        await event.reply("订阅了聊天分析功能喵~")

    @admin_group_filter
    @ca_group.command("unsubscribe", description="取消订阅聊天分析功能")
    async def cmd_unsubscribe(self, event: GroupMessageEvent):
        """取消订阅聊天分析功能"""
        subscribed_groups = self.config["subscribed_groups"]
        if str(event.group_id) not in subscribed_groups:
            await event.reply("本群组未订阅聊天分析功能喵~")
            return
        self.config["subscribed_groups"].remove(str(event.group_id))
        await event.reply("取消订阅了聊天分析功能喵~")

    @admin_group_filter
    @ca_group.command("help", description="获取聊天分析帮助信息")
    @param("command", default="", help="指令名称", required=False)
    @require_subscription
    async def cmd_help(self, event: GroupMessageEvent, command: str = ""):
        """获取聊天分析帮助信息"""
        help_message = f"插件版本：{self.version}\n"
        help_generator = HelpGenerator()
        try:
            if not command:
                help_message += help_generator.generate_group_help(self.ca_group)
            else:
                command_obj = self.ca_group.commands.get(command, None)  # type: ignore
                if not command_obj:
                    await event.reply(f"未找到指令 {command} 喵，请确认指令名称是否正确喵~")
                    return
                help_message += help_generator.generate_command_help(command_obj)
            await event.reply(help_message)
        except Exception as e:
            await event.reply(f"生成帮助信息时出错了喵：\n{e}")