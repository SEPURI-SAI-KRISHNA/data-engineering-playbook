The Cassandra Blueprint

Apache Cassandra is a powerhouse in the world of distributed databases. If you are preparing for a system design interview, you need to understand it not just as a "NoSQL database," but as a highly specialized engine designed for **massive scale** and **high availability**.

---

## 0] What does it do primarily?

**Primary Function:** It stores massive amounts of data across many servers (nodes) without a single point of failure. It is designed to handle **huge write volumes** and stay online even if multiple servers go dark.

* **Real-Life Example:** Think of **Netflix**. When you watch a movie, Netflix needs to track your progress (e.g., "User X is at 23:04 in Movie Y"). Millions of people are doing this every second. Cassandra stores these "heartbeats" because it can handle millions of tiny writes instantly across the globe.

---

## 1] What is it and what is it NOT?

* **What it IS:** A distributed, wide-column NoSQL database based on a "Leaderless" (Peer-to-Peer) architecture.
* **What it is NOT:** It is **not** a Relational Database (RDBMS). There are no JOINs, no Foreign Keys, and no ACID transactions across multiple tables (usually).
* **Misconception:** "It's just like MongoDB." **False.** Cassandra is optimized for writes and structured schemas; MongoDB is document-oriented and historically had a Master-Slave setup.

---

## 2] Scalability, Availability, & Reliability

* **Scalability:** **Linear.** If 2 nodes handle 100k writes/sec, 4 nodes will handle 200k. You just add more nodes.
* **Availability:** **High.** Since every node is equal (no master), if one node dies, the others just keep working.
* **Reliability:** **High.** Data is replicated (copied) to multiple nodes automatically.

---

## 3] Core Components

| Component | Definition | Example |
| --- | --- | --- |
| **Node** | A single server running Cassandra. | An EC2 instance in AWS. |
| **Data Center** | A collection of related nodes. | "US-East-1" group of nodes. |
| **Cluster** | All Data Centers joined together. | The entire global Netflix database. |
| **Commit Log** | A crash-recovery file on disk. | The first place a write is "saved." |
| **Memtable** | In-memory cache for recent writes. | Temporary "waiting room" in RAM. |
| **SSTable** | Sorted String Table (permanent file). | The final "book" stored on your SSD. |

---

## 4] What is this tool?

It is a **Distributed NoSQL Database**. It is specifically a "Wide-Column Store."

---

## 5] Is it distributed?

**Yes.** It is distributed by design. It uses **Consistent Hashing** to decide which node stores which piece of data. There is no "Master" node; every node can talk to every other node via the **Gossip Protocol**.

---

## 6] Can it be used in production?

**Absolutely.** It is the backbone for Apple, Uber, Instagram, and Spotify. It is one of the most "battle-tested" distributed systems in existence.

---

## 7] Failure Handling

If a node goes down:

1. **Gossip:** Other nodes notice it's gone and stop sending it requests.
2. **Hinted Handoff:** If a write was meant for the dead node, a neighbor stores a "hint" (a note). When the dead node comes back, the neighbor gives it the missed data.
3. **Read Repair:** If a read happens and data is old, Cassandra fixes it on the fly.

---

## 8] Background Processes

* **Compaction:** Cassandra never updates a file. It just writes new ones. Compaction merges small files into big ones and removes old data.
* **Gossip:** Nodes "chat" every second to share state (who is alive, who is loaded).
* **Anti-Entropy Repair:** A manual "health check" that ensures all replicas have the exact same data.

---

## 9] The Internal Architecture: How it Works

### The Write Path (Optimized for Speed)

1. **Coordinator:** You send a write to *any* node. That node becomes the "Coordinator."
2. **Commit Log:** The node immediately appends the write to a disk log (very fast).
3. **Memtable:** The data is written to a RAM structure. **The Write is now successful!** (Latency < 1ms).
4. **Flush:** When Memtable is full, it is flushed to an **SSTable** (Disk).

### The Read Path (The "Hard" Part)

1. **Bloom Filter:** Checks if the data *might* be in an SSTable (prevents useless disk reads).
2. **Key Cache:** Checks RAM for the data's location.
3. **Partition Summary/Index:** Locates the data on disk.
4. **Merge:** Cassandra merges data from the Memtable and multiple SSTables to find the "latest" version.

---

## 10] Writes vs. Reads

