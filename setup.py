import os
import sys

from setuptools import setup

if sys.version_info[0] < 3:
    with open("README.rst") as f:
        long_description = f.read()
else:
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()

version = {}
# with open(os.path.join('numerov', 'version.py')) as f:
#    exec(f.read(), version)

setup(
    name="ofsc",
    packages=["ofsc"],
    version="v1.16",
    license="MIT",  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description="Python Wrapper for Oracle Field Service API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Borja Toron",
    author_email="borja.toron@gmail.com",
    url="https://github.com/btoron/pyOFSC",
    download_url="https://github.com/btoron/pyOFSC/archive/v1.16.tar.gz",
    keywords=[
        "OFSC",
        "Python",
        "ORACLE FIELD SERVICE CLOUD",
        "OFS",
        "ORACLE FIELD SERVICE",
    ],  # Keywords that define your package best
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
)
