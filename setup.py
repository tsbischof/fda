import setuptools

setuptools.setup(
    name="fda",
    version="0.1.0",
    author="Thomas Bischof",
    author_email="tsbischof@gmail.com",
    description="Scraper and aggregator for analysis of FDA 510(k) and related documents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tsbischof/fda",
    packages=setuptools.find_packages(),
    install_requires=[
        "graphviz",
        "networkx",
        "pandas",
        "pdf2image",
        "PyPDF2"
    ]
)
