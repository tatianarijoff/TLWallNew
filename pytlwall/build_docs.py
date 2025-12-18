#!/usr/bin/env python3
"""
build_docs.py — PyTlWall Documentation Builder

Converts all Markdown files to HTML using pandoc with:
- Collapsible sidebar navigation
- Documentation links + page TOC
- Logo integration
- Internal link fixing (.md → .html)

Authors:
    Tatiana Rijoff <tatiana.rijoff@gmail.com>
    Carlo Zannini <carlo.zannini@cern.ch>

Copyright: CERN
"""

import argparse
import subprocess
import shutil
import sys
import re
from pathlib import Path
from typing import Tuple, Optional, List, Dict
from datetime import datetime

# === CONFIGURATION ===

BASE_DIR = Path(__file__).resolve().parent

DOC_PATHS = {
    "user": {
        "source": BASE_DIR.parent / "doc",
        "description": "User Documentation",
    },
    "dev": {
        "source": BASE_DIR.parent / "tests" / "doc",
        "description": "Developer/Test Documentation",
    },
}

# Assets
CSS_FILENAME = "style.css"
CSS_HREF = "./style.css"
LOGO_FILENAME = "logo005.png"
JS_FILENAME = "sidebar.js"

# Authors
AUTHORS = [
    {"name": "Tatiana Rijoff", "email": "tatiana.rijoff@gmail.com"},
    {"name": "Carlo Zannini", "email": "carlo.zannini@cern.ch"},
]

# Document structure for navigation
# Order matters! First item is the main doc
CORE_MODULES = [
    ("API_REFERENCE", "API Reference"),
    ("API_REFERENCE_BEAM", "beam"),
    ("API_REFERENCE_FREQUENCIES", "frequencies"),
    ("API_REFERENCE_LAYER", "layer"),
    ("API_REFERENCE_CHAMBER", "chamber"),
    ("API_REFERENCE_TLWALL", "tlwall"),
    ("API_REFERENCE_CFGIO", "cfg_io"),
]

GUI_MODULES = [
    ("GUI", "Pytlwall interface"),
    ("GUI_MENU_BAR", "Gui menu bar"),
    ("GUI_SIDEBAR", "Gui sidebar"),
    ("GUI_DATA_PANEL", "Gui data panel"),
    ("GUI_PLOT_PANEL", "Gui plot panel"),
    ("GUI_VIEW_IO", "Gui view IO"),
]

UTILITY_MODULES = [
    ("LOGGING_README", "logging"),
    ("PLOTTING_README", "plotting"),
    ("OUTPUT_README", "output"),
]

EXAMPLES_MODULES = [
    ("EXAMPLES", "Examples Overview"),
    ("EXAMPLES_BEAM", "beam examples"),
    ("EXAMPLES_FREQUENCIES", "frequencies examples"),
    ("EXAMPLES_LAYER", "layer examples"),
    ("EXAMPLES_CHAMBER", "chamber examples"),
    ("EXAMPLES_TLWALL", "tlwall examples"),
    ("EXAMPLES_LOGGING", "logging examples"),
]

OTHER_DOCS = [
    ("PYTLWALL_THEORY", "PyTlWall theory"),
    ("ConfigModel", "Configuration"),
    ("CHAMBER_SHAPES_REFERENCE", "Chamber Shapes"),
    ("RUN_TESTS_DEEP_README", "Deep Test Runner"),
]

# Pandoc options
PANDOC_OPTIONS = [
    "--standalone",
    "--toc",
    "--toc-depth=3",
    "--mathjax",
    "--metadata=lang:en",
    "--highlight-style=pygments",
    "--wrap=none",
]

for author in AUTHORS:
    PANDOC_OPTIONS.append(f"--metadata=author:{author['name']}")


# === UTILITIES ===

def log_info(tag: str, message: str) -> None:
    print(f"[{tag:6}] {message}")

def log_error(message: str) -> None:
    print(f"[ERROR ] {message}", file=sys.stderr)

def log_warn(message: str) -> None:
    print(f"[WARN  ] {message}", file=sys.stderr)

def check_pandoc() -> bool:
    if shutil.which("pandoc") is None:
        log_error("'pandoc' not found in PATH. Please install pandoc.")
        return False
    return True

