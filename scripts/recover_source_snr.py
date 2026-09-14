"""Digitize source SNR medians and report an explicitly conditional correction."""
import hashlib
from io import BytesIO
import json
from pathlib import Path

import fitz
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/thesis_metrics_v22/analysis'
SOURCE = ROOT/'sources/UAV_Bermudez_Granados_2026_MSc_thesis.pdf'


def recover():
    result = {
        'scope': 'Source plot digitization, not source raw data or a verified corrected result.',
        'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'source_equation_printed_page': 10,
        'noise_explanation_printed_page': 14,
        'noise_table_printed_page': 15,
        'bandwidth_hz': 180000*8,
        'source_initial_noise_value': -174.0,
        'source_final_noise_dbm': -112.41,
        'noise_figure_db': 9.0,
        'conditional_offset_db': 61.59,
        'bandwidth_log_term_db': float(10*np.log10(180000*8)),
        'correction_confirmed': False,
        'plot_reading_tolerance_db': 1.0,
        'tolerance_definition': 'Conservative pixel, calibration and integer rounding allowance; not a statistical interval and not uncertainty about the cause.',
        'figures': [],
    }
    with fitz.open(SOURCE) as pdf:
        explanation = pdf[15].get_text()
        assert '-174' in explanation and '-112.41' in explanation
        for page, xref, policies in (
            (18, 44, [('Equal PPO', 'purple'), ('Greedy', 'red')]),
            (20, 60, [('Transmission delay PPO', 'purple'), ('Interference PPO', 'green'), ('Handover PPO', 'red')]),
        ):
            assert xref in [r[0] for r in pdf[page+1].get_images(full=True)]
            embedded = pdf.extract_image(xref)['image']
            a = np.asarray(Image.open(BytesIO(embedded)).convert('RGB')).astype(int)
            assert a.shape == (480, 640, 3)
            # Tick labels and CDF endpoints were checked on the complete source pages.
            ticks = np.flatnonzero(np.all(a[425] < 100, axis=1))
            ticks = ticks[(ticks >= 100) & (ticks <= 540)]
            assert len(ticks) == 5
            values = np.array([40., 60., 80., 100., 120.])
            slope, intercept = np.polyfit(ticks, values, 1)
            f = {'printed_page': page, 'pdf_viewer_page': page+2, 'image_xref': xref,
                 'embedded_image_sha256': hashlib.sha256(embedded).hexdigest(),
                 'x_tick_pixels': ticks.tolist(), 'x_tick_values_db': values.tolist(),
                 'cdf_zero_y_pixel': 422, 'cdf_one_y_pixel': 20,
                 'median_scan_rows': [219, 220, 221, 222, 223],
                 'calibration_max_residual_db': float(np.max(np.abs(slope*ticks+intercept-values))),
                 'policies': []}
            for name, color in policies:
                roi = a[219:224]
                r, g, b = (roi[:, :, i] for i in range(3))
                masks = {
                    # This also detects purple visible through red antialiasing in Fig. 8.
                    'purple': (b-g > 30) & (r-g > 60) & (g < 130),
                    'red': (r > 230) & (g < 100) & (b < 100),
                    'green': (r > 70) & (r < 190) & (g > 230) & (b > 120) & (b < 220),
                }
                points = [np.flatnonzero(row).tolist() for row in masks[color]]
                assert all(points) and all(500 < x < 610 for row in points for x in row)
                centers = [float(np.mean(row)) for row in points]
                assert max(centers)-min(centers) <= 1
                pixel_estimate = float(slope*np.mean(centers)+intercept)
                rounded = float(round(pixel_estimate))
                f['policies'].append({
                    'policy': name, 'color': color, 'trace_x_pixels_by_row': points,
                    'pixel_estimate_db': pixel_estimate, 'reported_plot_median_db': rounded,
                    'conditional_corrected_median_db': round(rounded-61.59, 2),
                    'purple_red_overlap': page == 20 and color == 'purple',
                })
            result['figures'].append(f)
    return result


def write_report():
    result = recover()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'source_snr_recovery.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    lines = ['### Recovering the Original Thesis SNR', '',
        '**The actual corrected source result is still unverified.** We recovered the plot medians from the '
        'original embedded images. A specific possible explanation is omission of the noise bandwidth conversion: '
        'the thesis starts from −174 and explicitly gives −112.41 dBm after accounting for 180 kHz × 8 '
        '[printed p. 14, Sec. 6.1; p. 15, Table 3]. If its plotted calculation used the initial value instead, '
        'each SNR would be too high by 61.59 dB. The resulting conditional estimates are:', '',
        '| Original thesis policy (SNR: higher is better) | Plotted CDF median (dB) | Conditional corrected CDF median (dB) | Source location |',
        '| --- | ---: | ---: | --- |']
    for figure in result['figures']:
        for row in figure['policies']:
            lines.append(f"| {row['policy']} | ≈{row['reported_plot_median_db']:.0f} | "
                         f"≈{row['conditional_corrected_median_db']:.1f} | Printed p. {figure['printed_page']}, "
                         f"Fig. {6 if figure['printed_page'] == 18 else 8}. |")
    lines += ['', '**Conditional calculation:** `corrected median = plotted median − 61.59 dB`. '
        'Allow approximately ±1 dB for image reading and rounding; this is not a confidence interval. '
        'It does not quantify uncertainty about the assumed error. The figure has no raw samples or clear CDF '
        'aggregation specification, and the linked source repository still returned 404 on 14 September 2026. '
        '**These are estimates under a hypothesis, not recovered actual measurements.**', '',
        'V2.2 has a measured pooled sample median of 65.41 dB on both fresh splits. The conditional greedy '
        'estimate is also about 65.4 dB, so even this hypothesis does not establish superiority over the thesis. '
        'Routes, failure handling and aggregation are unmatched. The verified source result rows below remain '
        'NR; the conditional values belong only in this explicitly labeled table.', '',
        '[Full derivation, pixel extraction and limitations](docs/57_source_snr_recovery.md).', '']
    (OUT/'source_snr_readme_fragment.md').write_text('\n'.join(lines), encoding='utf-8')
    return result


if __name__ == '__main__':
    print(json.dumps(write_report(), indent=2))
