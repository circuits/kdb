#!/usr/bin/env python


from glob import glob


from setuptools import setup, find_packages


def parse_requirements(filename):
    with open(filename, "r") as f:
        for line in f:
            if line and line[:2] not in ("#", "-e"):
                yield line.strip()


from kdb.version import version


setup(
    name="kdb",
    version=version,
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
    package_data={
        "kdb.plugins.web": [
            "static/css/*",
            "static/ico/*",
            "static/js/*",
            "templates/*",
        ],
    },
    include_package_data=True,
    scripts=glob("bin/*"),
    dependency_links=[
        "https://bitbucket.org/circuits/circuits/get/tip.zip#egg=circuits-3.0.0.dev",  # noqa
    ],
    install_requires=list(parse_requirements("requirements.txt")),
    entry_points={
        "console_scripts": [
            "kdb=kdb.main:main",
        ]
    },
    test_suite="tests.main.main",
    zip_safe=False
)
