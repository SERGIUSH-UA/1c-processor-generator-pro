"""
Setup script for 1c-processor-generator
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="1c-processor-generator",
    version="2.73.0",
    author="ITDEO",
    author_email="itdeo.tech@gmail.com",
    description="Automatic generation of external data processors for 1C:Enterprise 8.3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://itdeo.tech/1c-processor-generator",
    license="MIT (Open Source) + Proprietary (PRO Module)",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "1c_processor_generator": [
            "templates/*.j2",
            "templates/macros/*.j2",
            "yaml_schema.json",
            "*.pyd",
            "_protected_bins/**/*.pyd",
            "pro/LICENSE",
            "pro/*.pyd",
            "pro/_bins/**/*.pyd",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "jinja2>=3.1.0",
        "pyyaml>=6.0",
        "jsonschema>=4.0.0",
        "cryptography>=41.0.0",  # v2.51.0: Required for PRO token encryption
    ],
    entry_points={
        "console_scripts": [
            "1c-processor-generator=1c_processor_generator.__main__:main",
        ],
    },
    keywords="1c enterprise generator bsl yaml automation epf",
    project_urls={
        "Homepage": "https://itdeo.tech/1c-processor-generator",
        "Bug Reports": "https://github.com/SERGIUSH-UA/1c-processor-generator-pro/issues",
        "Source": "https://github.com/SERGIUSH-UA/1c-processor-generator-pro",
        "Documentation": "https://itdeo.tech/1c-processor-generator",
        "Buy PRO": "https://itdeo.tech/1c-processor-generator/#pricing",
    },
)
