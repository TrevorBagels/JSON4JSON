import pathlib
from setuptools import _install_setup_requires, setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
setup(
	name = "JSON4JSON",
	version = "0.3.0",
	description = "Configure JSON with JSON",
	long_description = README,
	long_description_content_type = "text/markdown",
	url = "https://github.com/TrevorBagels/JSON4JSON",
	license = "GNU GPLv3",
	classifiers=[
		"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.7",
    ],
	author = "Trevor Bagels",
	author_email = "trevorbagels@gmail.com",
	packages=find_packages(),
	include_package_data=True
)

#notes for building and releasing
#python3 -m build
#python3 -m twine upload --repository pypi dist/*