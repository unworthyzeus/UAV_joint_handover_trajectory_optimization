"""Additional source motivated measurements without changing transitions."""
import numpy as np


def radio_measurements(rss_dbm, serving):
    rss = np.asarray(rss_dbm, dtype=np.float64)
    selected = rss[np.arange(len(rss)), serving]
    watts = np.where(rss > -128, 10. ** ((rss - 30.) / 10.), 0.)
    selected_w = watts[np.arange(len(rss)), serving]
    snr = np.where(selected > -128, selected + 112.41 - 9., np.nan)
    others = np.maximum(0., watts.sum(axis=1) - selected_w)
    literal = rss.sum(axis=1) - selected
    return snr, others * 1e6, literal


def literal_energy_update(previous, speed):
    """Literal Eq. (10) score, not physical energy or a unit conversion."""
    return previous - 3. * speed / (370. * .55 * 5.) + .1


class ThesisMetrics:
    def __init__(self, env):
        self.env = env
        self.samples = {k: np.full((env.n, env.cfg.horizon), np.nan)
                        for k in ('snr_db', 'neighbor_rss_power_uw', 'literal_rss_sum',
                                  'remaining_energy_kj', 'literal_energy_score', 'rss_dbm')}
        self.literal_energy = np.full(env.n, 1000.)
        self.counts = np.zeros(env.n, dtype=int)

    def record(self, active, completed):
        env = self.env
        rss = env.radio.query(env.pos)
        snr, neighbors, literal = radio_measurements(rss, env.serving)
        speed = np.linalg.norm(env.vel, axis=1)
        self.literal_energy[active] = literal_energy_update(self.literal_energy[active], speed[active])
        rows = np.flatnonzero(active)
        indices = self.counts[active]
        values = {'snr_db': snr, 'neighbor_rss_power_uw': neighbors, 'literal_rss_sum': literal,
                  'remaining_energy_kj': (env.cfg.battery_j - env.energy) / 1000.,
                  'literal_energy_score': self.literal_energy,
                  'rss_dbm': rss[env.rows, env.serving]}
        for key, value in values.items():
            self.samples[key][rows, indices] = value[active]
        self.counts += active
        for episode in completed:
            i = episode['lane']; n = int(self.counts[i])
            signal = self.samples['snr_db'][i, :n]
            episode.update(snr_mean_db=float(np.nanmean(signal)) if np.isfinite(signal).any() else None,
                           snr_sample_median_db=float(np.nanmedian(signal)) if np.isfinite(signal).any() else None,
                           missing_signal_samples=int(np.isnan(signal).sum()),
                           neighbor_rss_power_mean_uw=float(self.samples['neighbor_rss_power_uw'][i, :n].mean()),
                           literal_rss_sum_mean=float(self.samples['literal_rss_sum'][i, :n].mean()),
                           remaining_energy_kj=float(values['remaining_energy_kj'][i]),
                           literal_energy_score=float(self.literal_energy[i]),
                           handovers_per_second=float(episode['handovers'] / episode['time_s']),
                           metric_samples=n)

