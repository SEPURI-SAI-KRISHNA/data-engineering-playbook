# Why Shuffle Is Expensive in Apache Spark

Shuffle is one of the most common performance bottlenecks in Spark jobs.

## What happens during shuffle
1. Data is repartitioned based on a key
2. Map tasks write intermediate data to disk
3. Data is transferred over the network
4. Reduce tasks read, merge, and sort data

## Why it hurts
- Disk I/O from spills
- Network transfer amplification
- CPU cost of sorting
- Straggler tasks due to skew

## Common triggers
- Wide transformations (groupBy, join)
- Poor partitioning strategy
- Skewed keys

## Mitigation strategies
- Reduce shuffle width
- Use broadcast joins where possible
- Salting skewed keys
- Proper partition sizing

Shuffle is not bad by default — **uncontrolled shuffle is**.
