from setuptools import setup, find_packages

setup(
    name="geolocationAnalysis",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas',
        'duckdb'
    ],
)