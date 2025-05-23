from setuptools import setup

package_name = 'params_manager_py'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, ['params_manager_py/params_manager.py'])
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dotX Automation s.r.l.',
    maintainer_email='info@dotxautomation.com',
    description='Python component to easily manage ROS 2 node parameters.',
    license='Apache-2.0',
    tests_require=['pytest']
)
