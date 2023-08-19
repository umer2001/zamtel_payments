from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in zamtel_payments/__init__.py
from zamtel_payments import __version__ as version

setup(
	name="zamtel_payments",
	version=version,
	description="A frappe app that provides a way to pay through zamtel",
	author="DNDEV Agency",
	author_email="umer2001.uf@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
