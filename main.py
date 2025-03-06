# main.py
from astrbot.api.event.filter import command
from astrbot.api.star import Context, Star, register
import psutil
import platform
import datetime
import asyncio
from typing import Optional

@register("简单系统状态查询", "腾讯元宝", "服务器状态监控插件", "1.0.0", "https://github.com/Meguminlove/astrbot_plugin_server_status")
class ServerMonitor(Star):
    def __init__(self, context: Context):
        super().__init__(context)  # 正确调用父类构造
        self.config = getattr(context, 'config', {})  # 安全获取配置
        self._monitor_task: Optional[asyncio.Task] = None

    async def initialize(self):
        """初始化定时任务"""
        if (interval := self.config.get('monitor_interval', 0)) > 0:
            self._monitor_task = asyncio.create_task(self._monitor_loop(interval))

    async def _monitor_loop(self, interval: int):
        """定时监控循环"""
        while True:
            await asyncio.sleep(interval)
            # 这里可以添加定时推送逻辑

    @command("状态查询", alias=["status"])
    async def server_status(self, event):
        try:
            # 获取系统信息
            cpu_usage = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()

            # 构建状态信息
            status_msg = (
                "🖥️ 服务器状态报告\n"
                "------------------\n"
                f"• 系统版本  : {platform.platform()}\n"
                f"• CPU使用率 : {cpu_usage}%\n"
                f"• 内存使用  : {self._bytes_to_gb(mem.used)}G/{self._bytes_to_gb(mem.total)}G({mem.percent}%)\n"
                f"• 磁盘使用  : {self._bytes_to_gb(disk.used)}G/{self._bytes_to_gb(disk.total)}G({disk.percent}%)\n"
                f"• 网络流量  : ↑{self._bytes_to_mb(net.bytes_sent)}MB ↓{self._bytes_to_mb(net.bytes_recv)}MB\n"
                f"• 当前时间  : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            yield event.plain_result(status_msg)
        except Exception as e:
            yield event.plain_result(f"⚠️ 状态获取失败: {str(e)}")

    @staticmethod
    def _bytes_to_gb(bytes_num: int) -> float:
        return round(bytes_num / 1024**3, 1)
    
    @staticmethod
    def _bytes_to_mb(bytes_num: int) -> float:
        return round(bytes_num / 1024**2, 1)

    async def terminate(self):
        if self._monitor_task and not self._monitor_task.cancelled():
            self._monitor_task.cancel()
        await super().terminate()