def get_pandoc_version() -> str:
    try:
        result = subprocess.run(["pandoc", "--version"], capture_output=True, text=True, check=True)
        return result.stdout.splitlines()[0]
    except Exception:
        return "unknown"

def validate_source_dir(source_dir: Path, doc_type: str) -> bool:
    if not source_dir.is_dir():
        log_error(f"Source directory not found: {source_dir}")
        return False
    md_files = list(source_dir.glob("*.md"))
    if not md_files:
        log_warn(f"No .md files found in {source_dir}")
        return False
    return True


# === ASSET MANAGEMENT ===

def ensure_css(source_dir: Path, output_dir: Path) -> None:
    """Copy the project CSS into the output folder.

    Priority:
      1) <doc_source>/style.css
      2) <scripts_dir>/style.css (same folder as build_docs.py)

    We intentionally DO NOT auto-generate a fallback CSS, because that can
    silently produce wrong styling.
    """
    css_dest = output_dir / CSS_FILENAME

    candidates = [
        source_dir / CSS_FILENAME,
        BASE_DIR / CSS_FILENAME,
    ]

    for css_source in candidates:
        if css_source.is_file():
            shutil.copy2(css_source, css_dest)
            log_info("CSS", f"Copied {CSS_FILENAME} from {css_source}")
            return

    raise FileNotFoundError(
        f"{CSS_FILENAME} not found. Expected it in {source_dir} or {BASE_DIR}."
    )

def ensure_logo(source_dir: Path, output_dir: Path) -> Optional[Path]:
    logo_dest = output_dir / LOGO_FILENAME
    if logo_dest.is_file():
        return logo_dest
    candidates = [
        source_dir / LOGO_FILENAME,
        source_dir.parent / LOGO_FILENAME,
        source_dir / "html" / LOGO_FILENAME,
    ]
    for candidate in candidates:
        if candidate.is_file():
            shutil.copy2(candidate, logo_dest)
            log_info("ASSET", f"Copied {LOGO_FILENAME}")
            return logo_dest
    log_warn(f"Logo {LOGO_FILENAME} not found")
    return None


def ensure_img_assets(source_dir: Path, output_dir: Path) -> None:
    """Copy documentation images (doc/img) into the HTML output folder.

    Pandoc keeps relative paths to images; therefore the same relative layout
    must exist under <output_dir>.
    """
    img_src = source_dir / "img"
    img_dst = output_dir / "img"
    if not img_src.is_dir():
        return
    if img_dst.exists():
        shutil.rmtree(img_dst)
    shutil.copytree(img_src, img_dst)
    log_info("ASSET", "Copied img/ directory")
def create_sidebar_js(source_dir: Path, output_dir: Path) -> None:
    """Ensure sidebar.js exists in the output.

    Priority:
      1) <doc_source>/sidebar.js
      2) <scripts_dir>/sidebar.js
      3) Generate a minimal default
    """
    js_path = output_dir / JS_FILENAME

    candidates = [
        source_dir / JS_FILENAME,
        BASE_DIR / JS_FILENAME,
    ]
    for c in candidates:
        if c.is_file():
            shutil.copy2(c, js_path)
            log_info("JS", f"Copied {JS_FILENAME} from {c}")
            return

    # Fallback generator (only if nothing provided)
    js_content = '''// Sidebar collapsible sections
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.nav-section-header').forEach(function(header) {
    header.addEventListener('click', function() {
      const section = this.parentElement;
      section.classList.toggle('collapsed');
      const sectionId = section.dataset.section;
      if (sectionId) {
        const collapsed = section.classList.contains('collapsed');
        localStorage.setItem('sidebar-' + sectionId, collapsed ? 'collapsed' : 'expanded');
      }
    });
  });

  document.querySelectorAll('.nav-section[data-section]').forEach(function(section) {
    const sectionId = section.dataset.section;
    const savedState = localStorage.getItem('sidebar-' + sectionId);
    if (savedState === 'collapsed') section.classList.add('collapsed');
  });

  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-section a').forEach(function(link) {
    if (link.getAttribute('href') === currentPage) {
      link.classList.add('active');
      const section = link.closest('.nav-section');
      if (section) section.classList.remove('collapsed');
    }
  });
});
'''
    js_path.write_text(js_content, encoding="utf-8")
    log_info("JS", f"Created default {JS_FILENAME}")

