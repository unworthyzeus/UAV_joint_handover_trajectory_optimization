"""Check the compiled connectivity report and both experiment freezes."""
import hashlib
import json
import re
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    hashes = {}
    for manifest in ("configs/frozen_comparison_v1.json", "configs/frozen_connectivity_v2.json"):
        data = json.loads((ROOT / manifest).read_text())
        hashes[manifest] = {n: sha256(ROOT / n) == expected for n, expected in data["source_hashes"].items()}
        assert all(hashes[manifest].values())
    original = json.loads((ROOT / "configs/frozen_comparison_v1.json").read_text())
    dataset = sha256(ROOT / "dataset/Barcelona_dataset_January.h5")
    assert dataset == original["dataset_sha256"]
    source = (ROOT / "paper/connectivity.tex").read_text(encoding="utf-8")
    citations = []
    for match in re.finditer(r"\\cite(?:\[([^\]]*)\])?\{([^}]*)\}", source):
        if "thesis" in match[2].split(","):
            assert match[1] and re.search(r"pp?\.\s*~?\s*\d", match[1])
            citations.append({"line": source.count("\n", 0, match.start()) + 1, "locator": match[1]})
    pdf_path = ROOT / "paper/UAV_connectivity_repair_IEEE.pdf"
    pdf = pymupdf.open(pdf_path)
    review = ROOT / "outputs/connectivity_paper_review"
    review.mkdir(parents=True, exist_ok=True)
    fonts = {}
    text = ""
    for i, page in enumerate(pdf):
        text += page.get_text()
        page.get_pixmap(matrix=pymupdf.Matrix(1.25, 1.25)).save(review / f"page_{i+1}.png")
        for item in page.get_fonts(full=True):
            if item[0] not in fonts:
                font = pdf.extract_font(item[0])
                fonts[item[0]] = {"name": item[3], "type": item[2], "embedded": bool(font[3])}
    assert "??" not in text and "NaN" not in text and "nan%" not in text
    assert all(f["embedded"] and f["type"] != "Type3" for f in fonts.values())
    replay = json.loads((ROOT / "results/connectivity_experiment/replay_v2/audit.json").read_text())
    stats = json.loads((ROOT / "results/connectivity_experiment/analysis_v2/statistics.json").read_text())
    assert replay["exact_episode_matches"] == stats["total_evaluated_episodes"] == 5600
    checkpoints = list((ROOT / "results/connectivity_experiment/confirmatory_v2").glob("*_seed_*/checkpoint.pt"))
    assert len(checkpoints) == 10
    report = {"pdf_sha256": sha256(pdf_path), "pages": len(pdf), "fonts": fonts,
              "all_fonts_embedded_and_no_type3": True, "unresolved_reference_markers": False,
              "tfm_citation_count": len(citations), "tfm_citations": citations,
              "all_tfm_citations_have_printed_page_locators": True, "frozen_source_checks": hashes,
              "dataset_sha256": dataset, "dataset_matches_original": True,
              "final_checkpoint_count": len(checkpoints), "exact_replayed_episodes": 5600,
              "all_reported_successes_meet_sampled_constraints": stats["all_reported_successes_meet_sampled_constraints"],
              "render_directory": str(review), "visual_review": "Required separately after rendering"}
    output = ROOT / "results/connectivity_experiment/analysis_v2/artifact_audit.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pages": len(pdf), "fonts": len(fonts), "tfm_citations": len(citations),
                      "exact_replays": 5600, "both_freezes_unchanged": True, "dataset_unchanged": True}))


if __name__ == "__main__":
    main()
