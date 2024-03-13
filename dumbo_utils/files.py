from pathlib import Path


def load_file(__file__: str | Path, path: str | Path) -> str:
    return open(Path(__file__).parent / path).read()
