"""Check the complete V2.1 delivery without changing experiment outcomes."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def tables(text):
    result=[];block=[]
    for line in text.splitlines()+['']:
        if line.startswith('|'):
            block.append([v.strip() for v in line.strip('|').split('|')])
        elif block:
            assert len(block)>=2 and len({len(r) for r in block})==1
            result.append(block);block=[]
    return result


def main():
    s=json.loads((ROOT/'results/service_reward_v21/analysis/statistics.json').read_text())
    frozen={}
    for name in ['frozen_comparison_v1.json','frozen_connectivity_v2.json','frozen_reward_comparison_v15.json','frozen_service_reward_v21.json']:
        d=json.loads((ROOT/'configs'/name).read_text())
        frozen.update(d['source_hashes'])
        for p,h in d.get('reused_checkpoint_hashes',{}).items(): assert sha(ROOT/p)==h,p
    for p,h in frozen.items(): assert sha(ROOT/p)==h,p
    models=[]
    for name in ['checkpoint_manifest.json','service_reward_manifest.json']:
        d=json.loads((ROOT/'models'/name).read_text());models+=d['checkpoints']
        for r in d['checkpoints']:
            assert sha(ROOT/r['path'])==r['sha256'] and (ROOT/r['path']).stat().st_size==r['bytes'],r['path']
    assert len(models)==20
    replay=json.loads((ROOT/'results/service_reward_v21/replay/audit.json').read_text())
    assert replay['exact_episode_matches']==18000
    for p in (ROOT/'results/service_reward_v21/confirmatory').glob('*/*.json'):
        if p.stem not in ['test','longer_test']: continue
        original=json.loads(p.read_text())['episodes']
        repeat=json.loads((ROOT/'results/service_reward_v21/replay'/p.relative_to(ROOT/'results/service_reward_v21/confirmatory')).read_text())['episodes']
        assert original==repeat,p
    for p in (ROOT/'results/service_reward_v21/confirmatory').glob('*_test.json'):
        assert json.loads(p.read_text())['episodes']==json.loads((ROOT/'results/service_reward_v21/replay'/p.name).read_text())['episodes'],p
    readme=(ROOT/'README.md').read_text(encoding='utf-8'); ts=tables(readme)
    assert all(any('original' in c.lower() for c in t[0]) for t in ts)
    completion=next(t for t in ts if t[0][1]=='New standard success (higher is better)')
    arms=['service','full','original','straight_radio','joint_mpc','joint_lookahead']
    for row,arm in zip(completion[2:],arms):
        for i,split in [(1,'test'),(2,'longer_test')]:
            assert row[i]==f"{100*s['groups'][arm+'_'+split]['success_rate']:.2f}%"
    paired=next(t for t in ts if t[0][0]=='Metric and preferred direction'
                and 'V2.1' in t[0][1])
    metrics=[('time_s',1),('delay_proxy_mean_s',1),('handovers',1),('energy_proxy_j',.001),('sinr_mean_db',1)]
    for row,(metric,scale) in zip(paired[2:],metrics):
        for ix,split in [(1,'test'),(3,'longer_test')]:
            d=s['contrasts']['service_minus_full_'+split][metric]
            assert row[ix]==' / '.join(f'{d[k]*scale:.3f}' for k in ['right_mean_on_common_success','left_mean_on_common_success'])
            expected=f"{d['paired_mean_difference']*scale:+.3f} ["+', '.join(f'{v*scale:.3f}' for v in d['difference_ci95'])+']'
            assert row[ix+1]==expected
    # Preserve the completed initial study exactly, including source figure assets.
    retained=['results/reward_comparison/analysis_v15/statistics.json',
              'results/reward_comparison/analysis_v15/reward_comparison_example.pdf',
              'results/reward_comparison/analysis_v15/reward_comparison_diagnostics.pdf',
              'results/reward_comparison/analysis_v15/reward_comparison_success.pdf']
    for p in retained:
        expected=subprocess.check_output(['git','show','d53b293:'+p],cwd=ROOT)
        assert (ROOT/p).read_bytes()==expected,p
    paths=['README.md','docs/README.md','docs/12_task_status.md','docs/13_logbook.md',
           'docs/35_dataset_and_model_setup.md','paper/README.md']
    paths += [p.relative_to(ROOT).as_posix() for p in (ROOT/'docs').glob('4[5-9]_*.md')]
    paths += ['docs/50_clear_metric_descriptions_and_units.md']
    links=0
    for name in paths:
        p=ROOT/name;t=p.read_text(encoding='utf-8');tables(t)
        assert t.count('```')%2==0,name
        for u in re.findall(r'\[[^\]]*\]\(([^)]+)\)',t):
            if '://' in u: continue
            target,_,anchor=unquote(u).partition('#')
            q=(p.parent/target).resolve() if target else p
            assert q.exists(),(name,u)
            if anchor and q.suffix=='.md':
                headings=re.findall(r'^#+ (.+)$',q.read_text(encoding='utf-8'),re.M)
                slugs=[re.sub(r'[^\w\s-]','',h.lower()).replace(' ','-') for h in headings]
                assert anchor in slugs,(name,u)
            links+=1
    paper=json.loads((ROOT/'results/reward_comparison/analysis_v15/paper_audit.json').read_text())
    assert sha(ROOT/'paper/UAV_joint_reward_connectivity_IEEE.pdf')==paper['pdf_sha256']
    assert paper['visual_review'].startswith('Passed')
    for p,h in paper['source_hashes'].items(): assert sha(ROOT/p)==h,p
    test_log=ROOT/'results/service_reward_v21/analysis/implementation_tests.txt'
    assert '88 passed' in test_log.read_text()
    assert not subprocess.check_output(['git','ls-files','*.h5','*.hdf5'],cwd=ROOT).strip()
    assert readme.count('Historical V1 was')==1
    report={'scope':'V2.1 component checks within the current README and paper; V2.2 and V2.3 have separate delivery audits.',
            'current_delivery_validation':'results/signal_guard_v23/analysis/delivery_validation.json',
            'frozen_source_protocol_files_verified':len(frozen),'checkpoint_count':len(models),
            'checkpoint_bytes':sum(r['bytes'] for r in models),'implementation_tests_passed':88,
            'implementation_test_log_sha256':sha(test_log),
            'initial_statistics_and_figures_unchanged':True,'fresh_evaluations':18000,'exact_fresh_replays':18000,
            'readme_tables_with_original_comparisons':len(ts),'new_success_rates_checked':12,
            'new_paired_means_checked':20,'new_paired_intervals_checked':10,'local_links_checked':links,
            'paper_pages':paper['pages'],'paper_sha256':paper['pdf_sha256'],'paper_visual_review':paper['visual_review'],
            'dataset_same_as_thesis':True,'private_hdf5_untracked':True,
            'primary_completion_and_delay_gate':s['primary_completion_and_delay_gate'],
            'candidate_promoted_as_main_model':bool(s['primary_completion_and_delay_gate'])}
    out=ROOT/'results/service_reward_v21/analysis/delivery_validation.json'
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
