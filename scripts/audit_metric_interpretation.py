"""Verify published metric interpretation against the unchanged initial results."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[1]
s=json.loads((root/'results/reward_comparison/analysis_v15/statistics.json').read_text())
text=(root/'README.md').read_text(encoding='utf-8')

def get_table(first):
    start=text.index('| '+first+' |'); end=text.index('\n\n',start)
    return [[v.strip() for v in row.strip('|').split('|')] for row in text[start:end].splitlines()]

table=get_table('Outcome, unit and preferred direction')
assert all(len(r)==6 for r in table)
rows={r[0]:r for r in table[2:]}
metrics=[('Arrival flight time (s)','time_s',1),('SINR (dB)','sinr_mean_db',1),
         ('Downlink interference (µW)','interference_mean_w',1e6),('Consumed energy proxy (kJ)','energy_proxy_j',.001),
         ('Executed handovers (count per flight)','handovers',1),('Transmission delay proxy (s)','delay_proxy_mean_s',1),
         ('Accumulated radio cost (dimensionless)','radio_cost_sum',1)]
count=0
for prefix,metric,scale in metrics:
    row=next(r for label,r in rows.items() if label.startswith(prefix+':'))
    for index,split in [(3,'test'),(4,'longer_test')]:
        c=s['contrasts'][f'full_minus_original_{split}'][metric]
        pair=' / '.join(f'{c[k]*scale:.3f}' for k in ['right_mean_on_common_success','left_mean_on_common_success'])
        assert pair in row[index],(prefix,pair,row[index])
        count+=2
completion=next(r for label,r in rows.items() if label.startswith('Joint mission'))
for index,split in [(3,'test'),(4,'longer_test')]:
    pair=' / '.join(f"{s['groups'][f'{arm}_{split}']['success_rate']*100:.1f}%" for arm in ['original','full'])
    assert completion[index]==pair
for prefix,reason in [('RSS first failures (flights)','connectivity'),('Buffer first failures (flights)','buffer')]:
    row=next(r for label,r in rows.items() if label.startswith(prefix+':'))
    for index,split in [(3,'test'),(4,'longer_test')]:
        pair=' / '.join(str(s['groups'][f'{arm}_{split}']['failure_counts'][reason]) for arm in ['original','full'])
        assert row[index]==pair+' out of 1,000'

paired=get_table('Metric')
for row,(prefix,metric,scale) in zip(paired[2:],[metrics[i] for i in [0,4,5,3,1,2,6]]):
    assert '; ' in row[0]
    expected=[]
    for split in ['test','longer_test']:
        c=s['contrasts'][f'full_minus_original_{split}'][metric]
        expected += [f'{c[k]*scale:.3f}' for k in ['right_mean_on_common_success','left_mean_on_common_success']]
    assert row[1:5]==expected

# Convert each retained source interference reading, preserving its approximate
# status and median interpretation rather than treating it as a new mean.
source_interference=next(r for label,r in rows.items() if label.startswith('Source uplink interference'))
interference=next(r for label,r in rows.items() if label.startswith('Downlink interference'))
source_dbm=[[-35,-28],[-40,-40,-38]]
for col,values in zip([1,2],source_dbm):
    converted=' / '.join(f'≈{1000*10**(value/10):.3f}' for value in values)
    assert converted in source_interference[col]
assert source_interference[3:5]==['Not evaluated','Not evaluated']
assert interference[1:3]==['NR','NR']
paired_interference=next(r for r in paired[2:] if r[0].startswith('Downlink interference'))
assert 'downlink result NR' in paired_interference[-1]
assert '≈' not in paired_interference[-1]
assert 'dBm' not in ' '.join(interference+source_interference+paired_interference)
energy=next(r for label,r in rows.items() if label.startswith('Consumed energy proxy'))
source_energy=next(r for label,r in rows.items() if label.startswith('Source remaining energy display'))
assert 'kW' not in ' '.join(energy) and 'kJ' not in ' '.join(source_energy)
assert all(cell=='NR' for cell in energy[1:3])
assert all('NC:' in cell for cell in source_energy[3:5])
source_handovers=next(r for label,r in rows.items() if label.startswith('Source handover CDF'))
assert all('NC:' in cell for cell in source_handovers[3:5])
assert 'less negative' not in text and 'more negative' not in text
direction_tables=[table,paired,get_table('Metric and preferred direction'),get_table('First failure')]
direction_rows=0
for metric_table in direction_tables:
    for row in metric_table[2:]:
        assert re.search(r'\b(higher|lower)\b.*\bis better\b',row[0]),row[0]
        direction_rows+=1
for header in ['New standard success','New longer success','Standard joint success','Longer joint success']:
    assert '| '+header+' (higher is better) |' in text
assert '| Observed success difference (higher is better for V2) |' in text

for split in ['test','longer_test']:
    c=s['contrasts'][f'full_minus_original_{split}']
    for metric in ['handovers','delay_proxy_mean_s','energy_proxy_j','radio_cost_sum']:
        assert f"{abs(c[metric]['relative_difference_pct']):.1f}%" in text
    assert f"{abs(c['sinr_mean_db']['paired_mean_difference']):.3f}" in text

files=['README.md','docs/README.md','docs/45_metric_directions_and_interpretation.md','docs/50_clear_metric_descriptions_and_units.md',
       'docs/46_service_reward_development_protocol.md']
link_count=0
for file in files:
    p=root/file; t=p.read_text(encoding='utf-8'); block=[]
    for line in t.splitlines()+['']:
        if line.startswith('|'): block.append(line.count('|'))
        elif block:
            assert len(set(block))==1,(file,block)
            block=[]
        if line.startswith('|'):
            assert not ('uplink' in line.lower() and 'downlink' in line.lower()),(file,line)
    assert t.count('```')%2==0,file
    for url in re.findall(r'\[[^\]]+\]\(([^)]+)\)',t):
        if '://' in url: continue
        path=url.split('#')[0]
        assert (p.parent/path).exists() if path else True,(file,url)
        link_count+=1

assert text.count('Historical V1 was')==1
prior=subprocess.check_output(['git','show','d53b293:results/reward_comparison/analysis_v15/statistics.json'],cwd=root)
assert prior==(root/'results/reward_comparison/analysis_v15/statistics.json').read_bytes()
out={'source_comparison_current_means_checked':count,'paired_table_means_checked':28,
     'source_interference_unit_conversions_checked':5,'incompatible_source_quantities_separated':True,
     'uplink_and_downlink_rows_separate':True,'missing_direction_results_not_invented':True,
     'result_rows_with_explicit_better_direction':direction_rows,
     'success_rates_checked':4,'first_failure_counts_checked':8,
     'derived_changes_checked':10,'local_links_checked':link_count,
     'existing_statistics_unchanged':True,'all_source_plot_readings_remain_approximate':True}
(root/'results/service_reward_v21/analysis/interpretation_checks.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
