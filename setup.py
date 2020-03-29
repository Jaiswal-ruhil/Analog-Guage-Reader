import setuptools
from os.path import join, dirname, isfile

requirementPath = join(dirname(os.path.realpath(__file__)), 'requirements.txt')
install_requires = []  

if isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = list(f.read().splitlines())

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
    install_requires=install_requires,
    python_requires='>=3.7',
)
