from setuptools import setup, find_packages

setup(
    name="ai-tool-intelligence",
    version="0.1.0",
    description="Comprehensive AI tool intelligence platform using AWS Strands Agents",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "Flask>=2.3.3",
        "Flask-SQLAlchemy>=3.0.5",
        "Flask-CORS>=4.0.0",
        "strands-agents>=0.1.0",
        "strands-agents-tools>=0.1.0",
        "boto3>=1.34.0",
        "botocore>=1.34.0",
        "beautifulsoup4>=4.12.2",
        "requests>=2.31.0",
        "lxml>=4.9.3",
        "pandas>=2.1.0",
        "numpy>=1.24.3",
        "python-dotenv>=1.0.0",
        "click>=8.1.7",
        "schedule>=1.2.0",
        "psutil>=5.9.5",
        "pytest>=7.4.0",
        "pytest-flask>=1.2.1",
        "python-dateutil>=2.8.2",
        "gunicorn>=21.2.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)