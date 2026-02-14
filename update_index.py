"""
Update index.html: convert ref spans to links and add Further Reading section.
"""

import re
from pathlib import Path

INDEX = Path(__file__).parent / "index.html"

# Map display names to their slugs in references.html
# Some vault filenames differ from display names (e.g. "Ad astra" vs "Ad Astra")
SLUG_OVERRIDES = {
    "Ad Astra": "ad-astra",
    "Kids aren't a barrier to our happiness. They are a doorway.": "kids-aren-t-a-barrier-to-our-happiness-they-are-a-doorway",
}


def slugify(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def get_slug(name: str) -> str:
    return SLUG_OVERRIDES.get(name, slugify(name))


def update():
    html = INDEX.read_text(encoding='utf-8')

    # Convert <span class="ref">Name</span> to <a href="references.html#slug" class="ref">Name</a>
    def replace_ref(m):
        name = m.group(1)
        slug = get_slug(name)
        return f'<a href="references.html#{slug}" class="ref">{name}</a>'

    html = re.sub(r'<span class="ref">([^<]+)</span>', replace_ref, html)

    # Add .ref a styles if not present
    if 'a.ref' not in html and '.ref:hover' not in html:
        html = html.replace(
            '.ref {',
            '.ref {\n            text-decoration: none;\n            transition: background 0.2s;'
        )
        # Add hover state
        style_insert = '''

        .ref:hover {
            background: #e5dfd3;
        }

        a.ref {
            text-decoration: none;
        }
'''
        html = html.replace('/* --- Blockquotes ---', style_insert + '/* --- Blockquotes ---')

    # Add Further Reading section before the footer
    further_reading = '''
<!-- ============ FURTHER READING ============ -->
<section class="conclusion" id="further-reading">
    <h2>Further Reading</h2>
    <p>The chapters above draw on 43 source notes from the Nexus vault. Each contains Tim's original thinking, enriched with research and cross-references. They are the raw material from which this thesis was composed.</p>
    <p style="text-align: center; margin: 2rem 0;"><a href="references.html" style="font-family: 'Helvetica Neue', Arial, sans-serif; background: #2c5f2d; color: #fff; padding: 0.75em 2em; border-radius: 6px; text-decoration: none; font-size: 0.95rem; display: inline-block;">Read the source notes &rarr;</a></p>
</section>

<!-- ============ FOOTER ============ -->'''

    html = html.replace('<!-- ============ FOOTER ============ -->', further_reading)

    # Also add Further Reading to the TOC
    html = html.replace(
        '<li><a href="#conclusion">Conclusion: The Diamond</a></li>',
        '<li><a href="#conclusion">Conclusion: The Diamond</a></li>\n        <li><a href="#further-reading">Further Reading</a> <span class="toc-sub">\u2014 43 source notes from the vault</span></li>'
    )

    INDEX.write_text(html, encoding='utf-8')
    print("Updated index.html with links and Further Reading section")


if __name__ == '__main__':
    update()
