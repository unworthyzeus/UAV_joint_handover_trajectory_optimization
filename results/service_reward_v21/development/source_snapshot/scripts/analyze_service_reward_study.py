"""Declared V2.1 analysis with completion first and conditional service metrics."""
import json

import numpy as np

from run_service_reward_study import BASE, SEEDS, verify_history, verify_new, save, learner
from analyze_connectivity_experiment import interval

METRICS=['time_s','delay_proxy_mean_s','handovers','energy_proxy_j','sinr_mean_db',
         'interference_mean_w','radio_cost_sum','path_m','final_buffer_bits',
         'network_interventions','motion_interventions']


def paired(left,right):
    if len(right)==1 and len(left)>1:
        right=right*len(left)
    assert len(left)==len(right)
    for a,b in zip(left,right):
        assert [r['scenario_id'] for r in a]==[r['scenario_id'] for r in b]
    a=np.array([[r['success'] for r in run] for run in left])
    b=np.array([[r['success'] for r in run] for run in right])
    common=a&b; delta=a.astype(float)-b.astype(float)
    result={'success_difference_pp':float(100*delta.mean()),
            'success_difference_ci95_pp':[100*x for x in interval(delta,seed=64000,draws=5000)],
            'paired_success_count':int(common.sum()),'paired_evaluations':int(common.size)}
    for metric in METRICS:
        x=np.array([[r[metric] for r in run] for run in left])
        y=np.array([[r[metric] for r in run] for run in right])
        result[metric]={'left_mean_on_common_success':float(x[common].mean()) if common.any() else None,
                        'right_mean_on_common_success':float(y[common].mean()) if common.any() else None,
                        'paired_mean_difference':float((x-y)[common].mean()) if common.any() else None,
                        'difference_ci95':interval(x-y,common,seed=64000,draws=5000),
                        'relative_difference_pct':float(100*(x[common].sum()/y[common].sum()-1))
                        if metric!='sinr_mean_db' and common.any() and y[common].sum()!=0 else None}
    return result


def main():
    verify_history(); frozen=verify_new()
    data={}; groups={}
    for split in ['test','longer_test']:
        data[split]={}
        for arm in ['service','full','original','straight_radio','joint_mpc','joint_lookahead']:
            runs=[]
            for seed in SEEDS if arm in ['service','full','original'] else [None]:
                name=f'{arm}_seed_{seed}/{split}.json' if seed else f'{arm}_{split}.json'
                rows=json.loads((BASE/'confirmatory'/name).read_text())['episodes']
                assert len(rows)==500
                for r in rows:
                    if r['success']:
                        assert r['minimum_rss_dbm']>=-96 and r['outage_s']==0 and r['dropped_bits']==0
                        assert r['time_s']<=200 and r['final_distance_m']<=10 and r['final_speed_mps']<=2
                runs.append(rows)
            data[split][arm]=runs
            groups[f'{arm}_{split}']=learner.summarize([r for run in runs for r in run])
            groups[f'{arm}_{split}']['per_seed_success_rates']=[learner.summarize(v)['success_rate'] for v in runs]
    contrasts={}
    for split in data:
        for right in ['full','original','straight_radio','joint_mpc','joint_lookahead']:
            contrasts[f'service_minus_{right}_{split}']=paired(data[split]['service'],data[split][right])
    primary=contrasts['service_minus_full_test']
    success=primary['success_difference_ci95_pp'][0]>0
    delay=primary['delay_proxy_mean_s']['difference_ci95'][1]<=0
    result={'scope':'Fresh 54012/54013 evaluation of the validation selected V2.1 candidate; no retuning after tests.',
            'selected':frozen['selected'],'groups':groups,'contrasts':contrasts,
            'total_evaluated_episodes':sum(g['episodes'] for g in groups.values()),
            'primary_contrast':'service_minus_full_test','primary_completion_improvement':bool(success),
            'primary_delay_no_regression_evidence':bool(delay),
            'primary_completion_and_delay_gate':bool(success and delay),
            'bootstrap_seed':64000,'bootstrap_draws':5000,
            'deterministic_comparison_note':'A deterministic route record is paired with every learned seed, without counting the repeated pairing as additional evaluation episodes.'}
    assert result['total_evaluated_episodes']==18000
    save(BASE/'analysis/statistics.json',result)
    print(json.dumps({'selected':frozen['selected'],'primary_gate':result['primary_completion_and_delay_gate'],
                      'success_rates':{k:v['success_rate'] for k,v in groups.items()},'primary':primary},indent=2))


if __name__=='__main__': main()
