#!/usr/bin/env python

from glob import glob
from imp import new_module
from os import getcwd, path


from setuptools import setup, find_packages


version = new_module("version")

exec(
    compile(
        open(
            path.join(
                path.dirname(
                    globals().get("__file__", path.join(getcwd(), "kdb"))
                ),
                "kdb/version.py"
            ),
            "r"
        ).read(),
        "kdb/version.py",
        "exec"
    ),
    version.__dict__
)


setup(
    name="kdb",
    version=version.version,
    description="Knowledge (IRC) Database Bot",
    long_description="{0:s}\n\n{1:s}".format(
        open("README.rst").read(), open("CHANGES.rst").read()
    ),
    author="James Mills",
    author_email="James Mills, prologic at shortcircuit dot net dot au",
    url="http://bitbucket.org/prologic/kdb/",
    download_url="http://bitbucket.org/prologic/kdb/downloads/",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Communications :: Chat :: Internet Relay Chat",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    license="MIT",
    keywords="Knowledge Database IRC Bot Framework",
    platforms="POSIX",
    packages=find_packages("."),
    scripts=glob("bin/*"),
    dependency_links=[
        "https://bitbucket.org/circuits/circuits/get/tip.zip#egg=circuits-3.0.0.dev",  # noqa
    ],
    setup_requires=[
        "fabric",
    ],
    install_requires=(
        "procname==0.3",
        "pymills==3.4.0",
        "circuits==3.0.0.dev",
    ),
    entry_points={
        "console_scripts": [
            "kdb=kdb.main:main",
        ]
    },
    test_suite="tests.main.main",
    zip_safe=True
)
