### Basic In-Memory Rate Limiter (Single Node)

At this level, your application runs on a single server. We will use the **Token Bucket algorithm**, which is highly efficient and allows for brief bursts of traffic.

**Concept:**

* Imagine a bucket that holds a maximum number of tokens (capacity).
* Tokens are added to the bucket at a fixed rate (refill rate).
* Every time a request arrives, it tries to take a token. If a token is available, the request is allowed. If the bucket is empty, the request is dropped (HTTP 429 Too Many Requests).

**Infrastructure Setup:**

* **Compute:** A single application server (e.g., a single AWS EC2 instance, DigitalOcean Droplet, or just your local laptop).
* **Network:** Direct client-to-server connection. No load balancers are strictly necessary.

**Python Code (In-Memory Token Bucket):**
We use a Python dictionary to store the state and `threading.Lock` to prevent race conditions when concurrent requests hit the server.


**Limitations:** If you scale out to multiple application servers, each server keeps its own independent bucket. A user limited to 5 requests/sec could make 15 requests/sec if routed across 3 different servers.
