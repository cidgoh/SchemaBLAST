🧬 SchemaProber

CIDGOH Schema Alignment Tool
Hsiao Lab | Centre for Infectious Disease Genomics and One Health

SchemaProber is a Python utility designed for extracting,
indexing, and auditing data schemas. It allows researchers to “probe”
new datasets against established standards (such as OCA or LinkML) using
alignment reports to identify attribute overlap and critical data gaps.

------------------------------------------------------------------------

🚀 Key Features

-   Alignment Reports
-   Gap Analysis visualization
-   Schema-BLAST style probing (no pre-indexing required)
-   Modular architecture (JSON/YAML extractors, Solr-backed search)
-   Similarity scoring using Jaccard Similarity and Levenshtein distance

------------------------------------------------------------------------


📐 Identity Score (Jaccard Similarity)

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


🛠 Installation

Prerequisites

-   Python 3.8+
-   Apache Solr (running at http://localhost:8983)

Local Setup

Clone the repository:

    git clone https://github.com/cidgoh/schema-prober.git
    cd schema-prober

Install in editable mode:

    pip install -e .

------------------------------------------------------------------------

📖 Usage

1. Probe a Local File

Generate a console report:

    schema-compare probe ./my_schemas/mpox_v2.yaml

Generate a HTML report:

    schema-compare probe ./my_schemas/mpox_v2.yaml --html

------------------------------------------------------------------------

2. Find Similar Schemas (ID Search)

    schema-compare compare schema_abc12345

------------------------------------------------------------------------

3. Database Management

List all indexed schemas:

    schema-compare list

Index a new schema:

    schema-compare upload ./standard_schema.yml

Delete a specific schema:

    schema-compare delete schema_57a13d45abee

Wipe the entire database:

    schema-compare delete --all

------------------------------------------------------------------------

📊 Alignment Report Example

  MpoxInternational (ID: schema_33b855bfb07d)
  Score: 57.3% | Identity: 102/117
  ———————————————————— SHARED ATTRIBUTES (102): anatomical_material
  anatomical_part antiviral_therapy …

GAPS IN ALIGNMENT (Fields in query missing from target): [ QUERY ]—( x
)—[ MISSING IN TARGET ] : gene_name_1 [ QUERY ]—( x )—[ MISSING IN
TARGET ] : gene_name_2

------------------------------------------------------------------------

📝 License

Distributed under the MIT License. See LICENSE for more information.

Contact: jun_duan@sfu.ca 
         wwhsiao@sfu.ca
Website: https://www.cidgoh.ca
