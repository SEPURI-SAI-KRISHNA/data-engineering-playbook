# Postgresql fuzzy based search
You don't necessarily need to spin up a separate Elasticsearch cluster. PostgreSQL has excellent built-in extensions that can handle fuzzy search, typo-tolerance, and matching for millions of rows.
Here are the three best ways to do it directly in Postgres.

### The Best All-Rounder: Trigrams (pg_trgm)
This is the closest you will get to Elasticsearch-style fuzzy matching. It breaks text into chunks of 3 characters (trigrams) and compares how many chunks overlap. It is excellent for catching typos (e.g., matching "Postgres" with "Postgrse").

#### Step 1: Enable the extension
```SQL
CREATE EXTENSION pg_trgm;
```


#### Step 2: Create a GIN Index (Crucial for speed)
Without this, the search will be slow on large tables.
```SQL
CREATE INDEX trgm_idx ON my_table USING GIN (my_column gin_trgm_ops);
```

#### Step 3: Query using the % operator

The % operator means "is similar to" based on a threshold (default is 0.3).
```SQL
SELECT * FROM my_table WHERE my_column % 'search_term';
```



#### Step 4: Rank results by similarity
You can order by "distance" (<->), where 0 is a perfect match and 1 is no match.

```SQL
SELECT *, (my_column <-> 'search_term') as distance
FROM my_table
WHERE my_column % 'search_term'
ORDER BY distance ASC;
```

