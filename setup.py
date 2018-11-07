#!/usr/bin/env python3
import codecs
import os
import typing as typ

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
about: typ.Dict[str, typ.Any] = {}


with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()


with open(os.path.join(here, "matomo_dl", "__version__.py")) as v:
    exec(v.read(), about)  # noqa: S102


required = [
    "attrs~=18.2",
    "beautifulsoup4~=4.6",
    "cattrs==0.9.0",
    "click~=7.0",
    "click-log",
    "colorama==0.4.0",
    "lxml~=4.2",
    "packaging~=18.0",
    "requests~=2.20",
    "toml==0.10.0",
]


setup(
    name="matomo_dl",
    version=about["__version__"],
    description=".",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Opal Symes",
    author_email="opal@catalyst.net.nz",
    packages=find_packages(include=["matomo_dl", "matomo_dl.*"]),
    entry_points={
        "console_scripts": [
            "matomo-dl=matomo_dl.__main__:cli",
            "matomo_dl=matomo_dl.__main__:cli",
        ]
    },
    python_requires=">=3.6",
    install_requires=required,
    extras_require={"cache": ["requests_cache==0.4.13"]},
    include_package_data=True,
    license="GPLv3+",
)
