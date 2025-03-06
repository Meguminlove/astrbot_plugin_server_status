# astrbot_plugin_server_status
# AstrBot 服务器状态监控插件

[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-3.4%2B-orange.svg)](https://github.com/Soulter/AstrBot)

实时监控服务器资源使用情况，支持多平台运行，提供清晰的系统状态报告。

## 📦 安装

```bash
# 克隆仓库到插件目录
cd /AstrBot/data/plugins
git clone https://github.com/Meguminlove/astrbot_plugin_server_status/astrbot_plugin_server_status.git

# 安装依赖
pip install -r astrbot_plugin_server_status/requirements.txt
```

## 🛠️ 功能特性
- 实时 CPU/内存/磁盘/网络监控
- 智能阈值告警系统
- 定时状态推送
- 跨平台支持 (Linux/Windows/macOS)

## ⌨️ 使用命令

### 基础命令
```plaintext
/状态查询  或  /status
```
**示例输出：​**
```
🖥️ 服务器状态报告
------------------
• 系统版本  : Linux-5.15.0-78-generic-x86_64
• CPU使用率 : 12.3%
• 内存使用  : 3.8G/7.6G(50.2%)
• 磁盘使用  : 28.5G/50.0G(57.0%)
• 网络速率  : ↑1.5MB/s ↓2.3MB/s
• 当前时间  : 2024-02-20 16:30:45
```

### 高级功能
```plaintext
/状态配置 <参数> <值>
```
可用参数：  
✅ `interval` - 监控间隔 (单位：秒)  
✅ `threshold.cpu` - CPU告警阈值 (%)  
✅ `threshold.mem` - 内存告警阈值 (%)

**配置示例：​**
```plaintext
/状态配置 interval 600
/状态配置 threshold.cpu 85
```

## ⚙️ 配置文件
编辑 `data/config/server_status_config.json`：
```json
{
    "monitor_interval": 300,
    "alert_threshold": {
        "cpu": 90,
        "memory": 85
    },
    "chart_style": "gradient"
}
```

## 📌 注意事项
1. Linux 系统需安装基础工具：
```bash
sudo apt-get install procps sysstat
```
2. 首次使用需授予执行权限
3. 推荐监控间隔 ≥ 60 秒

## 🤝 参与贡献
1. Fork 本仓库
2. 创建新分支 (`git checkout -b feature/awesome-feature`)
3. 提交修改 (`git commit -m 'Add some feature'`)
4. 推送更改 (`git push origin feature/awesome-feature`)
5. 创建 Pull Request

## 📜 开源协议
本项目采用 [MIT License](LICENSE)
