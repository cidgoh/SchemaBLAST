# schema_comparator/utils/branding.py

LOGO = r"""
  ______  _____  ______      ______     ___   ____  ____
 .' ___  ||_   _||_   _ `.  .' ___  |  .'   `.|_   ||   _|
/ .'   \_|  | |    | | `. \/ .'   \_| /  .-.  \ | |__| |
| |         | |    | |  | || |  ____ | |   | | |  __  |
\ `.___.'\ _| |_  _| |_.' /\ `.___]  |\  `-'  /_| |  | |_
 `.____ .'|_____||______.'  `._____.'  `.___.'|____||____|
"""

LAB_INFO = """
Hsiao Lab | Centre for Infectious Disease Genomics and One Health (CIDGOH)
Faculty of Health Sciences, Simon Fraser University | Blusson Hall 
8888 University Dr., Burnaby, B.C. V5A 1S6
E-mail: wwhsiao@sfu.ca | Tel: +1-778-782-3299 | Web: www.cidgoh.ca
"""
version = "0.1.0"

def get_report_header(query_count: int, tool_name: str = "SchemaBLAST") -> str:
    """Returns the full branded header including contact details."""
    header = LOGO
    header += "\n" + "="*95 + "\n"
    header += f"     {tool_name.upper()} - SCHEMA MANAGEMENT TOOL (v{version})\n"
    header += "="*95 + "\n"
    header += LAB_INFO
    # header += "-"*95 + "\n"
    # header += f" SCHEMA ALIGNMENT REPORT | QUERY SIZE: {query_count} ATTRIBUTES\n"
    header += "="*95 + "\n"
    return header