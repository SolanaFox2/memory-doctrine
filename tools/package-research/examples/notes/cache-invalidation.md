---
title: Cache invalidation
---

# The staleness problem

A cached copy can become stale when the underlying source data changes but the
cache still holds the old value. Serving a stale value returns data that no
longer matches the source, so caches need a way to invalidate or refresh
entries.

# Time-to-live

A common approach is a time-to-live (TTL): each entry is given an expiry time,
and once that time passes the entry is treated as invalid and refetched. A short
TTL reduces staleness but lowers the hit rate, while a long TTL raises the hit
rate at the cost of serving older data. Choosing a TTL is therefore a trade-off
between freshness and efficiency.
