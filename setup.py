from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="anyrun-tg-bot",
    version="0.5.3",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author="Kirill Bykov",
    author_email="me@bykovk.pro",
    description="A Telegram bot for interacting with the ANY.RUN API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bykovk-pro/ANY.RUN-for-Telegram",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "python-telegram-bot==20.3",
        "python-dotenv==1.0.0",
        "requests==2.25.0",
        "pyyaml==6.0",
    ],
    extras_require={
        "dev": [
            "pyinstaller==6.10.0",
            "pyinstaller-hooks-contrib==2024.8",
            "python-daemon==3.0.1",
            "setuptools==75.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "anyrun-tg-bot=main:main",
        ],
    },
)