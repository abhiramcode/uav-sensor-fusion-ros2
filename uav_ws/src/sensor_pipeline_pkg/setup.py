from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'sensor_pipeline_pkg'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), 
            glob('launch/*.py')),
    ],
    install_requires=['setuptools', 'psutil', 'numpy'],
    zip_safe=True,
    maintainer='Abhiram',
    maintainer_email='abhiramsulige@gmail.com',
    description='SUAS-style sensor processing pipeline',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'imu_simulator = sensor_pipeline_pkg.sensor_simulators:imu_main',
            'gps_simulator = sensor_pipeline_pkg.sensor_simulators:gps_main',
            'camera_simulator = sensor_pipeline_pkg.sensor_simulators:camera_main',
            'lidar_simulator = sensor_pipeline_pkg.sensor_simulators:lidar_main',
            'autopilot_processor = sensor_pipeline_pkg.autopilot_processor:main',
            'monitoring_node = sensor_pipeline_pkg.monitoring_node:main',
        ],
    },
)