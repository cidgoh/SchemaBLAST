import argparse
import sys
import os
from datetime import datetime
from .comparator import ComparatorEngine
from .utils.branding import get_report_header, LOGO, LAB_INFO
from .utils.html_generator import generate_html_report

def print_matches(matches, query_attributes, global_stats=None, fuzzy_cutoff=85.0):
    """
    Report with Summary, Detailed Alignments, and Linguistic Mapping.
    Handles the 3-item tuple (query, target, score) from the engine.
    """
    if not matches:
        print("🤷 No similar schemas found above the threshold.")
        return

    # --- HEADER & STATS ---
    print(get_report_header(len(query_attributes)))
    
    if global_stats:
        print("="*95)
        print(f" DATABASE STATS: {global_stats['total_schemas']} Schemas | "
              f"{global_stats['unique_attributes']} Unique Attributes | "
              f"Avg: {global_stats['avg_attributes_per_schema']} fields/schema")
        print("="*95)

    if fuzzy_cutoff < 75:
        print(f"\n⚠️  WARNING: Low fuzzy threshold ({fuzzy_cutoff}%) may result in semantic inaccuracies.")

    query_count = len(query_attributes)

    # --- SECTION 1: SUMMARY ---
    print("\n" + "="*95)
    print(f"      SCHEMA ALIGNMENT SUMMARY | QUERY SIZE: {query_count} ATTRIBUTES")
    print("="*95)
    print(f"{'TARGET SCHEMA':<30} | {'SCORE':<8} | {'SIMILARITY':<10} | {'MATCHES'}")
    print("-" * 95)
    for m in matches:
        print(f"{m.target_schema_name[:30]:<30} | {m.similarity_score:>7.1%} | {m.quality_label:<10} | {len(m.matching_attributes)} / {query_count} shared")

    # --- SECTION 2: DETAILED ALIGNMENTS ---
    print("\n" + "="*95)
    print("      DETAILED ATTRIBUTE ALIGNMENTS & LINGUISTIC MAPPING")
    print("="*95)

    for m in matches:
        exact_matches = []
        fuzzy_matches = [] # List of (query, target, score)
        
        matched_query_names = set()
        
        for q_attr, t_attr, score in m.matching_attributes:
            matched_query_names.add(q_attr)
            if score == 100.0:
                exact_matches.append(q_attr)
            else:
                fuzzy_matches.append((q_attr, t_attr, score))
        
        unmatched = sorted([a for a in query_attributes if a not in matched_query_names])

        print(f"\n> {m.target_schema_name} (ID: {m.target_schema_id})")
        print(f"  Confidence: {m.quality_label} | Identity Score: {m.similarity_score:.1%}")
        print("-" * 60)

        if exact_matches:
            print(f"  ✅ EXACT MATCHES ({len(exact_matches)}):")
            for i in range(0, len(exact_matches), 3):
                row = sorted(exact_matches)[i:i+3]
                print(f"     " + "".join(f"{name:<30}" for name in row))

        if fuzzy_matches:
            print(f"\n  🔍 LINGUISTIC MAPPING (Near-Matches):")
            for q_attr, t_attr, score in sorted(fuzzy_matches, key=lambda x: x[2], reverse=True):
                print(f"     [ QUERY: {q_attr:<20} ] ≈≈> [ TARGET: {t_attr:<20} ] ({score}%)")

        if unmatched:
            print(f"\n  ❌ TRUE GAPS (No equivalent found):")
            for attr in unmatched:
                print(f"     [!] {attr}")
        else:
            print(f"\n  ✨ PERFECT COVERAGE: All fields accounted for.")

        print("\n" + "." * 95)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nReport Generated at: {timestamp}")
    print("="*95 + "\n")