Cassandra is **Heavily Optimized for Writes**.

* **Writes:** Append-only, no disk seeking.
* **Reads:** Slower because it might have to check multiple files (SSTables) to find the most recent version of a row.

---

## 11] CAP Theorem & Tunability

Cassandra is an **AP** system (Availability & Partition Tolerance). However, it is **Tunable**.

* **Consistency Level (CL):** You decide how many nodes must agree.
* **Formula for Strong Consistency:**  (Read nodes + Write nodes > Replication Factor).
* **Example:** If  and you write with `QUORUM` (2 nodes) and read with `QUORUM` (2 nodes), you get **Strong Consistency** because .

---

## 12] Why is it sometimes slow?

Even if optimized, it can be slow because of:

1. **GC Pauses:** Since it's written in Java, Garbage Collection can freeze the node.
2. **Tombstones:** If you delete a lot, the read path has to scan thousands of "deleted" markers.
3. **Large Partitions:** If one user has 10GB of data in one row, it crashes the node.

---

## 13] Tricky Parts: The "Leaky" Abstraction

* **LSM Trees:** Unlike SQL (B-Trees), Cassandra uses Log-Structured Merge-Trees. This is why writes are fast but reads are "complex."
* **JVM:** You are at the mercy of the Java Virtual Machine. Memory tuning is 50% of the job.

---

## 14] Alternatives

* **ScyllaDB:** A C++ rewrite of Cassandra. 5x faster, no JVM/GC issues. (Usually better for modern high-perf).
* **DynamoDB:** AWS's managed version. Easier to use, but can be more expensive and has vendor lock-in.
* **HBase:** Better for heavy "Scans" but much more complex to maintain (requires Hadoop/Zookeeper).

---

## 15] When to use it?

* You have **petabytes** of data.
* You have a **global** audience (Multi-Region replication).
* Your **write-to-read ratio** is high (e.g., IoT sensors, logs).

---

## 16] When NOT to use it?

* You need **ACID Transactions** (like a bank transfer between two different tables).
* You need to perform **Ad-hoc queries** (e.g., "Find all users who like pizza AND live in NYC" - if you didn't design the table for this, it will fail).
* Your data fits in a single SQL server.

---

## 17] Datalake vs. Datawarehouse?

Cassandra fits in the **Operational Data Layer (Serving Layer)**.

* **Why?** It is too slow for "Analytics" (Datawarehouse) because it hates large table scans. It is meant to serve fast, live data to users.

---

## 18] Deletes and "Tombstones"

**Internally:** Cassandra **cannot** delete data immediately because it is an append-only system.

1. When you delete, Cassandra writes a **Tombstone** (a marker).
2. During a Read, Cassandra sees the marker and hides the data.
3. During **Compaction**, if the tombstone is older than `gc_grace_seconds` (default 10 days), the data is finally purged.

* **Danger:** If you delete too much, your reads slow down to a crawl because the "scanning" takes too long.

---

## 19] Extra: Interview Preparation Kit

### Common Interview Questions (Short Answers)

* **Q: What is a Replication Factor?**
* *A: The total number of nodes where a single piece of data is stored.*


* **Q: What is a Partition Key?**
* *A: The part of the Primary Key that determines which node the data lives on.*


* **Q: What is Hinted Handoff?**
* *A: A temporary storage of a write for a downed node to ensure eventual consistency.*



### Operational Tuning Checklist

* [ ] **Compaction Strategy:** Use `STCS` for writes, `LCS` for reads, `TWCS` for time-series.
* [ ] **Partition Size:** Keep partitions under 100MB.
* [ ] **Consistency:** Use `LOCAL_QUORUM` for multi-region to avoid high cross-region latency.

### Example Scenario (Numbers)

> **Interviewer:** "Design a system for 1 Million writes per second."
> **You:** "I'll use Cassandra. With a cluster of 50-100 nodes, each node handling 10-20k writes/sec. I'll use a RF of 3 and Consistency Level ONE for maximum throughput if data loss of the last second is acceptable."

### Data Model Samples

1. **User Profile (by ID):** `PRIMARY KEY (user_id)` -> Fast lookup.
2. **User Comments (by Post):** `PRIMARY KEY (post_id, created_at)` -> `post_id` is the partition (where it lives), `created_at` is the clustering key (how it's sorted).
