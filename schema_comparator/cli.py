import argparse
import sys
from datetime import datetime
from .comparator import ComparatorEngine
from .utils.branding import get_report_header

def print_matches(matches, query_attributes):
    """
    NCBI-style report with Summary, Detailed Alignments, and Gap Analysis.
    """
    if not matches:
        print("🤷 No similar schemas found above the threshold.")
        return

    print(get_report_header(len(query_attributes)))
    
    query_count = len(query_attributes)
    query_set = set(query_attributes)

    # --- SECTION 1: SUMMARY ---
    print("\n" + "="*95)
    print(f"      SCHEMA ALIGNMENT REPORT | QUERY SIZE: {query_count} ATTRIBUTES")
    print("="*95)
    print(f"{'MATCHING SCHEMA':<30} | {'SCORE':<8} | {'MATCHES'}")
    print("-" * 95)
    for m in matches:
        common_count = len(m.matching_attributes)
        print(f"{m.target_schema_name:<30} | {m.similarity_score:>6.1%} | {common_count} / {query_count} shared")

    # --- SECTION 2: DETAILED ALIGNMENTS & GAPS ---
    print("\n" + "="*95)
    print("      DETAILED ATTRIBUTE ALIGNMENTS & GAPS")
    print("="*95)

    for m in matches:
        # Attributes present in query but NOT in this specific target
        target_attrs = {attr[1] for attr in m.matching_attributes}
        unmatched = sorted(list(query_set - target_attrs))
        
        print(f"\n> {m.target_schema_name} (ID: {m.target_schema_id})")
        print(f"  Score: {m.similarity_score:.1%} | Identity: {len(target_attrs)}/{query_count}")
        print("-" * 60)
        
        # Shared Attributes
        common_names = sorted([attr[0] for attr in m.matching_attributes])
        print(f"  ✅ SHARED ATTRIBUTES ({len(common_names)}):")
        for i in range(0, len(common_names), 3):
            row = common_names[i:i+3]
            print(f"     " + "".join(f"{name:<30}" for name in row))
        
        # Gap Visualization
        if unmatched:
            print(f"\n  ⚠️  GAPS IN ALIGNMENT (Fields in query missing from {m.target_schema_name}):")
            for attr in unmatched:
                # Creative DNA-bridge style gap visualization
                print(f"     [ QUERY ]---( x )---[ MISSING IN TARGET ] : {attr}")
        else:
            print(f"\n  ✨ PERFECT COVERAGE: No gaps found.")
            
        print("\n" + "." * 95)

    # --- FOOTER ---
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nReport Generated at: {timestamp}")
    print("="*95 + "\n")

def main():
    parser = argparse.ArgumentParser(prog="schema-compare", description="CLI tool to index and compare schemas.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ... (Keep Upload and Batch parsers as they were) ...
    up = subparsers.add_parser("upload", help="Index a new schema")
    up.add_argument("file"); up.add_argument("--name"); up.add_argument("--description", default=""); up.add_argument("--format", default="auto")

    batch = subparsers.add_parser("batch", help="Import a directory")
    batch.add_argument("directory"); batch.add_argument("--format", default="auto")

    subparsers.add_parser("list", help="List all schemas")

    comp = subparsers.add_parser("compare", help="Compare by ID")
    comp.add_argument("schema_id"); comp.add_argument("--threshold", type=float, default=0.4); comp.add_argument("--limit", type=int, default=5)

    probe = subparsers.add_parser("probe", help="Probe a local file")
    probe.add_argument("file"); probe.add_argument("--threshold", type=float, default=0.4); probe.add_argument("--limit", type=int, default=5); probe.add_argument("--format", default="auto")

    args = parser.parse_args()
    engine = ComparatorEngine()

    if args.command == "upload":
        sids = engine.process_and_upload(args.file, args.format, args.name, args.description)
        for sid in sids: print(f"✅ Indexed: {sid}")
    elif args.command == "batch":
        res = engine.batch_upload(args.directory, args.format)
        print(f"✅ Indexed {res['schemas_indexed']} schemas.")
    elif args.command == "list":
        # ... (Keep your existing List logic here) ...
        schemas = engine.db.list_all()
        for s in schemas: print(f"{s.get('schema_id')} | {s.get('schema_name')}")
    elif args.command == "compare":
        print(f"🔍 Analyzing similarity for ID: {args.schema_id}...")
        matches, query_attrs = engine.find_similar_schemas(args.schema_id, args.threshold, args.limit)
        print_matches(matches, query_attrs)
    elif args.command == "probe":
        print(f"🔭 Probing local file: {args.file} against database...")
        matches, query_attrs = engine.probe_file(args.file, args.format, args.threshold, args.limit)
        print_matches(matches, query_attrs)

if __name__ == "__main__":
    main()