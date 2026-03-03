import argparse
import sys
from datetime import datetime
from .comparator import ComparatorEngine
from .utils.branding import get_report_header

# def print_matches(matches, query_attributes):
#     """
#     Report with Summary, Detailed Alignments, and Gap Analysis.
#     """
#     if not matches:
#         print("🤷 No similar schemas found above the threshold.")
#         return

#     print(get_report_header(len(query_attributes)))
    
#     query_count = len(query_attributes)
#     query_set = set(query_attributes)

#     # --- SECTION 1: SUMMARY ---
#     print("\n" + "="*95)
#     print(f"      SCHEMA ALIGNMENT REPORT | QUERY SIZE: {query_count} ATTRIBUTES")
#     print("="*95)
#     print(f"{'MATCHING SCHEMA':<30} | {'SCORE':<8} | {'MATCHES'}")
#     print("-" * 95)
#     for m in matches:
#         common_count = len(m.matching_attributes)
#         print(f"{m.target_schema_name:<30} | {m.similarity_score:>6.1%} | {common_count} / {query_count} shared")

#     # --- SECTION 2: DETAILED ALIGNMENTS & GAPS ---
#     print("\n" + "="*95)
#     print("      DETAILED ATTRIBUTE ALIGNMENTS & GAPS")
#     print("="*95)

#     for m in matches:
#         # Attributes present in query but NOT in this specific target
#         target_attrs = {attr[1] for attr in m.matching_attributes}
#         unmatched = sorted(list(query_set - target_attrs))
        
#         print(f"\n> {m.target_schema_name} (ID: {m.target_schema_id})")
#         print(f"  Score: {m.similarity_score:.1%} | Identity: {len(target_attrs)}/{query_count}")
#         print("-" * 60)
        
#         # Shared Attributes
#         common_names = sorted([attr[0] for attr in m.matching_attributes])
#         print(f"  ✅ SHARED ATTRIBUTES ({len(common_names)}):")
#         for i in range(0, len(common_names), 3):
#             row = common_names[i:i+3]
#             print(f"     " + "".join(f"{name:<30}" for name in row))
        
#         # Gap Visualization
#         if unmatched:
#             print(f"\n  ⚠️  GAPS IN ALIGNMENT (Fields in query missing from {m.target_schema_name}):")
#             for attr in unmatched:
#                 # Creative DNA-bridge style gap visualization
#                 print(f"     [ QUERY ]---( x )---[ MISSING IN TARGET ] : {attr}")
#         else:
#             print(f"\n  ✨ PERFECT COVERAGE: No gaps found.")
            
#         print("\n" + "." * 95)

#     # --- FOOTER ---
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     print(f"\nReport Generated at: {timestamp}")
#     print("="*95 + "\n")


def print_matches(matches, query_attributes):
    if not matches:
        print("🤷 No similar schemas found above the threshold.")
        return

    print(get_report_header(len(query_attributes)))
    query_count = len(query_attributes)

    # --- SECTION 1: SUMMARY ---
    # (Keep your existing Summary table logic here...)

    # --- SECTION 2: DETAILED ALIGNMENTS ---
    print("\n" + "="*95)
    print("      DETAILED ATTRIBUTE ALIGNMENTS & LINGUISTIC MAPPING")
    print("="*95)

    for m in matches:
        # Categorize matches
        exact_matches = []
        fuzzy_matches = [] # List of (query, target)
        
        matched_query_names = set()
        for q_attr, t_attr in m.matching_attributes:
            matched_query_names.add(q_attr)
            if q_attr == t_attr:
                exact_matches.append(q_attr)
            else:
                fuzzy_matches.append((q_attr, t_attr))
        
        # Truly missing = in query but not in matched_query_names
        unmatched = sorted([a for a in query_attributes if a not in matched_query_names])

        print(f"\n> {m.target_schema_name} (ID: {m.target_schema_id})")
        print(f"  Score: {m.similarity_score:.1%} | Identity: {len(matched_query_names)}/{query_count}")
        print("-" * 60)

        # 1. Exact Matches
        if exact_matches:
            print(f"  ✅ EXACT MATCHES ({len(exact_matches)}):")
            for i in range(0, len(exact_matches), 3):
                row = sorted(exact_matches)[i:i+3]
                print(f"     " + "".join(f"{name:<30}" for name in row))

        # 2. Fuzzy Section (Linguistic Mapping)
        if fuzzy_matches:
            print(f"\n  🔍 LINGUISTIC MAPPING (Near-Matches):")
            for q_attr, t_attr in sorted(fuzzy_matches):
                print(f"     [ QUERY: {q_attr:<20} ] ≈≈> [ TARGET: {t_attr:<20} ]")

        # 3. True Gaps
        if unmatched:
            print(f"\n  ❌ TRUE GAPS (No equivalent found):")
            for attr in unmatched:
                print(f"     [!] {attr}")
        else:
            print(f"\n  ✨ PERFECT COVERAGE: All fields accounted for.")

        print("\n" + "." * 95)

