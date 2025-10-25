# setup.py
from setuptools import setup, find_packages

setup(
    name='ftp-transfer-agent',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'requests>=2.31.0',
        'paramiko>=3.3.1',
        'lz4>=4.3.2',
        'psutil>=5.9.5',
        'pywin32>=306',  # For Windows service
    ],
    entry_points={
        'console_scripts': [
            'ftp-agent=agent.main:main',
        ],
    },
)
