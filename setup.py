from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="engram",
    version="0.1.0",
    author="Engram Team",
    author_email="team@engram.ai",
    description="Universal Memory Layer for Multi-Provider LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/engram",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.1",
            "httpx>=0.25.2",
            "faker>=20.1.0",
            "ruff>=0.1.6",
            "black>=23.11.0",
            "isort>=5.12.0",
            "mypy>=1.7.1",
            "pre-commit>=3.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "engram=engram.api.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "engram": ["py.typed"],
    },
)
