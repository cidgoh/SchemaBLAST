# 🧬 SchemaBLAST: Schema Alignment Tool

**Hsiao Lab**\
*Centre for Infectious Disease Genomics and One Health (CIDGOH)*

------------------------------------------------------------------------

## 📌 Overview

SchemaBLAST is a Python utility designed for extracting, indexing, and
auditing data schemas.

It allows researchers to probe new datasets against established
standards (such as OCA or LinkML) to identify:

-   Attribute overlap
-   Schema similarity
-   Critical data gaps

------------------------------------------------------------------------

## 🚀 Key Features

-   **Hybrid Alignment Reports** --- Combines exact matches with fuzzy
    linguistic mapping
-   **Linguistic Mapping** --- Levenshtein-based fuzzy logic (e.g.,
    `case_id` ≈ `caseid`)
-   **Gap Analysis** --- Clearly highlights missing attributes
-   **Global Database Stats** --- Real-time indexed schema summary
-   **Flexible Output** --- Terminal summaries, standalone HTML reports,
    and CSV mappings

------------------------------------------------------------------------

## 📐 Identity Score (Jaccard Similarity)

SchemaBLAST uses **Jaccard Similarity (Intersection over Union)** as the
Identity Score.

Score = (Attributes in BOTH) / (Total UNIQUE attributes in EITHER
schema)

### Example

-   Query (Q): 117 attributes
-   Target (T): 143 attributes
-   Common (Q ∩ T): 100 attributes

Union = 117 + 143 - 100 = 160
Score = 100 / 160 = 0.625 (62.5%)

**Important:**

-   `100 / 117 = 85.5%` → Query coverage
-   `100 / 160 = 62.5%` → True schema similarity (Jaccard Score)

------------------------------------------------------------------------

## 📐 Similarity Confidence

  Confidence   Identity Score   Interpretation
  ------------ ---------------- ---------------------
  **HIGH**     \> 75%           Excellent alignment
  **MEDIUM**   40% -- 75%       Moderate overlap
  **LOW**      \< 40%           Poor alignment

------------------------------------------------------------------------

## 🛠 Installation

### Prerequisites

-   Python 3.8+
-   Apache Solr (default: http://localhost:8983)

### Setup

``` bash
git clone https://github.com/cidgoh/schema-prober.git
cd schema-prober
pip install -e .
```

------------------------------------------------------------------------

## 📖 Execution Examples

### 📥 Upload a Single Schema

``` bash
schemablast upload all_schema/mpox_schema.yaml
```

### 📦 Batch Upload Schemas

``` bash
schemablast batch schema_folder
```

### 📃 List All Schemas in Database

``` bash
schemablast list
```

### 🗑 Delete a Specific Schema

``` bash
schemablast delete schema_cfb4e323bde4
```

### 🔥 Delete All Schemas

``` bash
schemablast delete --all
```

------------------------------------------------------------------------

## 🔍 Probing Examples

### ✅ Perfect Match (Exact Alignment)

``` bash
schemablast probe query.yaml   -o result_perfect_match.txt   --html result_perfect_match.html   --threshold 0.5
```

### 🔎 Fuzzy Match (Linguistic Alignment)

``` bash
schemablast probe query.yaml   -o result_fuzzy.txt   --html result_fuzzy.html   --threshold 0.5   --fuzzy   --fuzzy_cutoff 90
```

------------------------------------------------------------------------

## 📊 Alignment Report Structure

Each probe report contains:

1.  **Database Stats** --- Overview of indexed schemas\
2.  **Summary Table** --- Identity scores and confidence levels\
3.  **Detailed Alignments**
    -   ✅ Exact Matches\
    -   🔍 Linguistic Matches\
    -   ❌ True Gaps

------------------------------------------------------------------------

## 🤝 Contact

**Jun Duan**\
jun_duan@sfu.ca

**William Hsiao**\
wwhsiao@sfu.ca

Web: https://www.cidgoh.ca/
