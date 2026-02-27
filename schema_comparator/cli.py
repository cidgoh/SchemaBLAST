import argparse
import sys
from .comparator import ComparatorEngine

def main():
    parser = argparse.ArgumentParser(
        prog="schema-compare",
        description="CLI tool to index and compare OCA schemas via Solr."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- UPLOAD COMMAND ---
    up = subparsers.add_parser("upload", help="Extract attributes and index a new schema")
    up.add_argument("file", help="Path to the JSON or YAML schema file")
    up.add_argument("--name", help="Human-readable name for the schema")
    up.add_argument("--description", help="Optional description (overrides file content)", default="")

    # --- LIST COMMAND ---
    subparsers.add_parser("list", help="List all indexed schemas in the database")

    # --- COMPARE COMMAND ---
    comp = subparsers.add_parser("compare", help="Find schemas similar to a specific ID")
    comp.add_argument("schema_id", help="The ID of the schema to use as a source")
    comp.add_argument("--threshold", type=float, default=0.4, help="Similarity threshold (0.0 to 1.0)")
    comp.add_argument("--limit", type=int, default=5, help="Max number of results to show")

    args = parser.parse_args()
    engine = ComparatorEngine()

    # --- EXECUTION LOGIC ---
    if args.command == "upload":
        sid = engine.process_and_upload(
            file_path=args.file, 
            name=args.name, 
            user_description=args.description
        )
        if sid:
            print(f"✅ Successfully indexed: {sid}")
        else:
            print("❌ Failed to index schema.")
            sys.exit(1)

    elif args.command == "list":
        # We use the list_all method from SolrManager via the engine
        schemas = engine.db.list_all()
        if not schemas:
            print("📭 No schemas found in the database.")
            return

        print(f"{'ID':<20} | {'NAME':<25} | {'ATTRS':<5} | {'DESCRIPTION'}")
        print("-" * 80)
        for s in schemas:
            # Handle Solr potentially returning text as a list
            desc = s.get('description', "")
            if isinstance(desc, list): desc = desc[0]
            
            # Truncate description for clean table view
            short_desc = (desc[:40] + '..') if len(desc) > 40 else desc
            
            print(f"{s['schema_id']:<20} | {s['schema_name']:<25} | {s['attribute_count']:<5} | {short_desc}")

    elif args.command == "compare":
        print(f"🔍 Analyzing similarity for {args.schema_id}...")
        matches = engine.find_similar_schemas(
            schema_id=args.schema_id, 
            threshold=args.threshold, 
            limit=args.limit
        )

        if not matches:
            print("🤷 No similar schemas found above the threshold.")
            return

        print(f"\n{'MATCHING SCHEMA':<25} | {'SCORE':<8} | {'COMMON ATTRIBUTES'}")
        print("-" * 80)
        for m in matches:
            # Extract only the attribute names from the tuples in m.matching_attributes
            common_names = [attr[0] for attr in m.matching_attributes]
            attr_list = ", ".join(common_names[:5]) # Show first 5 matches
            if len(common_names) > 5: attr_list += "..."
            
            print(f"{m.target_schema_name:<25} | {m.similarity_score:>6.1%} | {attr_list}")

if __name__ == "__main__":
    main()