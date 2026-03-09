from setuptools import setup

setup(
    name="Caching-Proxy",
    version="1.0",
    py_modules=["main"],
    entry_points={
        "console_scripts": [
            "Caching-Proxy=main:main",
        ],
    },
)
