
### Basic Consistent Hashing (The Hash Ring)

At this level, we introduce the fundamental concept of the hash ring. We map physical nodes to a circle and route requests by finding the "next" node on the ring.

**Concept:**

* Imagine a circle representing a huge number space (e.g., $0$ to $2^{32}-1$).
* We hash the IP or ID of our servers and place them on this ring.
* When a request comes in, we hash the request key (like a User ID), place it on the ring, and walk **clockwise** until we hit the first server. That server handles the request.
* If a server is added or removed, only the keys immediately adjacent to it are reassigned. The rest of the cluster is unaffected.

**Infrastructure Setup:**

* **Routing Layer:** A single application or load balancer that holds the hash ring in memory.
* **Compute:** 3-5 basic caching servers.


**Limitations:** The basic ring has a major flaw: **Data Skew**. Because hashing is random, Server A and Server B might end up right next to each other on the ring, while Server C handles half the entire circle. Server C will get crushed with traffic.