def main():
    parser = argparse.ArgumentParser(prog="schema-compare", description="CIDGOH SchemaProber: CLI tool to index and compare schemas.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ... (Keep Upload and Batch parsers as they were) ...
    up = subparsers.add_parser("upload", help="Index a new schema")
    up.add_argument("file"); up.add_argument("--name"); up.add_argument("--description", default=""); up.add_argument("--format", default="auto")

    batch = subparsers.add_parser("batch", help="Import a directory")
    batch.add_argument("directory"); batch.add_argument("--format", default="auto")

    subparsers.add_parser("list", help="List all schemas")

    comp = subparsers.add_parser("compare", help="Compare by ID")
    comp.add_argument("schema_id"); 
    comp.add_argument("--threshold", type=float, default=0.4);
    comp.add_argument("--limit", type=int, default=5)
    comp.add_argument("--fuzzy", action="store_true", help="Enable fuzzy attribute matching")
    comp.add_argument("--fuzzy_cutoff", type=float, default=85.0, help="Similarity threshold 0-100 (default: 85)")

    probe = subparsers.add_parser("probe", help="Probe a local file")
    probe.add_argument("file")
    probe.add_argument("--threshold", type=float, default=0.4) 
    probe.add_argument("--limit", type=int, default=5)
    probe.add_argument("--format", default="auto")
    probe.add_argument("--html", action="store_true", help="Generate an HTML report file")
    probe.add_argument("--fuzzy", action="store_true", help="Enable fuzzy attribute matching")
    probe.add_argument("--fuzzy_cutoff", type=float, default=85.0, help="Similarity threshold 0-100 (default: 85)")


    deleter = subparsers.add_parser("delete", help="Remove schemas")
    deleter.add_argument("schema_id", nargs="?", help="Schema ID to delete")
    deleter.add_argument("--all", action="store_true", help="Delete all schemas")

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
        matches, query_attrs = engine.probe_file(
            args.file, 
            args.format, 
            args.threshold, 
            args.limit, 
            fuzzy=args.fuzzy,
            fuzzy_cutoff=args.fuzzy_cutoff  # Pass the new parameter
        )
        print_matches(matches, query_attrs)
        if args.html:
            from .utils.branding import LOGO, LAB_INFO
            from .utils.html_generator import generate_html_report
            path = generate_html_report(matches, query_attrs, LOGO, LAB_INFO)
            print(f"🌐 HTML report generated at: {path}")
    if args.command == "delete":
        if args.all:
            confirm = input("⚠️  Wipe ALL schemas? (y/N): ")
            if confirm.lower() == 'y' and engine.clear_all_data():
                print("💥 Database wiped.")
        elif args.schema_id:
            if engine.remove_schema(args.schema_id):
                print(f"🗑️  Deleted: {args.schema_id}")
            else:
                print(f"❌ Deletion failed.")
if __name__ == "__main__":
    main()