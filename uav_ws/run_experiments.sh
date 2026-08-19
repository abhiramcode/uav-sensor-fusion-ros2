#!/bin/bash
# Run all experiments and collect data

echo "========================================"
echo "SUAS Sensor Pipeline Experiments"
echo "========================================"
echo ""

echo "Starting Experiment 1: Light Workload"
echo "Running for 20 seconds..."
timeout 20 ros2 launch sensor_pipeline_pkg pipeline_launch.py processing_level:=light loop_count:=500 2>&1 | tail -50

echo ""
echo "========================================"
echo ""

echo "Starting Experiment 2: Medium Workload"
echo "Running for 20 seconds..."
timeout 20 ros2 launch sensor_pipeline_pkg pipeline_launch.py processing_level:=medium loop_count:=1000 2>&1 | tail -50

echo ""
echo "========================================"
echo ""

echo "Starting Experiment 3: Heavy Workload"
echo "Running for 20 seconds..."
timeout 20 ros2 launch sensor_pipeline_pkg pipeline_launch.py processing_level:=heavy loop_count:=1500 2>&1 | tail -50

echo ""
echo "========================================"
echo "Experiments Complete!"
echo "========================================"
