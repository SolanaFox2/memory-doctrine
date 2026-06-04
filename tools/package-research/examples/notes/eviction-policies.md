---
title: Eviction policies
---

# Why eviction is needed

A cache has limited capacity, so when it fills up it must remove an existing
entry before adding a new one. The rule that decides which entry to remove is
called an eviction policy.

# Common policies

Least Recently Used (LRU) evicts the entry that has gone the longest without
being accessed, on the assumption that recently used items are most likely to be
used again soon. Least Frequently Used (LFU) instead evicts the entry with the
fewest accesses. The best policy depends on the workload's access pattern, so no
single policy is optimal for every case.
