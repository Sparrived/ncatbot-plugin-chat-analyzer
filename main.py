from ncatbot.plugin_system import NcatBotPlugin, admin_filter, command_registry, option, param
from ncatbot.utils import get_log
from ncatbot.core import BaseMessageEvent, GroupMessageEvent, PrivateMessageEvent


class ChatAnalyzer(NcatBotPlugin):
    name = "ChatAnalyzer"
    version = "1.0.0"
    description = "一个用于检查机器人宿主机IP地址的插件，支持定时检查并播送到指定群聊/个人。"
    log = get_log(name)

    def init_config(self):
        """注册配置项"""
        self.register_config("last_ip", "127.0.0.1", value_type=str) # 上一次获取的IP
        self.register_config("check_interval", 30, value_type=int) # 检查间隔
        self.register_config("notify", {"enabled": False, "private": [], "group": []}, value_type=dict) # 订阅信息的群/个人
        self._last_ip = self.config["last_ip"]
        self._notify = self.config["notify"]


    # ======== 初始化插件 ========
    async def on_load(self):
        self.init_config()

    # ======== 注册指令 ========
