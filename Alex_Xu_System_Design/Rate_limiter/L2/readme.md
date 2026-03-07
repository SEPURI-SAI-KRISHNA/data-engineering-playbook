### Distributed Rate Limiter (Multi-Node)

To support multiple application servers, the rate-limiting state must be centralized. We move the counters out of the application's memory and into a fast, in-memory datastore: **Redis**.

**Concept:**
We will use a **Fixed Window Counter** algorithm for simplicity at this scale.

* We map the current timestamp to a specific window (e.g., the current minute).
* We use Redis's atomic `INCR` command to increment the request count for that user in that specific window.
* We use `EXPIRE` to clean up old windows so Redis doesn't run out of memory.

**Infrastructure Setup:**

* **Load Balancer:** Distributes traffic across your app servers (e.g., AWS ALB, Nginx).
* **Compute:** Multiple Application Servers (Auto-scaling group).
* **Storage:** A centralized Redis instance (e.g., AWS ElastiCache, Redis Cloud).

**Limitations:**
The fixed window algorithm suffers from the "boundary effect." A user could send 5 requests at 10:00:09 and 5 more at 10:00:11. While technically within the 10-second window limits, they effectively sent 10 requests within 2 seconds. Furthermore, performing multiple network hops to Redis per request adds latency.

