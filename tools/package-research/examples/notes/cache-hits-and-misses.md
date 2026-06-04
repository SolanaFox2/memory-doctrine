---
title: Cache hits and misses
---

# Hits and misses

A cache hit happens when requested data is already in the cache and can be
returned directly. A cache miss happens when the data is absent, so the system
must fetch or compute it from the slower source and then store the result.

# Hit rate

The hit rate is the fraction of requests served from the cache. A higher hit
rate means more requests avoid the slow path, so the average response time drops
as the hit rate rises. Workloads where the same items are requested repeatedly
tend to have high hit rates.
