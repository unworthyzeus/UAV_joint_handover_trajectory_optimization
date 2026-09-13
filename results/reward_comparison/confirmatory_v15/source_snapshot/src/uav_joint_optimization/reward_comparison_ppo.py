"""Frozen V2 PPO with only the original reward environment adapter imported."""
from __future__ import annotations

import csv
import json
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.distributions import Categorical, Normal

from .connectivity_env import ConnectivityConfig as EnvironmentConfig
from .original_reward_env import RewardComparisonBatch as ConnectivityBatch


@dataclass(frozen=True)
class PPOConfig:
    environments: int = 64
    rollout: int = 128
    minibatch: int = 512
    epochs: int = 4
    learning_rate: float = 0.0003
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip: float = 0.2
    entropy: float = 0.005
    value_weight: float = 0.5
    grad_norm: float = 0.5
    hidden: int = 64
    steps: int = 524288
    threads: int = 2


class HybridPolicy(nn.Module):
    def __init__(self, obs_dim: int, hidden: int = 64):
        super().__init__()
        def net():
            return nn.Sequential(nn.Linear(obs_dim, hidden), nn.Tanh(),
                                 nn.Linear(hidden, hidden), nn.Tanh())
        self.actor, self.critic = net(), net()
        self.motion = nn.Linear(hidden, 2)
        self.network = nn.Linear(hidden, 61)
        self.value_head = nn.Linear(hidden, 1)
        self.log_std = nn.Parameter(torch.full((2,), -0.5))
        for layer in self.modules():
            if isinstance(layer, nn.Linear):
                nn.init.orthogonal_(layer.weight, np.sqrt(2))
                nn.init.zeros_(layer.bias)
        nn.init.orthogonal_(self.motion.weight, .01)
        nn.init.orthogonal_(self.network.weight, .01)
        nn.init.orthogonal_(self.value_head.weight, 1.)

    def value(self, obs):
        return self.value_head(self.critic(obs)).squeeze(-1)

    def distributions(self, obs, mask):
        hidden = self.actor(obs)
        normal = Normal(self.motion(hidden), self.log_std.clamp(-2.3, .5).exp())
        categorical = Categorical(logits=self.network(hidden).masked_fill(~mask, -1e9))
        return normal, categorical

    def action(self, obs, mask, deterministic=False):
        normal, categorical = self.distributions(obs, mask)
        latent = normal.mean if deterministic else normal.sample()
        choice = categorical.logits.argmax(-1) if deterministic else categorical.sample()
        logp = normal.log_prob(latent).sum(-1) + categorical.log_prob(choice)
        return latent, choice, logp, self.value(obs)

    def score(self, obs, mask, latent, choice):
        normal, categorical = self.distributions(obs, mask)
        logp = normal.log_prob(latent).sum(-1) + categorical.log_prob(choice)
        entropy = normal.entropy().sum(-1) + categorical.entropy()
        return logp, entropy, self.value(obs)


class RewardNormalizer:
    """Running variance of discounted returns; rewards are not mean centered."""
    def __init__(self, n, gamma):
        self.gamma, self.returns = gamma, np.zeros(n, dtype=np.float64)
        self.mean, self.var, self.count = 0., 1., .0001

    def apply(self, reward, done):
        self.returns = self.gamma * self.returns + reward
        batch_mean, batch_var, size = self.returns.mean(), self.returns.var(), len(reward)
        delta, total = batch_mean - self.mean, self.count + size
        self.var = (self.var * self.count + batch_var * size + delta**2 * self.count * size / total) / total
        self.mean += delta * size / total
        self.count = total
        result = np.clip(reward / np.sqrt(self.var + 1e-8), -10, 10).astype(np.float32)
        self.returns[done] = 0
        return result


def gae(rewards, values, dones, last_value, gamma, lam):
    advantages = np.zeros_like(rewards)
    carry = np.zeros_like(last_value)
    for t in reversed(range(len(rewards))):
        following = last_value if t == len(rewards)-1 else values[t+1]
        keep = 1. - dones[t]
        delta = rewards[t] + gamma * following * keep - values[t]
        carry = delta + gamma * lam * keep * carry
        advantages[t] = carry
    return advantages, advantages + values


