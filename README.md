# uav-sensor-fusion-ros2

Add sensor processing pipeline package for UAV

- Created `sensor_pipeline_pkg` with a complete sensor processing pipeline for autonomous UAV systems.
- Implemented sensor simulators for IMU, GPS, Camera, and LiDAR.
- Developed an autopilot processor node for handling sensor data and performing CPU-intensive processing.
- Added a monitoring node to log system performance and message latencies.
- Created launch file to manage the execution of all nodes in the pipeline.
- Included a script to run experiments with varying workloads.
- Added package metadata and configuration files for ROS 2 integration.
- Implemented unit tests for copyright, flake8, and PEP257 compliance.
