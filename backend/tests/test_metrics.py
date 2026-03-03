"""
Tests for Metrics Module
"""

import pytest
from modules.metrics import MetricsCollector


class TestMetricsCollector:
    
    def test_increment_counter(self):
        """Test counter increment"""
        metrics = MetricsCollector()
        
        metrics.inc_counter("test_counter")
        assert metrics.get_counter("test_counter") == 1
        
        metrics.inc_counter("test_counter", 5)
        assert metrics.get_counter("test_counter") == 6
    
    def test_set_gauge(self):
        """Test gauge setting"""
        metrics = MetricsCollector()
        
        metrics.set_gauge("test_gauge", 42.5)
        assert metrics.get_gauge("test_gauge") == 42.5
        
        metrics.set_gauge("test_gauge", 100.0)
        assert metrics.get_gauge("test_gauge") == 100.0
    
    def test_observe_histogram(self):
        """Test histogram observations"""
        metrics = MetricsCollector()
        
        metrics.observe_histogram("test_histogram", 1.0)
        metrics.observe_histogram("test_histogram", 2.0)
        metrics.observe_histogram("test_histogram", 3.0)
        
        stats = metrics.get_histogram_stats("test_histogram")
        assert stats["count"] == 3
        assert stats["avg"] == 2.0
        assert stats["min"] == 1.0
        assert stats["max"] == 3.0
    
    def test_histogram_percentiles(self):
        """Test histogram percentile calculation"""
        metrics = MetricsCollector()
        
        # Add 100 observations
        for i in range(1, 101):
            metrics.observe_histogram("test_histogram", float(i))
        
        stats = metrics.get_histogram_stats("test_histogram")
        assert stats["p50"] == pytest.approx(50, abs=2)
        assert stats["p95"] == pytest.approx(95, abs=2)
        assert stats["p99"] == pytest.approx(99, abs=2)
    
    def test_get_all_metrics(self):
        """Test getting all metrics"""
        metrics = MetricsCollector()
        
        metrics.inc_counter("counter1")
        metrics.set_gauge("gauge1", 100.0)
        metrics.observe_histogram("histogram1", 5.0)
        
        all_metrics = metrics.get_all_metrics()
        
        assert "timestamp" in all_metrics
        assert "uptime_seconds" in all_metrics
        assert "counters" in all_metrics
        assert "gauges" in all_metrics
        assert "histograms" in all_metrics
        
        assert all_metrics["counters"]["counter1"] == 1
        assert all_metrics["gauges"]["gauge1"] == 100.0
    
    def test_export_prometheus(self):
        """Test Prometheus format export"""
        metrics = MetricsCollector()
        
        metrics.inc_counter("http_requests_total")
        metrics.set_gauge("active_connections", 5.0)
        
        prometheus_output = metrics.export_prometheus()
        
        assert "http_requests_total" in prometheus_output
        assert "active_connections" in prometheus_output
        assert "# TYPE" in prometheus_output
    
    def test_reset_metrics(self):
        """Test metrics reset"""
        metrics = MetricsCollector()
        
        metrics.inc_counter("counter1")
        metrics.set_gauge("gauge1", 100.0)
        
        metrics.reset()
        
        assert metrics.get_counter("counter1") == 0
        assert metrics.get_gauge("gauge1") == 0.0
