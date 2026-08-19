#!/usr/bin/env python3
"""
Autopilot-Style Processing Node
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import numpy as np
import time
from collections import defaultdict
from threading import Lock

from sensor_msgs.msg import Imu, NavSatFix, Image, PointCloud2
from std_msgs.msg import Header
from geometry_msgs.msg import PoseStamped


class AutopilotProcessor(Node):
    
    def __init__(self):
        super().__init__('autopilot_processor')
        
        self.callback_group = ReentrantCallbackGroup()
        
        self.qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        # Message counters
        self.msg_counts = defaultdict(int)
        self.last_rate_log_time = time.time()
        self.rate_log_interval = 3.0
        self.count_lock = Lock()
        
        # Processing statistics
        self.total_processed = 0
        self.processing_times = []
        
        # Parameters
        self.declare_parameter('processing_level', 'medium')
        self.declare_parameter('loop_count', 1000)
        
        self.processing_level = self.get_parameter('processing_level').value
        self.loop_count = self.get_parameter('loop_count').value
        
        self._setup_subscribers()
        
        self.processed_pub = self.create_publisher(
            PoseStamped,
            '/autopilot/processed_output',
            10
        )
        
        self.rate_timer = self.create_timer(
            self.rate_log_interval, 
            self.log_message_rates
        )
        
        # Running calibration
        self._calibrate()
        
        self.get_logger().info(
            f'Autopilot Processor initialized\n'
            f'  Processing level: {self.processing_level}\n'
            f'  Loop count: {self.loop_count}'
        )
    
    def _calibrate(self):
        start = time.perf_counter()
        self._do_processing()
        cal_time = (time.perf_counter() - start) * 1000
        self.get_logger().info(f'Calibration: single processing takes {cal_time:.2f} ms')
    
    def _setup_subscribers(self):
        self.imu_sub = self.create_subscription(
            Imu, '/sensors/imu', self.imu_callback,
            self.qos_profile, callback_group=self.callback_group
        )
        self.gps_sub = self.create_subscription(
            NavSatFix, '/sensors/gps', self.gps_callback,
            self.qos_profile, callback_group=self.callback_group
        )
        self.camera_sub = self.create_subscription(
            Image, '/sensors/camera', self.camera_callback,
            self.qos_profile, callback_group=self.callback_group
        )
        self.lidar_sub = self.create_subscription(
            PointCloud2, '/sensors/lidar', self.lidar_callback,
            self.qos_profile, callback_group=self.callback_group
        )
        self.get_logger().info('All sensor subscriptions created')
    
    def _do_processing(self):
        """
        CPU-intensive processing with three distinct levels.
        """
        level = self.processing_level
        count = self.loop_count
        
        if level == 'light':
            # Light: Simple arithmetic in tight loop
            total = 0.0
            for i in range(count):
                total += (i * 3.14159) / (i + 1)
                total = total * 0.999
            
            # Small array operations
            arr = np.arange(100, dtype=np.float64)
            for _ in range(count // 100):
                arr = np.sin(arr) * np.cos(arr)
                _ = np.mean(arr)
        
        elif level == 'medium':
            # Medium: Matrix operations in loop
            size = 30
            for _ in range(count // 50):
                a = np.random.randn(size, size).astype(np.float32)
                b = np.random.randn(size, size).astype(np.float32)
                c = np.matmul(a, b)
                _ = np.mean(c)
                _ = np.std(c)
            
            # Additional tight loop
            total = 0.0
            for i in range(count * 2):
                total += (i * 2.71828) / (i + 1)
        
        elif level == 'heavy':
            # Heavy: Larger matrices + eigenvalue decomposition
            size = 50
            for _ in range(count // 25):
                a = np.random.randn(size, size).astype(np.float32)
                b = np.random.randn(size, size).astype(np.float32)
                c = np.matmul(a, b)
                
                # Eigenvalue decomposition
                sym = (c + c.T) / 2
                eigenvalues = np.linalg.eigvalsh(sym)
                
                # Normalization
                normalized = (c - np.mean(c)) / (np.std(c) + 1e-8)
                _ = np.tanh(normalized)
            
            # Additional tight loop
            total = 0.0
            for i in range(count * 5):
                total += (i * 1.41421) / (i + 1)
        
        else:
            # Default to medium
            self.processing_level = 'medium'
            self._do_processing()
    
    def cpu_intensive_processing(self):
        """Wrapper"""
        start_time = time.perf_counter()
        self._do_processing()
        processing_time = time.perf_counter() - start_time
        self.processing_times.append(processing_time)
        return processing_time
    
    def process_and_publish(self, topic_name: str, header: Header):
        with self.count_lock:
            self.msg_counts[topic_name] += 1
            self.total_processed += 1
        
        proc_time = self.cpu_intensive_processing()
        
        output_msg = PoseStamped()
        output_msg.header.stamp = self.get_clock().now().to_msg()
        output_msg.header.frame_id = 'processed_output'
        
        output_msg.pose.position.x = float(self.total_processed)
        output_msg.pose.position.y = proc_time * 1000
        output_msg.pose.position.z = float(self.msg_counts[topic_name])
        output_msg.pose.orientation.w = 1.0
        
        self.processed_pub.publish(output_msg)
    
    def imu_callback(self, msg: Imu):
        self.process_and_publish('/sensors/imu', msg.header)
    
    def gps_callback(self, msg: NavSatFix):
        self.process_and_publish('/sensors/gps', msg.header)
    
    def camera_callback(self, msg: Image):
        self.process_and_publish('/sensors/camera', msg.header)
    
    def lidar_callback(self, msg: PointCloud2):
        self.process_and_publish('/sensors/lidar', msg.header)
    
    def log_message_rates(self):
        current_time = time.time()
        elapsed = current_time - self.last_rate_log_time
        
        if elapsed <= 0:
            return
        
        self.get_logger().info('=' * 60)
        self.get_logger().info(f'PROCESSING REPORT (level: {self.processing_level})')
        self.get_logger().info('-' * 60)
        self.get_logger().info('MESSAGE RECEPTION RATES:')
        
        with self.count_lock:
            total_rate = 0
            for topic, count in sorted(self.msg_counts.items()):
                rate = count / elapsed
                total_rate += rate
                self.get_logger().info(f'  {topic}: {rate:.2f} Hz')
            
            self.get_logger().info(f'  TOTAL INPUT: {total_rate:.2f} Hz')
            self.get_logger().info(f'  Total messages processed: {self.total_processed}')
            
            if self.processing_times:
                recent = self.processing_times[-200:]
                avg_ms = np.mean(recent) * 1000
                min_ms = np.min(recent) * 1000
                max_ms = np.max(recent) * 1000
                std_ms = np.std(recent) * 1000
                
                self.get_logger().info(f'  Processing time - Avg: {avg_ms:.2f} ms | '
                                      f'Min: {min_ms:.2f} ms | Max: {max_ms:.2f} ms | '
                                      f'Std: {std_ms:.2f} ms')
                
                # Calculating the theoretical max throughput
                if avg_ms > 0:
                    max_throughput = 1000.0 / avg_ms
                    self.get_logger().info(
                        f'  Theoretical max throughput: {max_throughput:.1f} msgs/sec')
            
            self.msg_counts.clear()
        
        self.last_rate_log_time = current_time
        self.get_logger().info('=' * 60)


def main(args=None):
    rclpy.init(args=args)
    node = AutopilotProcessor()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()