# Exactly-Once Semantics in Apache Flink

Exactly-once means each record affects the final result **once and only once**, even in the presence of failures.

## How Flink achieves this
- Stateful operators
- Checkpointing
- Barrier alignment
- Two-phase commit sinks

## Common pitfalls
- External systems not supporting transactions
- Large state causing checkpoint delays
- Misconfigured checkpoint intervals

## When exactly-once is overkill
- Idempotent sinks
- Approximate analytics
- Low-latency systems

Exactly-once is a **contract**, not magic.
