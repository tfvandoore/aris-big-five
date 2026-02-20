"""
Build the multi-page Ari's Big Five site.

Generates:
  - index.html          (Introduction / landing)
  - ch1.html .. ch5.html (Five chapters)
  - conclusion.html     (Conclusion + Further Reading link)
  - references/index.html  (Index of all 43 source notes)
  - references/<slug>.html (Individual reference pages)

Usage:
  python build_site.py
"""

import re, shutil
from pathlib import Path
import mistune

ROOT = Path(__file__).parent
SRC_HTML = ROOT / "index_source.html"      # original single-page (renamed)
VAULT_DIR = Path(r"C:\Users\Tim\Documents\Ari\Aris place\Aris big five")
REF_DIR = ROOT / "references"

# ── Reference files in chapter order ──────────────────────────────────
REFERENCED_FILES = [
    # Ch1: Identity
    "Identity and Standards", "The Giant Is You", "The Shame Gap",
    "The Gaining of Maturity", "The big mountain", "The Braces Paradox",
    "Privilege", "Identity and Self", "People Change", "Moon Shot",
    # Ch2: Adversity
    "Ad astra", "Good Timber", "The fight", "Resilience",
    "Character comes from imperfections", "Grief and Loss",
    "Anxiety and Waiting", "Career and Ambition", "Seasons of Life",
    "The psychology of sideways",
    # Ch3: Compounding
    "Investment Philosophy", "Systems over Goals", "Taking Action",
    "Dopamine and Effort", "Level Up Mindset", "Money life as sport",
    "Success Mindset", "How to Win", "Sales Philosophy",
    # Ch4: Trust
    "Trust Equation", "PEACE Framework",
    "Explaining something is like playing catch", "Communication Tips",
    "Leadership Insights", "Management Principles",
    "Hold the Knife by the Handle", "Value of Advice", "Referral Framework",
    # Ch5: Legacy
    "Temporal Love", "Parenting Wisdom",
    "Kids aren't a barrier to our happiness. They are a doorway",
    "Family Values", "Legacy and Wealth Transfer",
]

CHAPTER_MAP = {
    "Identity and Standards": 1, "The Giant Is You": 1, "The Shame Gap": 1,
    "The Gaining of Maturity": 1, "The big mountain": 1, "The Braces Paradox": 1,
    "Privilege": 1, "Identity and Self": 1, "People Change": 1, "Moon Shot": 1,
    "Ad astra": 2, "Good Timber": 2, "The fight": 2, "Resilience": 2,
    "Character comes from imperfections": 2, "Grief and Loss": 2,
    "Anxiety and Waiting": 2, "Career and Ambition": 2, "Seasons of Life": 2,
    "The psychology of sideways": 2,
    "Investment Philosophy": 3, "Systems over Goals": 3, "Taking Action": 3,
    "Dopamine and Effort": 3, "Level Up Mindset": 3, "Money life as sport": 3,
    "Success Mindset": 3, "How to Win": 3, "Sales Philosophy": 3,
    "Trust Equation": 4, "PEACE Framework": 4,
    "Explaining something is like playing catch": 4, "Communication Tips": 4,
    "Leadership Insights": 4, "Management Principles": 4,
    "Hold the Knife by the Handle": 4, "Value of Advice": 4, "Referral Framework": 4,
    "Temporal Love": 5, "Parenting Wisdom": 5,
    "Kids aren't a barrier to our happiness. They are a doorway": 5,
    "Family Values": 5, "Legacy and Wealth Transfer": 5,
}

CHAPTER_TITLES = {
    1: "The Giant Within",
    2: "Through, Not Around",
    3: "The First Rule of Compounding",
    4: "The Thrower Adapts",
    5: "Love in Finite Time",
}

CHAPTER_SUBS = {
    1: "On identity, standards, and the person you're becoming",
    2: "On adversity, resilience, and the forge that makes you",
    3: "On systems, patience, and the life that grows like interest",
    4: "On trust, communication, and the architecture of connection",
    5: "On legacy, parenting, and the urgency of presence",
}

