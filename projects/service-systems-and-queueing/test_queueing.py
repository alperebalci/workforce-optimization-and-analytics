import math
from queueing import erlang_c, mm_s_metrics, service_level, minimum_servers, simulate_mm_s


def test_m_m_1_matches_closed_form_wait():
    lam, mu = 2.0, 3.0
    m = mm_s_metrics(lam, mu, 1)
    assert math.isclose(m.probability_wait, lam/mu, rel_tol=1e-10)
    assert math.isclose(m.expected_wait, lam/(mu*(mu-lam)), rel_tol=1e-10)


def test_more_servers_improve_service_level():
    assert service_level(8, 3, 4, 0.2) > service_level(8, 3, 3, 0.2)


def test_minimum_servers_hits_target_and_previous_does_not():
    s = minimum_servers(20, 4, 0.8, 0.25)
    assert service_level(20, 4, s, 0.25) >= 0.8
    if s > 6:
        assert service_level(20, 4, s-1, 0.25) < 0.8


def test_simulation_agrees_with_erlang_c_reasonably():
    lam, mu, s = 4.0, 3.0, 2
    analytical = erlang_c(lam, mu, s)
    simulated = simulate_mm_s(lam, mu, s, n_customers=70000, warmup=3000, seed=9)
    assert abs(simulated["probability_wait"] - analytical) < 0.03
