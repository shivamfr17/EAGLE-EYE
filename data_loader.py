import re
from pathlib import Path

import pandas as pd
import pymupdf


COLUMN_NAMES = [
    "component",
    "component name",
    "component label",
    "label",
    "tag",
    "reference",
    "reference designator",
    "device",
    "part number",
    "designation",
]

# Common electrical reference prefixes; drawings may use other conventions.
TAG_PATTERN = re.compile(
    r"\b(?:QF|QS|FU|KM|KA|KT|FR|Q|K|M|X|S|H|HL|SB|A|T|PE|XP|XT)"
    r"\s*[-_]?\s*\d+[A-Z]?\b",
    re.IGNORECASE,
)


def clean_label(value):
    """Normalize whitespace and capitalization without changing label content."""
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip().upper()


def load_excel(file_path, column=None):
    """Load labels from .xlsx, .xls, or .csv and return unique non-empty labels."""
    path = Path(file_path)

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    if df.empty:
        raise ValueError("The input spreadsheet is empty.")

    if column is None:
        lookup = {str(name).strip().lower(): name for name in df.columns}
        for candidate in COLUMN_NAMES:
            if candidate in lookup:
                column = lookup[candidate]
                break

    if column is None:
        raise ValueError(
            "Could not identify the component column. "
            f"Available columns: {list(df.columns)}. "
            "Call load_excel(file_path, column='YourColumnName')."
        )

    if column not in df.columns:
        raise ValueError(
            f"Column {column!r} not found. Available columns: {list(df.columns)}"
        )

    labels = [clean_label(value) for value in df[column]]
    # Preserve the original order while removing empty and duplicate values.
    return list(dict.fromkeys(label for label in labels if label))


def load_pdf(file_path):
    """
    Extract likely component reference tags from selectable PDF text.
    Scanned/image-only PDFs need OCR and may return an empty list.
    """
    labels = []

    with pymupdf.open(file_path) as document:
        for page in document:
            text = page.get_text()
            labels.extend(clean_label(match.group()) for match in TAG_PATTERN.finditer(text))

    return list(dict.fromkeys(label for label in labels if label))


def load_expected_components(file_path, column=None):
    """Main project interface: return a list of expected component labels."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    extension = path.suffix.lower()

    if extension in {".xlsx", ".xls", ".csv"}:
        return load_excel(path, column=column)
    if extension == ".pdf":
        return load_pdf(path)

    raise ValueError("Unsupported file type. Use .xlsx, .xls, .csv, or .pdf.")


if __name__ == "__main__":
    # Run: python data_loader.py components.xlsx
    import sys

    file_path = sys.argv[1] if len(sys.argv) > 1 else "components.xlsx"

    try:
        components = load_expected_components(file_path)
        print("Expected components:")
        for component in components:
            print(f"- {component}")
        print(f"\nTotal unique labels: {len(components)}")
        if file_path.lower().endswith(".pdf") and not components:
            print(
                "No likely component tags were found. The PDF may be scanned, "
                "or it may use a different reference-label convention."
            )
    except (FileNotFoundError, ValueError, OSError, ImportError) as error:
        print(f"Error: {error}")