# === NAVIGATION HTML GENERATION ===

def generate_nav_section(title: str, section_id: str, items: List[Tuple[str, str]], 
                         existing_files: List[str], collapsed: bool = False) -> str:
    """Generate HTML for a collapsible navigation section."""
    
    # Filter to only include existing files
    valid_items = [(f, label) for f, label in items if f"{f}.html" in existing_files]
    
    if not valid_items:
        return ""
    
    collapsed_class = " collapsed" if collapsed else ""
    
    links_html = "\n".join([
        f'                <li><a href="{filename}.html">{label}</a></li>'
        for filename, label in valid_items
    ])
    
    return f'''
        <div class="nav-section{collapsed_class}" data-section="{section_id}">
            <div class="nav-section-header">
                <span class="nav-section-title">{title}</span>
                <span class="nav-toggle-icon"></span>
            </div>
            <ul class="nav-section-content">
{links_html}
            </ul>
        </div>'''


def generate_docs_navigation(existing_files: List[str]) -> str:
    """Generate the full documentation navigation HTML."""
    
    sections = []
    
    # Core modules (expanded by default)
    core_nav = generate_nav_section(
        "📚 Core Modules", "core", 
        CORE_MODULES, existing_files, 
        collapsed=False
    )
    if core_nav:
        sections.append(core_nav)
    
    # GUI (collapsed by default)
    gui_nav = generate_nav_section(
        "🖥️ Pytlwall Graphical Interface", "gui",
        GUI_MODULES, existing_files,
        collapsed=True
    )
    if gui_nav:
        sections.append(gui_nav)

    # Utility modules (collapsed by default)
    util_nav = generate_nav_section(
        "🔧 Utilities", "utilities",
        UTILITY_MODULES, existing_files,
        collapsed=True
    )
    if util_nav:
        sections.append(util_nav)
    
    # Examples (collapsed by default)
    examples_nav = generate_nav_section(
        "📝 Examples", "examples",
        EXAMPLES_MODULES, existing_files,
        collapsed=True
    )
    if examples_nav:
        sections.append(examples_nav)
    
    # Other docs (collapsed by default)
    other_nav = generate_nav_section(
        "📄 Other Docs", "other",
        OTHER_DOCS, existing_files,
        collapsed=True
    )
    if other_nav:
        sections.append(other_nav)
    
    return "\n".join(sections)


# === LINK FIXING ===

MD_LINK_RE = re.compile(r'href="((?![^"]*://)[^"]*?)\.md(#[^"]*)?"')

def fix_internal_links(html: str) -> str:
    return MD_LINK_RE.sub(r'href="\1.html\2"', html)


# === HTML POST-PROCESSING ===

