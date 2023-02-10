import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="diskit",
    version="0.0.1.post1",
    license='Apache',
    keywords=['quantum', 'distributed', 'simulator', 'qiskit', 'diskit'],
    author="Anuranan Das, Stephen DiAdamo",
    author_email="stephen.diadamo@gmail.com",
    description="Distributed circuit remapping for Qiskit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Interlin-q/diskit",
    install_requires=[
        'qiskit'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6"
)