def evaluate(policy, radio, scenarios, env_config, out_prefix=None, pd=False,
             reward="full", terminate_success=True, traces=4):
    env = ConnectivityBatch(radio, len(scenarios), scenarios, reward, env_config)
    obs, mask = env.observe()
    paths = [[] for _ in range(min(traces, env.n))]
    results = []
    for _ in range(env_config.horizon):
        for i in range(len(paths)):
            if not env.done[i]:
                paths[i].append([*env.pos[i].tolist(), float(np.linalg.norm(env.vel[i])), int(env.serving[i])])
        if pd:
            motion, network = env.controller(pd if isinstance(pd, str) else "straight_radio")
        else:
            with torch.no_grad():
                latent, choice, _, _ = policy.action(torch.from_numpy(obs), torch.from_numpy(mask), True)
            motion, network = env.decode_residual(torch.tanh(latent).numpy()), choice.numpy()
        obs, mask, _, _, completed = env.step(motion, network)
        results.extend(completed)
        for row in completed:
            i = row["lane"]
            if i < len(paths):
                paths[i].append([*env.pos[i].tolist(), float(np.linalg.norm(env.vel[i])), int(env.serving[i])])
        if env.done.all():
            break
    assert len(results) == len(scenarios)
    results.sort(key=lambda r: r["lane"])
    if out_prefix is not None:
        out_prefix = Path(out_prefix)
        out_prefix.parent.mkdir(parents=True, exist_ok=True)
        with out_prefix.with_suffix(".csv").open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0]))
            writer.writeheader(); writer.writerows(results)
        out_prefix.with_suffix(".json").write_text(json.dumps({"episodes": results, "traces": paths,
            "scenarios": scenarios[:len(paths)], "summary": summarize(results)}, indent=2)+"\n", encoding="utf-8")
    return results


def summarize(results):
    success = [r for r in results if r["success"]]
    summary = {"failure_counts": {reason: sum(r["outcome"] == reason for r in results) for reason in ("connectivity", "buffer", "timeout", "energy", "boundary")}, "episodes": len(results), "success_rate": len(success)/len(results),
        "feasible_success_rate": np.mean([r["success"] for r in results]).item(),
        "failure_distance_mean_m": float(np.mean([r["final_distance_m"] for r in results if not r["success"]]))
        if len(success) != len(results) else None}
    for metric in ("time_s", "path_m", "energy_proxy_j", "handovers", "outage_s", "dropped_bits",
                   "delay_proxy_mean_s", "interference_mean_w", "sinr_mean_db", "sinr_p05_db", "radio_cost_sum", "radio_cost_mean", "resource_changes", "final_buffer_bits"):
        summary[f"successful_{metric}"] = float(np.mean([r[metric] for r in success])) if success else None
    return summary


