

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="analog_gauge_reader",  # Replace with your own username
    version="0.0.2",
    author="Ruhil Jaiswal",
    author_email="ruhiljaiswal@gmail.com",
    description="Analod dial reader with opencv",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jaiswal-ruhil/Analog-Guage-Reader",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
