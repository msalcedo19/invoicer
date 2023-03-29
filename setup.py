"""Python installation definition for {{ cookiecutter.api_name }}"""
import os
import re

from setuptools import setup

PACKAGE = "ms_invoicer"
PACKAGE_PATH = os.path.join(os.path.dirname(__file__), PACKAGE)

with open(os.path.join(PACKAGE_PATH, "__init__.py")) as package_file:
    package_contents = package_file.read()
    version_match = re.search(r"""^__version__\s*=\s*['"]([^'"]*)['"]""", package_contents, re.M)
    if version_match:
        VERSION = version_match.group(1)
    else:
        raise RuntimeError(f"No __version__ specified in {package_file.name}")

    python_requirement_match = re.search(
        r"""^__python_requires__\s*=\s*['"]([^'"]*)['"]""", package_contents, re.M
    )
    if python_requirement_match:
        PYTHON_REQUIREMENT = python_requirement_match.group(1)
    else:
        raise RuntimeError(f"No __python_requires__ specified in {package_file.name}")

setup(
    name=PACKAGE,
    version=VERSION,
    python_requires=PYTHON_REQUIREMENT,
    description="{{ short_description }}",
    author="m.salcedo30",
    author_email="m.salcedor30@gmail.com",
    url="",
    install_requires=[],
    packages=[PACKAGE],
)