def train(radio, scenarios, validation, reward, terminate_success, seed, output,
          config=PPOConfig(), env_config=EnvironmentConfig(), validation_every=16):
    if config.gamma != env_config.gamma:
        raise ValueError("Learner and shaping discounts must match")
    torch.set_num_threads(config.threads)
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    metadata = {"seed": seed, "reward": reward, "terminate_success": terminate_success,
                "ppo": asdict(config), "environment": asdict(env_config), "source": radio.path,
                "map_stride": radio.stride, "torch": torch.__version__, "numpy": np.__version__}
    (output / "config.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    env = ConnectivityBatch(radio, config.environments, scenarios, reward, env_config)
    obs, mask = env.observe()
    policy = HybridPolicy(obs.shape[1], config.hidden)
    optimizer = torch.optim.Adam(policy.parameters(), lr=config.learning_rate, eps=1e-5)
    normalizer = RewardNormalizer(config.environments, config.gamma)
    log = []; start_time = time.perf_counter()
    updates = int(np.ceil(config.steps / (config.environments * config.rollout)))
    episode_window = []
    for update in range(1, updates + 1):
        storage = {k: [] for k in ("obs", "mask", "latent", "choice", "logp", "value", "reward", "done")}
        for _ in range(config.rollout):
            with torch.no_grad():
                latent, choice, logp, value = policy.action(torch.from_numpy(obs), torch.from_numpy(mask))
            storage["obs"].append(obs); storage["mask"].append(mask)
            storage["latent"].append(latent.numpy()); storage["choice"].append(choice.numpy())
            storage["logp"].append(logp.numpy()); storage["value"].append(value.numpy())
            obs, mask, raw_reward, done, completed = env.step(env.decode_residual(torch.tanh(latent).numpy()), choice.numpy())
            storage["reward"].append(normalizer.apply(raw_reward, done)); storage["done"].append(done)
            episode_window.extend(completed)
            if done.any():
                obs, mask = env.reset(done)
        arrays = {k: np.stack(v) for k,v in storage.items()}
        with torch.no_grad():
            last_value = policy.value(torch.from_numpy(obs)).numpy()
        advantage, returns = gae(arrays["reward"], arrays["value"], arrays["done"], last_value, config.gamma, config.gae_lambda)
        arrays.update(advantage=advantage, returns=returns)
        batch = {k: torch.from_numpy(v.reshape((-1, *v.shape[2:]))) for k,v in arrays.items()}
        size = len(batch["obs"])
        losses, kls, entropies = [], [], []
        for _ in range(config.epochs):
            permutation = np.random.permutation(size)
            for begin in range(0, size, config.minibatch):
                ix = permutation[begin:begin+config.minibatch]
                new_logp, entropy, value = policy.score(batch["obs"][ix], batch["mask"][ix], batch["latent"][ix], batch["choice"][ix])
                logratio = new_logp - batch["logp"][ix]
                ratio = logratio.exp()
                adv = batch["advantage"][ix]
                adv = (adv - adv.mean()) / (adv.std() + 1e-8)
                policy_loss = torch.maximum(-adv * ratio, -adv * ratio.clamp(1-config.clip, 1+config.clip)).mean()
                value_loss = .5 * (value - batch["returns"][ix]).square().mean()
                loss = policy_loss + config.value_weight * value_loss - config.entropy * entropy.mean()
                optimizer.zero_grad(); loss.backward()
                nn.utils.clip_grad_norm_(policy.parameters(), config.grad_norm)
                optimizer.step()
                losses.append(float(value_loss.detach()))
                kls.append(float(((ratio-1)-logratio).mean().detach()))
                entropies.append(float(entropy.mean().detach()))
        row = {"update": update, "steps": update * size, "seconds": time.perf_counter()-start_time,
               "value_loss": float(np.mean(losses)), "approx_kl": float(np.mean(kls)),
               "entropy": float(np.mean(entropies)), "return_std": float(np.sqrt(normalizer.var)),
               "train_episodes": len(episode_window), "train_success": float(np.mean([x["success"] for x in episode_window[-200:]])) if episode_window else 0.}
        if validation_every and (update % validation_every == 0 or update == updates):
            metrics = summarize(evaluate(policy, radio, validation, env_config))
            row["validation_success"] = metrics["success_rate"]
            row["validation_failure_distance"] = metrics["failure_distance_mean_m"]
            print(json.dumps({"run": output.name, **row}), flush=True)
        elif update % 8 == 0:
            print(json.dumps({"run": output.name, **row}), flush=True)
        log.append(row)
        (output / "training_log.json").write_text(json.dumps(log, indent=2)+"\n", encoding="utf-8")
        if update % 16 == 0 or update == updates:
            torch.save({"policy": policy.state_dict(), "obs_dim": obs.shape[1], "hidden": config.hidden,
                        "metadata": metadata, "steps": row["steps"]}, output / "checkpoint.pt")
    final_validation = evaluate(policy, radio, validation, env_config, output / "validation", traces=4)
    (output / "summary.json").write_text(json.dumps({"validation": summarize(final_validation),
        "wall_seconds": time.perf_counter()-start_time, "steps": updates*size}, indent=2)+"\n", encoding="utf-8")
    return policy
