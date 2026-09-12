"""Check pinpoint TFM citations and unchanged frozen experiment sources.

This checks citation structure, not semantic source support. Source page,
equation, and table content was manually reviewed for note 25.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    citations = []
    for name in ('paper/main.tex', 'paper/thesis_comparison.tex'):
        source = (ROOT / name).read_text(encoding='utf-8')
        for match in re.finditer(r'\\cite(?:\[([^\]]*)\])?\{([^}]*)\}', source):
            if 'thesis' not in match[2].split(','):
                continue
            locator = match[1]
            assert locator and re.search(r'pp?\.\s*~?\s*\d', locator), (
                f'TFM citation lacks a printed page: {name}:{source.count(chr(10), 0, match.start()) + 1}'
            )
            citations.append({'file': name,
                              'line': source.count('\n', 0, match.start()) + 1,
                              'locator': re.sub(r'\s+', ' ', locator)})
    assert citations, 'No TFM citations found'
    frozen = json.loads((ROOT / 'configs/frozen_comparison_v1.json').read_text())
    hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
              for name, expected in frozen['source_hashes'].items()}
    assert all(hashes.values()), 'A frozen experiment source changed'
    report = {'printed_to_pdf_page_offset': 2,
              'citation_count': len(citations),
              'all_tfm_citations_have_page_locators': True,
              'citations': citations, 'frozen_hashes_match': hashes,
              'semantic_review_record': 'docs/25_exact_changes_from_tfm.md',
              'scope': 'Structural citation and frozen source checks; content support requires source review'}
    out = ROOT / 'results/tables/tfm_traceability_audit.json'
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'{len(citations)} TFM citations have page locators; all frozen source hashes match.')


if __name__ == '__main__':
    main()
