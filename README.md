🧬 SchemaProber: Schema Alignment Tool

**Hsiao Lab | Centre for Infectious Disease Genomics and One Health (CIDGOH)**

[![GitHub Repo](https://img.shields.io/badge/GitHub-schema--prober-blue?logo=github)](https://github.com/cidgoh/schema-prober)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

SchemaProber is a Python utility designed for extracting, indexing, and auditing data schemas. It allows researchers to “probe” new datasets against established standards (such as OCA or LinkML) using alignment reports to identify attribute overlap and critical data gaps.

------------------------------------------------------------------------

## 🚀 Key Features

- **Hybrid Alignment Reports**: Combines Exact matches with Fuzzy linguistic mapping.
- **Linguistic Mapping**: Uses Levenshtein-based fuzzy logic to find semantically similar fields (e.g., `case_id` ≈ `caseid`).
- **Gap Analysis**: Visualizes exactly which fields in your query are missing from the target standard.
- **Global Database Stats**: Real-time summary of the total indexed schema landscape.
- **Flexible Output**: Support for terminal summaries, standalone HTML reports, and raw CSV mappings.

------------------------------------------------------------------------

## 📐 dentity Score (Jaccard Similarity)



The Identity Score measures how similar two schemas are overall.

It uses Jaccard Similarity (Intersection over Union):

Score = (Attributes in BOTH) / (Total UNIQUE attributes in EITHER)

Example

Query (Q): 117 attributes
Common (Q ∩ T): 100 attributes
Target (T): 143 attributes

Union = 117 + 143 - 100 = 160

Score = 100 / 160 = 0.625 (62.5%)

Note:

-   100 / 117 = 85.5% → Coverage of your query
-   100 / 160 = 62.5% → True schema similarity (Jaccard Score)

The tool reports the Jaccard score as the Identity Score. A higher Identity Score indicates better coverage of your dataset by the target standard.

## 📐 Similarity Confidence

Matches are categorized by "Similarity" (High, Medium, Low) based on the linguistic distance between attributes when fuzzy matching is enabled.  

 The criteria are defined in the ComparatorEngine logic using the following thresholds:

   | Confidence Label | Identity Score Range | Interpretation |
   |------------------|----------------------|---------------|
   | **HIGH** | > 75% | Excellent alignment. The schemas are nearly identical or the standard covers almost all query fields. |
   | **MEDIUM** | 40% – 75% | Moderate alignment. Significant overlap exists, but there are notable gaps or structural differences. |
   | **LOW** | < 40% | Poor alignment. Only a few fields match; the schemas likely serve different purposes or data domains. |

## 🛠 Installation

### Prerequisites
- Python 3.8+
- Apache Solr (Default: `http://localhost:8983`)

### Setup

```bash
git clone https://github.com/cidgoh/schema-prober.git
cd schema-prober
pip install -e .

------------------------------------------------------------------------

📖 Usage Examples
-----------------

### 1\. Probing with Fuzzy Matching (Linguistic Mapping)

To catch fields that are named slightly differently, use the --fuzzy flag. You can tune the sensitivity with --fuzzy\_cutoff (default is 85.0).

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   Bashschema-compare probe query.yaml --fuzzy --fuzzy_cutoff 90.0   `

### 2\. Generating Professional Reports

Generate a standalone HTML report and an accompanying CSV mapping file for data curators.

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   Bash# Saves to default 'report.html' and 'report_mapping.csv'  schema-compare probe query.yaml --html  # Specify a custom location  schema-compare probe query.yaml --html exports/mpox_audit.html   `

### 3\. Saving Terminal Output to a File

If you want to keep a text-based audit log of the terminal summary:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   Bashschema-compare probe query.yaml -o alignment_summary.txt   `

📊 Alignment Report Anatomy
---------------------------

When running a probe, the report is divided into three sections:

*   **Database Stats**: Overview of the current indexing environment.
    
*   **Summary Table**: High-level comparison of Identity Scores and Similarity Confidence.
    
*   **Detailed Alignments**:
    
    *   ✅ **Exact Matches**: Fields that match 1:1.
        
    *   🔍 **Linguistic Mapping**: Near-matches found via fuzzy logic (e.g., lab\_result ≈ lab\_results).
        
    *   ❌ **True Gaps**: Fields in your query that have no equivalent in the target schema.
        

📝 CLI Reference
----------------

**CommandArgumentDescription**uploadfileIndex a new schema into the database.listNoneList all currently indexed schemas and their IDs.probefileCompare a local file against everything in the database.deleteidRemove a specific schema (use --all to wipe DB).

### Flags for probe & compare:

*   \-o, --output: Path to save the text summary.
    
*   \--html: Path to save the HTML report.
    
*   \--fuzzy: Enable linguistic near-matching.
    
*   \--fuzzy\_cutoff: Set the sensitivity (0-100).
    
*   \--threshold: Minimum Identity Score to show a schema in results (default 0.4).
    

🤝 Contact
----------

*   **Jun Duan**: [jun\_duan@sfu.ca](mailto:jun_duan@sfu.ca)
    
*   **William Hsiao**: [wwhsiao@sfu.ca](mailto:wwhsiao@sfu.ca)
    

**Web**: [www.cidgoh.ca](https://www.cidgoh.ca/)