def main():
    parser = argparse.ArgumentParser(
        prog="schemablast", 
        description="SchemaBLAST: A utility for indexing and aligning metadata schemas"
    )
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---------------------------------------------------------
    # 1. ALIGN COMMAND 
    # ---------------------------------------------------------
    align_parser = subparsers.add_parser("align", help="Run a SchemaBLAST alignment against the indexed database")
    
    # Input files/IDs (Mutually exclusive: must provide exactly one)
    input_group = align_parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-q", "--query", help="Path to the local query schema file")
    input_group.add_argument("-i", "--id", help="Database Schema ID to use as the query")
    align_parser.add_argument("--format", default="auto", help="Input file format (json/yaml)")

    # Engine parameters
    align_parser.add_argument("-t", "--threshold", type=float, default=0.4, help="Similarity threshold (0-1.0)")
    align_parser.add_argument("-l", "--limit", type=int, default=5, help="Max number of hits to return")
    align_parser.add_argument("-f", "--fuzzy", action="store_true", help="Enable linguistic fuzzy matching")
    align_parser.add_argument("-c", "--cutoff", type=float, default=85.0, help="Fuzzy match sensitivity (0-100)")
    
    # Output parameters
    align_parser.add_argument("-o", "--output", help="Save text summary to file")
    align_parser.add_argument("-r", "--report", nargs='?', const='report.html', help="Generate HTML report (optional: filename.html)")

    # ---------------------------------------------------------
    # 2. DATABASE COMMANDS
    # ---------------------------------------------------------
    db_parser = subparsers.add_parser("database", help="Manage the SchemaBLAST database index")
    db_sub = db_parser.add_subparsers(dest="db_command", required=True)

    # Upload
    upload = db_sub.add_parser("upload", help="Index a single new schema")
    upload.add_argument("file")
    upload.add_argument("-n", "--name", help="Custom name for the schema")
    upload.add_argument("-d", "--description", default="", help="Description string")
    upload.add_argument("--format", default="auto")

    # Batch
    batch = db_sub.add_parser("batch", help="Batch import a directory of schemas")
    batch.add_argument("directory")
    batch.add_argument("--format", default="auto")

    # List
    db_sub.add_parser("list", help="List all indexed schemas")

    # Delete
    deleter = db_sub.add_parser("delete", help="Remove schemas from the index")
    deleter.add_argument("schema_id", nargs="?", help="Specific Schema ID to delete")
    deleter.add_argument("--all", action="store_true", help="Wipe entire database")

    args = parser.parse_args()
    engine = ComparatorEngine()

    # --- EXECUTION LOGIC ---

    if args.command == "align":
        stats = engine.get_database_stats()
        
        # Determine if we are querying via File or ID
        if args.id:
            print(f"🔍 Analyzing Database ID: {args.id}...")
            matches, query_attrs = engine.find_similar_schemas(
                args.id, args.threshold, args.limit, args.fuzzy, args.cutoff
            )
        else:
            print(f"🔭 Probing Local File: {args.query}...")
            matches, query_attrs = engine.probe_file(
                args.query, args.format, args.threshold, args.limit, args.fuzzy, args.cutoff
            )
        
        # 1. Handle HTML Report Generation (-r / --report)
        if args.report:
            path = generate_html_report(
                matches, 
                query_attrs, 
                LOGO, 
                LAB_INFO, 
                stats, 
                threshold=args.threshold,
                limit=args.limit,
                fuzzy_enabled=args.fuzzy,
                fuzzy_cutoff=args.cutoff,
                output_path=args.report
            )
            print(f"🌐 HTML report and CSV mapping generated at: {path}")

        # 2. Handle Text Output (-o / --output or screen)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                original_stdout = sys.stdout
                sys.stdout = f
                try:
                    print_matches(matches, query_attrs, global_stats=stats, fuzzy_cutoff=args.cutoff)
                finally:
                    sys.stdout = original_stdout
            print(f"📄 Text summary saved to: {os.path.abspath(args.output)}")
        else:
            print_matches(matches, query_attrs, global_stats=stats, fuzzy_cutoff=args.cutoff)

    elif args.command == "database":
        if args.db_command == "upload":
            sids = engine.process_and_upload(args.file, args.format, args.name, args.description)
            for sid in sids: print(f"✅ Indexed: {sid}")

        elif args.db_command == "batch":
            res = engine.batch_upload(args.directory, args.format)
            print(f"✅ Indexed {res['schemas_indexed']} schemas.")

        elif args.db_command == "list":
            schemas = engine.db.list_all()
            for s in schemas: print(f"{s.get('schema_id'):<20} | {s.get('schema_name')}")

        elif args.db_command == "delete":
            if args.all:
                if input("⚠️  Wipe ALL schemas? (y/N): ").lower() == 'y':
                    engine.clear_all_data()
                    print("💥 Database wiped.")
            elif args.schema_id:
                if engine.remove_schema(args.schema_id): print(f"🗑️  Deleted: {args.schema_id}")

if __name__ == "__main__":
    main()