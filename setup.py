from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='adaptivecardbuilder',
    version='0.0.2',
    description='Easily Build and Export Adaptive Cards Through Python',
    py_modules=['adaptivecardbuilder'],
    package_dir={'': 'src'},
    data_files = [("", ["LICENSE.txt"])],
    url="https://github.com/ku222/AdaptiveCardBuilder",
    author="Kovid Uppal",
    author_email="kovid.uppal@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning"
    ]
)
