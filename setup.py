from setuptools import setup, find_packages

setup(
    name="PhantomTrace",
    version="0.8.0",
    description="PhantomTrace — a mathematical framework where numbers exist in present or absent states",
    long_description=open("PKG_README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/jordanbeitchman-spec/PhantomTrace",
    packages=find_packages(include=["absence_calculator", "absence_calculator.*"]),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "phantomtrace=absence_calculator.calculator:interactive_calculator",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
)
