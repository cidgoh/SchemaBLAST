# 🧬 SchemaBLAST: Schema Alignment Tool

**Hsiao Lab** *Centre for Infectious Disease Genomics and One Health (CIDGOH)*

---

## 📌 Overview

**SchemaBLAST** is a CLI tool designed for indexing and aligning metadata schemas. 

It allows researchers to "BLAST" new datasets against established standards (such as OCA or LinkML) to identify structural overlaps, linguistic similarities, and critical data gaps.

---

## 🚀 Key Features

* **Hybrid Alignment** — Combines exact attribute matches with fuzzy linguistic mapping.
* **Linguistic Mapping** — Levenshtein-based fuzzy logic (e.g., `case_id` ≈ `caseid`).
* **Jaccard Identity Scoring** — Mathematical rigor for schema similarity.
* **Flexible Reporting** — Terminal summaries, standalone HTML reports, and CSV mappings.

---

## 📐 Identity Score (Jaccard Similarity)

SchemaBLAST uses **Jaccard Similarity (Intersection over Union)** as the primary Identity Score.

$$Score = \frac{|Query \cap Target|}{|Query \cup Target|}$$

### Example
* **Query (Q):** 117 attributes
* **Target (T):** 143 attributes
* **Common (Q ∩ T):** 100 attributes

**Union** = $117 + 143 - 100 = 160$  
**Identity Score** = $100 / 160 = 0.625$ (**62.5%**)


---

## 📊 Similarity Confidence

| Confidence | Identity Score | Interpretation |
| :--- | :--- | :--- |
| **HIGH** | > 75% | Excellent alignment |
| **MEDIUM** | 40% – 75% | Moderate overlap |
| **LOW** | < 40% | Poor alignment |

---

## 🛠 Installation

### Prerequisites
* Python 3.8+
* Apache Solr (Running at `http://localhost:8983`)

### Setup
```bash
git clone https://github.com/cidgoh/SchemaBLAST.git
cd SchemaBLAST
pip install -e .
```

---

## 📖 Usage Guide

### 📂 Database Management
Manage your local index of standards and schemas.

| Action | Command |
| :--- | :--- |
| **List** | `schemablast database list` |
| **Upload File** | `schemablast database upload <file> [-n custom_name]` |
| **Batch Import** | `schemablast database batch <directory>` |
| **Delete One** | `schemablast database delete <schema_id>` |
| **Delete All** | `schemablast database delete --all` |

---

### 🔍 Alignment (The "BLAST" Query)
Align a query file against the indexed database.

#### ✅ Basic Alignment
Run a standard alignment and save a text summary.
```bash
schemablast align -q query.yaml -o results.txt
```

#### 🔎 Fuzzy Linguistic Alignment
Enable fuzzy matching with a custom threshold and generate a visual HTML report.
```bash
# -f: fuzzy, -c: fuzzy cutoff (0-100), -t: global threshold (0-1.0), -r: report
schemablast align -q query.yaml -f -c 90 -t 0.5 -r my_report.html
```

#### 🆔 Internal Database Alignment
Align one indexed schema against all others in the database using its ID.
```bash
schemablast align -i schema_cfb4e323bde4 -f -r internal_comparison.html
```

---

## 📑 Parameters Reference

| Short | Long | Description | Default |
| :--- | :--- | :--- | :--- |
| `-q` | `--query` | Path to local query file | Required |
| `-i` | `--id` | Internal Database ID to use as query | Required (if no -q) |
| `-t` | `--threshold` | Minimum Identity Score to report (0-1.0) | `0.4` |
| `-l` | `-limit` | Max number of matching schemas to return | `5` |
| `-f` | `--fuzzy` | Enable Levenshtein-based fuzzy matching | `False` |
| `-c` | `--cutoff` | Sensitivity for fuzzy matches (0-100) | `85.0` |
| `-o` | `--output` | Save text summary to a specific file | `Stdout` |
| `-r` | `--report` | Generate branded HTML report & CSV | `None` |

---

## 🤝 Contact

**Jun Duan** jun_duan@sfu.ca

**William Hsiao** wwhsiao@sfu.ca

**Web:** [www.cidgoh.ca](https://www.cidgoh.ca/)
