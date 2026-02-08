The Apache Airflow Blueprint
### **0] What does the tool do primarily?**

**Primary Function:** Airflow is a platform to **programmatically author, schedule, and monitor workflows**. It manages dependencies between tasks (e.g., "Do B only after A succeeds").

* **Real-Life Example:** Think of **Uber Eats**. Every night at 2 AM, they need to:
1. Ingest raw order logs from the app database.
2. Clean the data (remove cancelled orders).
3. Calculate "Total Revenue" for the day.
4. Send a PDF report to the CFO.
Airflow triggers step 1, waits for it to finish, triggers step 2, and so on. If step 2 fails, it retries or alerts the engineer.



### **1] What is it and what is it NOT?**

* **What it IS:** A **Workflow Orchestrator**. It is "Configuration as Code" (Python).
* **What it is NOT:** It is **NOT a Data Streaming Solution** (like Kafka) and **NOT a Data Processing Engine** (like Spark).
* **Misconception:** "Airflow processes the data." **False.** Airflow tells *other* tools (like Spark, Snowflake, or Pandas) to process data. It is the conductor, not the musician.

### **2] Scalability, Availability, & Reliability**

* **Scalability:** **High.** You can add more **Workers** (horizontal scaling) to handle thousands of concurrent tasks.
* **Availability:** **Medium/High.** The Webserver and Scheduler can be made redundant (in newer versions with HA setup), but the Metadata Database is often the single point of failure (SPOF) if not clustered.
* **Reliability:** **High.** It has built-in retry mechanisms, timeouts, and SLAs.

### **3] Core Components**

| Component | Definition | Example |
| --- | --- | --- |
| **Scheduler** | The "Brain." It monitors time and triggers tasks. | "It's 2 AM, time to run the daily ETL." |
| **Webserver** | The UI to visualize pipelines and logs. | The dashboard where you click "Retry." |
| **Metadata DB** | The "Memory." Stores state of all tasks. | Postgres/MySQL storing "Task A = Success." |
| **Executor** | Decides *how* and *where* tasks run. | CeleryExecutor, KubernetesExecutor. |
| **Worker** | The actual compute node executing the logic. | A server running the Python script. |
| **DAG** | Directed Acyclic Graph. The workflow definition. | The Python file defining Task A -> Task B. |

### **4] What is this tool?**

It is a **Workflow Orchestration Framework** or "Task Scheduler on Steroids."

### **5] Is it distributed?**

**Yes.**

* **Centralized Control:** Scheduler & Metadata DB.
* **Distributed Execution:** Tasks (Workers) can run on hundreds of different servers spread across a cluster (Kubernetes/Celery).

### **6] Can it be used in production?**

**Yes.** Used by Airbnb (creators), Twitter, PayPal, and almost every modern data engineering team. It is the industry standard for batch orchestration.

### **7] Failure Handling**

* **Task Failure:** Configurable `retries` (e.g., retry 3 times with 5-minute delays).
* **Scheduler Failure:** If the scheduler dies, tasks stop being scheduled. You need a process monitor (like Supervisor/K8s) to restart it immediately.
* **Zombies:** If a worker dies while running a task, the Scheduler eventually detects the "Zombie" task and marks it as failed so it can be retried.

### **8] Background Processes**

* **DAG Processor:** Continually parses your Python files (DAGs) to check for updates or syntax errors.
* **Scheduler Loop:** A tight loop that checks: "Are dependencies met? Is it time to run? Do we have free slots?"
* **Heartbeats:** Workers send heartbeats to the Metadata DB to say "I'm alive."

### **9] Architecture: How it Works (The Lifecycle of a Task)**

1. **Authoring:** You write a Python file (DAG) and push it to the `dags/` folder.
2. **Parsing:** The **Scheduler** (DAG Processor) scans the folder, reads the file, and updates the **Metadata DB** with the DAG structure.
3. **Scheduling:** The **Scheduler** checks the DB.
* *Time matches?* Create a `DagRun` (an instance of the workflow).
* *Dependencies met?* Create `TaskInstance` with state `SCHEDULED`.


4. **Queuing:** The **Scheduler** sends the task to the **Executor** (e.g., puts it in a Redis Queue for Celery). State becomes `QUEUED`.
5. **Execution:** A **Worker** picks up the task from the queue.
* State becomes `RUNNING`.
* Worker executes the logic (or triggers external system).


6. **Completion:** Worker updates **Metadata DB** with state `SUCCESS` or `FAILED`.
7. **Next Step:** Scheduler sees `SUCCESS` and triggers the downstream task.

### **10] Reads vs. Writes (Database Context)**

Since Airflow uses a standard RDBMS (Postgres/MySQL) for its Metadata:

* **Writes:** Heavy. Every heartbeat, task status change, and log update writes to the DB.
* **Reads:** Heavy. The Scheduler constantly queries the DB to find what to run next.
* **Implication:** The Metadata DB is often the bottleneck in massive Airflow clusters.

### **11] CAP Theorem**

Airflow is an **Orchestrator**, not a distributed database, so CAP applies loosely.

* It leans towards **CP** (Consistency). If the Metadata DB is down (Partition), the Scheduler stops (Availability loss) to prevent running tasks twice or corrupting state.

