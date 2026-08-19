#!/usr/bin/env python3
"""
Launch file for the complete sensor processing pipeline.
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    
    processing_level_arg = DeclareLaunchArgument(
        'processing_level',
        default_value='medium',
        description='Processing intensity: light, medium, or heavy'
    )
    
    loop_count_arg = DeclareLaunchArgument(
        'loop_count',
        default_value='1000',
        description='Base loop count for processing workload'
    )
    
    imu_simulator = Node(
        package='sensor_pipeline_pkg',
        executable='imu_simulator',
        name='imu_simulator',
        output='screen'
    )
    
    gps_simulator = Node(
        package='sensor_pipeline_pkg',
        executable='gps_simulator',
        name='gps_simulator',
        output='screen'
    )
    
    camera_simulator = Node(
        package='sensor_pipeline_pkg',
        executable='camera_simulator',
        name='camera_simulator',
        output='screen'
    )
    
    lidar_simulator = Node(
        package='sensor_pipeline_pkg',
        executable='lidar_simulator',
        name='lidar_simulator',
        output='screen'
    )
    
    autopilot_processor = TimerAction(
        period=2.0,
        actions=[
            Node(
                package='sensor_pipeline_pkg',
                executable='autopilot_processor',
                name='autopilot_processor',
                output='screen',
                parameters=[{
                    'processing_level': LaunchConfiguration('processing_level'),
                    'loop_count': LaunchConfiguration('loop_count'),
                }]
            )
        ]
    )
    
    monitoring_node = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='sensor_pipeline_pkg',
                executable='monitoring_node',
                name='monitoring_node',
                output='screen'
            )
        ]
    )
    
    return LaunchDescription([
        processing_level_arg,
        loop_count_arg,
        imu_simulator,
        gps_simulator,
        camera_simulator,
        lidar_simulator,
        autopilot_processor,
        monitoring_node
    ])