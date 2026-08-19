#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import numpy as np

from sensor_msgs.msg import Imu, NavSatFix, Image, PointCloud2, PointField
from std_msgs.msg import Header
from builtin_interfaces.msg import Time

import time



class BaseSensorSimulator(Node):
    """Base class for all following sensor simulators with common functionality."""
    
    def __init__(self, node_name, topic_name, msg_type, frequency: float):
        super().__init__(node_name)

        self.qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        self.publisher = self.create_publisher(msg_type, topic_name, self.qos_profile)
        self.timer = self.create_timer(1.0 / frequency, self.publish_callback)
        self.frequency = frequency
        self.msg_count = 0
        
        self.get_logger().info(
            f'{node_name} initialized - Publishing to {topic_name} at {frequency} Hz'
        )
    
    def get_current_header(self):
        header = Header()
        now = self.get_clock().now()
        header.stamp = now.to_msg()
        return header
    
    def publish_callback(self):
        """Gets Override in child classes to publish specific sensor data."""
        raise NotImplementedError


class IMUSimulator(BaseSensorSimulator):
    """
    Simulates IMU data.
    Generates realistic accelerometer and gyroscope readings with noise.
    """
    
    def __init__(self):
        super().__init__(
            node_name='imu_simulator',
            topic_name='/sensors/imu',
            msg_type=Imu,
            frequency=100.0
        )
        
        # Noise parameters for realistic simulation
        self.accel_noise_std = 0.05  # m/s²
        self.gyro_noise_std = 0.01   # rad/s
        
    def publish_callback(self):
        msg = Imu()
        msg.header = self.get_current_header()
        msg.header.frame_id = 'imu_link'
        
        # Accelerometer data (gravity + noise)
        msg.linear_acceleration.x = np.random.normal(0.0, self.accel_noise_std)
        msg.linear_acceleration.y = np.random.normal(0.0, self.accel_noise_std)
        msg.linear_acceleration.z = np.random.normal(-9.81, self.accel_noise_std)
        
        # Gyroscope data (small rotations + noise)
        msg.angular_velocity.x = np.random.normal(0.0, self.gyro_noise_std)
        msg.angular_velocity.y = np.random.normal(0.0, self.gyro_noise_std)
        msg.angular_velocity.z = np.random.normal(0.0, self.gyro_noise_std)
        
        # Orientation quaternion
        msg.orientation.w = 1.0
        msg.orientation.x = np.random.normal(0.0, 0.001)
        msg.orientation.y = np.random.normal(0.0, 0.001)
        msg.orientation.z = np.random.normal(0.0, 0.001)
        
        # Covariance matrices
        msg.orientation_covariance = [0.01] + [0.0]*2 + [0.01] + [0.0]*2 + [0.01] + [0.0]*2
        msg.angular_velocity_covariance = [0.001] + [0.0]*2 + [0.001] + [0.0]*2 + [0.001] + [0.0]*2
        msg.linear_acceleration_covariance = [0.01] + [0.0]*2 + [0.01] + [0.0]*2 + [0.01] + [0.0]*2
        
        self.publisher.publish(msg)
        self.msg_count += 1


class GPSSimulator(BaseSensorSimulator):
    """
    Simulates GPS data.
    Generates position data with GPS and realistic noise.
    """
    
    def __init__(self):
        super().__init__(
            node_name='gps_simulator',
            topic_name='/sensors/gps',
            msg_type=NavSatFix,
            frequency=10.0
        )
        
        # Base coordinates
        self.base_latitude = 38.14326
        self.base_longitude = -76.42839
        self.base_altitude = 50.0
        
        # GPS noise
        self.lat_lon_noise = 0.00002
        self.alt_noise = 5.0
        
    def publish_callback(self):
        msg = NavSatFix()
        msg.header = self.get_current_header()
        msg.header.frame_id = 'gps_link'
        
        # Simulating GPS position with noise
        msg.latitude = self.base_latitude + np.random.normal(0, self.lat_lon_noise)
        msg.longitude = self.base_longitude + np.random.normal(0, self.lat_lon_noise)
        msg.altitude = self.base_altitude + np.random.normal(0, self.alt_noise)

        # GPS fix status
        msg.status.status = 2  # STATUS_GBAS_FIX
        msg.status.service = 1  # SERVICE_GPS
        
        # Position covariance (ENU frame)
        msg.position_covariance = [
            6.25, 0.0, 0.0,   # East variance
            0.0, 6.25, 0.0,   # North variance  
            0.0, 0.0, 25.0    # Up variance
        ]
        msg.position_covariance_type = 2  # COVARIANCE_TYPE_DIAGONAL_KNOWN
        
        self.publisher.publish(msg)
        self.msg_count += 1


class CameraSimulator(BaseSensorSimulator):
    """
    Simulates camera image data
    """
    
    def __init__(self):
        super().__init__(
            node_name='camera_simulator',
            topic_name='/sensors/camera',
            msg_type=Image,
            frequency=30.0
        )
        
        self.width = 160
        self.height = 120
        self.channels = 3
        
        # Pre-created fixed image data
        total_bytes = self.height * self.width * self.channels
        self.image_data = bytes([128] * total_bytes)  # gray pixels
        
        self.get_logger().info(
            f'Camera configured: {self.width}x{self.height} RGB, '
            f'payload size: {len(self.image_data) / 1024:.1f} KB'
        )
        
    def publish_callback(self):
        msg = Image()
        msg.header = self.get_current_header()
        msg.header.frame_id = 'camera_link'
        
        msg.height = self.height
        msg.width = self.width
        msg.encoding = 'rgb8'
        msg.is_bigendian = False
        msg.step = self.width * self.channels
        msg.data = self.image_data
        
        self.publisher.publish(msg)
        self.msg_count += 1


class LiDARSimulator(BaseSensorSimulator):
    """
    Simulates LiDAR data at lower frequency.
    """
    
    def __init__(self):
        super().__init__(
            node_name='lidar_simulator',
            topic_name='/sensors/lidar',
            msg_type=PointCloud2,
            frequency=10.0
        )
        
        # Point cloud parameters
        self.num_points = 1000
        
    def publish_callback(self):
        msg = PointCloud2()
        msg.header = self.get_current_header()
        msg.header.frame_id = 'lidar_link'
        
        # Generating random point cloud
        points = np.random.uniform(-50, 50, (self.num_points, 3)).astype(np.float32)
        
        # Defining point fields (x, y, z)
        msg.fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
        ]
        
        msg.is_bigendian = False
        msg.point_step = 12
        msg.row_step = msg.point_step * self.num_points
        msg.height = 1
        msg.width = self.num_points
        msg.is_dense = True
        msg.data = points.tobytes()
        
        self.publisher.publish(msg)
        self.msg_count += 1


# main functions for each simulator
def imu_main(args=None):
    rclpy.init(args=args)
    node = IMUSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


def gps_main(args=None):
    rclpy.init(args=args)
    node = GPSSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


def camera_main(args=None):
    rclpy.init(args=args)
    node = CameraSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


def lidar_main(args=None):
    rclpy.init(args=args)
    node = LiDARSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
