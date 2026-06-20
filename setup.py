from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="plotmind",
    version="0.1.0",
    author="PlotMind Contributors",
    description="Convert any CSV into meaningful graphs automatically.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/plotmind",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "plotly>=5.0.0",
        "matplotlib>=3.4.0",
        "kaleido>=0.2.1",
    ],
    extras_require={
        "seaborn": ["seaborn>=0.11.0"],
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "plotmind=plotmind.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Visualization",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    keywords="csv visualization charts graphs data plotly matplotlib",
)
