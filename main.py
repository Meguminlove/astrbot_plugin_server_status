from astrbot.api.event.filter import command
from astrbot.api.star import Context, Star, register
import psutil
import platform
import datetime
import asyncio
import os
from typing import Optional

@register("服务器状态监控", "腾讯元宝", "增强版状态监控插件", "1.1.0", "https://github.com/Meguminlove/astrbot_plugin_server_status")
class ServerMonitor(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.config = getattr(context, 'config', {})
        self._monitor_task: Optional[asyncio.Task] = None

    def _get_uptime(self) -> str:
        """获取系统运行时间"""
        boot_time = psutil.boot_time()
        now = datetime.datetime.now().timestamp()
        uptime_seconds = int(now - boot_time)
        
        # 转换为可读格式
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        time_units = []
        if days > 0:
            time_units.append(f"{days}天")
        if hours > 0:
            time_units.append(f"{hours}小时")
        if minutes > 0:
            time_units.append(f"{minutes}分")
        time_units.append(f"{seconds}秒")
        
        return " ".join(time_units)

    def _get_load_avg(self) -> str:
        """获取系统负载信息"""
        try:
            load = os.getloadavg()
            return f"{load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}"
        except AttributeError:
            return "不可用（Windows系统）"

    @command("状态查询", alias=["status"])
    async def server_status(self, event):
        try:
            # 获取系统信息
            cpu_usage = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()

            # 构建增强版状态信息
            status_msg = (
                "🖥️ 服务器状态报告\n"
                "------------------\n"
                f"• 系统信息  : {platform.system()} {platform.release()}\n"
                f"• 运行时间  : {self._get_uptime()}\n"
                f"• 系统负载  : {self._get_load_avg()}\n"
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