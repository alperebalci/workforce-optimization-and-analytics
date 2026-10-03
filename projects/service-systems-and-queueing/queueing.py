from __future__ import annotations

from dataclasses import dataclass
import heapq
import math
import numpy as np


@dataclass(frozen=True)
class MMSMetrics:
    probability_wait: float
    expected_wait: float
    expected_system_time: float
    queue_length: float
    utilization: float


def erlang_c(arrival_rate: float, service_rate: float, servers: int) -> float:
    if arrival_rate < 0 or service_rate <= 0 or servers < 1:
        raise ValueError("Rates must be valid and servers >= 1")
    offered = arrival_rate / service_rate
    rho = offered / servers
    if rho >= 1:
        raise ValueError("M/M/s queue is unstable: arrival_rate >= servers * service_rate")
    term = 1.0
    partial = 1.0
    for k in range(1, servers):
        term *= offered / k
        partial += term
    term_s = term * offered / servers if servers > 1 else offered
    tail = term_s / (1.0 - rho)
    return float(tail / (partial + tail))


def mm_s_metrics(arrival_rate: float, service_rate: float, servers: int) -> MMSMetrics:
    pw = erlang_c(arrival_rate, service_rate, servers)
    spare = servers * service_rate - arrival_rate
    wq = pw / spare
    return MMSMetrics(
        probability_wait=pw,
        expected_wait=float(wq),
        expected_system_time=float(wq + 1.0 / service_rate),
        queue_length=float(arrival_rate * wq),
        utilization=float(arrival_rate / (servers * service_rate)),
    )


def service_level(arrival_rate: float, service_rate: float, servers: int, wait_threshold: float) -> float:
    if wait_threshold < 0:
        raise ValueError("wait_threshold must be non-negative")
    pw = erlang_c(arrival_rate, service_rate, servers)
    spare = servers * service_rate - arrival_rate
    return float(1.0 - pw * math.exp(-spare * wait_threshold))


def minimum_servers(arrival_rate: float, service_rate: float, target_service_level: float, wait_threshold: float, max_servers: int = 1000) -> int:
    if not 0 < target_service_level < 1:
        raise ValueError("target_service_level must lie in (0,1)")
    start = max(1, math.floor(arrival_rate / service_rate) + 1)
    for s in range(start, max_servers + 1):
        if service_level(arrival_rate, service_rate, s, wait_threshold) >= target_service_level:
            return s
    raise ValueError("target service level not reached within max_servers")


def interval_staffing(arrival_rates, service_rate: float, target_service_level: float, wait_threshold: float):
    return [minimum_servers(float(lam), service_rate, target_service_level, wait_threshold) for lam in arrival_rates]


def simulate_mm_s(arrival_rate: float, service_rate: float, servers: int, n_customers: int = 50000, warmup: int = 2000, seed: int = 2026):
    if arrival_rate >= servers * service_rate:
        raise ValueError("unstable queue")
    rng = np.random.default_rng(seed)
    arrivals = np.cumsum(rng.exponential(1.0 / arrival_rate, size=n_customers)) if arrival_rate > 0 else np.arange(n_customers, dtype=float)
    available = [0.0] * servers
    heapq.heapify(available)
    waits = np.empty(n_customers)
    for i, a in enumerate(arrivals):
        free_at = heapq.heappop(available)
        start = max(a, free_at)
        waits[i] = start - a
        finish = start + rng.exponential(1.0 / service_rate)
        heapq.heappush(available, finish)
    sample = waits[min(warmup, n_customers):]
    return {"mean_wait": float(sample.mean()), "probability_wait": float(np.mean(sample > 1e-12))}