CHAPTER_WORDS = {
    1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
}

# ── Navigation structure ─────────────────────────────────────────────
NAV_ITEMS = [
    ("index.html",      "Introduction",                   None),
    ("ch1.html",        "The Giant Within",                "Chapter 1"),
    ("ch2.html",        "Through, Not Around",             "Chapter 2"),
    ("ch3.html",        "The First Rule of Compounding",   "Chapter 3"),
    ("ch4.html",        "The Thrower Adapts",              "Chapter 4"),
    ("ch5.html",        "Love in Finite Time",             "Chapter 5"),
    ("conclusion.html", "Conclusion & Further Reading",    None),
]


def slugify(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


# ── Shared CSS ────────────────────────────────────────────────────────
SHARED_CSS = '''
:root {
    --text: #1a1a1a;
    --text-secondary: #5c564e;
    --bg: #faf8f4;
    --bg-card: #fff;
    --accent: #b08d57;
    --accent-hover: #96763f;
    --accent-light: #f5f0e6;
    --border: #ddd8cf;
    --quote-bg: #f8f5ee;
    --quote-border: #c9a96e;
    --ref: #8a6d2f;
    --ref-bg: #f3edd9;
    --ref-hover: #e8dfc8;
    --sidebar-bg: #f4f1ea;
    --sidebar-width: 280px;
    --hero-gradient-1: #1e2d3d;
    --hero-gradient-2: #0d1821;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; font-size: 18px; }

body {
    font-family: 'Georgia', 'Times New Roman', serif;
    color: var(--text);
    background: var(--bg);
    line-height: 1.75;
    -webkit-font-smoothing: antialiased;
}

/* ── Sidebar ── */
.sidebar {
    width: var(--sidebar-width);
    position: fixed;
    top: 0; left: 0; bottom: 0;
    background: var(--sidebar-bg);
    border-right: 1px solid var(--border);
    overflow-y: auto;
    padding: 1.5rem 0;
    z-index: 100;
}

.sidebar-brand {
    padding: 0.5rem 1.5rem 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1rem;
}

.sidebar-brand a {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--accent);
    text-decoration: none;
}

.sidebar-brand .brand-sub {
    display: block;
    font-family: 'Georgia', serif;
    font-size: 0.75rem;
    color: var(--text-secondary);
    font-style: italic;
    margin-top: 0.2rem;
}

.sidebar nav ul {
    list-style: none;
    padding: 0;
}

.sidebar nav li {
    margin: 0;
}

.sidebar nav a {
    display: block;
    padding: 0.55rem 1.5rem;
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 0.82rem;
    color: var(--text);
    text-decoration: none;
    border-left: 3px solid transparent;
    transition: all 0.15s;
}

.sidebar nav a:hover {
    background: var(--accent-light);
    color: var(--accent);
}

.sidebar nav a.active {
    background: var(--accent-light);
    color: var(--accent);
    border-left-color: var(--accent);
    font-weight: 600;
}

.sidebar nav .nav-label {
    display: block;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-secondary);
    opacity: 0.7;
}

.sidebar-ref-link {
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--border);
    margin-top: 1rem;
}

.sidebar-ref-link a {
    display: block;
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 0.8rem;
    color: var(--accent);
    text-decoration: none;
    padding: 0.5rem 1rem;
    background: var(--accent-light);
    border-radius: 6px;
    text-align: center;
    transition: background 0.2s;
}

.sidebar-ref-link a:hover {
    background: var(--ref-hover);
}

/* ── Mobile menu toggle ── */
.menu-toggle {
    display: none;
    position: fixed;
    top: 1rem; left: 1rem;
    z-index: 200;
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 0.75rem;
    font-size: 1.2rem;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

/* ── Main content ── */
.main-content {
    margin-left: var(--sidebar-width);
    min-height: 100vh;
}

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, var(--hero-gradient-1), var(--hero-gradient-2));
    color: #fff;
    padding: 4rem 2rem 3rem;
    text-align: center;
}

.hero h1 {
    font-size: 2.5rem;
    font-weight: 400;
    letter-spacing: 0.02em;
    margin-bottom: 0.4rem;
}

.hero .subtitle {
    font-style: italic;
    font-size: 1.05rem;
    opacity: 0.85;
    margin-bottom: 1rem;
}

.hero .epigraph {
    max-width: 600px;
    margin: 0 auto;
    font-style: italic;
    font-size: 0.9rem;
    opacity: 0.7;
    border-top: 1px solid rgba(255,255,255,0.2);
    padding-top: 1.25rem;
}

/* ── Container ── */
.container {
    max-width: 720px;
    margin: 0 auto;
    padding: 0 1.5rem;
}

/* ── Chapter content ── */
.chapter-content {
    max-width: 720px;
    margin: 3rem auto;
    padding: 0 1.5rem;
}

.chapter-header {
    text-align: center;
    margin-bottom: 2.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}

.chapter-number {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--accent);
    margin-bottom: 0.3rem;
}

.chapter-header h2 {
    font-size: 2rem;
    font-weight: 400;
    margin-bottom: 0.3rem;
}

.chapter-header .chapter-sub {
    font-style: italic;
    color: var(--text-secondary);
    font-size: 1rem;
}

/* ── Typography ── */
h3 {
    font-size: 1.3rem;
    font-weight: 400;
    margin: 2.5rem 0 1rem;
    color: var(--text);
}

p { margin-bottom: 1.25rem; }
strong { font-weight: 700; }
em { font-style: italic; }

ul, ol { margin-bottom: 1.25rem; padding-left: 1.5rem; }
li { margin-bottom: 0.3rem; }

/* ── Vault references ── */
.ref {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 0.82rem;
    background: var(--ref-bg);
    color: var(--ref);
    padding: 0.15em 0.5em;
    border-radius: 3px;
    white-space: nowrap;
    font-weight: 500;
    text-decoration: none;
    transition: background 0.2s;
}

.ref:hover { background: var(--ref-hover); }
a.ref { text-decoration: none; }

/* ── Blockquotes ── */
blockquote {
    border-left: 3px solid var(--quote-border);
    background: var(--quote-bg);
    padding: 1.25rem 1.5rem;
    margin: 2rem 0;
    border-radius: 0 6px 6px 0;
    font-style: italic;
}

blockquote p { margin-bottom: 0; }

blockquote .attribution {
    display: block;
    text-align: right;
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-top: 0.5rem;
    font-style: normal;
}

/* ── Equation ── */
.equation {
    text-align: center;
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 1.05rem;
    letter-spacing: 0.03em;
    color: var(--accent);
    margin: 1.5rem 0;
    font-weight: 600;
}

/* ── Diamond items ── */
.diamond-item {
    padding-left: 1.2rem;
    border-left: 3px solid var(--accent-light);
    margin-bottom: 1.25rem;
}

/* ── Observation items ── */
.observation {
    padding-left: 1.2rem;
    border-left: 3px solid var(--quote-border);
    margin-bottom: 1.25rem;
}

/* ── Arc list (intro) ── */
.arc-list { list-style: none; padding: 0; margin: 1.5rem 0; }

.arc-list li {
    margin-bottom: 0.4rem;
    padding-left: 1.5rem;
    position: relative;
}

.arc-list li::before {
    content: "";
    position: absolute;
    left: 0; top: 0.6em;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent);
}

.arc-flow {
    text-align: center;
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 0.9rem;
    letter-spacing: 0.1em;
    color: var(--text-secondary);
    margin: 1.5rem 0 2rem;
}

/* ── Dividers ── */
hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 3rem auto;
    max-width: 720px;
}

/* ── Page nav (prev/next) ── */
.page-nav {
    display: flex;
    justify-content: space-between;
    max-width: 720px;
    margin: 3rem auto 2rem;
    padding: 0 1.5rem;
    gap: 1rem;
}

.page-nav a {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 0.85rem;
    color: var(--accent);
    text-decoration: none;
    padding: 0.6rem 1.2rem;
    border: 1px solid var(--border);
    border-radius: 6px;
    transition: all 0.2s;
    max-width: 48%;
}

.page-nav a:hover {
    background: var(--accent-light);
    border-color: var(--accent);
}

.page-nav .prev::before { content: "\\2190  "; }
.page-nav .next::after { content: "  \\2192"; }
.page-nav .spacer { flex: 1; }

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 2rem 1.5rem 3rem;
    color: var(--text-secondary);
    font-size: 0.85rem;
    max-width: 720px;
    margin: 0 auto;
}

/* ── Reference note page ── */
.note-content {
    max-width: 720px;
    margin: 2.5rem auto;
    padding: 0 1.5rem;
}

.note-content h2 {
    font-size: 1.6rem;
    font-weight: 400;
    margin-bottom: 1.5rem;
    color: var(--text);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
}

.note-content h1 { font-size: 1.4rem; font-weight: 400; margin: 1.5rem 0 1rem; }
.note-content h3 { font-size: 1.15rem; font-weight: 700; margin: 2rem 0 0.75rem; }
.note-content h4 { font-size: 1rem; font-weight: 700; margin: 1.5rem 0 0.5rem; }

.back-link-bar {
    max-width: 720px;
    margin: 0 auto;
    padding: 1.5rem 1.5rem 0;
}

.back-link-bar a {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 0.85rem;
    color: var(--accent);
    text-decoration: none;
}

.back-link-bar a:hover { text-decoration: underline; }

/* ── References index cards ── */
.ref-grid {
    max-width: 720px;
    margin: 0 auto;
    padding: 0 1.5rem;
}

.ref-chapter-group {
    margin-bottom: 2.5rem;
}

.ref-chapter-label {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--accent);
    background: var(--accent-light);
    display: inline-block;
    padding: 0.35em 1em;
    border-radius: 20px;
    margin-bottom: 1rem;
}

.ref-list {
    list-style: none;
    padding: 0;
}

.ref-list li {
    margin-bottom: 0.4rem;
}

.ref-list a {
    font-size: 0.95rem;
    color: var(--text);
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: all 0.2s;
}

.ref-list a:hover {
    color: var(--accent);
    border-bottom-color: var(--accent);
}

/* ── CTA button ── */
.cta-button {
    display: inline-block;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    background: var(--accent);
    color: #fff;
    padding: 0.75em 2em;
    border-radius: 6px;
    text-decoration: none;
    font-size: 0.95rem;
    transition: background 0.2s;
}

.cta-button:hover { background: var(--accent-hover); }

/* ── Responsive ── */
@media (max-width: 900px) {
    .sidebar {
        transform: translateX(-100%);
        transition: transform 0.3s;
        box-shadow: none;
    }
    .sidebar.open {
        transform: translateX(0);
        box-shadow: 4px 0 20px rgba(0,0,0,0.15);
    }
    .menu-toggle { display: block; }
    .main-content { margin-left: 0; }
    .hero { padding: 3.5rem 1.5rem 2.5rem; }
    .hero h1 { font-size: 2rem; }
}

@media (max-width: 600px) {
    html { font-size: 16px; }
    .hero { padding: 3rem 1rem 2rem; }
    .hero h1 { font-size: 1.6rem; }
    .page-nav { flex-direction: column; }
    .page-nav a { max-width: 100%; }
}
'''

# ── JavaScript for mobile menu ───────────────────────────────────────
MENU_JS = '''
<script>
document.querySelector('.menu-toggle').addEventListener('click', function() {
    document.querySelector('.sidebar').classList.toggle('open');
});
document.querySelector('.main-content').addEventListener('click', function() {
    document.querySelector('.sidebar').classList.remove('open');
});
</script>
'''


def build_sidebar(active_href, is_subdir=False):
    """Build sidebar HTML. is_subdir=True for references/ pages."""
    prefix = "../" if is_subdir else ""
    lines = [
        '<aside class="sidebar">',
        '  <div class="sidebar-brand">',
        f'    <a href="{prefix}index.html">Ari\'s Big Five</a>',
        '    <span class="brand-sub">A thesis on the Nexus vault</span>',
        '  </div>',
        '  <nav><ul>',
    ]
    for href, title, label in NAV_ITEMS:
        full_href = f"{prefix}{href}"
        cls = ' class="active"' if href == active_href else ''
        label_html = f'<span class="nav-label">{label}</span>' if label else ''
        lines.append(f'    <li><a href="{full_href}"{cls}>{label_html}{title}</a></li>')
    lines += [
        '  </ul></nav>',
        '  <div class="sidebar-ref-link">',
        f'    <a href="{prefix}references/index.html">Source Notes (43) &rarr;</a>',
        '  </div>',
        '</aside>',
    ]
    return '\n'.join(lines)


def page_template(title, body_html, active_href, is_subdir=False, description=""):
    """Wrap body content in the full page template."""
    sidebar = build_sidebar(active_href, is_subdir)
    desc = description or "A thesis on the most valuable ideas in the Nexus."
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <style>{SHARED_CSS}</style>
</head>
<body>

<button class="menu-toggle" aria-label="Toggle navigation">&#9776;</button>

{sidebar}

<div class="main-content">
{body_html}
</div>

{MENU_JS}
</body>
</html>'''


def build_page_nav(idx, items):
    """Build prev/next navigation between pages."""
    parts = ['<div class="page-nav">']
    if idx > 0:
        prev_href, prev_title, _ = items[idx - 1]
        parts.append(f'<a href="{prev_href}" class="prev">{prev_title}</a>')
    else:
        parts.append('<span class="spacer"></span>')
    if idx < len(items) - 1:
        next_href, next_title, _ = items[idx + 1]
        parts.append(f'<a href="{next_href}" class="next">{next_title}</a>')
    else:
        parts.append('<span class="spacer"></span>')
    parts.append('</div>')
    return '\n'.join(parts)


FOOTER_HTML = '''
<footer class="footer">
    <p class="credit">Written by Ari, February 2026</p>
</footer>
'''


# ── Extract content from original single-page HTML ───────────────────
def extract_sections(html):
    """Extract each section's inner HTML from the original index.html."""
    markers = {
        'intro':      (r'<!-- ============ INTRODUCTION ============ -->\s*',
                       r'\s*<hr[^>]*>\s*<!-- ============ CHAPTER 1'),
        'ch1':        (r'<!-- ============ CHAPTER 1 ============ -->\s*',
                       r'\s*<hr[^>]*>\s*<!-- ============ CHAPTER 2'),
        'ch2':        (r'<!-- ============ CHAPTER 2 ============ -->\s*',
                       r'\s*<hr[^>]*>\s*<!-- ============ CHAPTER 3'),
        'ch3':        (r'<!-- ============ CHAPTER 3 ============ -->\s*',
                       r'\s*<hr[^>]*>\s*<!-- ============ CHAPTER 4'),
        'ch4':        (r'<!-- ============ CHAPTER 4 ============ -->\s*',
                       r'\s*<hr[^>]*>\s*<!-- ============ CHAPTER 5'),
        'ch5':        (r'<!-- ============ CHAPTER 5 ============ -->\s*',
                       r'\s*<hr[^>]*>\s*<!-- ============ CONCLUSION'),
        'conclusion': (r'<!-- ============ CONCLUSION ============ -->\s*',
                       r'\s*<!-- ============ FURTHER READING'),
    }
    sections = {}
    for key, (start_pat, end_pat) in markers.items():
        m = re.search(start_pat + r'(.*?)' + end_pat, html, re.DOTALL)
        if m:
            sections[key] = m.group(1).strip()
        else:
            print(f"WARNING: Could not extract section '{key}'")
            sections[key] = f'<p>Section {key} not found.</p>'
    return sections


def fix_ref_links(html):
    """Convert references.html#slug links to references/slug.html links."""
    return re.sub(
        r'href="references\.html#([^"]+)"',
        r'href="references/\1.html"',
        html
    )


def fix_ref_links_from_subdir(html):
    """For pages inside references/, convert references.html#slug to slug.html."""
    return re.sub(
        r'href="references\.html#([^"]+)"',
        r'href="\1.html"',
        html
    )


# ── Build main pages ─────────────────────────────────────────────────
def build_main_pages(sections):
    """Generate the 7 main pages."""

    # 1. Introduction / landing page
    intro_body = f'''
<header class="hero">
    <h1>Ari's Big Five</h1>
    <p class="subtitle">A thesis on the most valuable ideas in the Nexus</p>
    <p class="epigraph">"Note taking is documenting encounters. Without synthesis, the only expression is further note taking."</p>
</header>

<div class="chapter-content">
{fix_ref_links(sections['intro'])}
</div>

{build_page_nav(0, NAV_ITEMS)}
{FOOTER_HTML}
'''
    write_page(ROOT / "index.html", "Ari's Big Five", intro_body, "index.html")

    # 2–6. Chapter pages
    for ch in range(1, 6):
        key = f'ch{ch}'
        content = fix_ref_links(sections[key])
        ch_body = f'''
<header class="hero">
    <h1>{CHAPTER_TITLES[ch]}</h1>
    <p class="subtitle">Chapter {CHAPTER_WORDS[ch]} - {CHAPTER_SUBS[ch]}</p>
</header>

<div class="chapter-content">
{content}
</div>

{build_page_nav(ch, NAV_ITEMS)}
{FOOTER_HTML}
'''
        # Strip the chapter-header div from content since we have the hero
        ch_body = re.sub(
            r'\s*<div class="chapter-header">\s*'
            r'<div class="chapter-number">.*?</div>\s*'
            r'<h2>.*?</h2>\s*'
            r'<p class="chapter-sub">.*?</p>\s*'
            r'</div>',
            '',
            ch_body,
            count=1,
            flags=re.DOTALL
        )
        # Remove the wrapping <article> tags
        ch_body = re.sub(r'<article[^>]*>', '', ch_body)
        ch_body = ch_body.replace('</article>', '')

        write_page(ROOT / f"ch{ch}.html",
                   f"Chapter {ch}: {CHAPTER_TITLES[ch]} - Ari's Big Five",
                   ch_body, f"ch{ch}.html")

    # 7. Conclusion + Further Reading
    conclusion_content = fix_ref_links(sections['conclusion'])
    conclusion_body = f'''
<header class="hero">
    <h1>Conclusion: The Diamond</h1>
    <p class="subtitle">Five facets of one worldview</p>
</header>

<div class="chapter-content">
{conclusion_content}

<hr>

<h2 id="further-reading">Further Reading</h2>
<p>The chapters above draw on 43 source notes from the Nexus vault. Each contains Tim's original thinking, enriched with research and cross-references. They are the raw material from which this thesis was composed.</p>
<p style="text-align: center; margin: 2rem 0;">
    <a href="references/index.html" class="cta-button">Read the source notes &rarr;</a>
</p>
</div>

{build_page_nav(6, NAV_ITEMS)}
{FOOTER_HTML}
'''
    # Remove wrapping tags
    conclusion_body = re.sub(r'<section[^>]*>', '', conclusion_body)
    conclusion_body = conclusion_body.replace('</section>', '')

    write_page(ROOT / "conclusion.html",
               "Conclusion - Ari's Big Five",
               conclusion_body, "conclusion.html")


def write_page(path, title, body, active_href, is_subdir=False, desc=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    html = page_template(title, body, active_href, is_subdir, desc)
    html = normalize_dashes(html)
    path.write_text(html, encoding='utf-8')
    print(f"  wrote {path.relative_to(ROOT)}")


# ── Build reference pages ────────────────────────────────────────────
def strip_version_notes(content):
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    content = re.sub(r'^up::.*$', '', content, flags=re.MULTILINE)
    content = content.lstrip('\n')
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()


def remove_see_also(html):
    """Remove 'See also:' paragraphs."""
    return re.sub(r'<p>See also:.*?</p>', '', html, flags=re.DOTALL)


def normalize_dashes(html):
    """Replace em-dashes and double hyphens with single hyphens in content.

    Preserves CSS custom properties (--var-name) and HTML comments.
    Tim uses single hyphens consistently.
    """
    # Replace &mdash; entity
    html = html.replace('&mdash;', '-')
    # Replace literal em-dash character
    html = html.replace('\u2014', '-')
    # Replace en-dash character
    html = html.replace('\u2013', '-')
    # Replace double hyphens in content, but NOT in CSS (-- as custom properties)
    # or HTML comments. We do this by splitting on <style> blocks and only
    # replacing in non-style content.
    parts = re.split(r'(<style>.*?</style>|<!--.*?-->)', html, flags=re.DOTALL)
    for i, part in enumerate(parts):
        if not part.startswith('<style>') and not part.startswith('<!--'):
            # Replace " -- " with " - " (spaced double-hyphen)
            parts[i] = part.replace(' -- ', ' - ')
            # Replace remaining double-hyphens not in CSS context
            parts[i] = re.sub(r'(?<!-)--(?![->\w])', '-', parts[i])
    return ''.join(parts)


def fix_poem_line_breaks(html):
    """Convert soft newlines inside <p> blocks to <br> for poem formatting.

    Targets paragraphs where every line ends with a rhyming/poetic pattern
    (lines within a single <p> separated only by newlines). This handles the
    Good Timber poem and any similar poetry in reference notes.
    """
    def add_breaks(m):
        content = m.group(1)
        # Only apply to blocks with 4+ lines (likely a poem stanza)
        lines = content.strip().split('\n')
        if len(lines) >= 4:
            return '<p>' + '<br>\n'.join(lines) + '</p>'
        return m.group(0)
    return re.sub(r'<p>((?:[^\n<]+\n){3,}[^\n<]+)</p>', add_breaks, html)


def remove_context_and_duplicate_heading(html, note_name):
    """Remove <context>...</context> paragraphs and duplicate h1 heading."""
    # Remove <p>&lt;context&gt;...&lt;/context&gt;</p>
    html = re.sub(r'<p>&lt;context&gt;.*?&lt;/context&gt;</p>\s*', '', html, flags=re.DOTALL)
    # Remove the first <h1> - it always duplicates the note title which is
    # already shown as the page <h2>. We remove any first <h1> since the
    # template provides the title. Handles case/punctuation/apostrophe variants.
    html = re.sub(r'<h1>[^<]+</h1>\s*', '', html, count=1)
    return html


def convert_wikilinks_to_ref_links(html):
    """Convert [[wikilinks]] to reference page links."""
    def replace_wl(m):
        name = m.group(1)
        slug = slugify(name)
        return f'<a href="{slug}.html" class="ref">{name}</a>'
    return re.sub(r'\[\[([^\]]+)\]\]', replace_wl, html)


# Set of valid reference slugs (pages that actually exist)
VALID_REF_SLUGS = {slugify(name) for name in REFERENCED_FILES}


def remove_broken_ref_links(html):
    """Replace ref links to non-existent pages with plain text spans."""
    def replace_if_broken(m):
        href = m.group(1)
        text = m.group(2)
        slug = href.replace('.html', '')
        if slug in VALID_REF_SLUGS:
            return m.group(0)  # keep valid links
        return text  # replace with plain text (no tag at all)
    return re.sub(r'<a href="([^"]+\.html)" class="ref">([^<]+)</a>', replace_if_broken, html)


def build_reference_pages():
    """Generate individual reference pages and the references index."""
    REF_DIR.mkdir(parents=True, exist_ok=True)
    md = mistune.create_markdown()

    toc_by_chapter = {}
    for ch in range(1, 6):
        toc_by_chapter[ch] = []

    for name in REFERENCED_FILES:
        slug = slugify(name)
        chapter = CHAPTER_MAP.get(name, 0)

        # Find and read vault file
        candidates = list(VAULT_DIR.glob(f"{name}.md"))
        if not candidates:
            print(f"  WARNING: {name}.md not found, skipping")
            continue

        raw = candidates[0].read_text(encoding='utf-8')
        cleaned = strip_version_notes(raw)
        html_content = md(cleaned)
        html_content = convert_wikilinks_to_ref_links(html_content)
        html_content = remove_broken_ref_links(html_content)
        html_content = remove_see_also(html_content)
        html_content = remove_context_and_duplicate_heading(html_content, name)
        html_content = fix_poem_line_breaks(html_content)
        html_content = fix_ref_links_from_subdir(html_content)

        # Determine which chapter page links back
        ch_page = f"ch{chapter}.html"
        ch_title = CHAPTER_TITLES.get(chapter, "")

        body = f'''
<div class="back-link-bar">
    <a href="../{ch_page}">&larr; Back to Chapter {chapter}: {ch_title}</a>
</div>

<div class="note-content">
    <h2>{name}</h2>
    {html_content}
</div>

<div class="page-nav" style="max-width:720px;margin:2rem auto;padding:0 1.5rem;">
    <a href="index.html" class="prev">All Source Notes</a>
    <a href="../{ch_page}" class="next">Back to Chapter {chapter}</a>
</div>

<footer class="footer">
    <p>From Tim's personal knowledge vault (TheNexus3.0).</p>
    <p><a href="../index.html">&larr; Back to Ari's Big Five</a></p>
</footer>
'''
        write_page(
            REF_DIR / f"{slug}.html",
            f"{name} - Ari's Big Five",
            body, None, is_subdir=True,
            desc=f"Source note: {name}"
        )

        toc_by_chapter[chapter].append((name, slug))

    # Build references index page
    toc_html_parts = []
    for ch in range(1, 6):
        ch_title = CHAPTER_TITLES[ch]
        items = toc_by_chapter.get(ch, [])
        toc_html_parts.append(f'''
<div class="ref-chapter-group">
    <div class="ref-chapter-label">Chapter {ch}: {ch_title}</div>
    <ul class="ref-list">''')
        for name, slug in items:
            toc_html_parts.append(f'        <li><a href="{slug}.html">{name}</a></li>')
        toc_html_parts.append('    </ul>\n</div>')

    index_body = f'''
<header class="hero">
    <h1>Further Reading</h1>
    <p class="subtitle">43 source notes from the Nexus vault</p>
</header>

<div class="back-link-bar" style="margin-top:1.5rem;">
    <a href="../index.html">&larr; Back to Ari's Big Five</a>
</div>

<div class="ref-grid" style="margin-top:2rem;">
{''.join(toc_html_parts)}
</div>

<footer class="footer">
    <p>These notes are from Tim's personal knowledge vault (TheNexus3.0).
    They represent years of collected wisdom, experience, and reflection.</p>
    <p><a href="../index.html">&larr; Back to Ari's Big Five</a></p>
</footer>
'''
    write_page(
        REF_DIR / "index.html",
        "Further Reading - Ari's Big Five",
        index_body, None, is_subdir=True,
        desc="43 source notes from the Nexus vault referenced in Ari's Big Five."
    )


# ── Main ─────────────────────────────────────────────────────────────
def main():
    # Read the original single-page HTML
    # First time: rename index.html to index_source.html as backup
    original = ROOT / "index.html"
    if not SRC_HTML.exists() and original.exists():
        shutil.copy2(original, SRC_HTML)
        print(f"Backed up original to {SRC_HTML.name}")

    source = SRC_HTML if SRC_HTML.exists() else original
    html = source.read_text(encoding='utf-8')

    print("Extracting sections...")
    sections = extract_sections(html)

    print("\nBuilding main pages...")
    build_main_pages(sections)

    print("\nBuilding reference pages...")
    build_reference_pages()

    print(f"\nDone! Generated 7 main pages + 44 reference pages.")


if __name__ == '__main__':
    main()
