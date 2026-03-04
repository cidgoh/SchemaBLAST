# 🧬 SchemaBLAST: Schema Alignment Tool

**Hsiao Lab**\
*Centre for Infectious Disease Genomics and One Health (CIDGOH)*

[![GitHub
Repo](https://img.shields.io/badge/GitHub-schema--prober-blue?logo=github)](https://github.com/cidgoh/schema-prober)\
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)\
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

------------------------------------------------------------------------

## 📌 Overview

SchemaBLAST is a Python utility designed for extracting, indexing, and
auditing data schemas.

It allows researchers to "probe" new datasets against established
standards (such as OCA or LinkML) using alignment reports to identify:

-   Attribute overlap\
-   Schema similarity\
-   Critical data gaps

------------------------------------------------------------------------

## 🚀 Key Features

-   **Hybrid Alignment Reports** --- Combines exact matches with fuzzy
    linguistic mapping\
-   **Linguistic Mapping** --- Uses Levenshtein-based fuzzy logic (e.g.,
    `case_id` ≈ `caseid`)\
-   **Gap Analysis** --- Clearly highlights missing attributes\
-   **Global Database Stats** --- Real-time indexed schema summary\
-   **Flexible Output** --- Terminal summaries, standalone HTML reports,
    and CSV mappings

------------------------------------------------------------------------

## 📐 Identity Score (Jaccard Similarity)

The Identity Score measures overall schema similarity using **Jaccard
Similarity (Intersection over Union)**.

    Score = (Attributes in BOTH)
            --------------------------------------------
            (Total UNIQUE attributes in EITHER schema)

### Example

-   Query (Q): 117 attributes\
-   Target (T): 143 attributes\
-   Common (Q ∩ T): 100 attributes

```{=html}
<!-- -->
```
    Union = 117 + 143 - 100 = 160
    Score = 100 / 160 = 0.625 (62.5%)

**Important distinction:**

-   `100 / 117 = 85.5%` → Query coverage\
-   `100 / 160 = 62.5%` → True schema similarity (Jaccard Score)

SchemaBLAST reports the **Jaccard score as the Identity Score**.

------------------------------------------------------------------------

## 📐 Similarity Confidence

Matches are categorized by Identity Score:

  Confidence   Identity Score   Interpretation
  ------------ ---------------- ---------------------
  **HIGH**     \> 75%           Excellent alignment
  **MEDIUM**   40% -- 75%       Moderate overlap
  **LOW**      \< 40%           Poor alignment

------------------------------------------------------------------------

## 🛠 Installation

### Prerequisites

-   Python 3.8+\
-   Apache Solr (default: http://localhost:8983)

### Setup

``` bash
git clone https://github.com/cidgoh/schema-prober.git
cd schema-prober
pip install -e .
```

------------------------------------------------------------------------

## 📖 Usage Examples

### 1️⃣ Probing with Fuzzy Matching

``` bash
schema-compare probe query.yaml --fuzzy --fuzzy_cutoff 90.0
```

### 2️⃣ Generate HTML + CSV Reports

``` bash
# Default output
schema-compare probe query.yaml --html

# Custom location
schema-compare probe query.yaml --html exports/mpox_audit.html
```

### 3️⃣ Save Terminal Output

``` bash
schema-compare probe query.yaml -o alignment_summary.txt
```

------------------------------------------------------------------------

## 📊 Alignment Report Structure

Each probe report contains:

### 1. Database Stats

Overview of indexed schemas.

### 2. Summary Table

High-level Identity Scores and Confidence.

### 3. Detailed Alignments

-   ✅ **Exact Matches**\
-   🔍 **Linguistic Matches**\
-   ❌ **True Gaps**

------------------------------------------------------------------------

## 📝 CLI Reference

  Command           Description
  ----------------- ------------------------------------
  `upload <file>`   Index a new schema
  `list`            List indexed schemas
  `probe <file>`    Compare local file
  `delete <id>`     Remove schema (`--all` to wipe DB)

### Probe Flags

-   `-o, --output` --- Save text summary\
-   `--html` --- Save HTML report\
-   `--fuzzy` --- Enable fuzzy matching\
-   `--fuzzy_cutoff` --- Sensitivity (0--100)\
-   `--threshold` --- Minimum Identity Score (default: 0.4)

------------------------------------------------------------------------

## 🤝 Contact

**Jun Duan**\
jun_duan@sfu.ca

**William Hsiao**\
wwhsiao@sfu.ca

Web: https://www.cidgoh.ca/
