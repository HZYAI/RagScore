from setuptools import setup, find_packages

setup(
    name="ragscore",
    version="0.1.0",
    description="A pipeline for generating QA datasets to evaluate RAG systems.",
    author="Your Name",
    author_email="you@example.com",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9,<3.12",
    install_requires=[
        "pypdf2>=3.0.1",
        "nltk>=3.8.1",
        "tqdm>=4.66.1",
        "faiss-cpu>=1.7.4",
        "dashscope>=1.14.1",
        "langchain-community>=0.0.31",
        "numpy<2.0.0",
        "typer[all]>=0.9.0",
        "python-dotenv>=1.0.0",
        "sentence-transformers>=2.2.2",
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "python-multipart>=0.0.6",
        "websockets>=12.0",
    ],
    entry_points={
        "console_scripts": [
            "ragscore=ragscore.cli:app",
        ],
    },
)
