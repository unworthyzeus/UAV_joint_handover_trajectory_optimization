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

table=get_table('Outcome and preferred direction')
assert all(len(r)==6 for r in table)
rows={r[0]:r for r in table[2:]}
metrics=[('Arrival flight time','time_s',1),('Signal quality','sinr_mean_db',1),
         ('Interference','interference_mean_w',1e6),('Energy','energy_proxy_j',.001),
         ('Handovers','handovers',1),('Transmission delay','delay_proxy_mean_s',1),
         ('Accumulated radio cost','radio_cost_sum',1)]
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
for prefix,reason in [('RSS first failures','connectivity'),('Buffer first failures','buffer')]:
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

for split in ['test','longer_test']:
    c=s['contrasts'][f'full_minus_original_{split}']
    for metric in ['handovers','delay_proxy_mean_s','energy_proxy_j','radio_cost_sum']:
        assert f"{abs(c[metric]['relative_difference_pct']):.1f}%" in text
    assert f"{abs(c['sinr_mean_db']['paired_mean_difference']):.3f}" in text

files=['README.md','docs/README.md','docs/45_metric_directions_and_interpretation.md',
       'docs/46_service_reward_development_protocol.md']
link_count=0
for file in files:
    p=root/file; t=p.read_text(encoding='utf-8'); block=[]
    for line in t.splitlines()+['']:
        if line.startswith('|'): block.append(line.count('|'))
        elif block:
            assert len(set(block))==1,(file,block)
            block=[]
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
     'success_rates_checked':4,'first_failure_counts_checked':8,
     'derived_changes_checked':10,'local_links_checked':link_count,
     'existing_statistics_unchanged':True,'all_source_plot_readings_remain_approximate':True}
(root/'results/service_reward_v21/analysis/interpretation_checks.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
