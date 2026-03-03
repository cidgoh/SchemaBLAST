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
        
        # FIX: Unpack 3 values (q_attr, t_attr, score)
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

        # 1. Exact Matches
        if exact_matches:
            print(f"  ✅ EXACT MATCHES ({len(exact_matches)}):")
            for i in range(0, len(exact_matches), 3):
                row = sorted(exact_matches)[i:i+3]
                print(f"     " + "".join(f"{name:<30}" for name in row))

        # 2. Fuzzy Section (Linguistic Mapping)
        if fuzzy_matches:
            print(f"\n  🔍 LINGUISTIC MAPPING (Near-Matches):")
            for q_attr, t_attr, score in sorted(fuzzy_matches, key=lambda x: x[2], reverse=True):
                print(f"     [ QUERY: {q_attr:<20} ] ≈≈> [ TARGET: {t_attr:<20} ] ({score}%)")

        # 3. True Gaps
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
    parser = argparse.ArgumentParser(prog="schema-compare", description="CIDGOH SchemaProber: CLI tool to index and compare schemas.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Upload
    up = subparsers.add_parser("upload", help="Index a new schema")
    up.add_argument("file")
    up.add_argument("--name")
    up.add_argument("--description", default="")
    up.add_argument("--format", default="auto")

    # Batch
    batch = subparsers.add_parser("batch", help="Import a directory")
    batch.add_argument("directory")
    batch.add_argument("--format", default="auto")

    # List
    subparsers.add_parser("list", help="List all schemas")

    # Compare
    comp = subparsers.add_parser("compare", help="Compare by ID")
    comp.add_argument("schema_id")
    comp.add_argument("--threshold", type=float, default=0.4)
    comp.add_argument("--limit", type=int, default=5)
    comp.add_argument("--fuzzy", action="store_true", help="Enable fuzzy attribute matching")
    comp.add_argument("--fuzzy_cutoff", type=float, default=85.0)

    # Probe
    probe = subparsers.add_parser("probe", help="Probe a local file")
    probe.add_argument("file")
    probe.add_argument("--threshold", type=float, default=0.4) 
    probe.add_argument("--limit", type=int, default=5)
    probe.add_argument("--format", default="auto")
    probe.add_argument("--html", action="store_true", help="Generate an HTML report and CSV mapping")
    probe.add_argument("--fuzzy", action="store_true", help="Enable fuzzy attribute matching")
    probe.add_argument("--fuzzy_cutoff", type=float, default=85.0)

    # Delete
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
        schemas = engine.db.list_all()
        print(f"\n{'ID':<20} | {'SCHEMA NAME'}")
        print("-" * 50)
        for s in schemas: 
            print(f"{s.get('schema_id'):<20} | {s.get('schema_name')}")

    elif args.command == "compare":
        stats = engine.get_database_stats()
        print(f"🔍 Analyzing similarity for ID: {args.schema_id}...")
        matches, query_attrs = engine.find_similar_schemas(
            args.schema_id, args.threshold, args.limit, 
            fuzzy=args.fuzzy, fuzzy_cutoff=args.fuzzy_cutoff
        )
        print_matches(matches, query_attrs, global_stats=stats, fuzzy_cutoff=args.fuzzy_cutoff)

    elif args.command == "probe":
        stats = engine.get_database_stats()
        print(f"🔭 Probing local file: {args.file} against database...")
        matches, query_attrs = engine.probe_file(
            args.file, 
            args.format, 
            args.threshold, 
            args.limit, 
            fuzzy=args.fuzzy,
            fuzzy_cutoff=args.fuzzy_cutoff
        )
        
        if args.html:
            path = generate_html_report(matches, query_attrs, LOGO, LAB_INFO, stats, args.fuzzy_cutoff)
            print(f"🌐 HTML report and CSV mapping generated at: {path}")

        print_matches(matches, query_attrs, global_stats=stats, fuzzy_cutoff=args.fuzzy_cutoff)

    elif args.command == "delete":
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