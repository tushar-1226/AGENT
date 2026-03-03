"""
Metrics Module
Prometheus-compatible metrics for monitoring
"""

import time
from typing import Dict, List
from collections import defaultdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect application metrics"""
    
    def __init__(self):
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.start_time = time.time()
    
    def inc_counter(self, name: str, value: int = 1):
        """Increment a counter"""
        self.counters[name] += value
    
    def set_gauge(self, name: str, value: float):
        """Set a gauge value"""
        self.gauges[name] = value
    
    def observe_histogram(self, name: str, value: float):
        """Observe a value for histogram"""
        self.histograms[name].append(value)
        
        # Keep only last 1000 observations
        if len(self.histograms[name]) > 1000:
            self.histograms[name] = self.histograms[name][-1000:]
    
    def get_counter(self, name: str) -> int:
        """Get counter value"""
        return self.counters.get(name, 0)
    
    def get_gauge(self, name: str) -> float:
        """Get gauge value"""
        return self.gauges.get(name, 0.0)
    
    def get_histogram_stats(self, name: str) -> Dict:
        """Get histogram statistics"""
        values = self.histograms.get(name, [])
        
        if not values:
            return {"count": 0, "sum": 0, "avg": 0, "min": 0, "max": 0}
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        return {
            "count": count,
            "sum": sum(sorted_values),
            "avg": sum(sorted_values) / count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "p50": sorted_values[int(count * 0.5)],
            "p95": sorted_values[int(count * 0.95)],
            "p99": sorted_values[int(count * 0.99)] if count > 100 else sorted_values[-1]
        }
    
    def get_all_metrics(self) -> Dict:
        """Get all metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - self.start_time,
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {
                name: self.get_histogram_stats(name)
                for name in self.histograms.keys()
            }
        }
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        # Counters
        for name, value in self.counters.items():
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {value}")
        
        # Gauges
        for name, value in self.gauges.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")
        
        # Histograms
        for name in self.histograms.keys():
            stats = self.get_histogram_stats(name)
            lines.append(f"# TYPE {name} histogram")
            lines.append(f"{name}_count {stats['count']}")
            lines.append(f"{name}_sum {stats['sum']}")
            lines.append(f"{name}_avg {stats['avg']}")
        
        return "\n".join(lines)
    
    def reset(self):
        """Reset all metrics"""
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        logger.info("Metrics reset")


# Global metrics instance
_metrics_collector: MetricsCollector = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create metrics collector singleton"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


class MetricsMiddleware:
    """Middleware for tracking request metrics"""
    
    def __init__(self, app):
        self.app = app
        self.metrics = get_metrics_collector()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                duration = time.time() - start_time
                
                # Record metrics
                self.metrics.inc_counter("http_requests_total")
                self.metrics.observe_histogram("http_request_duration_seconds", duration)
                
                status_code = message.get("status", 0)
                if status_code >= 500:
                    self.metrics.inc_counter("http_requests_failed_total")
                elif status_code >= 400:
                    self.metrics.inc_counter("http_requests_client_error_total")
                else:
                    self.metrics.inc_counter("http_requests_success_total")
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