def postprocess_html(html: str, logo_filename: Optional[str], doc_title: str,
                     existing_files: List[str]) -> str:
    """
    Post-process generated HTML:
    1. Remove original logo figure
    2. Add logo to header
    3. Create collapsible sidebar with docs nav + page TOC
    4. Remove duplicate titles
    """
    
    # Fix internal links
    html = fix_internal_links(html)
    
    # Remove original logo figure from markdown
    html = re.sub(
        r'<figure>\s*<img[^>]*src="[^"]*logo[^"]*"[^>]*/?\s*>\s*<figcaption[^>]*>.*?</figcaption>\s*</figure>',
        '', html, flags=re.DOTALL | re.IGNORECASE
    )
    html = re.sub(
        r'<p>\s*<img[^>]*(?:src="[^"]*logo[^"]*"|alt="[^"]*logo[^"]*")[^>]*/?\s*>\s*</p>',
        '', html, flags=re.DOTALL | re.IGNORECASE
    )
    
    # Extract the page TOC
    toc_match = re.search(r'<nav id="TOC"[^>]*role="doc-toc"[^>]*>(.*?)</nav>', html, re.DOTALL)
    page_toc_content = ""
    if toc_match:
        # Extract just the ul content
        ul_match = re.search(r'(<ul>.*</ul>)', toc_match.group(1), re.DOTALL)
        if ul_match:
            page_toc_content = ul_match.group(1)
        html = html.replace(toc_match.group(0), '')
    
    # Generate documentation navigation
    docs_nav = generate_docs_navigation(existing_files)
    
    # Create page TOC section (expanded by default)
    page_toc_section = ""
    if page_toc_content:
        page_toc_section = f'''
        <div class="nav-section" data-section="toc">
            <div class="nav-section-header">
                <span class="nav-section-title">📑 On This Page</span>
                <span class="nav-toggle-icon"></span>
            </div>
            <div class="nav-section-content toc-content">
                {page_toc_content}
            </div>
        </div>'''
    
    # Build complete sidebar
    sidebar_html = f'''
    <aside class="sidebar">
        <div class="sidebar-header">
            <a href="index.html" class="sidebar-logo-link">PyTlWall</a>
        </div>
        <nav class="sidebar-nav">
            {docs_nav}
            {page_toc_section}
        </nav>
    </aside>'''
    
    # Add logo to header
    header_match = re.search(r'<header id="title-block-header">(.*?)</header>', html, re.DOTALL)
    if header_match:
        header_content = header_match.group(1)
        if logo_filename:
            logo_html = f'<img src="{logo_filename}" alt="PyTlWall" class="header-logo">'
            header_content = re.sub(
                r'(<h1 class="title">)(.*?)(</h1>)',
                rf'<div class="title-with-logo">\1\2\3{logo_html}</div>',
                header_content, flags=re.DOTALL
            )
        new_header = f'<header id="title-block-header">{header_content}</header>'
        html = html.replace(header_match.group(0), new_header)
    
    # Remove duplicate h1 (PyTlWall API Reference after header)
    html = re.sub(
        r'(</header>\s*)<h1[^>]*id="pytlwall-api-reference"[^>]*>.*?</h1>',
        r'\1', html, flags=re.DOTALL | re.IGNORECASE
    )
    
    # Wrap in layout structure
    body_match = re.search(r'(<body[^>]*>)(.*?)(</body>)', html, re.DOTALL)
    if body_match:
        body_start = body_match.group(1)
        body_content = body_match.group(2)
        body_end = body_match.group(3)
        
        new_body = f'''{body_start}
<div class="layout-wrapper">
    {sidebar_html}
    <main class="main-content">
        {body_content}
    </main>
</div>
<script src="{JS_FILENAME}"></script>
{body_end}'''
        html = html.replace(body_match.group(0), new_body)
    
    return html


# === BUILD ===

