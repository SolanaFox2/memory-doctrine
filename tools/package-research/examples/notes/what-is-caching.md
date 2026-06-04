---
title: What is caching
---

# What a cache is

A cache is a small, fast store that holds copies of data so future requests for
that data can be served without redoing expensive work. The first time a value
is computed or fetched it is saved; later requests read the saved copy instead.

# Why caches help

Caches help because reading from a nearby fast store is much cheaper than
recomputing a result or fetching it from a slow source. A cache trades a modest
amount of memory for a large reduction in latency on repeated requests.
