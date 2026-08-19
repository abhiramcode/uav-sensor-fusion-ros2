#!/usr/bin/env python3
"""
System Monitoring Node
"""

import rclpy
from rclpy.node import Node
import psutil
import time
from collections import deque

from geometry_msgs.msg import PoseStamped


class MonitoringNode(Node):
    
    def __init__(self):
        super().__init__('monitoring_node')

        self.processed_sub = self.create_subscription(
            PoseStamped,
            '/autopilot/processed_output',
            self.processed_callback,
            10
        )

        self.msg_count = 0
        self.last_log_time = time.time()
        self.log_interval = 2.0
        
        self.latencies = deque(maxlen=500)
        
        # CPU monitoring
        self.cpu_percentages = deque(maxlen=100)
        self.process = psutil.Process()

        self.monitor_timer = self.create_timer(self.log_interval, self.log_statistics)

        psutil.cpu_percent(percpu=True)
        self.process.cpu_percent()
        
        self.get_logger().info('Monitoring Node initialized')
        self.get_logger().info(f'CPU cores available: {psutil.cpu_count()}')
        self.get_logger().info(f'Memory available: {psutil.virtual_memory().total / (1024**3):.1f} GB')
    
    def processed_callback(self, msg: PoseStamped):
        """Handle processed output messages."""
        self.msg_count += 1
        
        # Calculating message latency
        current_time = self.get_clock().now()
        msg_time = rclpy.time.Time.from_msg(msg.header.stamp)
        latency_ns = (current_time - msg_time).nanoseconds
        latency_ms = latency_ns / 1e6
        
        self.latencies.append(latency_ms)
    
    def log_statistics(self):
        """Log processing and system statistics."""
        current_time = time.time()
        elapsed = current_time - self.last_log_time
        
        if elapsed <= 0:
            return
        
        # Calculating processing rate
        processing_rate = self.msg_count / elapsed
        
        # Getting CPU usage
        system_cpu = psutil.cpu_percent(percpu=False)
        per_core_cpu = psutil.cpu_percent(percpu=True)
        process_cpu = self.process.cpu_percent()
        
        # Memory usage
        memory = psutil.virtual_memory()
        process_memory = self.process.memory_info()
        
        self.get_logger().info('')
        self.get_logger().info('╔══════════════════════════════════════════════════╗')
        self.get_logger().info('║           SYSTEM MONITORING REPORT               ║')
        self.get_logger().info('╠══════════════════════════════════════════════════╣')
        
        self.get_logger().info('║ PROCESSING STATISTICS:                           ║')
        self.get_logger().info(f'║   Output Rate: {processing_rate:>8.2f} msgs/sec                 ║')
        self.get_logger().info(f'║   Total Processed: {self.msg_count:>8} msgs                 ║')

        if self.latencies:
            avg_latency = sum(self.latencies) / len(self.latencies)
            min_latency = min(self.latencies)
            max_latency = max(self.latencies)
            self.get_logger().info(f'║   Avg Latency: {avg_latency:>8.2f} ms                       ║')
            self.get_logger().info(f'║   Min/Max Latency: {min_latency:.1f}/{max_latency:.1f} ms                    ║')
        
        self.get_logger().info('╠══════════════════════════════════════════════════╣')
        
        # CPU statistics
        self.get_logger().info('║ CPU USAGE:                                       ║')
        self.get_logger().info(f'║   System Total: {system_cpu:>6.1f}%                          ║')
        self.get_logger().info(f'║   Process CPU: {process_cpu:>7.1f}%                          ║')
        
        core_str = ' '.join([f'{cpu:4.0f}%' for cpu in per_core_cpu[:4]])
        if len(per_core_cpu) > 4:
            core_str += ' ...'
        self.get_logger().info(f'║   Per-Core: {core_str}          ║')
        
        self.get_logger().info('╠══════════════════════════════════════════════════╣')
        
        # Memory statistics
        self.get_logger().info('║ MEMORY USAGE:                                    ║')
        self.get_logger().info(f'║   System: {memory.percent:>5.1f}% ({memory.used/(1024**3):.1f}/{memory.total/(1024**3):.1f} GB)                    ║')
        self.get_logger().info(f'║   Process RSS: {process_memory.rss/(1024**2):>6.1f} MB                         ║')
        
        self.get_logger().info('╚══════════════════════════════════════════════════╝')
        
        # Resetting counters
        self.msg_count = 0
        self.last_log_time = current_time


def main(args=None):
    rclpy.init(args=args)
    node = MonitoringNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()