## Overview

A ROS 2 Humble Python package simulating an onboard sensor processing pipeline for autonomous UAV systems. Demonstrates multi-topic sensor fusion and real-time processing under varying computational loads.

## Architecture

┌─────────────────────────────────────────────────────────────────┐
│                      SENSOR SIMULATORS                          │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                 │
│ │   IMU   │ │   GPS   │ │  Camera │ │  LiDAR  │                 │
│ │ 100 Hz  │ │  10 Hz  │ │  30 Hz  │ │  10 Hz  │                 │
│ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘                 │
│      │           │           │           │                      │
│      └───────────┴─────┬─────┴───────────┘                      │
│                        ▼                                        │
│            ┌───────────────────────┐                            │
│            │ AUTOPILOT PROCESSOR   │                            │
│            │ - Subscribes all      │                            │
│            │ - CPU processing      │                            │
│            │ - Rate logging        │                            │
│            └───────────┬───────────┘                            │
│                        ▼                                        │
│            ┌───────────────────────┐                            │
│            │ MONITORING NODE       │                            │
│            │ - Output rate         │                            │
│            │ - CPU/Memory stats    │                            │
│            └───────────────────────┘                            │
└─────────────────────────────────────────────────────────────────┘



## Message Types (Standard ROS 2)

| Sensor |            Topic            |        Message Type       | Frequency |
|--------|-----------------------------|---------------------------|-----------|
| IMU    | /sensors/imu                | sensor_msgs/Imu           | 100 Hz    |
| GPS    | /sensors/gps                | sensor_msgs/NavSatFix     | 10 Hz     |
| Camera | /sensors/camera             | sensor_msgs/Image         | 30 Hz     |
| LiDAR  | /sensors/lidar              | sensor_msgs/PointCloud2   | 10 Hz     |
| Output | /autopilot/processed_output | geometry_msgs/PoseStamped | Variable  |

## Quick Start

```bash
# Build
cd ~/ros2_ws
colcon build --packages-select sensor_pipeline_pkg
source install/setup.bash

# To Run with default settings
ros2 launch sensor_pipeline_pkg pipeline_launch.py

# To Run with specific workload
ros2 launch sensor_pipeline_pkg pipeline_launch.py processing_level:=light
ros2 launch sensor_pipeline_pkg pipeline_launch.py processing_level:=medium
ros2 launch sensor_pipeline_pkg pipeline_launch.py processing_level:=heavy
# or alternatively use the run_experiments.sh script to automate above
'''
