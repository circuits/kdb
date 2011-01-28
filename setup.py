#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
    HAS_SETUPTOOLS = True
except ImportError:
    from distutils.core import setup
    HAS_SETUPTOOLS = False

if not HAS_SETUPTOOLS:
    import os
    from distutils.util import convert_path

    def find_packages(where=".", exclude=()):
        """Borrowed directly from setuptools"""

        out = []
        stack = [(convert_path(where), "")]
        while stack:
            where, prefix = stack.pop(0)
            for name in os.listdir(where):
                fn = os.path.join(where, name)
                if ("." not in name and os.path.isdir(fn) and 
                        os.path.isfile(os.path.join(fn, "__init__.py"))):
                    out.append(prefix+name)
                    stack.append((fn, prefix + name + "."))

        from fnmatch import fnmatchcase
        for pat in list(exclude) + ["ez_setup"]:
            out = [item for item in out if not fnmatchcase(item, pat)]

        return out

setup(
    name="kdb",
    description="Knowledge (IRC) Database Bot",
    long_description=open("README", "r").read(),
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
    entry_points="""
    [console_scripts]
    kdb = kdb.main:main
    """,
    install_requires=("circuits",),
    setup_requires=("hgtools",),
    use_hg_version={"increment": "0.01"},
)
