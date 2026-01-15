"""
System Monitor Module
Provides comprehensive system information and monitoring
"""

import psutil
import platform
import os
from datetime import datetime
from typing import Dict, List
import subprocess


class SystemMonitor:
    """Monitor system resources and information"""

    def __init__(self):
        self.start_time = datetime.now()

    def get_cpu_info(self) -> Dict:
        """Get CPU information and usage"""
        cpu_freq = psutil.cpu_freq()
        cpu_percent_per_core = psutil.cpu_percent(interval=0.1, percpu=True)

        return {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "max_frequency": round(cpu_freq.max, 2) if cpu_freq else 0,
            "min_frequency": round(cpu_freq.min, 2) if cpu_freq else 0,
            "current_frequency": round(cpu_freq.current, 2) if cpu_freq else 0,
            "usage_percent": round(psutil.cpu_percent(interval=0.1), 2),
            "per_core_usage": [round(x, 2) for x in cpu_percent_per_core],
            "load_average": [round(x, 2) for x in psutil.getloadavg()] if hasattr(psutil, 'getloadavg') else []
        }

    def get_memory_info(self) -> Dict:
        """Get memory information and usage"""
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()

        return {
            "total": self._bytes_to_gb(virtual_mem.total),
            "available": self._bytes_to_gb(virtual_mem.available),
            "used": self._bytes_to_gb(virtual_mem.used),
            "percent": round(virtual_mem.percent, 2),
            "swap_total": self._bytes_to_gb(swap_mem.total),
            "swap_used": self._bytes_to_gb(swap_mem.used),
            "swap_percent": round(swap_mem.percent, 2)
        }

    def get_disk_info(self) -> List[Dict]:
        """Get disk information for all partitions"""
        disks = []

        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "filesystem": partition.fstype,
                    "total": self._bytes_to_gb(usage.total),
                    "used": self._bytes_to_gb(usage.used),
                    "free": self._bytes_to_gb(usage.free),
                    "percent": round(usage.percent, 2)
                })
            except PermissionError:
                continue

        return disks

    def get_network_info(self) -> Dict:
        """Get network information and statistics"""
        net_io = psutil.net_io_counters()
        net_if_addrs = psutil.net_if_addrs()

        interfaces = []
        for interface_name, addresses in net_if_addrs.items():
            interface_info = {"name": interface_name, "addresses": []}
            for addr in addresses:
                interface_info["addresses"].append({
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask if addr.netmask else "N/A"
                })
            interfaces.append(interface_info)

        return {
            "bytes_sent": self._bytes_to_gb(net_io.bytes_sent),
            "bytes_received": self._bytes_to_gb(net_io.bytes_recv),
            "packets_sent": net_io.packets_sent,
            "packets_received": net_io.packets_recv,
            "errors_in": net_io.errin,
            "errors_out": net_io.errout,
            "interfaces": interfaces
        }

    def get_process_info(self) -> Dict:
        """Get information about running processes"""
        process_list = []

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                process_list.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cpu_percent": round(proc.info['cpu_percent'], 2),
                    "memory_percent": round(proc.info['memory_percent'], 2)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage and get top 10
        top_processes = sorted(process_list, key=lambda x: x['cpu_percent'], reverse=True)[:10]

        return {
            "total_processes": len(process_list),
            "top_processes": top_processes
        }

    def get_system_info(self) -> Dict:
        """Get general system information"""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time

        return {
            "os": platform.system(),
            "os_version": platform.release(),
            "os_architecture": platform.machine(),
            "hostname": platform.node(),
            "python_version": platform.python_version(),
            "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_formatted": self._format_uptime(uptime)
        }

    def get_temperature_info(self) -> Dict:
        """Get system temperature information (if available)"""
        temps = {}

        try:
            if hasattr(psutil, "sensors_temperatures"):
                sensors = psutil.sensors_temperatures()
                if sensors:
                    for name, entries in sensors.items():
                        temps[name] = []
                        for entry in entries:
                            temps[name].append({
                                "label": entry.label or name,
                                "current": round(entry.current, 1),
                                "high": round(entry.high, 1) if entry.high else None,
                                "critical": round(entry.critical, 1) if entry.critical else None
                            })
        except Exception:
            pass

        return temps

    def get_battery_info(self) -> Dict:
        """Get battery information (if available)"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "percent": round(battery.percent, 2),
                    "power_plugged": battery.power_plugged,
                    "time_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "N/A"
                }
        except Exception:
            pass

        return None

    def get_complete_system_stats(self) -> Dict:
        """Get complete system statistics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": self.get_system_info(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disks": self.get_disk_info(),
            "network": self.get_network_info(),
            "processes": self.get_process_info(),
            "temperature": self.get_temperature_info(),
            "battery": self.get_battery_info()
        }

    @staticmethod
    def _bytes_to_gb(bytes_value: int) -> float:
        """Convert bytes to gigabytes"""
        return round(bytes_value / (1024 ** 3), 2)

    @staticmethod
    def _format_uptime(uptime) -> str:
        """Format uptime as human-readable string"""
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")

        return " ".join(parts)
