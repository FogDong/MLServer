import os

from typing import Dict
from setuptools import setup, find_packages

ROOT_PATH = os.path.dirname(__file__)
PKG_NAME = "mlserver-mllib"
PKG_PATH = os.path.join(ROOT_PATH, PKG_NAME)


def _load_version() -> str:
    version = ""
    version_path = os.path.join(PKG_NAME, "version.py")
    with open(version_path) as fp:
        version_module: Dict[str, str] = {}
        exec(fp.read(), version_module)
        version = version_module["__version__"]

    return version


setup(
    name=PKG_NAME,
    version=_load_version(),
    url=f"https://github.com/seldonio/{PKG_NAME}.git",
    author="Seldon Technologies Ltd.",
    author_email="hello@seldon.io",
    description="ML server",
    packages=find_packages(),
    install_requires=[
        "mlserver",
        "pyspark==3.0.1",
    ],
    entry_points={"console_scripts": ["mlserver-mllib=mlserver.cli:main"]},
)
