from setuptools import setup, find_packages

setup(
    name="terminalchat",
    version="0.2",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'terminalchat=terminalchat.main:main',
        ],
    },
    install_requires=[
        "websockets"
    ],
)