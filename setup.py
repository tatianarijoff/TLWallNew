"""
Setup script for pytlwall package.

pytlwall is a Python implementation for calculating resistive wall impedance
using transmission line theory, originally developed at CERN.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")
else:
    long_description = "Transmission line impedance calculation engine"

# Read version from _version.py
version_file = Path(__file__).parent / "pytlwall" / "_version.py"
version = "1.0.0"  # Default
if version_file.exists():
    with open(version_file) as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"').strip("'")
                break

#########
# Setup #
#########
setup(
    # Package metadata
    name="pytlwall",
    version=version,
    description="Transmission line impedance calculation engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # Author information
    author="Tatiana Rijoff, Carlo Zannini",
    author_email="tatiana.rijoff@gmail.com",
    maintainer="Tatiana Rijoff",
    maintainer_email="tatiana.rijoff@gmail.com",
    
    # URLs
    url="https://github.com/CERN/pytlwall",  # TODO Update with actual URL
    project_urls={
        "Bug Reports": "https://github.com/CERN/pytlwall/issues",
        "Source": "https://github.com/CERN/pytlwall",
        "Documentation": "https://github.com/CERN/pytlwall/blob/main/README.md",
    },
    
    # License
    license="MIT",
    
    # Classifiers for PyPI
    classifiers=[
        # Development Status
        "Development Status :: 5 - Production/Stable",
        
        # Intended Audience
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        
        # Topic
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Python versions
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        
        # Operating Systems
        "Operating System :: OS Independent",
        
        # Natural Language
        "Natural Language :: English",
    ],
    
    # Keywords for search
    keywords="impedance, transmission line, accelerator physics, CERN, beam dynamics",
    
    # Package discovery
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "matplotlib>=3.3.0",
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    
    # Package data - include Yokoya factors and other data files
    include_package_data=True,
    package_data={
        "pytlwall": [
            "yokoya_factors/*.txt",
            "yokoya_factors/*.dat",
            "yokoya_factors/*.csv",
        ],
    },
    
    # Entry points for command-line scripts (if needed)
    entry_points={
        "console_scripts": [
            "pytlwall=exec_pytlwall:main",  # If you want a CLI command
        ],
    },
    
    # Zip safe
    zip_safe=False,
)