### **12] Why is it sometimes slow?**

1. **Parsing Speed:** The Scheduler parses *every* DAG file constantly. If you have complex top-level code (e.g., making a DB connection *outside* a task), it slows down the entire system.
2. **DB Bottleneck:** If you have 10,000 tasks running, the DB gets hammered.
3. **Scheduler Latency:** There is a gap between "Task A finished" and "Task B started" because the Scheduler has to "wake up" and notice the change.

### **13] Tricky Parts (The "Gotchas")**

* **Top-Level Code:** Code in your DAG file runs *every time the scheduler parses it* (every 30s).
* *Bad:* Fetching data from AWS S3 at the top of the file -> Crashes the scheduler.
* *Good:* Fetching data *inside* a function/operator.


* **Execution Date:** In Airflow, if a run is scheduled for `2023-01-01`, it actually runs at `2023-01-02` (after the period has ended). This "data interval" concept confuses everyone.

### **14] Alternatives**

* **Prefect:** More modern, handles "dynamic" workflows better, easier local testing.
* **Dagster:** Focuses on "Data Assets" rather than just tasks. Stronger type checking.
* **Luigi:** Older, simpler, hard to scale.
* **AWS Step Functions:** Serverless, great for AWS-native, but vendor lock-in.

### **15] When to Consider Using It?**

* You have complex dependencies (B depends on A; C depends on A and B).
* You need to mix technologies (Task A = SQL, Task B = Python, Task C = Bash).
* You need backfilling (re-running historical data easily).

### **16] When NOT to Use It?**

* **Streaming:** Airflow is for batch (scheduled) jobs, not real-time events.
* **Data Passing:** Do not pass Gigabytes of data between tasks (XComs). It will crash the Metadata DB. Pass paths (S3 URIs) instead.
* **Sub-second Latency:** If you need a job to run *instantly* upon a trigger, Airflow's scheduler loop overhead (seconds) might be too slow.

### **17] Fit in Datalake/Datawarehouse?**

* **Role:** The **Control Plane**.
* **Location:** It sits *above* the Data Lake (S3) and Warehouse (Snowflake).
* **Why?** It triggers the copy command to load S3 to Snowflake. It doesn't store the data itself.

### **18] Deletes and "Clean Up"**

* **Metadata:** Airflow stores history forever by default. The DB grows huge.
* **Maintenance:** You must run a "Cleanup DAG" to delete old logs and DB entries (e.g., "Delete task history > 6 months").
* **Effect of Deletes:** If you delete a DAG file, the history remains in the DB (orphaned) until you manually clean it.

---

### **19] Extra: Interview Preparation Kit**

#### **Common Interview Questions**

* **Q: What is an XCom?**
* *A: "Cross-Communication." A way to let tasks exchange small messages (metadata like IDs or dates), stored in the Metadata DB.*


* **Q: What happens if two tasks modify the same file?**
* *A: Airflow doesn't handle resource locking natively. You must manage this yourself or use `Pools` to limit concurrency.*


* **Q: Difference between `CeleryExecutor` and `KubernetesExecutor`?**
* *A: Celery uses fixed worker nodes (always on). Kubernetes spins up a new pod for every single task (spins down after).*



#### **Operational & Tuning Checklist**

* [ ] **Scheduler Tuning:** Increase `min_file_process_interval` to reduce CPU load on parsing.
* [ ] **Pools:** Use Airflow Pools to prevent a low-priority DAG from hogging all DB connections.
* [ ] **SLA:** Define `sla` on tasks to get alerted if a job runs too long.

#### **Example Scenario (Numbers)**

> **Interviewer:** "Design a system to process 10,000 files arriving daily at unpredictable times."
> **You:** "I would use Airflow with a **Sensor**.
> * **Sensor Task:** Pokes S3 every 5 minutes to see if a file exists.
> * **Concurrency:** I'd use `KubernetesExecutor` so I don't pay for idle workers waiting for files.
> * **Scale:** If 10,000 files arrive at once, K8s scales to 10,000 pods (theoretically), but I'd limit it using `max_active_runs` to protect the DB."
> 
> 

#### **Common Pitfalls (Mention these!)**

* **The "Start Date" Trap:** Airflow only starts running *after* `start_date + schedule_interval`. It doesn't run *at* start date.
* **Heavy Parsing:** Putting DB calls at the top level of a DAG file.
* **Timezones:** Mixing UTC and Local time in schedules (always use UTC!).

#### **Data Model Samples (For Interview Problems)**

If asked to design the **Metadata DB schema** for a tool *like* Airflow:

1. **DagTable:** `dag_id (PK), schedule_interval, is_active, last_parsed_time`
2. **DagRun:** `run_id (PK), dag_id (FK), execution_date, state (running/success), start_time`
3. **TaskInstance:** `task_id, dag_id, run_id, state, try_number, hostname (worker)`
* *Key Insight:* The combination of `(dag_id, task_id, run_id)` must be unique.



**Final Recommendation:** Position Airflow as the **"Standard Orchestrator."** Admit its "latency" weakness but highlight its "reliability" and "ecosystem" strength. It is the glue that holds the modern data stack together.