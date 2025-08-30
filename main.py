from astrbot.api.event.filter import command
from astrbot.api.star import Context, Star, register
import psutil
import platform
import datetime
import asyncio
import os
from typing import Optional

@register("服务器状态监控", "腾讯元宝&Meguminlove", "简单状态监控插件", "1.9.1", "https://github.com/Meguminlove/astrbot_plugin_server_status")
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

    def _get_windows_version(self) -> str:
        """精确识别Windows版本"""
        # 实际上，platform.platform() 就能提供详细信息
        return platform.platform()

    def _get_load_avg(self) -> str:
        """获取系统负载信息"""
        try:
            load = os.getloadavg()
            return f"{load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}"
        except AttributeError:
            return "不可用（Windows系统）"
            
    def _get_disk_info(self) -> dict:
        """获取所有磁盘分区的总使用情况"""
        total_size = 0
        used_size = 0
        partitions = psutil.disk_partitions()
        for partition in partitions:
            # 某些分区类型（如CD-ROM）可能在未插入介质时引发错误
            # 使用 try-except 来跳过这些分区
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                total_size += usage.total
                used_size += usage.used
            except OSError:
                # 忽略无法访问的分区
                continue
        
        percent = (used_size / total_size * 100) if total_size > 0 else 0
        
        return {
            'total': total_size,
            'used': used_size,
            'percent': percent
        }

    @command("状态查询", alias=["status"])
    async def server_status(self, event):
        try:
            # 初始化CPU使用率采样
            psutil.cpu_percent(interval=0.5)
            cpu_usage = psutil.cpu_percent(interval=1, percpu=False)
            
            # 优化系统版本识别
            system_name = (
                self._get_windows_version()
                if platform.system() == "Windows"
                else f"{platform.system()} {platform.release()}"
            )

            mem = psutil.virtual_memory()
            disk = self._get_disk_info() # <-- 修改点：调用新的磁盘信息获取方法
            # 记录初始网络流量
            net1 = psutil.net_io_counters()
            await asyncio.sleep(1)
            # 记录1秒后的网络流量
            net2 = psutil.net_io_counters()
            # 计算每秒网络流量
            net_sent_per_sec = net2.bytes_sent - net1.bytes_sent
            net_recv_per_sec = net2.bytes_recv - net1.bytes_recv

            status_msg = (
                "🖥️ 服务器状态报告\n"
                "------------------\n"
                f"• CPU使用率 : {cpu_usage}%\n"
                f"• 系统版本  : {system_name}\n"
                f"• 运行时间  : {self._get_uptime()}\n"
                f"• 系统负载  : {self._get_load_avg()}\n"
                f"• 内存使用  : {self._bytes_to_gb(mem.used)}G/{self._bytes_to_gb(mem.total)}G({mem.percent}%)\n"
                # <-- 修改点：使用新的磁盘信息字典
                f"• 磁盘使用  : {self._bytes_to_gb(disk['used'])}G/{self._bytes_to_gb(disk['total'])}G({disk['percent']:.1f}%)\n"
                f"• 网络流量  : ↑{self._bytes_to_mb(net_sent_per_sec)}MB/s ↓{self._bytes_to_mb(net_recv_per_sec)}MB/s\n"
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

