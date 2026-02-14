"""
Build references.html from vault source .md files.
Strips version notes (<!-- AI-assisted ... --> comments, up:: lines, frontmatter).
"""

import re
from pathlib import Path
import mistune

SRC = Path(r"C:\Users\Tim\Documents\Ari\Aris place\Aris big five")
OUT = Path(__file__).parent / "references.html"

# All referenced files in chapter order
REFERENCED_FILES = [
    # Ch1: Identity
    "Identity and Standards",
    "The Giant Is You",
    "The Shame Gap",
    "The Gaining of Maturity",
    "The big mountain",
    "The Braces Paradox",
    "Privilege",
    "Identity and Self",
    "People Change",
    "Moon Shot",
    # Ch2: Adversity
    "Ad astra",
    "Good Timber",
    "The fight",
    "Resilience",
    "Character comes from imperfections",
    "Grief and Loss",
    "Anxiety and Waiting",
    "Career and Ambition",
    "Seasons of Life",
    "The psychology of sideways",
    # Ch3: Compounding
    "Investment Philosophy",
    "Systems over Goals",
    "Taking Action",
    "Dopamine and Effort",
    "Level Up Mindset",
    "Money life as sport",
    "Success Mindset",
    "How to Win",
    "Sales Philosophy",
    # Ch4: Trust
    "Trust Equation",
    "PEACE Framework",
    "Explaining something is like playing catch",
    "Communication Tips",
    "Leadership Insights",
    "Management Principles",
    "Hold the Knife by the Handle",
    "Value of Advice",
    "Referral Framework",
    # Ch5: Legacy
    "Temporal Love",
    "Parenting Wisdom",
    "Kids aren't a barrier to our happiness. They are a doorway",
    "Family Values",
    "Legacy and Wealth Transfer",
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


def slugify(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def strip_version_notes(content: str) -> str:
    """Remove AI-assisted comments, up:: lines, and other metadata."""
    # Remove <!-- AI-assisted: ... --> comments (can span lines)
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    # Remove up:: lines
    content = re.sub(r'^up::.*$', '', content, flags=re.MULTILINE)
    # Remove empty lines at start
    content = content.lstrip('\n')
    # Collapse 3+ newlines to 2
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()


def convert_wikilinks(html: str) -> str:
    """Convert any remaining [[wikilinks]] in HTML to styled spans."""
    def replace_wikilink(m):
        name = m.group(1)
        slug = slugify(name)
        return f'<a href="#{slug}" class="ref">{name}</a>'
    return re.sub(r'\[\[([^\]]+)\]\]', replace_wikilink, html)


def build():
    md = mistune.create_markdown()
    sections = []
    toc_entries = []
    current_chapter = None

    for name in REFERENCED_FILES:
        # Find file
        candidates = list(SRC.glob(f"{name}.md"))
        if not candidates:
            print(f"WARNING: {name}.md not found, skipping")
            continue

        raw = candidates[0].read_text(encoding='utf-8')
        cleaned = strip_version_notes(raw)
        html_content = md(cleaned)
        html_content = convert_wikilinks(html_content)
        slug = slugify(name)
        chapter = CHAPTER_MAP.get(name, 0)

        # Insert chapter divider if needed
        if chapter != current_chapter:
            current_chapter = chapter
            ch_title = CHAPTER_TITLES.get(chapter, "")
            sections.append(f'''
    <div class="chapter-divider">
        <span class="chapter-divider-label">Chapter {chapter}: {ch_title}</span>
    </div>''')

        toc_entries.append((name, slug, chapter))
        sections.append(f'''
    <article class="note" id="{slug}">
        <h2>{name}</h2>
        {html_content}
        <a href="#top" class="back-to-top">&uarr; Back to top</a>
    </article>
    <hr>''')

    # Build TOC grouped by chapter
    toc_html = []
    cur_ch = None
    for name, slug, chapter in toc_entries:
        if chapter != cur_ch:
            if cur_ch is not None:
                toc_html.append('</ul>')
            cur_ch = chapter
            ch_title = CHAPTER_TITLES.get(chapter, "")
            toc_html.append(f'<h3>Chapter {chapter}: {ch_title}</h3><ul>')
        toc_html.append(f'<li><a href="#{slug}">{name}</a></li>')
    toc_html.append('</ul>')

    page = TEMPLATE.format(
        toc='\n'.join(toc_html),
        sections='\n'.join(sections),
        count=len([e for e in toc_entries]),
    )
    OUT.write_text(page, encoding='utf-8')
    print(f"Built {OUT} with {len(toc_entries)} reference notes")


TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Further Reading — Ari's Big Five</title>
    <meta name="description" content="Source notes from the Nexus vault referenced in Ari's Big Five.">
    <style>
        :root {{
            --text: #1a1a1a;
            --text-secondary: #555;
            --bg: #fafaf8;
            --bg-card: #fff;
            --accent: #2c5f2d;
            --accent-light: #e8f0e8;
            --border: #e0ddd5;
            --quote-bg: #f5f3ee;
            --quote-border: #c9a96e;
            --ref: #6b5b3e;
            --ref-bg: #f0ece3;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        html {{ scroll-behavior: smooth; font-size: 18px; }}

        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            color: var(--text);
            background: var(--bg);
            line-height: 1.75;
            -webkit-font-smoothing: antialiased;
        }}

        .hero {{
            background: linear-gradient(135deg, #2c5f2d, #1a3a1a);
            color: #fff;
            padding: 4rem 2rem 3rem;
            text-align: center;
        }}

        .hero h1 {{ font-size: 2.5rem; font-weight: 400; margin-bottom: 0.4rem; }}
        .hero .subtitle {{ font-style: italic; font-size: 1rem; opacity: 0.8; margin-bottom: 1rem; }}
        .hero .back-link {{ color: rgba(255,255,255,0.7); font-size: 0.9rem; }}
        .hero .back-link a {{ color: #fff; text-decoration: underline; }}

        .container {{ max-width: 720px; margin: 0 auto; padding: 0 1.5rem; }}

        .toc {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 2rem 2.5rem;
            margin: 2.5rem auto;
            max-width: 720px;
        }}

        .toc h2 {{
            font-family: 'Helvetica Neue', 'Arial', sans-serif;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--text-secondary);
            margin-bottom: 1rem;
        }}

        .toc h3 {{
            font-size: 0.9rem;
            color: var(--accent);
            margin: 1.2rem 0 0.4rem;
            font-family: 'Helvetica Neue', 'Arial', sans-serif;
        }}

        .toc ul {{ list-style: none; padding-left: 0.5rem; }}
        .toc li {{ margin-bottom: 0.25rem; font-size: 0.9rem; }}
        .toc a {{ color: var(--text); text-decoration: none; border-bottom: 1px solid transparent; transition: border-color 0.2s; }}
        .toc a:hover {{ border-bottom-color: var(--accent); }}

        .chapter-divider {{
            text-align: center;
            margin: 3rem 0 1rem;
            padding: 1rem 0;
        }}

        .chapter-divider-label {{
            font-family: 'Helvetica Neue', 'Arial', sans-serif;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: var(--accent);
            background: var(--accent-light);
            padding: 0.4em 1.2em;
            border-radius: 20px;
        }}

        .note {{
            max-width: 720px;
            margin: 2rem auto;
            padding: 0 1.5rem;
        }}

        .note h2 {{
            font-size: 1.6rem;
            font-weight: 400;
            margin-bottom: 1.5rem;
            color: var(--text);
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.5rem;
        }}

        .note h1 {{ font-size: 1.6rem; font-weight: 400; margin: 1.5rem 0 1rem; }}
        .note h3 {{ font-size: 1.15rem; font-weight: 700; margin: 2rem 0 0.75rem; }}
        .note h4 {{ font-size: 1rem; font-weight: 700; margin: 1.5rem 0 0.5rem; }}
        p {{ margin-bottom: 1.1rem; }}
        ul, ol {{ margin-bottom: 1.1rem; padding-left: 1.5rem; }}
        li {{ margin-bottom: 0.25rem; }}

        blockquote {{
            border-left: 3px solid var(--quote-border);
            background: var(--quote-bg);
            padding: 1rem 1.25rem;
            margin: 1.5rem 0;
            border-radius: 0 6px 6px 0;
            font-style: italic;
        }}

        blockquote p {{ margin-bottom: 0.5rem; }}
        blockquote p:last-child {{ margin-bottom: 0; }}

        .ref {{
            font-family: 'Helvetica Neue', 'Arial', sans-serif;
            font-size: 0.82rem;
            background: var(--ref-bg);
            color: var(--ref);
            padding: 0.15em 0.5em;
            border-radius: 3px;
            white-space: nowrap;
            font-weight: 500;
            text-decoration: none;
        }}

        .ref:hover {{ background: #e5dfd3; }}

        hr {{
            border: none;
            border-top: 1px solid var(--border);
            margin: 2rem auto;
            max-width: 720px;
        }}

        .back-to-top {{
            display: inline-block;
            margin-top: 1rem;
            font-family: 'Helvetica Neue', 'Arial', sans-serif;
            font-size: 0.8rem;
            color: var(--text-secondary);
            text-decoration: none;
        }}

        .back-to-top:hover {{ color: var(--accent); }}

        .footer {{
            text-align: center;
            padding: 2rem 1.5rem 3rem;
            color: var(--text-secondary);
            font-size: 0.85rem;
            max-width: 720px;
            margin: 0 auto;
        }}

        @media (max-width: 600px) {{
            html {{ font-size: 16px; }}
            .hero {{ padding: 3rem 1.5rem 2rem; }}
            .hero h1 {{ font-size: 1.8rem; }}
            .toc {{ padding: 1.5rem; }}
        }}
    </style>
</head>
<body id="top">

<header class="hero">
    <h1>Further Reading</h1>
    <p class="subtitle">{count} source notes from the Nexus vault</p>
    <p class="back-link"><a href="index.html">&larr; Back to Ari's Big Five</a></p>
</header>

<nav class="toc container">
    <h2>Source Notes</h2>
    {toc}
</nav>

{sections}

<footer class="footer">
    <p>These notes are from Tim's personal knowledge vault (TheNexus3.0). They represent years of collected wisdom, experience, and reflection.</p>
    <p><a href="index.html">&larr; Back to Ari's Big Five</a></p>
</footer>

</body>
</html>'''


if __name__ == '__main__':
    build()
