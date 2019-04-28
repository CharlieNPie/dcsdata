import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dcsdata",
    version="0.0.9",
    author="Charles E. Jewers",
    author_email="charlesejewers@gmail.com",
    description="A text data tool for the University of Sheffield.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'beautifulsoup4',
        'bs4',
        'pandas',
        'mysqlclient',
        'SQLAlchemy',
        'requests',
        'Whoosh',
        'lxml'
    ],
    packages=[
        "dcsscrapers",
        "dcsscrapers.private",
        "dcssearch"
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)