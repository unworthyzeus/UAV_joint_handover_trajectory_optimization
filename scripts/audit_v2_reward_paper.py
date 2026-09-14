"""Check and render the current V2 paper and verify the reward comparison."""
import hashlib
import json
import re
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inputs = []

    def visit(path):
        if path in inputs:
            return
        inputs.append(path)
        for name in re.findall(r"\\input\{([^}]+)\}", path.read_text(encoding="utf-8")):
            visit(path.parent / name)

    visit(ROOT / "paper/unified.tex")
    citations = []
    for path in inputs:
        source = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\\cite(?:\[([^\]]*)\])?\{([^}]*)\}", source):
            if "thesis" in match[2].split(","):
                assert match[1] and re.search(r"pp?\.\s*~?\s*\d", match[1])
                citations.append({"file": path.relative_to(ROOT).as_posix(),
                                  "line": source.count("\n", 0, match.start()) + 1,
                                  "locator": match[1]})
    freezes = {}
    for name in ("frozen_comparison_v1.json", "frozen_connectivity_v2.json", "frozen_reward_comparison_v15.json",
                 "frozen_service_reward_v21.json", "frozen_thesis_metrics_v22.json"):
        manifest = json.loads((ROOT / "configs" / name).read_text())
        freezes[name] = {p: digest(ROOT / p) == value
                         for p, value in manifest["source_hashes"].items()}
        assert all(freezes[name].values())

    pdf_path = ROOT / "paper/UAV_joint_reward_connectivity_IEEE.pdf"
    pdf = pymupdf.open(pdf_path)
    review = ROOT / "outputs/unified_paper_review"
    review.mkdir(parents=True, exist_ok=True)
    fonts = {}
    page_texts = []
    bounds = []
    for i, page in enumerate(pdf):
        page_texts.append(page.get_text())
        page.get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3)).save(review / f"page_{i + 1}.png")
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    x0, y0, x1, y1 = span["bbox"]
                    if x0 < 0 or y0 < 0 or x1 > page.rect.width or y1 > page.rect.height:
                        bounds.append({"page": i + 1, "text": span["text"]})
        for item in page.get_fonts(full=True):
            if item[0] not in fonts:
                fonts[item[0]] = {"name": item[3], "type": item[2],
                                  "embedded": bool(pdf.extract_font(item[0])[3])}
    text = "\n".join(page_texts)
    assert "??" not in text and "NaN" not in text and "\ufffd" not in text
    assert not bounds, bounds
    assert all(x["embedded"] and x["type"] != "Type3" for x in fonts.values())
    assert "Guillem Moreno Garcia" in text and "Evgenii Vinogradov" in text
    assert not re.search(r"\bV1(?!\.5)\b|Study I\b", text), "Historical V1 material remains"
    replay = json.loads((ROOT / "results/reward_comparison/replay_v15/audit.json").read_text())
    assert replay["exact_episode_matches"] == 7600
    weights = json.loads((ROOT / "models/checkpoint_manifest.json").read_text())
    assert weights["count"] == 15
    assert all(digest(ROOT / row["path"]) == row["sha256"] for row in weights["checkpoints"])
    statistics = json.loads((ROOT / "results/reward_comparison/analysis_v15/statistics.json").read_text())
    assert statistics["total_evaluated_episodes"] == 7600
    macro_source = (ROOT / "paper/v15_macros.tex").read_text()
    for arm, prefix in (("original", "Original"), ("full", "Full"), ("arrival", "Arrival"), ("straight_radio", "Radio")):
        for split, suffix in (("test", "Std"), ("longer_test", "Long")):
            value = f"{100 * statistics['groups'][arm + '_' + split]['success_rate']:.1f}"
            assert f"\\newcommand{{\\{prefix}{suffix}}}{{{value}}}" in macro_source
            assert value in text
    assert statistics["primary_positive_completion_evidence"] is False
    service_weights = json.loads((ROOT / "models/service_reward_manifest.json").read_text())
    assert service_weights["count"] == 5
    assert all(digest(ROOT / row["path"]) == row["sha256"] for row in service_weights["checkpoints"])
    service = json.loads((ROOT / "results/service_reward_v21/analysis/statistics.json").read_text())
    service_replay = json.loads((ROOT / "results/service_reward_v21/replay/audit.json").read_text())
    assert service["total_evaluated_episodes"] == service_replay["exact_episode_matches"] == 18000
    assert "54012/54013" in text and "V2.1" in text
    for arm in ("original", "full", "service", "straight_radio", "joint_mpc", "joint_lookahead"):
        for split in ("test", "longer_test"):
            assert f"{100 * service['groups'][arm + '_' + split]['success_rate']:.2f}" in text
    service_primary = service["contrasts"]["service_minus_full_test"]
    service_interval = service_primary["success_difference_ci95_pp"]
    assert f"{service_primary['success_difference_pp']:+.3f}" in text
    assert all(f"{value:.3f}" in text for value in service_interval)
    guard = json.loads((ROOT / "results/thesis_metrics_v22/analysis/statistics.json").read_text())
    guard_replay = json.loads((ROOT / "results/thesis_metrics_v22/replay_audit.json").read_text())
    assert guard['total_evaluated_episodes'] == guard_replay['exact_episode_and_metric_matches'] == 23000
    assert guard_replay['all_sample_arrays_exact']
    assert '55012/55013' in text and 'V2.2' in text and '78.41' in text
    for arm in ('original', 'full', 'service', 'guard', 'straight_radio', 'joint_mpc', 'joint_lookahead'):
        for split in ('test', 'longer_test'):
            assert f"{100*guard['groups'][arm+'_'+split]['success_rate']:.2f}" in text
    guard_seeds = (ROOT / 'paper/v22_seed_table.tex').read_text(encoding='utf-8')
    for i, seed in enumerate(range(2101, 2106)):
        cells = [' / '.join(f"{100*guard['groups'][arm+'_'+split]['per_seed_success_rates'][i]:.1f}"
                           for split in ('test', 'longer_test')) for arm in ('original', 'full', 'service', 'guard')]
        assert str(seed)+' & '+' & '.join(cells)+r'\\' in guard_seeds
    for split in ('test', 'longer_test'):
        contrast = guard['contrasts']['guard_minus_full_'+split]
        assert f"{contrast['success_difference_pp']:+.3f}" in text
        assert all(f"{value:.3f}" in text for value in contrast['success_difference_ci95_pp'])
    seed_table = (ROOT / "paper/v21_seed_table.tex").read_text(encoding="utf-8")
    for i, seed in enumerate([2101, 2102, 2103, 2104, 2105]):
        cells = [' / '.join(f"{100 * service['groups'][arm + '_' + split]['per_seed_success_rates'][i]:.1f}"
                           for split in ("test", "longer_test")) for arm in ("original", "full", "service")]
        assert str(seed) + ' & ' + ' & '.join(cells) + r'\\' in seed_table
    illustration_path = ROOT / "results/reward_comparison/analysis_v15/long_route_illustration.json"
    illustration = json.loads(illustration_path.read_text())
    selection_path = ROOT / "configs/long_route_illustration_v15.json"
    assert illustration["selection"] == json.loads(selection_path.read_text())
    assert illustration["selection_sha256"] == digest(selection_path)
    assert illustration["source_sha256"] == digest(ROOT / "scripts/replay_long_route_illustration.py")
    assert illustration["statistics_sha256"] == digest(ROOT / "results/reward_comparison/analysis_v15/statistics.json")
    assert illustration["exact_episode_matches"] == 600
    assert len(illustration["station_ids"]) == len(illustration["station_positions_m"]) == 87
    scenarios = json.loads((ROOT / "configs/reward_comparison_scenarios_v15.json").read_text())["longer_test"]
    longest = min(scenarios, key=lambda r: (-sum((g-s)**2 for s, g in zip(r["start"], r["goal"])), r["id"]))
    assert longest == illustration["scenario"]
    assert longest["id"] in text and "1,784.7" in text
    for arm, row in illustration["arms"].items():
        assert row["record_sha256"] == digest(ROOT / row["record_path"])
        if row["checkpoint_path"]:
            assert row["checkpoint_sha256"] == digest(ROOT / row["checkpoint_path"])
        original = json.loads((ROOT / row["record_path"]).read_text())["episodes"]
        assert row["episode"] == original[illustration["selection"]["scenario_index"]]
        assert row["exact_episode_matches"] == len(original)
    archive = ROOT / "results/reward_comparison/analysis_v15/previous_222m_illustration"
    for name, expected in json.loads((archive / "provenance.json").read_text())["files"].items():
        assert digest(archive / name) == expected
    normalized_text = re.sub(r"\s+", " ", re.sub(r"-\s*\n\s*", "", text))
    assert "does not establish improved completion" in normalized_text
    assert "same Barcelona ray tracing dataset as the original thesis" in normalized_text
    current_sources = " ".join(p.read_text(encoding="utf-8") for p in inputs)
    current_sources = re.sub(r"\s+", " ", current_sources)
    for stale in ("exact source dataset version identity", "Exact dataset version and sentinel",
                  "does not prove an identical original dataset version"):
        assert stale not in current_sources, stale
    for start in range(0, len(pdf), 6):
        sheet = Image.new("RGB", (1224, 3 * 558), "#cccccc")
        draw = ImageDraw.Draw(sheet)
        for offset, i in enumerate(range(start, min(start + 6, len(pdf)))):
            thumb = Image.open(review / f"page_{i + 1}.png").convert("RGB")
            thumb.thumbnail((596, 530))
            x, y = (offset % 2) * 612, (offset // 2) * 558
            sheet.paste(thumb, (x, y + 22))
            draw.text((x + 8, y + 5), f"Page {i + 1}", fill="black")
        sheet.save(review / f"contact_{start // 6 + 1}.png")
    build = json.loads((ROOT / "paper/build_unified/compile_report.json").read_text(encoding="utf-8-sig"))
    log = build["attempts"][-1]["log"]
    assert build["attempts"][-1]["exitCode"] == 0
    final_pass = log.split("Rerunning TeX")[-1]
    assert not re.search(r"Overfull|undefined|Missing character", final_pass)
    report_path = ROOT / "results/reward_comparison/analysis_v15/paper_audit.json"
    previous = json.loads(report_path.read_text()) if report_path.exists() else {}
    report = {"pdf": pdf_path.relative_to(ROOT).as_posix(), "pdf_sha256": digest(pdf_path),
              "pages": len(pdf), "fonts": fonts, "all_fonts_embedded_and_no_type3": True,
              "no_unresolved_references_or_overfull_boxes": True, "text_outside_page": bounds,
              "tfm_citation_count": len(citations), "tfm_citations": citations,
              "source_hashes": {p.relative_to(ROOT).as_posix(): digest(p) for p in inputs},
              "frozen_sources_match": freezes,
              "statistic_hashes": {p: digest(ROOT / p) for p in (
                  "results/reward_comparison/analysis_v15/statistics.json",
                  "models/checkpoint_manifest.json",
                  "results/reward_comparison/replay_v15/audit.json",
                  "results/service_reward_v21/analysis/statistics.json",
                  "models/service_reward_manifest.json",
                  "results/service_reward_v21/replay/audit.json",
                  "results/thesis_metrics_v22/analysis/statistics.json",
                  "results/thesis_metrics_v22/replay_audit.json",
                  "results/thesis_metrics_v22/initial_replay/audit.json")},
              "guard_followup": {"episodes": 23000, "new_checkpoints": 0,
                  "per_seed_success_values_checked": 40,
                  "primary_completion_improvement": guard['primary_completion_improvement'],
                  "initial_recovered_episodes": 4000,
                  "report_builder_sha256": digest(ROOT / 'scripts/build_thesis_metrics_report.py')},
              "service_followup": {"episodes": 18000, "checkpoint_count": 5,
                  "per_seed_success_values_checked": 30,
                  "primary_completion_improvement": service["primary_completion_improvement"],
                  "primary_completion_and_delay_gate": service["primary_completion_and_delay_gate"],
                  "report_builder_sha256": digest(ROOT / "scripts/build_service_reward_report.py")},
              "visual_review": "Required separately after rendering",
              "dataset_identity": "Same dataset as the original thesis, confirmed by the researcher who supplied it; see note 43.",
              "long_route_illustration": {"scenario_id": longest["id"], "distance_m": illustration["selection"]["distance_m"],
                  "exact_existing_episode_matches": 600, "statistics_unchanged": True,
                  "artifact_hashes": {p: digest(ROOT / p) for p in (
                      "configs/long_route_illustration_v15.json", "scripts/replay_long_route_illustration.py",
                      "scripts/build_long_route_figures.py", "results/reward_comparison/analysis_v15/long_route_illustration.json",
                      "results/reward_comparison/analysis_v15/reward_comparison_example.pdf",
                      "results/reward_comparison/analysis_v15/reward_comparison_diagnostics.pdf")}},
              "scope": "One paper with the initial V1.5/V2 comparison, separate V2.1 reward and V2.2 supervisor studies, and source metric recovery. Historical V1 excluded; all outcomes retained."}
    if previous.get("pdf_sha256") == report["pdf_sha256"]:
        report["visual_review"] = previous.get("visual_review", report["visual_review"])
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pages": len(pdf), "tfm_citations": len(citations),
                      "fonts": len(fonts), "all_five_freezes_match": True,
                      "visual_review": report["visual_review"]}))


if __name__ == "__main__":
    main()