def build_one(md_path: Path, output_dir: Path, has_logo: bool, 
              existing_files: List[str], verbose: bool = False) -> bool:
    """Convert a single Markdown file to HTML."""
    stem = md_path.stem
    html_path = output_dir / f"{stem}.html"
    nice_title = stem.replace('_', ' ')

    cmd = [
        "pandoc", str(md_path), "-o", str(html_path),
        f"--css={CSS_HREF}",
        f"--metadata=title:{nice_title}",
    ] + PANDOC_OPTIONS

    if verbose:
        log_info("BUILD", f"{md_path.name} → {stem}.html")
    else:
        print(f"  • {md_path.name}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if verbose and result.stderr:
            log_warn(f"pandoc: {result.stderr.strip()}")

        # Post-process
        html = html_path.read_text(encoding="utf-8")
        logo = LOGO_FILENAME if has_logo else None
        html = postprocess_html(html, logo, stem, existing_files)
        html_path.write_text(html, encoding="utf-8")
        
        return True

    except subprocess.CalledProcessError as e:
        log_error(f"Failed to convert {md_path.name}")
        if verbose:
            log_error(f"stderr: {e.stderr}")
        return False


def build_docs(doc_type: str, verbose: bool = False, dry_run: bool = False) -> Tuple[int, int]:
    """Build all documentation for a given type."""
    config = DOC_PATHS[doc_type]
    source_dir = config["source"]
    output_dir = source_dir / "html"

    print("\n" + "=" * 60)
    print(f" Building: {config['description']}")
    print("=" * 60)
    print(f"Source: {source_dir}")
    print(f"Output: {output_dir}\n")

    if not validate_source_dir(source_dir, doc_type):
        return 0, 1

    md_files = sorted(source_dir.glob("*.md"))
    print(f"Found {len(md_files)} Markdown file(s).\n")

    if dry_run:
        print("[DRY RUN] Would convert:")
        for md in md_files:
            print(f"  • {md.name} → html/{md.stem}.html")
        return len(md_files), 0

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine which files will exist
    existing_files = [f"{md.stem}.html" for md in md_files] + ["index.html"]

    # Copy assets
    ensure_css(source_dir, output_dir)
    logo_path = ensure_logo(source_dir, output_dir)
    has_logo = logo_path is not None
    create_sidebar_js(source_dir, output_dir)
    ensure_img_assets(source_dir, output_dir)

    # Convert files
    print("\nConverting files:")
    ok = 0
    fail = 0
    
    for md in md_files:
        if build_one(md, output_dir, has_logo, existing_files, verbose):
            ok += 1
        else:
            fail += 1

    return ok, fail


# === INDEX PAGE ===

def create_index(doc_type: str) -> None:
    """Generate index.html."""
    config = DOC_PATHS[doc_type]
    output_dir = config["source"] / "html"

    if not output_dir.is_dir():
        return

    html_files = sorted(output_dir.glob("*.html"))
    html_files = [f for f in html_files if f.name != "index.html"]
    
    if not html_files:
        return
    
    existing_files = [f.name for f in html_files] + ["index.html"]
    
    logo_path = output_dir / LOGO_FILENAME
    has_logo = logo_path.is_file()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    logo_html = f'<img src="{LOGO_FILENAME}" alt="PyTlWall" class="header-logo">' if has_logo else ''
    author_html = ", ".join([a["name"] for a in AUTHORS])
    
    # Generate navigation
    docs_nav = generate_docs_navigation(existing_files)

    index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyTlWall Documentation</title>
    <link rel="stylesheet" href="{CSS_HREF}">
</head>
<body>
<div class="layout-wrapper">
    <aside class="sidebar">
        <div class="sidebar-header">
            <a href="index.html" class="sidebar-logo-link">PyTlWall</a>
        </div>
        <nav class="sidebar-nav">
            {docs_nav}
        </nav>
    </aside>
    <main class="main-content">
        <header id="title-block-header">
            <div class="title-with-logo">
                <h1 class="title">PyTlWall Documentation</h1>
                {logo_html}
            </div>
            <p class="subtitle">{config['description']}</p>
            <p class="authors">{author_html}</p>
        </header>
        
        <section class="welcome-section">
            <h2>Welcome</h2>
            <p>PyTlWall is a Python library for calculating beam coupling impedances 
               using the transmission line method.</p>
            <p>Use the navigation on the left to browse the documentation, 
               or start with the <a href="API_REFERENCE.html">API Reference</a>.</p>
        </section>
        
        <footer>
            <p><small>Generated by build_docs.py • {timestamp} • Copyright CERN</small></p>
        </footer>
    </main>
</div>
<script src="{JS_FILENAME}"></script>
</body>
</html>
'''

    index_path = output_dir / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    log_info("INDEX", "Created index.html")


# === CLI ===

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build HTML documentation from Markdown files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dev", "-d", action="store_true",
                        help="Build developer documentation")
    parser.add_argument("--all", "-a", action="store_true",
                        help="Build all documentation")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="Show what would be done")
    parser.add_argument("--no-index", action="store_true",
                        help="Skip index.html generation")
    parser.add_argument("--version", action="version",
                        version="build_docs.py v2.1 (PyTlWall)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not check_pandoc():
        return 1

    if args.verbose:
        print(f"Using {get_pandoc_version()}")

    if args.all:
        doc_types = ["user", "dev"]
    elif args.dev:
        doc_types = ["dev"]
    else:
        doc_types = ["user"]

    total_ok = 0
    total_fail = 0

    for doc_type in doc_types:
        ok, fail = build_docs(doc_type, args.verbose, args.dry_run)
        total_ok += ok
        total_fail += fail

        if not args.dry_run and not args.no_index and ok > 0:
            create_index(doc_type)

    print("\n" + "=" * 60)
    print(" BUILD SUMMARY")
    print("=" * 60)
    print(f"  ✓ Converted: {total_ok}")
    print(f"  ✗ Failed:    {total_fail}")

    if total_fail > 0:
        return 1

    print("\n✓ Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
