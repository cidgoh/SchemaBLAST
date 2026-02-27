# Schema Comparator

A modular, professional Python tool for extracting, indexing, and
comparing data schemas. Originally built for OCA (Overlays Capture
Architecture), this tool is designed to be extensible to support SQL,
GraphQL, and other schema formats.

------------------------------------------------------------------------

## 🚀 Features

-   **Modular Architecture**: Separate layers for data extraction,
    storage (Solr), and business logic.
-   **Multi-Format Support**: Handles JSON and YAML out of the box.
-   **Similarity Scoring**: Uses Levenshtein distance and Jaccard
    similarity to find matching attributes across different schemas.
-   **Extensible Extractors**: Easy-to-add support for new schema types.
-   **CLI Ready**: Installable as a system-wide command.

------------------------------------------------------------------------

## 🛠 Installation

### Prerequisites

-   Python 3.8+
-   Apache Solr (Running at `http://localhost:8984`)

### Local Setup

1.  Clone the repository:

``` bash
git clone https://github.com/your-repo/schema-comparator.git
cd schema-comparator
```

2.  Install in editable mode:

``` bash
pip install -e .
```

------------------------------------------------------------------------

## 📖 Usage

Once installed, you can use the `schema-compare` command directly.

### 1. Upload/Index a Schema

Extracts attributes from a file and stores them in Solr.

``` bash
schema-compare upload ./my_schemas/user_profile.json --name "User Profile V1"
```

### 2. Find Similar Schemas

Search for schemas in the database that share similar attributes.

``` bash
schema-compare find schema_abc12345 --threshold 0.5
```

### 3. List All Schemas

``` bash
schema-compare list
```

------------------------------------------------------------------------

## 🏗 Project Structure

    schema_comparator/
    ├── utils/
    │   ├── extractors.py   # Logic to parse different schema types
    │   └── text_math.py    # Similarity algorithms (Levenshtein, etc.)
    ├── storage.py          # Solr database communication
    ├── comparator.py       # Core logic orchestrator
    ├── models.py           # Data structures (Dataclasses)
    └── cli.py              # Argument parsing and terminal output

------------------------------------------------------------------------

## 🔧 Extending the Tool

To support a new schema type (e.g., SQL DDL), follow these steps:

1.  Open `schema_comparator/utils/extractors.py`.
2.  Create a new class inheriting from `BaseExtractor`:

``` python
class SQLExtractor(BaseExtractor):
    def extract(self, data: str) -> Set[str]:
        # Add logic to parse SQL and return a set of column names
        return {"column1", "column2"}
```

3.  Update the `ComparatorEngine` in `comparator.py` to use your new
    extractor based on the file extension.

------------------------------------------------------------------------

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
