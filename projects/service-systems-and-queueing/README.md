# Service Systems and Queueing

Analytical and simulation-based capacity planning for M/M/s service systems.

Implemented components:

- Erlang C probability of delay;
- expected waiting time, system time, queue length and utilization;
- service-level probability `P(wait <= threshold)`;
- minimum-server search for a target service level;
- interval-by-interval staffing for time-varying demand forecasts;
- a discrete-event M/M/s simulator used as an independent validation layer.

This extends workforce optimization from shift assignment into the queueing layer that determines how much capacity is required in the first place.

Run:

```bash
python -m pip install -r requirements.txt
pytest -q
```

Assumptions are explicit: Poisson arrivals, exponential service times, identical servers, FCFS service, no abandonment, and steady-state formulas within each interval. Erlang A, skill-based routing and nonstationary exact models are natural later extensions.
