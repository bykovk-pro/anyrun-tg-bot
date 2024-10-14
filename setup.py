from setuptools import setup, find_packages

setup(
    name="anyrun-tg-bot",
    version="0.5.12",
    author="Kirill Bykov",
    author_email="me@bykovk.pro",
    description="A Telegram bot for interacting with the ANY.RUN API",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bykovk-pro/ANY.RUN-for-Telegram",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Customer Service",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Security",
        "Topic :: Education",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows"
    ],
    python_requires=">=3.7",
    install_requires=[
        "python-telegram-bot==21.6",
        "python-dotenv==1.0.0",
        "requests==2.25.0",
        "aiosqlite==0.19.0",
        "pyzipper==0.3.6",
        "watchdog==2.2.1",
        "aiohttp==3.10.9",
    ],
    extras_require={
        "dev": [
            "pyinstaller==6.10.0",
            "pyinstaller-hooks-contrib==2024.8",
            "python-daemon==3.0.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "anyrun-tg-bot=main:main",
        ],
    },
)
