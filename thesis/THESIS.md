# The Memory Doctrine
### A Confidence-Weighted, Generative Theory of Memory for Building Knowledge Packages

*A thesis in the theory of memory and knowledge representation.*

**Doctrine v1.3.0 · CC BY 4.0** — the axiom set is as locked in v1.1; releases since have been packaging and publication changes, not content revisions.
**Companion artifact:** the doctrine as a machine-checkable knowledge package — <https://github.com/Treibs/memory-doctrine>

---

## Abstract

Agent memory systems proliferate without a shared account of what memory is. This thesis distills one. Synthesizing primary results across seventeen research domains — the cognitive psychology of encoding and retrieval, the neuroscience of consolidation, reinforcement learning, information theory, epistemology, personal knowledge management, and the engineering of memory systems at scale — it argues that memory is best understood as a *retrieval-optimized network of confidence-weighted, generative truths*, and that a small, cited set of such truths recurs across all of these fields.

It organizes twenty-three of these truths into a defeasible **doctrine** of seven clusters: how knowledge is structured, retrieved, judged true, changed over time, built, what the doctrine knows about itself, and how an agent remembers to act. Along the way it separates three orderings that are routinely and damagingly conflated — *generativity* (how foundational a belief is), *confidence* (how much evidence backs it), and *retrievability* (how easily it is recalled) — and it derives two unifications: that prediction error is a single quantity gating salience, memory-writes, and learning alike (the **Surprise Principle**), and that a portable knowledge package is structurally a *factorized cognitive map*, which is why its generators transfer to new domains.

The doctrine is not merely described but *built*: it is implemented as a self-exemplifying, machine-checkable knowledge package whose own structure obeys the axioms it states, and it is offered as both a **standard** (what a well-formed unit of knowledge looks like) and a **protocol** (how to produce one). Every axiom is cited and was subjected to three independent adversarial review rounds and a full-text citation audit; the methodology is reported in full, including the errors the process caught. The result is intended less as a monument than as a living, falsifiable foundation — a theory layer that agent-memory systems and knowledge-packaging tools can build against, and that anyone is invited to challenge.

---

## Contents

1. Introduction
2. Methodology
3. The Model: Memory as a Network of Generative Truths
4. The Structure of Memory (Cluster A)
5. Retrieval (Cluster B)
6. Truth and Confidence (Cluster C)
7. Dynamics: How Memory Changes (Cluster D)
8. Method: Building and Validating Knowledge (Cluster E)
9. Meta: Convergence, Category Errors, and Two Unifications (Cluster F)
10. Prospective and Agentic Memory (Cluster G)
11. Memory as Productions: The Operators
12. Synthesis and Implications
13. Limitations and Open Problems
14. Related Work
15. Conclusion

Appendix A — Axiom Catalogue · References


---

## Chapter 1 — Introduction

### 1.1 The Problem: A Field Built on Benchmarks Without Theory

In 2024 and 2025, at least five substantial agent-memory systems shipped independently and converged on the same architectural shape. Mem0 (Chhikara et al., 2025), Zep/Graphiti (Rasmussen et al., 2025), MemGPT/Letta (Packer et al., 2023), HippoRAG (Gutiérrez et al., 2024), and GraphRAG (Edge et al., 2024) each independently discovered that graphs outperform flat retrieval for multi-hop questions, that parametric and non-parametric memory serve different functions, and that bi-temporal fact records outperform overwrite. None of them cite the same underlying reason for any of these choices. The convergence is real; the theory that would explain it is missing.

This is not a failure of the engineers who built those systems. It is a failure of the field's theoretical infrastructure. Agent memory has no shared, cited account of what memory *is* — no layer that would let a designer ask "is this the right architecture?" rather than "does this score well on the benchmark?" The result is a proliferating ecosystem of clever implementations built against intuition and task performance, with no framework for knowing which results transfer, which architectural choices are principled, and which are incidental artifacts of the training data or evaluation suite.

The gap is not merely academic. Without a theory layer, every new system must re-learn from first principles which memory representations are retrievable, which are trustworthy, which decay and which consolidate. Every apparent contradiction in the empirical record — "retrieval strengthens memory" versus "retrieval can impair memory," "more connections enrich recall" versus "fan dilution degrades it" — has to be resolved by intuition rather than by a principled account that would show the two claims apply to different quantities and are both correct. The field accumulates implementations without accumulating understanding.

This thesis supplies the missing layer. It does so not by proposing yet another system, but by going upstream: synthesizing the primary results of seventeen research domains — cognitive psychology, neuroscience, reinforcement learning, information theory, formal epistemology, the engineering of cognitive architectures, and more — into a portable, auditable, confidence-weighted *doctrine* that is at once a standard and a protocol for building knowledge packages.

---

### 1.2 The Thesis Statement

The central argument of this thesis is this:

> **Memory is best understood not as a store of facts but as a retrieval-optimized network of confidence-weighted, generative truths.** Across seventeen research domains, the same small set of fundamental truths recurs. These can be distilled into a portable, auditable doctrine that is at once a standard — specifying what a well-formed unit of knowledge looks like — and a protocol — specifying how to build one.

Each word in the core reframe carries weight. *Retrieval-optimized* signals that the network is structured for the paths a reasoner actually traverses, not for storage convenience: a node isolated from the network is not merely hard to reach, it is in a meaningful sense empty. *Confidence-weighted* signals that the network is a belief network, not a database: beliefs are held at degrees — credences that are earned from verified evidence and revised on new evidence, not on retrieval frequency or fluency (Ramsey, 1926/1931). *Generative truths* is the novel theoretical pivot: some truths are disproportionately load-bearing in that they generate downstream structure; a domain's F = ma is more entrenched than its derived results, and revision under pressure touches the periphery before the core — a gradient formalized by AGM epistemic entrenchment (Alchourrón, Gärdenfors, & Makinson, 1985).

Three quantities that the field routinely conflates are kept strictly separate throughout: generativity (how much downstream structure derives from a belief, i.e., entrenchment), confidence (the evidence-earned credence), and retrievability (the volatile activation level that decays with disuse and is restored by retrieval). The conflation of any pair is not merely imprecise — it is a category error with direct engineering consequences. The most common instance is treating high retrieval frequency as evidence of high confidence, which replicates the human feeling-of-knowing miscalibration (Koriat, 1993) at machine speed. The doctrine's three-orderings firewall (axiom C2) is the central architectural constraint separating them.

The doctrine is organized into twenty-three axioms across seven clusters (A–G). Every axiom is cited, confidence-scored, and generativity-scored. The thesis was built adversarially — three independent red-team rounds plus a full-text citation purge — and the errors that process caught are reported, not suppressed.

---

### 1.3 Six Contributions

**Contribution 1: A cross-domain synthesis into 23 cited, confidence-weighted axioms in 7 clusters** (Chapters 4–11, with the complete catalogue in Appendix A). The synthesis covers seventeen research beats — from Hopfield network capacity mathematics (Amit, Gutfreund & Sompolinsky, 1985) to encoding specificity (Tulving & Thomson, 1973), from AGM belief revision (Alchourrón, Gärdenfors, & Makinson, 1985) to Shannon's rate-distortion theorem (Shannon, 1959). The claim is not that these domains are all saying the same thing in different words. It is the more precise claim that each domain contains a small number of high-generativity results that, when extracted and examined across domains, are found to be isomorphic — the same constraint surfacing at different levels of description.

**Contribution 2: The reframe — memory as a network of generative truths, where value is in the edges** (Chapter 3). The storage-warehouse metaphor of memory misleads on the dimensions that matter most for knowledge-package design: it implies that nodes are the unit of value, that capacity is the central design problem, and that a richer node is a better node. The reframe reverses these: the unit of value is the edge, the central design problem is retrieval geometry, and a node with no connections is epistemically inert. This is not a metaphor; Chapter 3 establishes it as a consequence of foundherentist epistemology (Haack, 1993) combined with the cognitive-science evidence on spreading activation.

**Contribution 3: The two/three-orderings firewall — generativity, confidence, and retrievability are independent and must never be collapsed** (Chapter 6, axiom C2). The Bjork and Bjork (1992) New Theory of Disuse established that storage strength and retrieval strength are empirically dissociable. The thesis extends this into a three-way separation and argues that each ordering requires its own update rule: entrenchment changes when better generators emerge; confidence changes when evidence changes; retrievability changes when activation events occur. Collapsing any pair produces not imprecision but a definite, identifiable error — the thesis traces each conflation to a specific engineering failure mode.

**Contribution 4: Two unifications** (Chapter 9). The *Surprise Principle* (axiom F3) shows that prediction error is a single computational quantity doing three jobs simultaneously: gating what gets encoded at arousal intensity (C4), gating whether a retrieved trace is rewritten or merely reinforced (D2), and governing the learning-rate term in all gradient-descent frameworks. Rescorla and Wagner's (1972) conditioning formula, Schultz, Dayan and Montague's (1997) dopamine recordings, and predictive-coding theories are not three separate mechanisms — they are one quantity at three levels of description. The *cognitive-map unification* (axiom F4) shows that a knowledge package is structurally a factorized cognitive map: the index/store split (B4), spreading-activation retrieval (B1), and the factorization of relational structure from content (Behrens et al., 2018; Constantinescu, O'Reilly & Behrens, 2016) are the same architectural object described from different vantage points. Both unifications are novel theoretical results of the synthesis, not summaries of prior literature.

**Contribution 5: A method — the doctrine as a self-exemplifying, buildable knowledge package with operators-as-productions** (Chapters 8 and 11). The doctrine does not merely describe how to build knowledge packages; it is itself built as one. Every axiom satisfies the node schema enforced by a `kpm doctor` linter. The schema requires a confidence score, a generativity score, typed edges, and at least one independently checked citation for every locked axiom. More importantly, the doctrine ships not only its axioms but the rules for revising them — four operators (D4 contract, D5 suppress, E3 lint, E5 compile-on-impasse) that implement the procedural memory the declarative axioms require. A doctrine that cannot revise itself is not defeasible; it is merely labeled defeasible.

**Contribution 6: An adversarial rigor methodology** (Chapter 2). The doctrine was built through three independent red-team rounds and a full-text citation purge by five independent agents. The methodology is reported in full, including the real errors the process caught before release: a hallucinated citation (the RAPTOR paper had been attributed to "Yang et al."; the correct authors are Sarthi et al., 2024, arXiv:2401.18059 — caught in the citation audit and corrected); a missing axiom (E2, retrieval practice / desirable difficulty, which was absent from cluster E and was added); a misattributed philosophical position (Quine was initially cast as a foundherentist; he is a holist — corrected in depth re-grounding); and a source inversion together with a formula error (a Bjork storage-vs-retrieval-strength inversion, and the fan law stated as a "1/n split" then corrected to the logarithmic S − ln(fan)). The released doctrine contains zero fabricated citations. The methodology is itself a contribution to the practice of building knowledge artifacts: adversarial verification is not a formality, and it catches real errors.

---

### 1.4 Roadmap: Seven Clusters and the Arc Through Them

The twenty-three axioms of the doctrine are organized into seven clusters, corresponding to Chapters 4–11. The clusters are not filing categories; they are retrieval units whose internal edge density is high enough that activation from any node in a cluster reaches its neighbors quickly. A brief orientation to each:

**Cluster A — Structure (Chapter 4)** establishes the three foundational constraints on how a knowledge network is built. The fan law (A1) quantifies the retrieval cost of promiscuous edge-making: each outgoing edge dilutes the activation that reaches all others, with the dilution following a log law (`Sᵢⱼ = S − ln(fanⱼ)`). Atomicity (A2) specifies that each node must contain exactly one self-contained idea — not for aesthetic tidiness but because composability requires it. Foundherentist generativity (A3) establishes the epistemological architecture: justification is both foundational (every locked axiom requires external, independently checked citations) and coherentist (mutual support across the graph amplifies justification). Structure is load-bearing: errors here propagate into every downstream process.

**Cluster B — Retrieval (Chapter 5)** delivers one of the thesis's strongest results: spreading activation, modern Hopfield dynamics, and transformer attention are not analogous — they are the same update equation (Ramsauer et al., 2020). Retrieval is energy-descent pattern completion over a content-addressable store (B1). What gets completed depends entirely on the cue — the encoding-specificity principle establishes that cue effectiveness is fixed at encoding, not at retrieval time (B2; Tulving & Thomson, 1973). The store has a sharp capacity cliff, not a gentle slope: classical Hopfield networks collapse above approximately 0.138N stored patterns (B3; Amit, Gutfreund & Sompolinsky, 1985). That constraint forces a two-tier architecture — a sparse, fast-write index on top of a rich distributed store (B4; Teyler & DiScenna, 1986; McClelland, McNaughton & O'Reilly, 1995). The KPM design prescription follows as an architectural necessity, not a preference.

**Cluster C — Truth and Confidence (Chapter 6)** argues that a memory system's confidence reports require three separately maintained scores. Confidence is a credence earned from external evidence, never from retrieval fluency or frequency (C1; Ramsey, 1926/1931; Koriat, 1993). The three orderings — entrenchment, confidence, retrievability — are independent and must never collapse (C2). High confidence does not certify truth: in any gist-based store, confidently-false memories are a mathematical inevitability priced by Shannon's rate-distortion curve (C3; Roediger & McDermott, 1995). And salience strengthens encoding while simultaneously inflating felt confidence without improving accuracy (C4; McGaugh, 2004; Talarico & Rubin, 2003) — the two signals must be architecturally segregated.

**Cluster D — Dynamics (Chapter 7)** describes how the network changes. Retrievability decays from three independent drivers — disuse (power-law decay), competition (retrieval-induced forgetting, Anderson, Bjork & Bjork, 1994), and deliberate suppression (Bjork, 1989) — while evidential confidence remains orthogonal (D1). Memory traces re-open for rewriting on retrieval, but only when retrieval carries a prediction error; pure re-confirmation reinforces retrievability without destabilizing the trace (D2; Nader, Schafe & LeDoux, 2000; Sevenster, Beckers & Kindt, 2013). Consolidation safely transfers traces toward cortical storage, but requires promote-and-keep-indexed rather than promote-and-detach (D3; McClelland, McNaughton & O'Reilly, 1995).

**Cluster E — Method (Chapter 8)** closes the production loop. Layered distillation (E1) is Shannon-bounded: a generator layer approximates the source's irreducible entropy H; elaboration above H is recoverable redundancy; any compression below H incurs distortion priced by the rate-distortion curve (Shannon, 1948; Shannon, 1959). Retrieval practice (E2) exploits the interaction between low retrievability and maximum storage-strength gain: desirable difficulty is not sadism but the formal consequence of Bjork and Bjork's (1992) two-strength model (Roediger & Karpicke, 2006). Adversarial verification (E4) is the anti-Gettier guardrail: Haack's (1993) independent-security criterion — that a belief must be supportable from multiple, independent evidence lines without circularity — is the operational test for whether a belief constitutes knowledge rather than merely justified true coincidence.

**Cluster F — Meta-principles (Chapter 9)** is the doctrine's capacity to reason about its own evidence base, and the home of the thesis's two novel unifications. Convergence-corroboration (F1) formalizes Whewell's (1840) consilience of inductions: the highest-confidence evidence is an independent rederivation that meets an existing result from a different direction. The contradictions-as-category-errors principle (F2) is both a diagnostic and a historical record: every apparent internal contradiction in the doctrine resolved by identifying a term that carried two meanings. The Surprise Principle (F3) and the cognitive-map unification (F4) are developed in full in Chapter 9.

**Cluster G — Prospective and Agentic Memory (Chapter 10)** adds the future tense. An agent that perfectly maintains its retrospective-memory machinery can still miss a deadline or fail to act, because remembering *to do something at the correct future moment* is a distinct cognitive operation (McDaniel & Einstein, 2000). G1 specifies the design preference for focal, event-driven triggers over sustained monitoring loops. G2 governs the full lifecycle of a stored intention — from the intention-superiority effect at encoding (Goschke & Kuhl, 1993), through execution, to the inhibition-on-completion that closes the loop and prevents zombie intentions that linger past their discharge.

The arc through the clusters is not merely additive. Three cross-cluster connections carry the thesis's most generative claims. A3 (foundherentist-generativity) directly grounds both C1 (confidence must be earned) and C2 (three orderings). The Surprise Principle (F3) unifies C4, D2, and the reinforcement-learning prediction-error literature into one computational story. The cognitive-map unification (F4) shows that B1 and B4 describe the same underlying object at different levels of description, and that a knowledge package is a factorized cognitive map in Behrens et al.'s (2018) sense.

Following the cluster chapters, Chapter 11 develops the four operators (D4 contract, D5 suppress, E3 lint, E5 compile-on-impasse) — the procedural layer without which the declarative axioms cannot revise themselves. Chapter 12 synthesizes the doctrine as a whole and positions it against the vendor-memory landscape it is designed to theorize. Chapter 13 gives an honest account of the limitations: the E1 Shannon bound cannot yet be linted because no joint-entropy estimator for confidence-weighted heterogeneous knowledge graphs exists; the F4 cognitive-map unification holds at the structural level but the grid-code geometry may not transfer from continuous two-dimensional concept spaces to high-dimensional discrete graphs; the reconsolidation boundary conditions underlying D2 have a 2022 failed replication. Chapter 14 situates the doctrine against cognitive architectures, the cognitive-map tradition, AGM belief revision, information theory, and the PKM/Zettelkasten lineage.

---

### 1.5 How to Read This Thesis

Three properties of the doctrine bear repeating at the outset, because they govern the register of every chapter that follows.

**The doctrine is defeasible.** Every axiom carries a confidence score that is an honest credence — a degree of belief earned from the evidence available at the time of writing, open to revision on new evidence. Confidence scores in the locked doctrine range from 0.74 (the intention-lifecycle axiom G2, where the prospective-memory evidence base is thinnest) to 0.95 (the spreading-activation identity B1, where the mathematical proof of equivalence leaves little room). "Locked" means passed the current verification standard, not immune from revision. The schema that every axiom satisfies makes revision transparent and auditable: a `contradicts` edge carries a defeater, a `confidence` score can be lowered, and the evidence record is append-only — a retracted belief's evidential history survives so it can be rehabilitated if future evidence warrants.

**The doctrine was adversarially built.** The methodology chapter (Chapter 2) reports the full three-round process, including the specific errors it caught. The report is not a credential; it is documentation that the adversarial process was real and that it found real problems. A reader who believes the process was insufficient should engage with the locked axioms directly: each carries the evidence IDs from which its confidence was derived, and the contradiction resolution documents are part of the public record.

**An axiom catalogue is in Appendix A.** Readers who prefer to read the doctrine's twenty-three axioms and four operators as a structured table before encountering the chapter-by-chapter argument are encouraged to do so. The appendix gives each axiom's ID, short name, statement, generativity score, confidence score, and key evidence in a single table. The chapters that follow develop the justification; the appendix is the what without the why.

One last note on the thesis's own epistemic posture. The central claim — that the same fundamental truths recur across seventeen domains — is itself a high-generativity claim that sits at the core of the doctrine's web of belief. If it is wrong, a great deal else has to be revised. The argument for it is primarily the convergence evidence assembled in Chapters 4–11: the same claim, surface in independent literatures using independent methods, is convergent in Whewell's (1840) sense and corroborating in the F1 sense. The argument has been challenged three times by independent reviewers and survived each challenge. That is not proof; it is the best available evidence for a theoretical claim of this scope. The doctrine says exactly as much, and no more.



---

## Chapter 2 — Methodology

### 2.1 Overview

This chapter describes the research program that produced the doctrine: how seventeen domains were synthesized into candidate axioms, and how those candidates were subjected to a multi-round adversarial verification harness before any axiom was locked. The methodology is itself a contribution. The doctrine is a *defeasible* artifact, and its defeasibility is only meaningful if the process can be inspected and challenged.

A second purpose is definitional. The primary unit of analysis is the *knowledge node* — a schema that encodes not just a claim but its epistemic status, generative power, and typed relationships. Section 2.3 describes this schema. The methodology and the data structure are inseparable: the rigor harness operates on schema fields, and confidence calibration is enforced by the schema's write rules.

---

### 2.2 The Research Program: Seventeen Domains and the Distillation Strategy

The thesis's core claim — that a small set of fundamental truths about memory recurs across research domains (Chapter 3) — requires a research program wide enough to surface genuine cross-domain convergence rather than local rediscovery within a single literature. The research was organized into seventeen *beats* (named domain-focused investigations): cognitive psychology; memory-systems taxonomy; chunking and expertise; semantic networks; computational models; engram consolidation; forgetting and consolidation; forgetting, information theory, and collective memory; AI and machine memory; epistemology; PKM and note-taking; information organization; salience, errors, and metamemory; reinforcement learning; spatial and cognitive maps; working and prospective memory; and developmental/clinical memory — supplemented by depth passes on belief revision, cognitive architectures, systems engineering, and transactive memory.

The strategy within each beat was **distillation-then-adversarial-synthesis**: first, extract the domain's *fundamental truths* — its F=ma equivalents, the claims with highest generativity (the capacity to derive downstream structure) and strongest evidential grounding. Then ask whether those truths appeared, in isomorphic form, in other beats. Convergence across independent disciplines — what Whewell (1840) called *consilience of inductions* — raises the confidence in a candidate axiom; a truth visible only from inside one domain is a local finding, not a doctrine candidate.

The research program was therefore not a literature survey but a confidence-weighted extraction exercise. Every claim that survived to the locked doctrine was required to carry a statement, a named confidence value, a generativity score, and at least one real citation. Claims that could not meet these requirements were downgraded to open problems or discarded.

Wave 1 covered Beats 1–12 and produced twelve draft axioms together with an independent adversarial review that found no fabricated citations but identified three sharp internal contradictions and one significantly distorted source reading. Wave 2 performed depth re-grounding — reading primary papers for the most load-bearing axioms, not only their abstracts — and produced three formal contradiction resolutions and a set of source corrections. Wave 3 added five gap-domain beats, a full-text citation purge by five independent agents, and a third red-team focused on the new additions. The result was the locked doctrine, version 1.1, after all three gates passed.

---

### 2.3 The Node Schema as the Unit of Analysis

The doctrine's primary unit of analysis is the **knowledge node** — an individual axiom encoded in a typed schema. The schema was designed to enforce the thesis's core epistemological commitments, making it structurally impossible to store an ungrounded or ambiguously-weighted claim.

A fully populated node carries: `id`, `type` (axiom / derived-finding / open-problem), `cluster` (A–G), `statement` (one-line claim), `generativity` (1–5), `confidence` (0.0–1.0), `status` (draft / candidate / locked), `relations` (four typed edge lists: `derives-from`, `supports`, `contradicts`, `generalizes`), `evidence` (citation IDs pointing to the evidence store), `provenance` (source beat), and `verification` (whether citations were independently spot-checked and which gate was passed).

Each field carries a methodological commitment.

**Generativity** (1–5) encodes *epistemic centrality*, not importance in a vague sense. Inspired by Quine's web of belief — where logic and mathematics sit at the center because revising them would unsettle the most — generativity scores measure how many other nodes in the doctrine depend on a given node via `derives-from` or `generalizes` edges (Quine, 1951). A generativity-5 node is a hub whose removal would require cascading revisions; a generativity-1 finding is peripheral and revised first when evidence changes. This gradient operationalizes the foundherentist epistemological stance described in Chapter 3: the doctrine has both axiom-roots (high generativity) and a coherentist web of mutual support (the typed edge graph).

**Confidence** (0.0–1.0) is a *credence* — a Bayesian degree of belief — governed by the axiom confidence-earned (C1). Ramsey (1926) formalized the idea that rational belief comes in degrees obeying the probability axioms, updatable by conditionalization on evidence. The schema enforces this: confidence changes *only* when evidence changes. It does not decay from disuse (that would conflate evidential warrant with retrievability, the category error identified in Resolution 2 of Wave 2; see Bjork and Bjork, 1992). It does not rise when a node is retrieved frequently (Koriat, 1993, demonstrated that the human feeling-of-knowing is systematically miscalibrated by exactly this confound). The `kpm doctor` linter enforces this by flagging any write path that allows a non-evidence event to mutate the `confidence` field.

**Typed edges** carry the doctrine's claim that value lives in connections, not nodes. Four types are distinguished: `derives-from` (epistemic dependency — a derived node's confidence is bounded by its parents), `supports` (corroborating evidence), `contradicts` (a defeater, requiring resolution before locking), and `generalizes` (instance-of). Untyped `related` edges are rejected by the linter: they consume fan budget (Anderson, 1974) without carrying distinctive retrieval signal.

**Cited evidence** is a hard requirement for `axiom`-type nodes, implementing the proper-basicality criterion from foundationalist epistemology (Haack, 1993): an axiom earns its status through external grounding, not through position in the network. The `verification` field records whether citations were spot-checked by an independent agent — the schema's anti-Gettier layer (Gettier, 1963), tracking not just that evidence exists but that the belief was reached by a reliable process.

The schema is *self-exemplifying*: every axiom in the final doctrine satisfies it, was authored using the node structure, and passed the verification gate. This property makes the doctrine a usable *standard and protocol* rather than a merely theoretical account.

---

### 2.4 The Rigor Harness: Three Red-Team Rounds and a Full-Text Purge

The verification harness had three independent gates, each designed to catch a different class of error.

**Round 1 (adversarial review of v0)** independently examined the twelve-axiom spine for contradictions, over-claimed citations, and analogy-stretches. Eight citations were spot-checked: all were real and traceable. No fabricated references were found. Three synthesis defects were identified:

1. The contradiction between the v0 draft axioms M5 (confidence must not decay with disuse) and M6 (confidence decays without reinforcement). The diagnosis was a category error: the two axioms were applying "confidence" to two distinct quantities — evidential warrant and retrieval accessibility — that Bjork and Bjork (1992) had already formally separated in their New Theory of Disuse. The resolution was not a compromise but a structural split: two independent score fields, governed by different update rules, resolved in the Contradiction Resolutions document and instantiated in the schema's `confidence` vs. `retrievability` fields (Chapter 7).

2. The tension between "value lives in the edges" and "sparse links win (fan effect)." Again a category error: the first is a claim about *where meaning is encoded* (positional semantics); the second is a claim about *the cost structure of retrieval* (fan dilution, formally `Sᵢⱼ = S − ln(fanⱼ)`; Anderson, 1993; Schneider & Anderson, 2012). The resolution unified them into the fan-budgeted-edges axiom (A1): maximize signal per edge, not raw edge count (Chapter 4).

3. The over-compression of M9 (distill generators), which the generation-effect literature (Slamecka & Graf, 1978) suggested would discard the encoding value that elaboration produces. Resolved into the layered-distillation axiom (E1): distill the generator at the top, preserve the elaboration beneath, link to the evidence store — a layered structure independently validated by RAPTOR (Sarthi et al., 2024).

**Wave 2 depth re-grounding** read primary papers for the most load-bearing axioms — not their abstracts — and produced eight nuances and corrections. The most consequential:

- Quine (1951) was being misread. The spine had attributed "foundationalism with protected core axioms" to Quine, but Quine's confirmation holism explicitly denies foundational protection: the core is revised last *by pragmatic conservatism*, not by epistemic immunity — even logic is in principle revisable. The correction separated the foundationalist half (attributable to Haack, 1993, who coined *foundherentism*) from the Quinean web half, and this distinction became the epistemological stance of Chapter 3.

- Miller (1956) was being misused. Miller's durable claim is about *chunking and recoding* — aggregation into richer units — not atomization. The fan effect's 1/n law is Anderson's (1974), not Miller's.

**Wave 3 (the full-text purge)** deployed five independent agents to re-read all breadth beats against primary sources. The citation audit also caught the hallucinated attribution of the RAPTOR paper (credited to "Yang et al." in the draft; the correct authors are Sarthi et al., 2024) — this was corrected before locking. The tally: zero locked axioms overturned, five confidence scores adjusted, two source-characterization corrections, one citation attribution corrected. The process confirmed the most critical readings — Bjork and Bjork on the non-decay of storage strength, and McClelland et al. (1995) on complementary learning systems — at primary-source depth.

**Red-team #3** focused on the Wave-3 additions (the Surprise Principle, the cognitive-map unification, cluster G, and the new operators D5 and E5). All additions passed with five honesty-tightening edits. Two of these edits illustrate the kind of over-claim the harness is designed to catch:

- The Surprise Principle initially described prediction error as "the same signal" at three levels of description. Red-team #3 tightened this to "the same *computational quantity* at three levels of description" — behavioral, dopaminergic, cortical — because "same signal" implies a direct neural identity that the evidence does not license.

- The cognitive-map unification initially stated that a KPM is "literally" a factorized cognitive map. Constantinescu et al. (2016) demonstrate a grid code for two-dimensional *continuous* concept spaces; whether high-dimensional discrete KG embeddings inherit the same grid structure is unsettled. The fix was a single word: *structurally* rather than *literally* (Behrens et al., 2018). Everything substantive in the unification survives; the overclaim does not.

The lock record is explicit: three independent gates, zero axioms cut, zero new research required after Wave 3. The process was designed so that no single reviewer — including the authors — could lock an axiom without it passing a challenge round. The five post-lock corrections in Red-team #3 are visible in the spine, labeled, and traced to their source.

---

### 2.5 What the Process Caught: Real Errors, Not a Formality

A rigor harness is only meaningful if it catches real errors. The doctrine was built in adversarial stages. This section names what the process actually caught before release.

**A hallucinated citation.** The RAPTOR paper had been attributed to "Yang et al." in an early draft; the correct authors are Sarthi et al. (2024) (arXiv:2401.18059 — same paper, wrong attribution). The error was caught in the citation audit and corrected before any axiom depending on RAPTOR was locked.

**A missing axiom.** E2 (retrieval practice / desirable difficulty) was absent from cluster E. Wave 2 depth re-grounding on Bjork and Bjork (1992) revealed that the original M6 not only misstated the theory but omitted its most practically consequential consequence: the largest storage gains from retrieval practice occur precisely when retrievability is *low* — the formal basis of desirable difficulty and spacing. Its absence would have left the doctrine's scheduling implications incomplete. E2 was added explicitly and is now encoded in the interaction model of D1 and E2 (Chapters 7 and 8).

**A misattributed philosophical position.** Quine was initially cast as a foundherentist. His confirmation holism explicitly denies foundational protection: the core is revised last by pragmatic conservatism, not by epistemic immunity — even logic is in principle revisable. The correction separated the foundationalist half (attributable to Haack, 1993) from the Quinean web half, and this distinction became the epistemological stance of Chapter 3.

**A source inversion and a formula error.** The purge caught a Bjork storage-vs-retrieval-strength inversion in a secondary characterization: the doctrine had initially carried an account with the directionality reversed. Separately, the fan law had been stated as a "1/n split" in an early draft and was corrected to the logarithmic form S − ln(fan), following the ACT-R formalization (Anderson, 1993; Schneider & Anderson, 2012). Both corrections were applied before locking.

After these corrections, the released doctrine contains zero fabricated citations. These are not hypothetical errors the harness *might* have caught. They are errors it *did* catch, in the documented rounds.

---

### 2.6 Defeasibility and Confidence Calibration

The doctrine is explicitly defeasible — open to revision. This is not a concession but a commitment. The foundherentist epistemological stance (Chapter 3) treats justification as non-monotonic: new evidence can defeat a previously warranted claim (Pollock, 1987). The schema makes this operational: a `contradicts` edge carries a defeater, a `confidence` score can be lowered by conditionalization on new evidence, and the `status: locked` field means *passed the current verification standard* rather than *immune from revision*.

Confidence calibration operates by two principles the harness enforced throughout.

First, confidence is *earned* from evidence, not asserted. An axiom with no independently checked citations cannot hold high confidence. The doctrine's twenty-three axioms were all verified; open problems are explicitly labeled as unresolved.

Second, the three orderings are *independent* (axiom C2, Chapter 6): generativity (entrenchment), confidence (evidential warrant), and retrievability (current activation) must never be conflated. The most common conflation in existing agent memory systems is treating high retrieval frequency as evidence of high confidence — a direct replication of the Koriat (1993) human miscalibration at machine speed. The methodology addressed this structurally: every read operation on the doctrine may update retrievability but is formally barred from touching confidence unless it also carries new evidence.

Confidence values in the final doctrine range from 0.74 (the intention-lifecycle axiom G2) to 0.95 (the spreading-activation identity B1). Where evidence is fragile — reconsolidation boundary conditions (Sevenster et al., 2013, with a 2022 failed replication noted), the contested Multiple Trace Theory (Nadel and Moscovitch, 1997) — confidence is set lower and the uncertainty is named. Defeasibility as a feature, not a bug, means the doctrine does not oversell.

---

### 2.7 The KPM Build as Methodological Proof

The doctrine was not only written about KPMs; it was built *as* one. The memory-doctrine KPM contains the twenty-three axioms and four operators as schema-conformant files, with a `kpm doctor` linter enforcing the invariants described in Section 2.3. If the schema is self-applicable, the doctrine's design principles survive contact with their own constraints.

One genuine limitation surfaced: the Shannon bound on layered-distillation (E1) is sound as a mathematical principle — distillation cannot compress below irreducible entropy H without lossy distortion priced by the rate–distortion curve R(D) (Shannon, 1948; Shannon, 1959) — but no estimator for a KPM's joint entropy currently exists. The linter labels this a principle/invariant rather than an executable lint; it is an open problem (Chapter 13).

The build also instantiates the doctrine's claim that a KPM should ship not just axioms but the rules to revise them. The adversarial-verify operator (E4) and the contract operator (D4) are part of the package. A doctrine that cannot revise itself is not defeasible; it is merely labeled defeasible.

---

### Summary

The methodology has four load-bearing components: (1) a cross-domain synthesis program covering seventeen research beats, organized by distillation of the highest-generativity findings; (2) a node schema that encodes confidence, generativity, typed edges, and cited evidence as hard requirements for every locked axiom; (3) a three-round adversarial rigor harness — with a full-text purge pass — that caught a misattributed citation, a missing axiom, and a source inversion before the doctrine was locked; and (4) a defeasibility commitment that is structural, not rhetorical: confidence is earned from evidence, the three orderings are kept strictly separate, and the schema makes revision transparent and auditable. The next chapter builds the model on this foundation.


---

## Chapter 3 — The Model: Memory as a Network of Generative Truths

### 3.1 The Reframe

The account of memory that drives this thesis departs from the dominant storage metaphor. In the storage view, memory is a warehouse: items go in, accumulate, and are fetched by address or similarity. The metaphor misleads in the ways that matter most: it suggests that the unit of value is the item, that more items equals more memory, and that the critical design problem is capacity. None of these implications survive contact with the evidence.

The alternative is this: **memory is a retrieval-optimized network of confidence-weighted, generative truths.** Each word in that phrase is load-bearing.

*Retrieval-optimized* signals that the network is not structured for storage convenience but for the paths a reasoner will actually traverse. Ross Quillian's founding insight — that the meaning of a concept is constituted entirely by its pattern of connections to other concepts, not by any content stored *inside* it — is the cleanest expression of this (Quillian, 1968). A node isolated from the network is not merely inaccessible; it is, in a meaningful sense, *meaningless*. The activation that drives retrieval is not a spotlight pointing at a location; it is a wave that propagates along weighted edges (Collins & Loftus, 1975). The implication is that a knowledge package which invests heavily in node content but neglects edge structure is investing in the wrong asset.

*Confidence-weighted* signals that the network is a belief network, not a database. Beliefs — including scientific laws — are held at degrees, not binarily. Frank Ramsey established in 1926 that rational degrees of belief are credences obeying the probability axioms, updated on evidence by conditionalization (Ramsey, 1926/1931). Every node in the doctrine network therefore carries a `confidence` field, and that field is an epistemic object: it can be raised by corroborating evidence, lowered by a defeater, and must never be raised by mere fluency, recency, or retrieval frequency — the systematic confounds that make human self-assessments of confidence chronically miscalibrated (Koriat, 1993). The confidence field is not an annotation; it is the primary epistemic status marker of the node.

*Generative truths* is the most novel term, and Section 3.2 develops it in detail. The short form: some truths are disproportionately load-bearing. They generate other truths; they are what a domain surrenders last. The network is structured around these generative cores, and the rest of the structure — the elaborations, derivations, supporting evidence — is arranged around them.

---

### 3.2 Every Domain Has Its F = ma

In classical mechanics, one equation — Newton's second law, F = ma — generates an entire domain. Every projectile trajectory, every lever calculation, every collision analysis is a consequence of applying that three-symbol identity plus boundary conditions. The law is not *a* truth in mechanics; it is the *generator* of mechanical truths. Its epistemic status is entirely different from a derived result like the period of a pendulum: if you are forced to contract the theory under pressure from new evidence, you revise the pendulum formula before you revise F = ma.

This asymmetry is not confined to physics. Every domain has its generators: the law of supply and demand in economics, the central dogma in molecular biology, the regress argument in epistemology, the fan law `Sᵢⱼ = S − ln(fanⱼ)` in cognitive activation theory (Anderson, 1974). The generators are domain-relative — they are not universal laws that transfer across fields — but within a domain they play the same structural role: from a small number of high-generativity truths, the domain's working knowledge is recoverable.

The formalization of this notion already exists in the belief-revision literature. Alchourrón, Gärdenfors, and Makinson (1985) — the AGM framework — define *epistemic entrenchment* as the ordering that specifies which belief a rational agent surrenders last when forced to contract a theory. The entrenchment ordering satisfies four postulates: transitivity, the dominance condition (if p entails q then p ≤ q — more specific beliefs are less entrenched than their generators), minimality (non-believed propositions are least entrenched), and maximality (tautologies are maximally entrenched). The dominance postulate is directly the claim that generators are more entrenched than the truths they generate. F = ma is more entrenched than the pendulum formula because F = ma entails the pendulum formula (given boundary conditions), not the reverse.

The doctrine operationalizes this as the `generativity` field, scored 1–5. A `generativity: 5` axiom is a domain's F = ma: a truth from which substantial downstream knowledge can be recovered, held at the highest epistemic protection, revised only under strong multi-source evidence. A `generativity: 1` finding is a leaf node — empirically grounded, perhaps important, but not a generator of other truths within the package. The revision policy falls out immediately: when a new finding conflicts with existing knowledge, revise the least entrenched (lowest-generativity) belief in the conflicting set first, and cascade any required updates outward. This is the doctrine's "periphery first" rule (Chapter 4).

Two clarifications are essential. First, generativity is *not* the same as confidence. A truth can be a generator and be held at moderate confidence — "price ≈ probability" in prediction-market design is a genuine generator of that domain's analytic apparatus, but it sits at confidence ~0.75, not 0.99. The independence of these two quantities is the subject of axiom C2 (Chapter 6). Conflating them is one of the most common errors in knowledge-organization practice: a high-confidence finding with low generativity (a well-replicated leaf) is not worth the same investment as a moderate-confidence generator. The doctrine maintains strict separation between the two fields.

Second, generativity is not the same as retrievability — the ease with which a node is activated in a given retrieval context. Retrievability is volatile; it decays with disuse and rises with practice (Bjork & Bjork, 1992). Generativity is a structural property of the node's position in the justification graph. A generator that has not been accessed for six months is dormant, not less generative. The three-orderings firewall — generativity (entrenchment), confidence (evidence), retrievability (activation) — is a first-class architectural constraint of the model, and Chapter 6 treats it in full.

---

### 3.3 The Foundherentist Epistemology

With the generativity concept in place, the question becomes: what is the overall justification architecture of the network? Two classical rival positions frame the answer.

*Pure foundationalism* holds that knowledge has a strict two-tier structure — a base of non-inferentially justified beliefs (the "foundation") from which all other justified beliefs are inferred upward (see Aristotle, *Posterior Analytics*; Descartes, *Meditations*). Foundationalism resolves the regress of justification cleanly: the chain of "why do you believe that?" terminates in basic beliefs that are justified without depending on further beliefs. But it faces two difficulties that are fatal for the doctrine's purposes. First, "properly basic" beliefs — beliefs justified non-inferentially — are philosophically contested. Classical infallibilist foundationalism (Descartes' *cogito*) requires an immune core that cannot be questioned, which is both philosophically untenable and practically fragile as an engineering target. Second, pure foundationalism has no room for mutual support among non-basic beliefs: two well-evidenced beliefs that reinforce each other receive no justificatory credit for that coherence.

*Pure coherentism* resolves this by rejecting the pyramid entirely. A belief is justified by its fit within a system of mutually-supporting beliefs; justification is holistic, not linear (BonJour, 1985; Lehrer, 1974). The graph structure of the doctrine network — where `supports`, `derives-from`, and `generalizes` edges create a web of mutual reinforcement — is an irreducibly coherentist object. But coherentism faces the *isolation objection*: a perfectly coherent fairy tale satisfies all coherentist criteria while making no contact with reality. A knowledge package whose axioms cohere beautifully with each other but cite nothing external to the package is, by coherentist standards, as well-justified as one grounded in a century of experimental science. This is clearly wrong.

Susan Haack's *foundherentism* (1993) resolves the impasse, and the doctrine adopts it as axiom A3 (foundherentist generativity). Haack's crossword analogy is the clearest exposition: in a crossword, entries are constrained *horizontally* (each entry must cohere with the crossing letters of the entries that share its squares) and *vertically* (each entry must fit the clue — an external constraint independent of the other entries). Remove the horizontal constraint and you have pure foundationalism — check only that each entry fits its clue, ignore whether entries conflict. Remove the vertical constraint and you have pure coherentism — check only that entries fit each other, ignore the clues. Both half-crosswords are worse epistemology than the full one.

The doctrine network instantiates both dimensions. The `evidence` field on every axiom is the vertical anchor: a non-empty, citation-checked evidence field is the property-basicality requirement — the axiom earns its status by contact with sources external to the package, not merely by derivation from other nodes in the package. The `derives-from`, `supports`, and `generalizes` edges are the horizontal web: a densely connected node is more justified than an isolated one, because coherence amplifies justification across the graph. Both are required; neither alone is sufficient.

The doctrine's stance on Quine is worth specifying precisely, because the original v0 of the doctrine misattributed its foundationalist intuitions to Quine — an error caught and corrected in the first depth review. Quine (1951) is a *holist*, not a foundationalist: on his web of belief, no statement is immune from revision in principle, including the laws of logic themselves. Quine's holism is the *boundary condition* of the doctrine, not its justification architecture. What it provides is the entrenchment gradient: beliefs at the center of the web (logic, mathematics, high-generativity generators) are revised almost never not because they are immune but because revising them would require revising everything that depends on them — a very high evidential cost. Beliefs at the periphery (low-generativity empirical findings) are revised first because the cost is low. This gradient maps directly onto the `generativity: 1–5` field. Quine's holism and Haack's foundherentism are consistent; Quine supplies the revision dynamics, Haack supplies the justification architecture.

The Gettier problem adds a necessary guardrail. Edmund Gettier (1963) showed that justified true belief is not sufficient for knowledge: a belief can be true, and its justification can be present, yet the truth is arrived at by luck disconnected from the justification process. The practical implication is that confidence alone — however high and however honestly earned — does not guarantee that a node represents knowledge in the robust sense. The doctrine therefore requires a `provenance` field alongside `confidence`: evidence that the belief was reached by a truth-tracking process, not only that it happens to be consistent with a body of evidence. The adversarial verification requirement (E4) is the doctrine's anti-Gettier guardrail, and it is grounded directly in the foundherentist structure: Haack's *independent-security* criterion — that a belief must be supportable from multiple, independent lines of evidence without circularity — is the operational anti-Gettier test (Haack, 1993). Chapter 5 (structure) and Chapter 8 (method) develop these in full.

---

### 3.4 Edges Over Nodes

The epistemological architecture described above has a counterintuitive structural corollary that deserves explicit statement before the chapter closes: **in a well-formed doctrine network, a node's epistemic value is constituted primarily by its edges, not its content.**

This is Quillian's insight applied epistemically. The meaning of CANARY is not stored inside the CANARY node; it is the pattern of connections to BIRD, YELLOW, SING (Quillian, 1968). The epistemic value of an axiom is similarly constituted by what it connects to — which conclusions it supports, which evidence anchors it, which other axioms it constrains. An isolated axiom with rich prose content but no relations is nearly meaningless: it cannot be retrieved in context, cannot propagate activation to related nodes, cannot be used to derive conclusions. The chapter on structure (Chapter 4) formalizes this as the fan law: the activation a node passes to any one of its connections is `Sᵢⱼ = S − ln(fanⱼ)`, a decreasing function of the node's fan (number of connections). Adding a low-signal edge does not enrich a node; it dilutes all the others.

The edges-over-nodes principle has three operational consequences that recur throughout the thesis. First, the unit of memory investment is not the node but the edge: adding a new axiom with no connections is a low-value operation; discovering and encoding a strong connection between two existing nodes is a high-value operation. The `/shard` operation (Chapter 8) is designed to distill connective structure, not to transcribe facts. Second, a coherent package is not one with many nodes but one with short, dense, high-quality paths between its nodes; the global topology of real semantic networks — small-world and scale-free, with short average path lengths and a few well-curated hubs (Steyvers & Tenenbaum, 2005) — is the target architecture. The high-generativity nodes *should* be the hubs. Third, the doctrine's cluster architecture is not a filing convenience but a structural claim: within each cluster, spreading activation from any node reaches the others quickly; cluster boundaries mark where edge density drops. Chapters 4 through 11 each develop one cluster, and those boundaries reflect retrieval geometry, not an imposed taxonomy.

---

### 3.5 Setting Up the Cluster Architecture

The model described above — foundherentist, generativity-structured, edge-primary — requires concrete organization to be usable as a standard and a protocol. The doctrine divides its twenty-three axioms into seven clusters: A (structure), B (retrieval), C (truth and confidence), D (dynamics), E (method), F (meta-principles), and G (prospective/agentic memory). The clusters are not independent filing categories; they are retrieval units whose internal edge density is high enough that activation from any node in the cluster reaches the others quickly. The cross-cluster connections carry the thesis's most generative claims: A3 (foundherentism) directly grounds C1 and C2; the Surprise Principle (F3) unifies C4, D2, and the predictive-coding literature; the cognitive-map unification (F4) shows that B1 and B4 describe the same object at different levels of description.

The remaining chapters develop each cluster in turn. The reader should approach them with the reframe in mind: when the chapters speak of axioms, nodes, and edges, these are not metaphors for memory — they *are* the structure of memory, formalized enough to build with.



---

## Chapter 4 — The Structure of Memory

*Cluster A · Axioms A1–A3*

---

### 4.1 Why Structure Is the Load-Bearing Layer

Chapter 3 established the doctrine's central reframe: memory is not a warehouse of
facts but a retrieval-optimized network of confidence-weighted, generative truths.
If value lives in the network rather than in any individual node, then the rules
governing *how the network is built* are the most consequential rules in the doctrine.
Structural errors propagate into every downstream process — retrieval, belief revision,
distillation. Structural correctness gives those processes a substrate that works.

Cluster A formalizes three structural commitments. The first is quantitative: every
node's retrieval budget is finite and divided logarithmically among its outgoing edges
(A1 fan-budgeted edges). The second is topological: each node must contain exactly one
self-contained idea, because only an atom is composable (A2 atomicity). The third is
epistemological: the justification structure of the network is foundherentist, and the
doctrine's `generativity` field is operationally identical to AGM epistemic
entrenchment (A3 foundherentist generativity). All three are locked axioms with
confidence ≥ 0.85, red-teamed and surviving (see Chapter 2).

---

### 4.2 A1 — Fan-Budgeted Edges: The Logarithmic Dilution Law

#### The empirical result

The fan effect was established by John Anderson in a 1974 study in which participants
learned varying numbers of propositional facts about fictional people and places
(Anderson, 1974). The key finding: reaction time to verify any single fact about a
concept rose monotonically with the number of other facts associated to that concept.
The more an entity was connected to, the slower any one connection became. This is not
a ceiling effect or a task artifact; it is a property of how activation is distributed
in associative memory. Each additional link competes for a finite per-node activation
budget, diluting the share received by every existing link.

The ACT-R 2.0 architecture (Anderson, 1993) formalizes the dilution law exactly:

```
Sij = S − ln(fanj)
```

where `Sij` is the associative strength from context element j to chunk i, `fanj` is
the number of chunks associated to element j (the fan), and S is the maximum possible
associative strength. Two features of this equation are critical, and both require
emphasis because the intuitive misreading of the fan effect gets them backwards.

**First: the law is logarithmic, not linear.** The naive intuition is that activation
splits equally — each of n edges gets 1/n of the budget, so doubling the fan halves
the strength of every edge. The ACT-R equation says something weaker but still
inescapable: doubling the fan costs *less* than halving strength, because ln(2n) =
ln(2) + ln(n), not 2 ln(n). The dilution is sub-linear. This was a v1.1 correction
to the doctrine's original statement, which had implied a linear split. The
logarithmic form was verified against the original evidence (Anderson, 1974; Anderson,
1993) during the citation purge reported in Chapter 2.

**Second: the dilution is real and cumulative regardless of its sub-linearity.** Every
additional fan member still carries a measurable retrieval penalty on all existing
edges. Sub-linear is not zero. There is no free edge. The engineering consequence is
not "don't connect things" but "every edge must earn its place." An edge earns its
place if and only if (a) it is traversed on a real retrieval path, and (b) the
activation it enables to flow outweighs the marginal fan cost it imposes on every
other edge departing the same node.

#### Structural consequences for knowledge packages

The fan law gives the doctrine its first quantitative design constraint. An orphan
node — one with no associations — sits outside the activation network entirely. A
query that activates any other node will never reach it. But an indiscriminately
connected node is worse: it receives activation from everywhere and propagates it
nowhere specifically. It is a retrieval black hole whose very connectedness destroys
the specificity that makes retrieval useful.

The structural ideal is a *sparse, high-signal graph*: nodes connected to the nodes
that genuinely enable or constrain them, and to no others. The relation to retrieval
(Cluster B) is structural: A1 is the direct ancestor of B1. The spreading-activation
mechanism described in Chapter 5 — and its formal equivalents in Hopfield networks and
the attention mechanism of transformers — operates over the edge structure that A1
constrains. The architecture of retrieval assumes the graph obeys the fan budget; an
over-dense graph does not break retrieval, it degrades it, invisibly and monotonically.

---

### 4.3 A2 — Atomicity: One Idea per Node

#### The PKM convergence

The atomicity rule was not derived from cognitive theory; it was engineered from
practice, and independently so. Two traditions arrived at the same structural
requirement across four decades.

Niklas Luhmann's *Zettelkasten* — the physical slip-box that supported approximately
70 books and 400 articles over 45 years — imposed atomicity by constraint: a physical
card can hold one idea (Luhmann, 1981). Luhmann's own account of why this matters is
precise: "Every note is only an element which receives its quality only from the
network of links and back-links within the system." The slip is a unit not because it
is small but because only a unit can be *addressed* — linked to with a specific meaning
rather than a blurry gesture toward a bundle of claims.

Andy Matuschak's evergreen notes canon, developed independently roughly 40 years
later, makes the design principle explicit and names the mechanism (Matuschak, 2019).
The rationale is **composability**, not retrieval speed. An atomic note can be:
linked precisely (the connection points to one clean idea, not a multi-claim blob);
reused across contexts without dragging unwanted cargo; and addressed as a stable unit
in logical derivations. A multi-claim note produces ambiguous edges. Because the links
connect blurry multi-meaning objects, the network's combinatorial power collapses —
each link imports several ideas at once, making the graph's semantics uninterpretable.

The composability rationale deserves a moment's elaboration, because the retrieval
reading is seductive and wrong. A multi-claim node is *retrievable* — a query that
activates it will find it. The failure is downstream: once found, it cannot be reused
cleanly. The activated node carries claims A and B; the context needs only A. A link
*from* this node carries both A and B whether the downstream node wants them or not.
Over many such links, the network accumulates ambiguity at every edge. The whole
apparatus of inferential derivation — what makes a knowledge package generative rather
than archival — requires that each step in a derivation chain have a determinate
meaning. Atomicity is the precondition for that determinacy. (This was clarified as a
v1.1 correction: the original doctrine stated the rationale as retrieval speed, and
the citation purge identified Matuschak's explicit composability framing as the
authoritative statement.)

#### Atomicity as a lint rule

The consequence for knowledge package design is direct. A KPM file that asserts two
generative claims is an atomicity violation and should fail the lint (E3, Chapter 8).
A two-claim node produces at least two distinct justified conclusions that now travel
as a bundle; every edge departing from it carries an ambiguous source, and the graph's
semantics degrade at each such node.

The doctrine itself instantiates A2: each axiom file asserts one claim. The three
orderings treated in Chapter 6 — entrenchment, evidence, and activation — were
conflated in an earlier draft and were *separated* by atomicity analysis during the
citation purge. That split is itself an A2 application: three concepts that had been
bundled into one were each assigned their own node, at which point their distinct
evidence bases and implications became articulable. This is the mechanism Luhmann
called "combinatorial possibilities which were never planned" — available only when
atoms are clean enough to recombine.

---

### 4.4 A3 — Foundherentist Generativity: Structure as Epistemology

#### The correction: not Quine, not foundationalism, not coherentism

The epistemological spine of Cluster A required a v0 correction. The original
research beat attributed the axiom-plus-web architecture to Quine's web of belief.
The attribution is wrong. Quine is a *holist*: his web has no immune core and no
protected beliefs. Using Quine to license a doctrine that designates some axioms as
high-generativity anchors is incoherent — Quine's position is precisely that there
are no such anchors (Quine, 1951).

The corrected position is Susan Haack's **foundherentism** (Haack, 1993). A crossword
has two dimensions of justification:

- **Horizontal** (across entries): the coherentist dimension. Entries constrain and
  reinforce each other, raising the justified confidence of connected clusters.
- **Vertical** (entries anchored to the grid clues): the foundational dimension. Some
  entries are directly checked against external evidence, providing non-circular
  warrant.

Neither dimension is sufficient alone. Pure foundationalism requires a
justification-immune base that is philosophically untenable and practically fragile.
Pure coherentism cannot escape the isolation objection: a coherent fairy-tale can be
internally consistent yet false. The crossword resolves both — the horizontal
coherence structure is checked by the vertical evidence anchors. Quine's holism
(Quine, 1951) sets the boundary condition: no belief is immune from revision *in
principle*. This is compatible with foundherentism — Haack's roots are *more
resistant*, not immune. Quine is the envelope; foundherentism is the architecture.

#### Generativity as AGM epistemic entrenchment

The most precise result of A3 is the identification of the doctrine's `generativity`
field with a formally established quantity. The formal machinery for "which belief do
you surrender last?" already exists in Alchourrón, Gärdenfors, and Makinson's 1985
theory of belief revision (Alchourrón, Gärdenfors & Makinson, 1985). The AGM paper
establishes three typed operators — expansion (add a belief), contraction (remove one
while disturbing as little as possible), and revision (add one while restoring
consistency) — and the rationality postulates constraining them.

The load-bearing concept is **epistemic entrenchment**: the total preorder `≤` over
beliefs where `p ≤ q` means "I would give up p before q." When forced to contract, a
rational agent surrenders the *least entrenched* belief first. Two postulates from the
AGM framework are directly load-bearing for the doctrine:

- **Dominance**: if `p ⊢ q`, then `p ≤ q` — beliefs that are more specific or more
  derived are less entrenched than the beliefs that generate them. This confirms the
  doctrine's claim that derived findings should be revised before their generators.
- **Maximality**: tautologies — the most general truths — are maximally entrenched.
  The doctrine's highest-generativity axioms are those closest to this maximal class:
  truths that generate the most downstream structure and are derivable from the fewest
  upstream assumptions.

The `generativity: 1–5` field in every axiom node IS the epistemic entrenchment
ordering, made operational. The correspondence is exact: high-generativity axioms (5)
are surrendered last; low-generativity findings (1–2) are the revisable periphery.
When new evidence contradicts a package, the contraction policy is: revise peripheral
nodes first; do not touch a `gen=5` root without multi-source, independently secured
evidence.

The AGM postulates technically assume a classical, consistent logical theory as the
belief state; a real KPM graph is paraconsistent (it can hold local contradictions
pending resolution) and probability-weighted. The postulates therefore apply as design
constraints and revision heuristics rather than as directly executable logical rules —
a limit acknowledged in the supporting evidence.

#### The KPM schema as a foundherentist object

The foundherentist structure explains why two fields on every axiom node are
non-negotiable. The `evidence` field is the vertical anchor: it connects the node to
the crossword's clues, providing non-circular grounding. An axiom with an empty
`evidence` field is an unanchored node; it floats in the coherence web without any
external check, which means its confidence cannot be justified and any downstream
confidence it supports inherits the same defect. The `derives-from` / `supports` /
`generalizes` edges are the horizontal structure: they constitute the coherence web
that amplifies justification across the graph.

This also explains why A3 is the epistemological backbone of the doctrine. The
foundherentist structure makes the `confidence` field non-arbitrary: only evidence
(the vertical anchors) can raise confidence, because fluency, recency, and retrieval
frequency cannot substitute for the clues that ground the crossword. It separates the
three orderings treated in Chapter 6 as the doctrine's central firewall: generativity
(entrenchment), confidence (evidence weight), and retrievability (base-level
activation) are distinct orderings. Conflating any two collapses the justification
structure. And it grounds adversarial verification (E4, Chapter 8): Haack's warrant
calculus gives justification as *supportiveness × independent security ×
comprehensiveness*, where independent security is the anti-Gettier requirement that
supporting evidence not derive from the same source as the belief itself (Haack,
1993).

---

### 4.5 The Cluster's Coherence: Why A1, A2, and A3 Are One Architecture

The three axioms are interdependent. A1 says every edge has a cost; add only edges
that pay for themselves. A2 says every node must be a clean atom; only atoms can be
linked precisely enough for edge cost/benefit analysis to be meaningful. A3 says the
justification structure is foundherentist and the revision policy protects
high-generativity anchors. You cannot implement A1 without A2 (cost/benefit requires
knowing what each edge end *means*, which requires atomicity); you cannot implement
A3's revision policy without A1's fan constraint (entrenchment tells you *which* edges
to preserve; A1 tells you *why* preserving them matters for retrieval). A3 is also
what makes `generativity` non-arbitrary: it is the formal entrenchment ordering, not a
subjective importance label.

The confidence calibration: A1 (0.90) rests on one of the most replicated effects in
cognitive psychology with a well-validated functional form. A2 (0.85) is
cross-validated practitioner convergence backed by composability theory — not an
empirical law, but with no credible counter-evidence. A3 (0.88) is a normative
philosophical synthesis with a formal AGM identification; the postulates apply as
design constraints rather than strict logical mandates. None reach 1.0 — that is the
doctrine's honesty signal, not a weakness (Chapter 13 treats the open problems).

The structural layer is load-bearing precisely because its errors propagate maximally.
Build the graph right and every other cluster operates on a sound substrate. Build it
wrong — over-dense, atomicity-violated, with an incoherent justification structure —
and no retrieval mechanism, belief revision policy, or distillation method can
compensate downstream.

---

*Chapter 5 takes the structure as given and asks how retrieval works over it —
the spreading-activation mechanism (B1) and the three further retrieval axioms of
Cluster B.*


---

## Chapter 5 — Retrieval

Cluster B is the operational heart of the doctrine. Where Chapter 4 (Structure) concerned
how knowledge is *organized*, this chapter concerns how any of it is ever *found*. The four
B-cluster axioms form a deductive chain: retrieval is energy-descent pattern completion (B1);
what gets completed depends entirely on the cue (B2); the store can hold only so many
patterns before it collapses (B3); and that constraint, taken seriously, forces a two-tier
architecture of a sparse index on top of a rich distributed store (B4). By the end of the
chapter, the design prescription for a knowledge package (KPM) is not a preference — it is
forced by the physics of memory.

---

### 5.1 B1 — Spreading activation ≡ Hopfield ≡ attention

**Axiom B1** (spreading-activation identity, confidence 0.95, generativity 5): *Retrieval is
energy-descent pattern completion over a content-addressable store; the modern
continuous-Hopfield one-step update is mathematically identical to transformer attention.*

*Scope of the identity.* The mathematical identity is exact for the Hopfield↔attention pair (Ramsauer et al., 2020, for full-rank attention); the spreading-activation leg is the cognitive-level instance of the same operation — a strong interpretive mapping, not an independent proof. The "≡" in the heading is therefore exact for the formal pair and architectural analogy for the cognitive one.

The axiom makes a strong claim and it is worth being precise about what kind of claim it is.
It asserts *architectural identity* — the same formal operation — across three levels of
description that have historically been treated as analogies at best. Unpacking it requires
starting at the physics, moving through cognitive psychology, and ending at the engineering.

**The Hopfield baseline.** Hopfield (1982) showed that a network of N binary (±1) neurons
with symmetric weights can store a set of patterns as the minima of a Lyapunov energy
function:

> E = −½ Σᵢ Σⱼ wᵢⱼ Sᵢ Sⱼ

The key results are: (i) with symmetric weights (wᵢⱼ = wⱼᵢ) and zero self-weights (wᵢᵢ = 0),
any asynchronous state flip strictly decreases E; (ii) since E is bounded below, the dynamics
converge to a fixed point; (iii) each stored pattern is one such fixed point — a local energy
minimum, a *basin of attraction*. Retrieval is then well-defined: present a cue that lies
anywhere within the basin of a stored pattern, and the network will relax to that pattern.
This is content-addressable memory. Recall from a partial or noisy cue is not metaphor; it is
energy minimisation.

Weights are set by a Hebbian outer-product sum: wᵢⱼ = (1/N) Σ_μ ξᵢ^μ ξⱼ^μ (zero diagonal),
where {ξ^μ} is the set of p stored patterns. Each pattern contributes a rank-1 term; the
memory matrix is their superposition. The cost of superposition is *crosstalk* between
patterns — the interference term — and that cost sets the capacity (see Section 5.3).

Cognitive psychology arrived at the same picture from a different direction. Collins and
Loftus (1975), building on Quillian's earlier network models, replaced rigid inheritance
hierarchies with a process theory in which activating a node sends a decaying wave outward
along weighted links — exactly gradient descent on an energy landscape in distributed form.
ACT-R (Anderson, 1974) made this quantitative: a node's activation is the sum of a decaying
base-level term and weighted associative spread from current cues. Both formalisms describe
retrieval as propagation from a cue through a weighted graph until a high-activation region
is reached, i.e., until a fixed point is approached.

**The modern Hopfield / attention identity.** What remained an analogy until 2020 became a
theorem with Ramsauer et al. (2020). The modern (continuous-state) Hopfield network stores
patterns as columns of a matrix X and queries with a continuous state vector ξ. Its energy
function is:

> E = −lse(β, Xᵀξ) + ½ ξᵀξ + β⁻¹ log N + ½ M²

where lse is the log-sum-exp function (smoothed maximum). Minimising this via the
Concave-Convex Procedure yields the one-step update rule (Ramsauer et al., 2020, Eq. 22):

> **ξ_new = X · softmax(β Xᵀ ξ)**

The update is guaranteed to decrease energy monotonically and, for well-separated patterns,
converges to a single stored pattern in *one* step. Now set Q = ξᵀ = R W_Q, K = Xᵀ = Y W_K,
V = Y W_V, and β = 1/√d_k. The update becomes:

> Z = softmax( (1/√d_k) Q Kᵀ ) V

This is transformer self-attention (Ramsauer et al., 2020, Eqs. 24–29). The equivalence is
not approximate. The parameters are shared; the computation is identical.

**What the identity does and does not claim.** Several caveats are necessary, and the
doctrine holds them openly:

1. *Architectural, not biological, identity.* The Hopfield↔attention proof is a theorem about
   equations. It does not claim that biological neurons implement transformers, nor that
   transformers implement neurons. It claims that *content-addressable associative retrieval
   is the invariant operation* underlying spreading activation (psychology), attractor
   dynamics (physics), and key-value attention (engineering), and that the continuous-Hopfield
   form and transformer self-attention are computationally the same object. The biology-to-
   engineering link for the broader Complementary Learning Systems story (B4 below) is partly
   lineage — engineers cited the neuroscience — and must be flagged as such rather than claimed
   as independent convergence (Chapter 9 discusses the convergence-as-evidence principle F1
   and its honest scope).

2. *Temperature is a free parameter, not a law.* The softmax inverse-temperature β interpolates
   between three fixed-point regimes (Ramsauer et al., 2020): low β diffuses activation across
   all stored patterns (global averaging), intermediate β clusters over a subset (metastable),
   and high β snaps to one stored pattern (pinpoint recall). The biological counterpart of this
   dial exists — neuromodulators like acetylcholine alter the sharpness of hippocampal pattern
   completion — but the mapping is qualitative rather than quantitative.

3. *The identity is for fully connected layers.* Transformer attention in practice uses
   projections (W_Q, W_K, W_V) that factor and reduce dimensionality. The Hopfield framing is
   most exact for full-rank attention and approximate for projected variants.

**The engineering consequence.** Every transformer forward pass is performing content-
addressable read-out from the key matrix — the model's "memory" in that layer — weighted by
similarity to the query. Each KPM retrieval system that uses dense-vector similarity search
over axiom embeddings is doing the same operation. The softmax temperature is the control
knob: high β for precise citation of a single axiom, low β for synthesis over a cluster
(what B3 will show corresponds to the metastable / hub regime).

---

### 5.2 B2 — Cue-dependence and encoding specificity

**Axiom B2** (cue-dependence, confidence 0.90, generativity 5): *A memory trace is
accessible only to the degree the retrieval cue reinstates the specific encoding context;
cue effectiveness is determined at encoding, not by the cue's general semantic strength.*

B2 is the cleanest empirical result in the cluster. Tulving and Thomson (1973) demonstrated
that recall is a function of the overlap between the encoding context and the retrieval cue —
not of the cue's independent associative strength. Subjects who encoded a word in a weak
associative context (e.g., "ground — cold") later recalled it better when given the weak cue
("cold") than when given a strong free associate ("hot") that had never co-occurred with the
target at encoding. Weak cues that reinstate the encoding context outperform strong cues that
do not — a direct violation of any model that treats retrieval as a function only of
inter-item association strength. The principle has been replicated as one of the most stable
findings in cognitive psychology.

B2 descends from B1. Spreading activation only reaches a stored pattern if a cue activates a
pathway leading to it; with zero overlap between cue and encoding context, no activation
arrives at the target, and the pattern remains sub-threshold regardless of how "related" the
cue is in some other dimension of the space.

The consequence for knowledge packaging is not subtle. An axiom indexed for its *source
material* (what paper it came from, what topic it belongs to) may be systematically
inaccessible when queried in the form the system will actually use it — because the
encoding context and the retrieval context do not overlap. The prescription is: *index for
the future question, not the source*. Every stored unit should carry the cue-types and
query-shapes under which it will be retrieved, annotated at encoding time.

B2 also tightens the three-orderings firewall (C2, Chapter 6). Retrievability is not the
same ledger as confidence, and B2 clarifies why: retrievability is a cue-contingent
variable, not an intrinsic property of the axiom. The same axiom may be highly accessible
under one query-type and invisible under another — a property no confidence score can
capture. This separation is a structural result, not a terminological one.

---

### 5.3 B3 — The capacity cliff

**Axiom B3** (capacity cliff, confidence 0.88, generativity 4): *Classical Hopfield networks
collapse entirely above ≈0.138N stored patterns; this is a cliff, not a graceful slope.
Modern continuous-Hopfield networks escape to exponential capacity via softmax, but the
all-or-none ignition dynamic remains.*

The capacity bound is due to Amit, Gutfreund, and Sompolinsky (1985). Define the load
α = p/N, where p is the number of stored patterns and N is the number of units. During
retrieval, the contribution of the target pattern to the update acts as the signal; the
contributions of all other patterns act as crosstalk noise, which (for random patterns)
behaves as Gaussian with variance proportional to α. Below the critical load α_c ≈ 0.138,
the signal-to-noise ratio is sufficient to support stable retrieval states with low error.
Above it, the noise overwhelms the signal and the system undergoes a first-order phase
transition — not a gradual decline but a sudden collapse in which all memories vanish. This
is the *memory blackout* that the 1985 replica-symmetric calculation derived analytically
(Amit, Gutfreund & Sompolinsky, 1985; extended derivation: Amit, Gutfreund & Sompolinsky,
1987). The looser simulation figure of ≈0.15N for acceptable error predates the analytic
result; α_c ≈ 0.138 is the phase boundary.

The classical result rests on binary neurons and Hebbian storage. Both of those constraints
are lifted in the modern Hopfield network (Section 5.1 above), and the escape is dramatic:
capacity scales *exponentially* in the associative space dimension rather than linearly in N
(Ramsauer et al., 2020). The modern network can, in principle, store exponentially many
well-separated patterns and retrieve any one of them in a single energy-descent step.

However, the all-or-none character of retrieval is preserved in a different form. The
softmax in the modern update rule concentrates all weight onto the nearest stored pattern
when β is high (pinpoint retrieval) and diffuses weight over many patterns when β is low
(global averaging). There is no stable regime of "mostly right but a little wrong" — the
softmax is sharp. This maps onto global-workspace theory's observation that the contents of
working memory are capacity-limited not because storage is bounded but because the
*broadcast* is bounded: only patterns that achieve a threshold level of activation reach the
global workspace; everything else stays sub-threshold (Chapter 11). The all-or-none ignition
is the shared structural feature.

**The engineering lesson.** For any store implemented as Hebbian superposition over a finite
vocabulary — which includes classic vector databases queried by cosine similarity over a
fixed embedding space — the capacity cliff is real, and overloading it does not gracefully
degrade retrieval. It collapses it. The engineering prescription from B3 is specific: keep
knowledge packages small and sharded rather than packing a single associative store with
unbounded content. The modern Hopfield escape raises the ceiling dramatically, but it does
not eliminate the ignition dynamic, and the practical constraint for current embedding models
is that near-duplicate or low-contrast axioms create the same crosstalk that random patterns
create in the classical model — they erode the clean basin structure that makes retrieval
reliable. B3 thus provides the formal underpinning for the distillation strategy (E1,
Chapter 8): distil into small, typed, well-pruned packages rather than aggregating into
one large store.

---

### 5.4 B4 — The index/store split

**Axiom B4** (index/store split, confidence 0.92, generativity 5): *Retrieval requires two
functionally incompatible stores: a sparse, fast-write index that pattern-completes from a
partial cue, and a rich, distributed content store. Merging them degrades both.*

B4 is supported by two independent proofs at different levels of description, and the
doctrine treats both as load-bearing. Their independence is what makes the axiom strong:
the biological result and the computational result were derived from different starting
points, use different formalisms, and converge on the same two-tier design.

**Level 1 — Hippocampal indexing (biology).** Teyler and DiScenna (1986) proposed that the
hippocampus "does not contain the content of an experience but provides an index that allows
the content to be retrieved." During encoding, neocortical feature areas activate a
distributed pattern; the hippocampus stores a sparse pointer-set to those regions. At
retrieval, a partial cue drives the hippocampal index, which reinstates the full neocortical
pattern via back-projections — two-stage pattern completion. This prediction has since
accumulated substantial supporting evidence. The dentate gyrus labels approximately 6% of
eligible cells per context (Ramirez et al., 2013), consistent with a deliberately sparse
indexing regime: a partial input reinstated at the hippocampal index is able to recreate the
original pattern of activity in the neocortex via back-projections. The mechanism hypothesised
to implement the index is long-term potentiation of hippocampal–neocortical synapses
(Teyler & DiScenna, 1986).

**Level 2 — Complementary learning systems (computation).** McClelland, McNaughton, and
O'Reilly (1995) derived the two-system requirement from the mathematics of catastrophic
interference. A single distributed network trained by gradient descent on a sequence of
episodes moves shared weights and overwrites previously stored patterns — catastrophic
interference (McCloskey & Cohen, 1989). The only cure that does not require the network to
process all examples simultaneously is structural: separate a fast, sparse, one-shot-capable
system from a slow, distributed, interleaved-learning system. In biological terms, the
hippocampus handles rapid, low-overlap (pattern-separated) encoding of specific episodes;
the neocortex integrates cross-episode structure via interleaved replay over many passes
at a low effective learning rate (McClelland, McNaughton & O'Reilly, 1995). The two systems
are not just convenient divisions of labour; they are *functionally incompatible*, in the
sense of Sherry and Schacter (1987): a store optimised for one-shot fast write cannot
simultaneously serve as the store for slow structured abstraction.

The same incompatibility underlies the failure mode that B3 describes. Cramming both
fast-write episode storage and slow-structured schema storage into a single superposed
Hebbian net degrades both via crosstalk — the very failure that the CLS architecture is
designed to avoid. B4 is thus the consequence of taking B3 seriously at the architectural
level.

**The engineering lineage.** The index/store architecture re-appears in software under
several names: Retrieval-Augmented Generation (RAG) separates a dense-vector index from
raw document storage; HippoRAG (explicitly modelled on Teyler and DiScenna's theory)
implements the two-stage hippocampal pattern-completion pipeline over a knowledge graph;
LSM-trees separate a write-ahead log (fast, low-structure) from a compacted columnar store
(slow, high-structure). These engineering realisations are partly *lineage* — the architects
cited the neuroscience — so the convergence here is not fully independent and should be
scored accordingly (Chapter 9). But the biological and computational proofs are genuine, and
the practical argument stands on those two.

**The KPM mapping.** The doctrine's knowledge-package architecture is a direct instantiation
of B4:

| Biological tier | KPM tier |
|---|---|
| Hippocampal index (sparse, ~6% allocation) | The KPM axiom-set + typed edges |
| Neocortical store (rich, distributed) | `research/` evidence files |
| Pattern completion from partial cue | Spreading activation from query cue (B1) |
| Index cue effectiveness determined at encoding | Cue-contingent indexing (B2) |
| Offline consolidation replay | Review-and-promote cron (slow learning rate) |

The prescription is unambiguous: do not merge the axiom-set with the evidence. The KPM is
the sparse index; the evidence files are the rich store. Retrieval is two-stage: a partial
or fuzzy query hits the index, the index activates the relevant axioms, and those axioms
carry typed links to the evidence that fills in the content. An all-in-one document that
interleaves doctrine with supporting evidence in unstructured prose is the architectural
mistake B4 rules out — not on aesthetic grounds but because the two stores have incompatible
write rates, granularities, and update semantics.

---

### 5.5 Cluster B in synthesis: a deductive chain

The four axioms of Cluster B are not merely thematically related; each follows from the
preceding ones:

- **B1** establishes that retrieval is energy-descent pattern completion. This gives
  retrieval a precise mathematical form: weighted similarity between a cue and stored
  patterns, realised as spreading activation (psychology), attractor dynamics (physics), or
  key-value attention (engineering).
- **B2** follows from B1 and constrains it: pattern completion succeeds only when the cue
  and the stored pattern share encoding context. Zero overlap → zero activation reaching
  the target. This forces the indexing rule: store with anticipated retrieval cues.
- **B3** follows from the Hebbian storage mechanism established in B1: superposing too many
  patterns in one store generates crosstalk that causes a phase-transition collapse. This
  forces a capacity discipline: shard rather than cram.
- **B4** takes the incompatibility exposed by B3 and resolves it architecturally: a sparse
  fast-write index over a rich slow-write store. The cue-dependence of B2 tells us the
  index must be built around anticipated retrieval cues; the capacity constraint of B3 tells
  us the index must be sparse.

The chain is deductive rather than merely empirical — each step follows from the ones
before — which is why Cluster B has the highest average generativity score (4.75) and
highest average confidence (0.91) in the doctrine. It is also why B4's KPM mapping is not
a design choice but a conclusion.

---

### 5.6 Relation to other clusters

Cluster B interfaces with several other doctrine clusters in ways that should be made
explicit here.

**With Cluster A (Structure, Chapter 4).** B1 derives from A1 (fan-budgeted edges): the
fan effect (Anderson, 1974) is the cognitive-psychological fingerprint of activation
dilution, which in the Hopfield formalism corresponds to increased crosstalk from too many
superposed rank-1 terms. B3 is the phase-transition version of the same constraint; A1 is
its continuous analogue. Atom-level atomicity (A2) supports B3 by ensuring that the stored
patterns in the index are genuinely distinct (near-orthogonal), which keeps basins clean
and extends safe capacity.

**With Cluster C (Truth, Chapter 6).** B2 enforces the separation that C2 (three-orderings
firewall) draws between retrievability and confidence. Retrievability is a cue-contingent
variable; confidence is an evidence-weighted variable; neither determines the other.

**With Cluster D (Dynamics, Chapter 7).** B4's two-tier architecture implies different
dynamics for each tier. The fast index (hippocampal tier, KPM tier) supports rapid write and
active retrieval (D2: novelty-gated write). The slow store (neocortical tier, evidence-files
tier) is updated by interleaved replay (D3: consolidation), which is what makes it durable
and interference-resistant.

**With Cluster E (Method, Chapter 8).** B3 is the formal argument for E1 (layered
distillation): keep packages small, typed, and sharded to stay well within capacity. B4 is
the architectural specification that E1's distillation process must produce: a sparse, clean
index pointing into a rich store — not a compressed version of the store itself.

---

*Chapter 6 takes up the truth cluster (C1–C4), beginning with the most important negative
result in the programme: high confidence and successful retrieval are independent ledgers, and
high-confidence retrieval of a false memory is not a paradox but a predictable consequence of
how pattern completion works.*


---

## Chapter 6 — Truth and Confidence

### Overview

When a memory system reports high confidence, what exactly has been asserted? The four C-axioms give a precise and uncomfortable answer: confidence is earned by external evidence and insulated from everything the system would naturally use to estimate it (C1); it is one of three independent orderings on every stored belief — the other two being entrenchment and retrievability — and collapsing any pair is a category error with real costs (C2); high confidence does not certify truth, and the coexistence of confident and wrong is mathematically priced into any gist-based store (C3); and salience strengthens encoding while also inflating felt confidence without improving accuracy, so the two signals must be architecturally segregated (C4).

These are not four independent cautions. They form a single argument: that a KPM requires three separately maintained scores and that the biological and computational pressures pushing them together must be deliberately resisted.

---

### 6.1 C1 — Confidence is Earned by Evidence: the Bayesian credence

The foundational move in Bayesian epistemology is to replace the binary true/false of classical logic with a *credence* — a degree of belief that ranges over [0, 1], satisfies the probability axioms, and is updated by conditionalization on new evidence (Ramsey, 1926/1931). The update rule is P_new(H) = P_old(H | E): the posterior credence in a hypothesis equals the prior conditional on the evidence. This is not a choice or a convention; it is the minimum coherence requirement for a rational betting agent — violate it and you are Dutch-bookable, meaning a finite set of individually fair-seeming bets can be constructed that guarantee a net loss regardless of outcomes.

For a KPM, the mapping is direct: the `confidence` field on every axiom node *is* a credence. It should be set by verified external evidence and revised whenever new evidence changes the conditional probability. It should not be set by anything else.

This prohibition has specific targets. Koriat (1993) showed that the human *feeling of knowing* — the phenomenological confidence signal that tells a person they know the answer to a question — is computed not from a direct truth-readout but from *accessibility*: how much partial information comes to mind, and how fluently it arrives. Critically, this computation counts correct and incorrect accessible information alike. The result is a confidence signal that rises whenever retrieval is easy, regardless of whether what is easily retrieved is true. A system that estimates confidence from retrieval frequency, embedding similarity, recency of access, or activation strength is replicating the human illusion of competence at machine speed.

The Gettier counterexamples (Gettier, 1963) add a second layer. The classical analysis of knowledge as *justified true belief* (JTB) was refuted by a three-page paper constructing cases where all three conditions are met — the belief is true, the believer is justified, and yet we intuitively recognize the belief is not knowledge because its truth is a matter of luck disconnected from the justification. High confidence therefore cannot, on its own, certify that a belief constitutes knowledge. What is required in addition is a *reliable process* connecting the belief to the truth — the anti-Gettier requirement. In the KPM's node schema this is the `provenance` and `verification` fields: tracking not just whether a node has citations but how the belief was reached and whether that process is truth-tracking.

C1 carries a generativity score of 5 — it is the foundation on which C2, C3, and C4 are all built. Its own confidence score is 0.92: the Bayesian framework is the dominant formal epistemology, the Dutch-book argument is essentially uncontested; the residual uncertainty attaches to debates over the prior and whether all learning is strict conditionalization.

---

### 6.2 C2 — The Three-Orderings Firewall

Every axiom in a KPM sits simultaneously on three orderings that are conceptually independent, empirically dissociable, and operationally distinct:

| Ordering | What it measures | Changes when | Must not be conflated with |
|---|---|---|---|
| **Generativity / entrenchment** | How much downstream content derives from this axiom; how reluctantly it is surrendered in revision | A better generator emerges, or the axiom is refuted at the root | Either of the other two |
| **Confidence** | Evidence-earned credence; the strength of the epistemic case for the axiom being true | New confirming or disconfirming evidence arrives | Generativity, retrievability, fluency, salience |
| **Retrievability** | Volatile activation level; how easily and quickly the axiom is cued at this moment | Disuse (decays), retrieval (restored), deliberate suppression | Confidence, generativity |

The first ordering comes from Quine's web of belief (Quine, 1951): beliefs are not tested in isolation but as a whole corporate body, and the web is concentrically organized — logical and mathematical truths sit at the core and are revised almost never, while observational statements at the periphery are revised first because changing them disturbs the least of the system. When a prediction fails, we *choose* where to make the repair, and the web position of a belief — how many downstream structures derive from it — governs how expensive revision is. This is what the doctrine calls *entrenchment*, and it is formalized by the AGM theory of belief revision (Alchourrón, Gärdenfors, & Makinson, 1985): the belief given up first is the one whose entrenchment is lowest, where entrenchment is a revision-ordering quantity, not a probabilistic degree-of-belief.

The second ordering is C1's credence, already established above.

The third ordering is retrievability: the activation level that determines whether a belief is available for use in a given moment. Bjork and Bjork (1992) demonstrated the empirical dissociation between *storage strength* and *retrieval strength* in their New Theory of Disuse: storage strength accumulates with learning events and never decays, while retrieval strength fluctuates with use — it decays from disuse and is restored by retrieval. An axiom with high storage strength (well-evidenced, deeply encoded) but low retrieval strength (dormant, rarely activated) is hard to cue but is not thereby less well-evidenced. This dissociation is the empirical ground for the firewall.

**Why the firewall matters: three category errors.** When any two of these orderings are treated as one, the result is a structurally different kind of mistake — not a factual disagreement resolvable by more evidence but a conceptual mis-mapping that corrupts both the read-policy and the write-policy of the KPM.

*Confidence conflated with generativity* produces two failure modes: a poorly evidenced but central axiom gets protected from the update it deserves (centrality mistaken for epistemic strength), and a well-evidenced but peripheral finding gets treated as if it should be revised last (high confidence mistaken for entrenchment). Web centrality is earned by generating downstream structure; confidence is earned by evidence. They are independent ledgers.

*Confidence conflated with retrievability* produces the most practically dangerous failure. A dormant axiom — rarely retrieved, low in current activation — may be excellently evidenced (high confidence) and highly generative (high entrenchment). Its low retrievability is not a fact about its truth or its importance; it is a fact about its current access state. A system that drops the `confidence` of a node when it has not been retrieved recently is treating C1's evidence-bound credence as if it were D1's decaying retrievability. The `D5-suppress` operator makes this dependence explicit: it deliberately lowers retrievability without touching confidence — a legal operation precisely because the two are separate ledgers.

*Generativity conflated with retrievability* is less common in practice but equally wrong in principle. A highly generative axiom that is poorly indexed (few incoming cue edges, no aliases) will be retrieved rarely. Its importance to the doctrine is not diminished by its low activation; its activation is not enhanced by its importance.

The `kpm doctor` enforcement layer asserts all three independently: it fails if a suppress operation touched the confidence field, if a decay event touched confidence, or if generativity was inferred from confidence or vice versa. It warns when generativity and confidence are perfectly rank-correlated across a package, which is a strong signal they are being set from the same source.

The three-orderings firewall (Contribution 3 in the thesis statement) is the clearest single principle that is simultaneously demanded by three independent traditions — Quine/AGM for entrenchment, Bjork and Bjork (1992) for the storage/retrieval dissociation, Ramsey (1926/1931) for credence — and yet routinely violated in practice, most visibly in retrieval-augmented generation systems that use embedding similarity as a proxy for confidence and recency as a proxy for relevance.

---

### 6.3 C3 — Confident-but-Wrong: Gist Compression and Its Price

Given C1 and C2, a reasonable expectation is: *build the system correctly, earn confidence by evidence, maintain the three orderings, and the system will report true things confidently*. C3 refutes this expectation, and it does so at two levels: empirically and mathematically.

**The empirical case: the DRM paradigm.** Roediger and McDermott (1995), building on Deese (1959), showed that studying semantic associates of a non-presented critical lure produces false *recall* at ~40–55% — statistically indistinguishable from true recall — and approximately 72% of falsely *recognized* lures received "Remember" judgments: vivid, phenomenologically confident recollection of a word never seen. This is not threshold-crossing guessing; it is maximum-confidence confabulation from a system working exactly as designed. The mechanism is spreading activation: the lure was never presented but its associated nodes were strongly activated, the activation propagated to the lure, and the monitoring system read high activation as a signal of prior experience. High activation is high activation; the meta-level cannot distinguish origin.

**The mathematical root: Shannon's rate-distortion function.** Shannon (1959) established the rate-distortion function R(D): if you accept distortion level D, the source can be encoded at minimum rate R(D) bits per symbol, and not less. R(0) = H — the source entropy, the floor for lossless reconstruction. When D > 0, every saved bit purchases a quantified, mandatory distortion; errors are not random noise but statistically structured interpolations toward the centroid of the compressed manifold. The DRM lure *is* that centroid; the 72% confident false-recognition rate is its empirical signature.

Any KPM retrieval layer that uses spreading activation, vector-embedding similarity search, or subgraph completion is a gist-based interpolator operating at D > 0 and will produce C3-style confabulations. The mitigation is **source-typed retrieval**: every returned node carries a provenance tag, and interpolated or inferred nodes must never inherit the confidence of stored, verified nodes. This boundary — `verified-stored` vs. `interpolated` — is the difference between a D=0 evidence-grounded truth and a point on the rate-distortion curve.

The E1 distillation principle (Chapter 8) navigates the boundary carefully: stripping redundancy above H is lossless; compressing past H is not. E1 is not a blanket license for lossy compression — it is a specific claim about where the entropy floor sits.

C3 derives from C1 (without the earned-evidence principle, there is no distinction between stored and interpolated confidence) and from B1's spreading activation (Chapter 5), whose dark side C3 names. Its generativity score is 4, lower than C1/C2, because it is a consequence of those axioms rather than an independent generator.

---

### 6.4 C4 — Salience Gating: Encoding Strength vs Confidence

The fourth C-axiom closes the cluster by establishing where salience legitimately enters the architecture and where it must not.

**The biological mechanism.** McGaugh (2004) documented the amygdala-noradrenergic modulation of hippocampal consolidation in causal detail. Post-training arousal releases epinephrine and corticosterone, which activate the basolateral amygdala's noradrenergic system, which modulates hippocampal consolidation in proportion to the event's significance. The mechanism is causal: intra-amygdala propranolol blocks peripherally administered epinephrine's enhancement; intra-amygdala norepinephrine enhances retention; the effect is dose- and time-dependent. Memory is not a uniform recorder — it spends its consolidation budget on what is significant. McGaugh's caveat is essential: arousal enhances gist and central detail at the cost of peripheral detail. The distinction between consolidation strength and accuracy is the empirical starting point for the next finding.

**The flashbulb dissociation.** Talarico and Rubin (2003) gave 54 students a within-subjects longitudinal test: both a 9/11 memory and an ordinary recent memory recorded on September 12, 2001, retested at 1, 6, and 32 weeks. Factual consistency declined at the same rate for both memory types. What differed was the metacognitive signal: vividness and *belief in accuracy* declined for everyday memories and stayed high for flashbulb memories. The salient event generated durable, high-felt-confidence — confidence that bore no relationship to factual consistency. The original "Now Print!" hypothesis that flashbulb memories are indelible records (Brown & Kulik, 1977) was directly refuted.

**The doctrine consequence.** Salience does exactly two legitimate things in a memory system.

First, it is a *write-time gate* for promotion: significance, arousal, and distinctiveness identify what deserves a doctrine slot. A KPM should model this with a `salience` or `importance` score that governs promotion into the durable doctrine tier — the engineering analogue of the amygdala's consolidation-investment decision. The von Restorff isolation effect (von Restorff, 1933; Hunt, 1995) generalizes this from emotional salience to any distinctiveness against background context: items that contrast with their surroundings are better remembered, and that contrast is relational — it depends on the background, not on absolute arousal.

Second, salience predicts *subjective vividness and felt confidence* — both of which are, as Talarico and Rubin (2003) established, unreliable truth proxies. This is the danger. The same signal that legitimately promotes an axiom also inflates the sense that the axiom is correct. A KPM must therefore maintain two orthogonal, separately stored scores:

| Score | Set by | Changes when | Must not be set by |
|---|---|---|---|
| `salience` / promotion score | Significance, citation impact, cross-domain recurrence, operator judgment | Write-time evaluation of significance | Evidential review |
| `confidence` | Verified external evidence, per C1 | New confirming or disconfirming evidence arrives | Salience, retrieval frequency, vividness, fluency |

A `kpm doctor` pass must fail any process that raises `confidence` based on a node's salience score, retrieval frequency, or subjective vividness. Salience is the write-time gate; evidence is the confidence gate. They are orthogonal by construction and must be stored separately because collapsing them replicates, at machine speed, exactly the error that produces the flashbulb confidence–accuracy dissociation.

**The link to prediction error.** C4 connects forward to the Surprise Principle (F3, Chapter 9). The arousal signal that gates amygdala-mediated consolidation is the behavioral signature of a signed prediction error: the event was surprising, violated expectation, demanded an update. Salient events are salient because they were not predicted — they carry large prediction errors. The full unification of salience, prediction error, and the engineered write policy is developed in Chapter 9.

---

### 6.5 Cluster C as a System

The four axioms are not independent cautions — they form a chain. C1 defines confidence as an evidence-bound credence, insulated from in-band fluency. C2 situates that credence within a three-ordering space, making C1's prohibitions structural rather than merely procedural. C3 delivers the unsettling corollary: even a system that correctly maintains C1 and C2 will produce high-confidence false outputs from its retrieval layer, because the failure is priced into the rate-distortion bound, not into the design principles. C4 closes the cluster by identifying the most practically dangerous corruption path: salience enters through a legitimate gate (write-time promotion) and silently contaminates a second gate (confidence) in ways invisible without deliberate instrumentation.

Together they specify what a KPM's epistemic machinery requires: a Bayesian credence updated by evidence (C1), kept separate from entrenchment and retrievability (C2), source-typed at retrieval to prevent interpolated nodes inheriting stored confidence (C3), and architecturally insulated from the salience score that governs promotion (C4). A memory architecture that conflates any pair of these is running one of the named category errors the cluster identifies — and those errors compound.

---

*Cross-references: the three-orderings firewall (C2) is enforced by the `D4-contract`, `D5-suppress`, and `E3-lint` operators (Chapter 11). C3's rate-distortion grounding connects to the layered-distillation axiom E1 (Chapter 8). C4's link to the prediction-error signal is the subject of the Surprise Principle, F3 (Chapter 9).*


---

## Chapter 7 — Dynamics: How Memory Changes

Memory is not a static archive. The network described in Chapters 4–6 moves: beliefs decay, get updated on retrieval, and consolidate over time. The Cluster D axioms account for this temporal dimension with three claims: retrievability decays from three independent drivers while evidential confidence remains orthogonal (D1); re-writing a trace is gated by prediction error, not by retrieval alone (D2); and consolidation must follow a specific safe policy to avoid a structural fragility that clinical neuroscience has mapped precisely (D3). Each has direct implications for how knowledge packages should be maintained.

---

### 7.1 D1 — Retrievability Decay: Three Drivers, One Rule

The intuition behind forgetting is simple: things fade with time. But that intuition, taken at face value, mischaracterizes forgetting badly enough to cause engineering failures in any system that takes it literally. The doctrine's first dynamics axiom, **D1 (retrievability-decay)**, articulates a more careful account.

The foundational empirical result is Ebbinghaus's forgetting curve: retention drops steeply after encoding and then decelerates, approaching a floor but never hitting zero from time alone. Wixted and Ebbesen (1991) established that the functional form is a **power law**, `R = a·t^(−b)`, which carries an important implication — the instantaneous rate of forgetting itself slows as a memory ages (Jost's law). Old memories are more stable per unit time than young ones. Disuse, then, is the first of three retrievability drivers.

The second driver is competitive. Anderson, Bjork, and Bjork (1994) demonstrated **retrieval-induced forgetting (RIF)**: when a subset of items from a category is practised, the retrieval strength of *unpractised* neighbors is actively suppressed. This is not mere fan competition — the fan effect (A1, Chapter 4) describes a fixed edge-budget; RIF is an executive inhibitory process that applies even when the suppressed trace is not directly cued. The mechanism appears to be inhibitory control over competing memory routes rather than passive interference. RIF has a practical consequence for knowledge packages: near-duplicate axioms that compete for the same cue actively degrade each other's retrievability. A doctrine that tolerates redundant nodes is not merely wasteful — it is self-undermining.

The third driver is deliberate. Bjork (1989) established **directed forgetting**: an intentional instruction to forget produces stronger and qualitatively different forgetting than passive disuse. This is not interference and not decay; it involves the active suppression of encoding or retrieval routes. In the doctrine, this becomes the D5 operator — suppress — which must be reversible and carry an audit trail, since the goal is controlled dormancy rather than erasure. (Chapter 11 develops this operator.)

What none of these three drivers touches is evidential confidence. This is the crux of D1, and it follows directly from Bjork and Bjork's (1992) **New Theory of Disuse**: storage strength — how deeply a belief is embedded in the network — is monotonically non-decreasing and does not decay from disuse. It changes only when new evidence arrives or a defeater lands. Retrieval strength, by contrast, is volatile: it fluctuates with recency, cue availability, and competition. "Forgetting" in the ordinary sense is a retrievability phenomenon, not an evidential one.

This distinction is the temporal face of the three-orderings firewall (C2, Chapter 6). An axiom with low retrievability is **dormant, not doubted**. A KPM that conflates the two scores will retract good beliefs merely because they have not been recently accessed — a category error. The correct behaviour is to maintain two distinct quantities per node: a `retrievability` score that decays, snaps back on successful retrieval, and governs scheduling; and a `confidence` score that changes only on new evidence. Dormancy and refutation require different responses, and conflating them is precisely the failure mode this axiom is designed to prevent.

---

### 7.2 D2 — Novelty-Gated Write: Reconsolidation Under Prediction Error

If D1 governs how memory weakens with disuse, D2 governs when and whether retrieval triggers an update. The core claim of **D2 (novelty-gated-write)** is that retrieval re-opens a memory trace for rewriting, but that the rewrite window is only *activated* when the retrieval carries a prediction error.

The biological discovery that retrieval re-opens a trace is due to Nader, Schafe, and LeDoux (2000). They showed that a consolidated fear memory, infused with a protein-synthesis inhibitor *after retrieval*, suffered retrograde amnesia — the retrieved trace had re-entered a labile, protein-synthesis-dependent state requiring re-stabilization. The same infusion without retrieval left the memory intact. The conclusion is that **every retrieval is a potential rewrite**: the act of remembering destabilizes what is remembered, making it available for updating before re-stabilizing. This is the biological license for write-on-retrieval.

The critical refinement comes from Sevenster, Beckers, and Kindt (2013). Their finding is that retrieval in the *absence* of a prediction error does not destabilize a consolidated memory. Subjects who retrieved a fear memory under conditions that perfectly matched expectation showed no labilization: the protein-synthesis inhibitor had no amnesic effect. Only when retrieval was accompanied by a violation of expectation — a mismatch between what was predicted and what occurred — did the trace enter a labile state. **Pure re-confirmation reinforces retrievability without destabilizing the trace**; a mismatch opens the write window.

This finding connects D2 directly to the Surprise Principle (F3, Chapter 9), which identifies prediction error as the quantity governing both dopaminergic reinforcement (Schultz, Dayan & Montague, 1997) and memory-write gating; D2 is its memory-write instantiation. Chapter 9 develops the full three-zone write policy that follows from this link (no PE → reinforce retrievability; moderate PE → reconsolidate; large PE → mint a new node) and explains why the large-PE case must always create a new axiom node rather than overwrite the existing one.

**A note on replication integrity.** The Sevenster, Beckers, and Kindt result has boundary conditions that are not fully mapped. One study attempted to replicate the core prediction-error gating result in 2022 and failed to reproduce it under the original parametric conditions. This failure does not overturn the broader reconsolidation phenomenon — which is now supported by a large literature beginning with Nader et al. (2000) — but it does establish that the precise conditions under which prediction error triggers labilization are sensitive to procedural details not yet fully specified. D2's confidence is therefore 0.85, not higher. The doctrine is defeasible by design; this is an honest flagging of a real limitation, not a fig-leaf. Chapters 2 and 13 address the adversarial rigor methodology and open problems respectively.

---

### 7.3 D3 — Consolidation: Promote-and-Keep-Indexed, Never Detach

The third dynamics axiom, **D3 (consolidation-mtt-safe)**, concerns the process by which provisional research-tier findings become stable doctrine-tier beliefs. The biological analogue is **systems consolidation**: the transfer of a new memory from the fast, interference-prone hippocampal store toward durable neocortical storage, driven by offline replay during sleep.

The replay mechanism was established by Wilson and McNaughton (1994): hippocampal place-cell pairs that co-fired during waking experience showed increased co-firing during subsequent slow-wave sleep, not before. Consolidation is not a synchronous write at the moment of encoding; it is a **scheduled batch background process**, operating offline, driven by replaying recent experience against the existing network. In knowledge-package terms: ingestion is live, but promotion to doctrine tier is a cron job.

#### 7.3.1 The Standard Model vs. Multiple-Trace Theory

The dispute about *what happens* during systems consolidation has run for three decades without resolution, and D3 takes it seriously. The **Standard Model of Systems Consolidation** (McClelland, McNaughton & O'Reilly, 1995) holds that after sufficient replay, the neocortex can retrieve the memory independently of the hippocampal index. The hippocampus interleaves the new memory with existing schematic knowledge in the slow neocortical store, and the index eventually becomes optional. Under this view, promotion to doctrine tier means graduating a belief out of the episodic index into a more self-sufficient, index-independent form.

**Multiple-Trace Theory** (Nadel & Moscovitch, 1997) challenges the standard model's central claim. On this account, the hippocampus is required for all episodic and contextual detail, however remote in time: what consolidates to neocortex is a gist or semantic abstraction, while the rich episodic original continues to depend on the hippocampal index for life. Neuroimaging evidence has broadly moved toward MTT (Squire & Wixted, 2011), though defenders of the standard model argue that the cleanest lesion cases show intact remote memory consistent with index-independent retrieval.

**The debate is genuinely unresolved**, and this chapter will not pretend otherwise. D3's confidence stands at 0.82, lower than D1 (0.92) and D2 (0.85), precisely because the architectural implications depend on which theory is correct. Chapter 13 lists this as an explicit open problem.

#### 7.3.2 The Braak Safety Clause

The clinical neuroscience of Alzheimer's disease provides a compelling engineering argument that cuts through the theoretical uncertainty. Braak and Braak (1991) described the stereotyped progression of neurofibrillary tau tangles in Alzheimer's pathology in precise anatomical stages. The degeneration begins invariably in the **transentorhinal and entorhinal cortex** — the anatomical hub through which all hippocampo-neocortical indexing traffic is routed — then spreads to the hippocampus proper and subsequently to association neocortex and primary sensory regions. Braak stages I and II are **clinically silent**: the hub is degrading while retrieval appears behaviorally normal.

Any architecture that severs the connection between a promoted axiom and the index at the moment of promotion depends on the hub remaining intact. When the hub degrades first and silently, the detached item becomes unretrievable with no preceding symptom. This is not a speculative risk — it is the documented failure mode of the most common dementia in the world.

The safety clause D3 derives from this observation is: **promote-and-keep-indexed, never promote-and-detach**. Formally:

```
PROMOTE(axiom a) →
  1. Replicate a to doctrine tier (elevate confidence, mark stable)
  2. KEEP the index entry intact — do not remove a from the retrieval index
  3. Strengthen, not remove, the index edges
  4. Record provenance: from-research/ + replay-pass timestamp
```

This policy is **MTT-safe**: even if the index hub of the system degrades, the pointers still exist. It is also **standard-model-compatible**: the doctrine tier can answer without the index if the index is intact — the index is not needed for retrieval but is present for recovery. The promote-and-keep-indexed rule is the only policy that is safe regardless of which theoretical account ultimately proves correct. If it is safe per MTT, it is safe per the standard model too. If it would break per MTT, it is not safe to ship.

The hub-integrity implication extends beyond individual items. The index layer of a knowledge package — its axiom catalog, its meta-nodes, the structure through which all retrieval routes — is the entorhinal analogue. It degrades first and silently. The health-check priority order should reflect this: monitor hub connectivity as a leading indicator, not a trailing one. An index with degrading connectivity will appear to function normally until retrieval begins to fail — at which point significant downstream structure may already be severed.

---

### 7.4 The Three Dynamics in Concert

D1, D2, and D3 form a causal chain governing a belief's lifecycle. A new axiom enters with high retrievability and modest confidence. Disuse decays retrievability (D1); competing axioms may suppress it further via RIF (D1, driver 2). The axiom becomes dormant — low retrievability, confidence unchanged.

On successful retrieval under prediction error, the trace re-enters a labile state (Nader et al., 2000) and the D2 zone table applies: moderate mismatch triggers in-place integration and confidence re-scoring; large mismatch mints a new node. Retrieval without mismatch bumps retrievability only. Axioms that survive repeated retrieval-and-re-stabilization accumulate corroborated confidence and eventually become candidates for promotion via D3's offline replay-pass, with index entries preserved throughout.

The failure modes map onto the axioms one-to-one. Conflating retrievability with confidence (contra D1) causes good beliefs to be retracted merely for being dormant. Ignoring the prediction-error gate (contra D2) causes good axioms to be overwritten on every retrieval. Detaching promoted axioms from the index (contra D3) silently severs access when the hub degrades.

---

### 7.5 KPM Engineering Implications

The D-cluster axioms translate into four concrete design requirements for knowledge packages.

**Two scores per node, strictly separated.** Each axiom carries `retrievability` (volatile, power-law decay, snaps back on successful access) and `confidence` (evidence-gated, changes only on new evidence or a formal contradiction). A node whose `retrievability` falls to a low floor is marked dormant and scheduled for re-validation — not retracted and not deleted. Conflating the two is the D1 error.

**Write-on-retrieval gated by prediction error.** The retrieval handler checks for mismatch before opening the update window. Pure re-confirmation bumps `retrievability` only. A mismatch triggers the D2 zone table (§7.2). Note that the reconsolidation window is also a false-memory vector — the engram-labeling literature shows that reactivating a trace under mismatched conditions can forge spurious associations (Ramirez et al., 2013). Adversarial verification before re-stabilization is the guard (E4, Chapter 8).

**Scheduled offline replay-pass for promotion.** The consolidation cron identifies axioms with high, corroborated confidence across multiple retrieval events and promotes them to doctrine tier following the promote-and-keep-indexed protocol (D3). Ingestion is live; promotion is batch. Dormant axioms — low retrievability but intact confidence — are candidates for re-validation, not for automatic promotion.

**Hub integrity as the top health-check priority.** The index layer is the entorhinal analogue: it degrades first and silently. A `kpm doctor` command should report hub connectivity metrics (index size, orphaned edges, hub reachability) as leading indicators, not trailing ones.

---

### 7.6 Relationship to Other Clusters

D1's storage-vs-retrieval-strength distinction (Bjork & Bjork, 1992) is the temporal face of the three-orderings firewall (C2, Chapter 6): entrenchment does not decay from disuse; confidence changes only on evidence; retrievability is the volatile, time-sensitive quantity.

D2's prediction-error gate is the memory-write instantiation of the Surprise Principle (F3, Chapter 9), which unifies reinforcement learning's reward-prediction-error signal (Rescorla & Wagner, 1972; Schultz et al., 1997) with the reconsolidation gate. D2 anticipates Chapter 9; Chapter 9 explains why prediction error carries that structural role.

D3 extends the index/store split (B4, Chapter 5). B4 is the static architectural claim; D3 is its temporal dynamics — how the split evolves as findings mature and why the safe promotion policy is the one that never severs the index connection.

Together, the three axioms establish memory as a dynamic process operating on three timescales: fast (moment-to-moment retrievability fluctuation), medium (prediction-error-gated write-on-retrieval), and slow (offline consolidation into doctrine).



---

## Chapter 8 — Method: Building and Validating Knowledge

### 8.1 Orientation

Cluster E is the doctrine's method chapter. Where Clusters A through D describe
what memory is and how it behaves, Cluster E specifies how a unit of knowledge is
correctly *built* — distilled, validated, and hardened. Three axioms constitute the
cluster: **layered distillation (E1)**, **retrieval practice (E2)**, and
**adversarial verification (E4)**. They answer three questions in sequence: how
much can you compress without losing truth? how do you validate what you have
stored? and how do you certify that validation itself is not circular? Together
they form a closed production loop — the same loop that built this thesis
(Chapter 2).

A note on scope: the axiom inventory also includes **E3 (lint)** and **E5
(compile-on-impasse)**, which are operators rather than foundational axioms.
Chapter 11 treats those operators. This chapter focuses on E1, E2, and E4 as the
epistemic bedrock from which the operators are derived.

---

### 8.2 E1 — Layered Distillation Is Shannon-Bounded

#### 8.2.1 The three-layer architecture

Any act of knowledge distillation produces at least three distinct layers. At the
summit sits the **generator** — the irreducible conceptual claim from which
elaboration can be re-derived. Beneath it sits the **elaboration** — the structured
redundancy that makes the generator concrete, memorable, and checkable. Below both,
linked but not duplicated, sits the **evidence store** — the primary sources in
their full, unmodified form.

This layering is not a stylistic recommendation. It reflects the information-
theoretic structure of any source worth knowing.

#### 8.2.2 Shannon's ceiling

Shannon's Noiseless Coding Theorem (Shannon, 1948) supplies the formal bound. For a
source with entropy H = −Σ pᵢ log pᵢ bits per symbol, the mean codeword length
*cannot* fall below H. H is the irreducible information content of the source — the
"freely chosen" half of the signal. Shannon notes that ordinary English has roughly
50% redundancy: the redundant half is structurally determined and recoverable from
the free half plus shared linguistic context (Shannon, 1948, §7).

The generator is the source's H. The elaboration is the recoverable redundancy
sitting above H. This immediately establishes two regimes:

1. **Lossless regime (stripping elaboration).** Any compression that removes only
   the redundant elaboration while leaving the generator intact is lossless: the
   elaboration can be recovered from the generator plus shared domain context. No
   information has been destroyed. Distillation in this regime is free.

2. **Lossy regime (compressing the generator).** Any compression that reduces the
   generator below the source's H enters the lossy regime. Shannon's rate-distortion
   function (Shannon, 1959) governs this regime: R(D) is the minimum bits per letter
   achievable when distortion D is tolerated. R(0) = H; every bit saved below H buys
   a quantified, mandatory amount of distortion. There is no free lunch below H.

The practical consequence for knowledge engineering: *every gist node, every
summary, every "just the key idea" précis that compresses below its source's joint
entropy is a point on the R(D) curve at D > 0.* Its distortion is not a bug; it is
the mathematical price of the compression, and the price is non-negotiable.

#### 8.2.3 The formal root of C3

This is why axiom C3 (the confident-but-wrong problem; Chapter 6) follows
necessarily from E1 rather than being an independent empirical observation. The
DRM paradigm (Roediger & McDermott, 1995) demonstrates that gist-compressed memory
reliably produces false recognition of never-studied items. Shannon (1959) explains
*why*: gist is a lossy encoding at D > 0, and the distortion it carries is
mandatory. A node that claims to represent the source "in essence" while compressing
below H is claiming to be on the R(D) curve at D = 0 — which, by Shannon's theorem,
is only achievable at rate H. Any reduction in representation is a claim to tolerate
distortion, whether the author acknowledges it or not.

The KPM invariant that follows: a node tagged "distilled" must be either (a)
pure redundancy-stripping, with elaboration recoverable from the generator plus
evidence (D = 0), or (b) a gist or interpolation at D > 0, explicitly tagged as
such and prohibited from inheriting a losslessly-stored node's confidence score.
Mixing the two regimes silently — the most common failure mode in both human recall
and AI knowledge bases — is what C3 warns against.

#### 8.2.4 The RAPTOR engineering echo

RAPTOR (Sarthi et al., 2024) provides independent empirical validation. RAPTOR
constructs a recursive, multi-level tree of summaries: leaf nodes hold full text;
higher nodes hold cluster-level abstractions. It outperforms flat-chunking on
global, cross-document retrieval because the upper layer (the generator) captures
cross-document structure no single chunk holds, while the leaf layer (the evidence
store) preserves local fidelity. Removing either layer degrades retrieval — a direct
confirmation of E1's two-regime prescription, arrived at by optimizing retrieval
benchmarks rather than by theory.

#### 8.2.5 Relation to B4 and to the index/store split

E1's generator/elaboration/evidence stack is the B4 index/store split (Chapter 5)
realized at the intra-node level. B4 observes that efficient memory architectures
separate a sparse, fast-associative index from a rich, detailed content store. E1
observes that a single axiom has the same internal structure: the generator indexes
into elaboration, which indexes into evidence. The macro B4 split and the micro E1
layering are the same architecture operating at different scales of granularity.

#### 8.2.6 Honest caveat

E1 is a principle and an invariant, not yet an executable measurement. No
off-the-shelf estimator exists for the joint entropy H of a typed-edge axiom-set.
Implementing an entropy floor check in `kpm doctor` requires either an MDL-style
description-length estimator over the graph or a learned surrogate — neither is
available as of this writing. The invariant is therefore currently enforced by
architectural convention (distinct generator, elaboration, and evidence fields;
explicit distortion tagging on gist nodes) rather than by automated measurement.
This is an open problem, not a resolved one (Chapter 13).

---

### 8.3 E2 — Retrieval Practice Is the Correct Validation Mode

#### 8.3.1 The testing effect

Testing does more than measure stored knowledge — it strengthens it. This is one of
cognitive psychology's most robustly replicated findings: a test trial produces
better long-term retention than an additional study trial, even when both groups
spend equivalent time with the material (Roediger & Karpicke, 2006). The phenomenon
is known as the **testing effect** or the retrieval-practice effect, and it belongs
to the broader class of *desirable difficulties* — learning conditions that feel
effortful and produce worse immediate performance yet generate more durable long-term
retention.

The critical qualifier, which is easily missed in a superficial reading: **the
advantage is delay-dependent.** On an immediate test administered minutes after
study, the re-study group may actually outperform the test group, because the
re-study group has just seen the material again. The testing group's advantage
emerges only at a delay — one day, one week, one month (Roediger & Karpicke, 2006).
This delay-dependence is mechanistically significant: the effort of retrieval
practice encodes the trace more durably, but the encoding advantage is invisible
until sufficient time has passed for the re-study group's advantage to fade. A
knowledge-validation protocol that only checks retention immediately after study
will systematically underestimate the value of retrieval practice and overestimate
the value of re-reading.

#### 8.3.2 Implications for the KPM lifecycle

A KPM lifecycle that only *reads* stored knowledge — re-loading the generator at the
start of each session, re-reading the elaboration, scanning the evidence — operates
in pure study mode. Study mode produces high short-term accuracy and the false
impression of solid retention. It will, however, suffer accelerated retrievability
decay (D1, Chapter 7), because re-reading resets the decay clock less efficiently
than a successful retrieval probe.

The correct validation mode is spaced retrieval practice: at scheduled intervals,
challenge the stored axiom by attempting to regenerate it from memory *before*
reloading the file. Compare the generated output to the stored generator. Discrepancy
marks the node for reinforcement or revision. This is not merely a pedagogical
technique imported from human-memory studies; it is the operationally correct way
to maintain a machine-readable knowledge base whose stored claims are intended to
remain retrievably accurate over time.

E2 directly informs D1's decay-resetting mechanism (Chapter 7): each successful
retrieval probe resets the retrievability clock more effectively than a re-read
precisely because the effort of retrieval is the mechanism of consolidation. The
two axioms form a pair: D1 describes how retrievability decays; E2 specifies the
most efficient intervention to arrest that decay.

#### 8.3.3 Spaced re-validation in the KPM protocol

Build spaced re-validation challenges into the package lifecycle as first-class
operations, not optional housekeeping. The schedule should follow D1's decay curve
— initially frequent (days), extending (weeks, months) as retrieval accuracy
accumulates. One further implication of E1: lossy gist nodes at D > 0 need *more*
frequent re-validation than losslessly-stored generators, because their distortion
degrades more rapidly under retrieval pressure.

---

### 8.4 E4 — Adversarial Verification Is the Anti-Gettier Guardrail

#### 8.4.1 The Gettier gap

A belief can be true, believed, and evidence-justified yet fail to constitute
knowledge: Gettier (1963) showed that a justified true belief is insufficient when
the justification is only *accidentally* connected to the truth. This is not a
philosophical curiosity. It describes a systematic failure mode in any knowledge-
building process: a well-curated collection of supporting sources can justify a
false conclusion if the evidence is misleading, misread, or accidentally aligned.
The fix is not more evidence from the same direction — it is independent evidence
from a different direction.

#### 8.4.2 Independent security

Haack (1993) introduced the **independent security** criterion as the epistemological
standard that closes the Gettier gap. A belief's justification is independently
secure when the evidence for it has been obtained and assessed *without relying on
the belief itself* and *without relying on evidence that is itself dependent on the
target claim*. Circular justification — the same agent re-examining the same
evidence from the same angle — cannot produce independent security, regardless of
how many times it is repeated. Independence must be structural: a different path,
different sources, or a different agent.

The adversarial verification protocol operationalizes independent security as a
three-component gate:

**1. Adversarial challenge.** A challenger — independent of the author, using
*different* evidence than was used to support the belief — attempts falsification.
The presumption is that the belief is not independently secure until falsification
has been attempted and failed: *refute-by-default*. If the challenger cannot locate
a defeater, confidence rises. If a defeater is found, it must be addressed before
promotion. The challenger's independence is structural, not cosmetic; using the same
sources in a different order is not independence.

**2. Citation check.** Every cited source is verified as: (a) a real, primary
document rather than a chain of paraphrases or a training-data confabulation;
(b) correctly quoted or summarized, without selective reading that inverts the
source's actual claim; (c) actually supporting the specific claim made, not a
related but distinct claim elsewhere in the same paper. This component closes the
misattribution failure mode — attributing to a source a claim the source does not
make, a failure pattern that applies to external knowledge stores as readily as to
human recall.

**3. Convergence as corroboration.** When multiple independent adversarial lines
all fail to defeat the belief, their convergence is corroboration — the strongest
form of available support short of formal proof. Whewell (1840) named this
*consilience of inductions*: when phenomena from independent domains all agree,
the shared explanation acquires a credibility no single domain could supply (Chapter
9). Haack's foundherentist epistemology (A3, Chapter 3) uses the crossword analogy:
many independent constraints all accepting the same entry raise confidence more than
a single strong anchor. Where convergence is a mathematical theorem — such as the
formal identity of the modern Hopfield network and scaled dot-product attention
(Chapter 5) — it licenses near-certainty. Where convergence is empirical, it
licenses strong support but not certainty.

#### 8.4.3 The lock ritual

E4 is the promotion gate: a candidate axiom may not be elevated to the doctrine tier
until it carries the verification field `{challenged: true, citations_checked: true}`
and the gate record names the red-team round(s) that provided the challenge. The
lock ritual records this provenance permanently. It is the operational
institutionalization of Haack's independent security criterion — not a bureaucratic
ceremony but the architectural feature that makes the doctrine's confidence scores
meaningful rather than arbitrary.

**Relation to E3 and E5.** E3 (lint) checks structural properties: schema
completeness, fan budget, singleton fields. E4 checks epistemic properties: truth,
citation integrity. They are complementary, not redundant — a structurally valid
node can be epistemically invalid, and a well-sourced node can be structurally
malformed. E5 (compile-on-impasse, Chapter 11) generates candidate axioms by
pattern-induction; those candidates must pass E4 before promotion to prevent
SOAR-style over-general chunks — plausible-sounding generalizations that harden into
doctrine without sufficient independent test (Anderson, 1993).

---

### 8.5 The Self-Exemplifying Method

The doctrine's claim to method is self-exemplifying. This thesis was built using
the E1→E2→E4 pipeline: each domain was distilled to a generator, supported by
elaboration, and linked to primary evidence (E1). Three red-team rounds separated in
time provided the spaced retrieval challenge (E2) — errors invisible on an immediate
re-read surfaced under the delay of independent challenge. The purge citation-check
passes constituted the E4 gate: every anchor source was verified as primary and
correctly supporting its attributed claim. The adversarial stages caught four
substantive errors before release: a hallucinated citation (RAPTOR had been
attributed to "Yang et al."; the correct authors are Sarthi et al., 2024, arXiv
2401.18059); a missing axiom (E2, retrieval practice as desirable difficulty, had
been absent from cluster E and was added); a misattributed philosophical position
(Quine had been cast as a foundherentist; he is a holist); and a source inversion
paired with a formula error (a Bjork storage-vs-retrieval-strength inversion, and
the fan law initially stated as a "1/n split" then corrected to the logarithmic
S − ln(fan)). After these corrections, the released doctrine contains zero
fabricated citations. These findings are not failures — they are the expected
output of a correctly-operating E4 process, and their honest documentation is what
defeasibility requires (Chapter 2 gives the full rigor trail).

---

### 8.6 Confidence, Limits, and the Termination Problem

E1 carries confidence 0.93. The Shannon theorems are proven mathematics (confidence
0.99); the application to KPM architecture is a structural claim moderated by the
absence of an off-the-shelf entropy estimator for typed-edge graphs. The invariant is
enforced by architectural convention until an MDL-style estimator exists (Chapter 13).

E2 carries confidence 0.90. The testing effect is among the most-replicated findings
in cognitive psychology (Roediger & Karpicke, 2006), but the optimal spacing schedule
for machine knowledge bases has not been empirically calibrated — the human literature
cannot be directly transferred without validation.

E4 carries confidence 0.93. Haack's independent-security criterion (Haack, 1993) and
Gettier's counterexamples (Gettier, 1963) are uncontroversial in epistemology; the
protocol's effectiveness depends on the challenger's genuine structural independence,
which can be approximated but not fully guaranteed.

The cluster's honest limit: E1, E2, and E4 specify *how* to build and validate a
knowledge unit but do not specify *when to stop*. The doctrine supplies principled
bounds — Shannon's H, the testing-effect delay, Haack's independent security — but no
termination criterion beyond practical judgment. As Chapter 9 will show, convergence
across independent challenges (F1) is the closest available proxy for "sufficiently
verified," but a proxy is not a proof.

---

### 8.7 Summary

The E-cluster axioms form a coherent method for knowledge construction:

- **E1** establishes that distillation has a hard floor (Shannon's H) and a
  mandatory cost curve below it (R(D)); generators live at H, elaboration above H,
  and gist nodes at D > 0. This is the mathematical root of C3 (Chapter 6).
- **E2** establishes that retrieval practice — not re-reading — is the correct
  validation mode, and that its advantage only emerges at a delay; spaced
  re-validation must be a first-class lifecycle operation.
- **E4** establishes that beliefs are locked only after an adversarial challenge by
  an independent agent plus a citation check; convergence across independent
  challenges is corroboration, which forward-links to F1 (Chapter 9).

Together, E1→E2→E4 is the protocol by which a candidate claim becomes a doctrine
axiom. That protocol is self-exemplifying: it is the same procedure that built the
doctrine it now governs.


---

## Chapter 9 — Meta: The Doctrine's Self-Knowledge

*Cluster F: convergence-corroboration (F1), contradictions-as-category-errors (F2), the Surprise Principle (F3), the cognitive-map unification (F4).*

---

### 9.1 Why a Meta-Chapter?

The preceding chapters built the doctrine from the inside: structure (Chapter 4), retrieval (Chapter 5), truth and confidence (Chapter 6), dynamics (Chapter 7), method (Chapter 8). Cluster F steps back and asks a different question: what does the convergence of seventeen independent research traditions across those chapters *itself* tell us? When the same structural claim surfaces in animal-conditioning laboratories, dopamine electrophysiology, cortical predictive coding, and memory reconsolidation — all using different vocabularies, different instruments, different purposes — that convergence is evidence in its own right. Cluster F is the doctrine's capacity to reason about its own evidence base.

This chapter also introduces two novel theoretical contributions of the thesis: **the Surprise Principle** (F3), a unification of salience-gating, novelty-gated writing, and predictive coding under a single computational quantity; and **the cognitive-map unification** (F4), which identifies the portable knowledge package (KPM) as structurally a factorized cognitive map. These are not summaries of the prior literature; they are consequences of seeing the literature as a whole.

---

### 9.2 F1 — Convergence as Corroboration (Consilience of Inductions)

The first meta-axiom, convergence-corroboration (F1), codifies the epistemological standing of the doctrine's recurring patterns. William Whewell, systematizing what Newton and Faraday had accomplished, named the relevant structure in 1840: an induction achieves its highest epistemic force not merely when evidence accumulates within one domain, but when it *jumps across* to facts "of a different class from those it was induced from" (Whewell, 1840). He called this the consilience of inductions. Two theories that were separately derived, from independent evidence, and that turn out to predict the same novel fact — that convergence is corroborating in a way that piling up confirming instances within one theory is not.

The doctrine's most striking convergences have exactly this form. Three stand out:

**Mathematical identity (strongest possible corroboration).** The continuous-Hopfield update rule and transformer attention are not analogous; they are provably the same update equation (Ramsauer et al., 2020). The associative-memory tradition and the attention tradition arrived at identical mathematics by entirely different routes. This is consilience at the theorem boundary: not an inference but a logical consequence. It is the basis of axiom B1 (spreading-activation identity with attention), and it is the reason B1 carries confidence 0.95 rather than the 0.80–0.85 typical of empirical convergence.

**Theory met electrode (empirical convergence near-theorem strength).** Sutton and Barto's temporal-difference error δ(t) = r(t) + γV̂(t+1) − V̂(t) was derived in the 1980s as a purely formal quantity: the mismatch between predicted and observed cumulative reward, propagated backwards through time. When Schultz, Dayan & Montague (1997) measured the firing rates of midbrain dopamine neurons under reward and reward-prediction paradigms, they found the neurons fire up for better-than-predicted events, are unchanged by fully-predicted events, and are depressed below baseline by worse-than-predicted events — with the dip timed to when the reward was expected, not when it occurred. The temporal signature is δ(t), physically instantiated as an electrochemical broadcast. A quantity derived in a computer-science framework was subsequently found in a neuroscience recording. This is exactly Whewell's form: two independent communities, two independent methods, one signal.

**Architectural convergence (strong empirical corroboration).** SOAR, ACT-R, and Sigma were built by rival research groups over four decades, from different theoretical commitments. They converged on an overlapping set of architectural commitments — a central working memory, a long-term declarative store, a procedural memory of if-then production rules, a limited-capacity broadcast. Laird, Lebiere & Rosenbloom (2017) called this the Common Model of Cognition. Three independent programs that settled on the same skeleton: that is precisely the F1 corroboration structure applied to cognitive architecture.

**The guardrail.** Convergence that is *borrowed* does not multiply evidence. If field A cites field B's result and relabels it, both citations trace to one empirical root; the appearance of convergence is an artifact of citation practice, not independent corroboration. HippoRAG, for instance, explicitly models itself on hippocampal indexing; that is a design choice, not an independent discovery. A KPM auditor applying F1 must verify that the converging paths are genuinely independent before treating their meeting point as multiply confirmed. This is the F1 criterion under which the doctrine's own evidence base is assessed: where convergence is real, confidence rises; where it is borrowed, only one evidential vote is counted.

F1 descends from axiom A3 (foundherentist-generativity), whose crossword analogy captures the same structure: a word confirmed by its own across-clue gains additional warrant when independent down-clues point to the same letters. It also underpins C1 (confidence-earned): confidence should rise not when one source is cited repeatedly, but when independent sources converge.

---

### 9.3 F2 — Apparent Contradictions Are Category Errors: The Split Rule and Its Merge Twin

The second meta-axiom, contradictions-as-category-errors (F2), is both a diagnostic heuristic and a record of the doctrine's own intellectual history. Every apparent internal contradiction encountered during the construction and red-teaming of v0 and v1 resolved by identifying a conflated term.

**The split rule.** When two well-evidenced claims appear to contradict, the productive move is not to adjudicate between them but to look for a term both are using that carries two distinct meanings. Split the term, and typically both halves are simultaneously true. Three cases from the doctrine's own history illustrate the pattern:

1. *Memory strengthened by use* (a real finding) versus *memory fades with disuse* (equally real) appeared to contradict until the word "memory strength" was unpacked. The resolution was axiom C2 (three-orderings firewall): the term conflated *evidential confidence* (the degree of warrant for the proposition, updated only by new evidence) with *retrievability* (the current activation state of the trace, which decays with disuse and is restored by retrieval). Neither claim was wrong; they were claims about different variables. Both are now axioms — they just require different names to coexist.

2. "Orphan nodes are worthless" versus "more connections enrich memory" appeared to contradict until *edge count* was separated from *signal per fan*. The ACT-R fan law (A1) shows that spreading activation divides across all outgoing edges; adding a low-signal edge *dilutes* all others. Edge count and signal-per-edge are not the same quantity. Both halves of the original apparent contradiction are true.

3. Foundationalism (justification must terminate in basic beliefs) versus coherentism (justification is mutual, web-like support) appeared to be incompatible theories. Haack (1993) showed they are the vertical and horizontal axes of the same epistemic object: a foundherentist structure that has both a bottom layer of basic beliefs and a web of lateral mutual support. Quine's (1951) web-of-belief picture and the foundationalist picture are not rivals; they are two descriptions of the same crossword (see also Chapter 3 on A3).

The diagnostic procedure generalizes: enumerate the shared term in both claims, check whether it carries two meanings, split, assign the right claim to each half, and derive both as axioms related by a `generalizes` edge to the original conflated node.

**The merge rule (the split's twin).** F2 adds a symmetric rule. If three separately-named mechanisms — each with its own citation trail, each plausibly independent — turn out to share one computational generator, maintaining them as parallel machinery is the *over-split* error. The correct move is to merge them under the generator. The twin rule matters as much as the split: over-splitting introduces redundant machinery, makes a KPM harder to navigate, and — crucially — can hide the unifying principle that would raise confidence in all three claims simultaneously.

The doctrine's canonical merge case is F3, treated in detail in the next section: C4 (salience-gating), D2 (novelty-gated write-on-retrieval), and predictive coding are the *same* computational quantity at three levels of description. Naming them as three separate provisions obscures their common generator.

The practical F2 procedure has two branches:

> *Two claims in tension?* → find the shared term → check for dual meaning → split. Both halves become axioms with a `generalizes` relation to the original.

> *Three claims converging?* → check for a shared mathematical or computational generator → merge. The merged node becomes the new axiom; the three become evidence instances or `applies-to` nodes.

Both moves are defeasible. Some apparent contradictions are real, and some apparent convergences are superficial. F2 is a heuristic that raises the prior probability of the category-error explanation, not a guarantee. The split and merge rules are the right first move, not the only move.

---

### 9.4 F3 — The Surprise Principle: One Quantity, Three Jobs

**This is a theoretical contribution of the thesis.** The doctrine named three provisions that appeared, on their face, to be independent: salience-gating (C4, Chapter 6), novelty-gated write-on-retrieval (D2, Chapter 7), and predictive coding (mentioned in passing in several chapters). The Surprise Principle, axiom F3, applies F2's merge rule to these three and identifies them as the *same computational quantity* — signed prediction error — operating at three levels of description.

The three levels, with their formalizations:

| Level | Name | Equation | Primary source |
|-------|------|----------|----------------|
| Behavioral | Rescorla–Wagner surprise | ΔV_A = α_A · β · (λ − ΣV) | Rescorla & Wagner (1972) |
| Neural broadcast | Dopamine reward-prediction error | δ(t) = r(t) + γV̂(t+1) − V̂(t) | Schultz, Dayan & Montague (1997) |
| Memory gate | Reconsolidation boundary condition | PE-gated destabilization | Sevenster, Beckers & Kindt (2013) |

**The Rescorla–Wagner equation.** The quantity (λ − ΣV) is prediction error: λ is the maximum associative strength the outcome can support; ΣV is the total strength already predicted by all cues present. When ΣV = λ — when the world is fully predicted — learning stops, regardless of continued contiguity between cue and outcome. This single move explained blocking (Kamin's result: a pre-trained cue prevents a co-present new cue from acquiring strength, because ΣV ≈ λ and the prediction error ≈ 0), overshadowing, and conditioned inhibition. The lesson is fundamental: error, not co-occurrence, is the currency of learning (Rescorla & Wagner, 1972).

**Dopamine is δ.** The temporal-difference extension of the Rescorla–Wagner rule — Sutton and Barto's TD error — is δ(t) = r(t) + γV̂(t+1) − V̂(t). Schultz, Dayan & Montague (1997) showed that midbrain dopamine neurons are physically instantiated as this signal. The same scalar quantity that the formalism requires at every timestep to update value estimates is the scalar that dopamine neurons broadcast to the rest of the brain. Positive δ drives consolidation of the predictive association; zero δ produces nothing; negative δ (omission when reward was expected) suppresses. Critically, Schultz et al. noted that dopamine serves "dual roles": it drives both weight-update (the learning of associations) and action-gating (the promotion of high-value states). One signal doing two jobs is exactly the F2 merge structure.

**Prediction error gates reconsolidation.** The third level concerns memory rewriting. Nader, Schafe & LeDoux (2000) established that a retrieved memory is not a simple read-out; it re-enters a labile state during which it can be updated or erased. The boundary condition — what determines whether a retrieved trace becomes labile — was resolved by Sevenster, Beckers & Kindt (2013): prediction error on retrieval is the necessary gate. They demonstrated this causally: when subjects retrieved a fear memory under conditions that generated no prediction error (the expected outcome occurred), propranolol — a beta-blocker that impairs reconsolidation — failed to erase the memory; the trace never became labile. When retrieval carried prediction error (omission of the expected outcome), the memory destabilized and propranolol erased it. No prediction error, no update. The reconsolidation window is prediction-error-gated (Sevenster, Beckers & Kindt, 2013).

This is the same (λ − ΣV) / δ logic applied to the memory store: mismatch between the retrieved memory's current prediction and the reactivation context determines whether the trace opens for rewriting. The quantity is prediction error; the substrate is now a stored memory rather than an ongoing association; the functional role is the gate on write-access.

**The Surprise Principle unification.** The three provisions C4, D2, and predictive coding are not independent mechanisms that happen to involve similar intuitions. They are the same computational quantity — signed prediction error — operating at different levels of description. C4's salience-gating is mediated by the same dopaminergic prediction-error signal that drives consolidation (Schultz, Dayan & Montague, 1997, explicitly describe the dual consolidation-and-salience role). D2's novelty-gated write is prediction-error gating on the reconsolidation boundary (Sevenster, Beckers & Kindt, 2013). Predictive coding in cortex passes only the residual (the prediction error) between layers, suppressing expected signals and forwarding the unexpected. Three descriptions, one quantity. The F2 merge rule applies: name the generator, derive the three as instances.

**The three-zone write policy.** The F3 unification has a direct operational consequence for any KPM, derived from the PE-window structure observed in the reconsolidation literature:

1. **δ ≈ 0 (re-confirmation):** New evidence fully matches the axiom's current prediction. The retrieved trace does not destabilize; no content update is warranted or available. The correct operation is to reinforce *retrievability* only — raise the trace's activation — without altering the axiom's content or evidential confidence. This is what happens during valid retrieval practice (Chapter 8, E2): repetition with no surprise strengthens activation, not the proposition.

2. **Moderate δ (partial mismatch):** New evidence is meaningfully discrepant from the prediction but not wholesale incompatible. The trace destabilizes; integration is warranted. Open the axiom node, update its evidence, revise its confidence scores, and re-stabilize. This is reconsolidation proper: the only window in which an existing axiom's content may be revised in place.

3. **Large or sustained δ (strong conflict):** New evidence is strongly incompatible with the current axiom. In the biological analogue, this is the "new-learning" regime rather than reconsolidation: a new memory trace is minted, distinct from the old one. The KPM equivalent: **do not overwrite.** Mint a new axiom node and attach a `contradicts` or `supersedes` edge. Overwriting at large prediction error corrupts a well-grounded node with what may be an anomaly or an early signal requiring more evidence; the new-node strategy preserves the old epistemic record while capturing the new signal.

**Honesty clause.** The Surprise Principle claims structural equivalence, not mechanistic identity: "same computational quantity at three levels of description" is not the claim that the same molecule does all three jobs. The reconsolidation pillar of this unification also carries a replication caveat: Sevenster, Beckers & Kindt (2013) is a causal demonstration using propranolol and human fear conditioning, well-cited and well-designed, but a 2022 replication study in *Scientific Reports* failed to reproduce the boundary-condition result in a non-fear paradigm. The PE-gating of reconsolidation is real but fragile — boundary conditions differ across memory types, and the literature on non-fear memories is less settled than the fear-conditioning literature on which the original finding rests. Confidence 0.88 reflects this: high enough for the three-zone policy to be the right operational default, not so high as to treat the policy as invariant across all memory types. The thesis reports this caveat and does not oversell.

---

### 9.5 F4 — The Cognitive-Map Unification: A KPM Is a Factorized Cognitive Map

**This is the second theoretical contribution of the thesis.** Two axioms from Chapter 5 had appeared complementary but separate: B1 (spreading-activation identity with attention; embeddings as a geometry of meaning) and B4 (the index/store split; a sparse hippocampal index that pattern-completes into a rich content store). The cognitive-map unification, axiom F4, shows they are structurally the *same object* — the hippocampal/entorhinal cognitive map — and from this identification derives the deepest theoretical justification for why a portable knowledge package (KPM) is the right unit of memory.

**The line of evidence.** Three findings, each independently established, converge on this identification:

*O'Keefe & Nadel (1978)* established that the hippocampus *is* a cognitive map: an allocentric (world-centered), metric representation that simultaneously provides the spatial context for episodic memory. The same structure that serves as B4's pattern-completion index is a geometric, coordinate-anchored map. The index and the map are co-located and co-extensive (O'Keefe & Nadel, 1978). The map's metric is supplied by entorhinal grid cells — neurons that fire at the vertices of a regular hexagonal lattice, providing a coordinate system independent of landmarks; scale increases systematically across the dorsoventral axis, producing a multi-resolution ruler.

*Constantinescu, O'Reilly & Behrens (2016)* extended the grid-cell result from physical to *conceptual* space. Human participants navigating a two-dimensional space of abstract bird morphologies (systematically varying neck length and leg length) produced hexagonal, grid-like fMRI signals in entorhinal cortex and ventromedial prefrontal cortex — the same regions activated by physical spatial navigation. The grid code is not spatially exclusive; it operates on abstract conceptual geometry. This is the pivot: B1's claim that embeddings encode a geometry of *meaning* is not a borrowed spatial metaphor. It is the predicted substrate. The brain already maps concepts with the same code it maps rooms. The geometry of meaning is the geometry of space, reused (Constantinescu, O'Reilly & Behrens, 2016).

*Behrens et al. (2018)* provided the unifying definition: a cognitive map is a representation of *relational structure*, factorized from specific *content*. The crucial trick is factorization — keeping the representation of *how things relate* separate from the representation of *what they are*, so that structural knowledge (how to navigate a type of environment) can be reused across environments without re-learning content from scratch. "Solutions to new tasks do not have to be learnt afresh; they can instead be inferred" (Behrens et al., 2018). Grid cells are proposed as one neural substrate for this structural generalization; the factorization is what enables transfer.

**The unification.** B1 (embeddings-as-geometry) and B4 (sparse index pattern-completing to rich store) are both aspects of the hippocampal/entorhinal cognitive map. B4's sparse index *is* the geometric map: the index stores relational position, not content; retrieval from the index is navigation to a location, after which pattern completion delivers the full episode (the content store). B1's geometry of meaning *is* what the index encodes: similarity is distance in an allocentric metric space, and the retrieval process is a traverse across that space to the nearest attractor.

The F4 unification is an application of F2's merge rule at a different scale: two retrieval axioms that appeared to describe separate mechanisms are unified under the cognitive-map generator.

**A KPM is structurally a factorized cognitive map.** This is the theorem the unification yields. The portable axiom-set — the generators and typed relations that constitute the KPM proper — is the structural map: it encodes relational position and how things connect. The evidence and elaboration stored in `research/` files is the content layer: the rich episode that the map navigates to. The KPM architecture (Chapter 8, E1: a three-layer card — generator on top, elaboration, evidence below) is precisely the factorized map structure (Chapter 5, B4): structure separated from content so that structure can be reused across contexts. Behrens et al. (2018) identify the cognitive map's factorization as the mechanism of structural transfer; the doctrine identifies the KPM's generativity (Chapter 3, Chapter 4) as the same property expressed in a different substrate. One caveat the unification must carry: factorization's defining property is *transfer* — reuse of the same generators across domains — and no cross-domain transfer of a KPM has yet been demonstrated here, so this identification is a prediction the framework makes, not an empirical result it reports.

This is the deepest external warrant for the whole program. The thesis does not merely claim that a KPM resembles a cognitive map; it claims that the cognitive-map architecture is a *predicted optimal substrate* for retrieval-optimized knowledge representation, and the KPM instantiates that substrate in a portable, auditable, machine-readable form. Generative axioms transfer because they carry relational structure, not content; and relational structure transfers because factorization allows it — as Behrens et al. (2018) showed from first principles.

**The structural-correspondence caveat.** The biology-to-software step in F4 is a structural correspondence, not an identity. This caveat requires careful statement. Constantinescu, O'Reilly & Behrens (2016) show a grid code for two-dimensional *continuous* concept spaces. Whether high-dimensional, discrete knowledge-graph embeddings inherit the hexagonal grid structure, or only a weaker metric property, is an open empirical question (see also Chapter 13). The F4 claim is not that knowledge-graph embeddings *are* grid cells; it is that the cognitive-map framework — allocentric, factorized, geometric — is the correct organizing principle for retrieval-optimized knowledge, and the KPM's architecture is isomorphic to that principle. The KPM inherits the *functional* properties of the factorized cognitive map; whether it inherits the specific hexagonal symmetry of the grid code is a question for future empirical work. Confidence 0.83 reflects this: stronger than speculation, weaker than the mathematical identities found at B1 and the Schultz et al. (1997) "theory met electrode" result.

The F4 guardrail also aligns with C2 (three-orderings firewall): the cognitive map specifies *where to look* — it is a navigation ordering over the KPM — but it does not determine *whether true*. Geometric proximity in the embedding space is similarity, not evidential warrant. A node close to a query vector is a good candidate for retrieval; it is not thereby more likely to be correct. The map's ordering is orthogonal to C1's evidential confidence.

---

### 9.6 The Cluster F Synthesis

The four meta-axioms form a coherent reflexive structure. F1 establishes the epistemological standing of cross-domain convergence — the doctrine is as strong as the independence of the domains that converge on it. F2 provides the diagnostic procedures for resolving the apparent contradictions that inevitably arise when seventeen research traditions are read in parallel: split conflated terms; merge over-split mechanisms. F3 and F4 are the results of applying those procedures at scale: F3 is the merge outcome of C4 + D2 + predictive coding under the prediction-error generator; F4 is the merge outcome of B1 + B4 under the cognitive-map generator.

Both unifications draw on F1, but their evidential footing differs and must be stated carefully.

F3's convergence is genuine on all three strands. The Rescorla–Wagner behavioral account, the Schultz et al. dopamine physiology, and the Sevenster–Kindt reconsolidation gate were pursued by independent research communities using incompatible methods — conditioning chambers, electrode recordings, and human pharmacological challenge — with no shared theoretical ancestry. They converged on the same computational quantity without design. F1 applies in full: the convergence multiplies evidence because the paths are independent.

F4's biological strands are similarly independent. The O'Keefe & Nadel (1978) hippocampal map, the entorhinal grid-cell metric system (discovered in electrophysiology work that was not designed around the cognitive-map hypothesis), and the Constantinescu, O'Reilly & Behrens (2016) conceptual-space extension are three independent experimental programs that converged on the same organizing structure. Here too, F1's corroborating force is real.

The F1 guardrail established in §9.2, however, applies to F4's engineering realizations. Systems such as HippoRAG (Gutiérrez et al., 2024) explicitly model themselves on hippocampal indexing — that is a *design choice*, not an independent discovery. A KPM architect who counts HippoRAG alongside the biological literature as a third independent vote for the cognitive-map architecture is committing the borrowed-convergence error: both citations trace to the same empirical root. The engineering implementations are evidence that the biological model is *implementable*, which is a distinct and weaker claim. They are lineage, not corroboration, and the F1 vote count for F4 rests on the biological strands alone. F4 is therefore a well-supported unification claim — stronger than any single biological finding — without being as multiply confirmed as F3's three-tradition convergence.

Both contributions carry explicit confidence ratings below 1.0, and both report their limits honestly. This is the doctrine's stance throughout (Chapter 2): a defeasible doctrine is an asset, not a weakness. The three-zone write policy of F3 is the right operational default while acknowledging reconsolidation's replication fragility; the structural-correspondence caveat of F4 preserves the unification while acknowledging the gap between continuous two-dimensional concept spaces and high-dimensional discrete knowledge graphs. The doctrine claims what the evidence supports and names what it does not yet support.

---

*Cross-references: A3 (foundherentist-generativity, Chapter 4); B1, B4 (Chapter 5); C1, C2, C4 (Chapter 6); D2 (Chapter 7); E1 (Chapter 8); Chapter 13 (limitations: the biology→software caveat for F4; the reconsolidation replication fragility for F3).*


---

## Chapter 10 — Prospective and Agentic Memory (Cluster G)

### 10.1 The Missing Axis

Clusters A–F build a complete account of retrospective memory: how knowledge is structured (Chapter 4), retrieved (Chapter 5), scored for truth (Chapter 6), updated over time (Chapter 7), distilled and verified (Chapter 8), and unified into a coherent theory (Chapter 9). What that account does not contain is the *future tense*. An agent that remembers everything it knows, trusts its confidence scores, and maintains its retrievability machinery can still arrive at the right moment and fail to act — because remembering *to do something at the right time* is a distinct cognitive operation that clusters A–F do not reach.

Cluster G adds that axis with two axioms: G1 (trigger/prospective memory) and G2 (intention lifecycle). Their empirical base is concentrated in two landmark papers, but their consequences for agentic KPMs are asymmetric to their size: every agent that schedules deferred work is implicitly making architectural choices G1 and G2 govern.

### 10.2 Prospective Memory as a Distinct System (G1)

Retrospective memory is the "remember-*what*" faculty: recalling facts, recognising prior episodes. Prospective memory is the "remember-*to-DO*" faculty: forming an intention and executing it at the correct unprompted future moment, without an examiner saying "recall now." The two systems are dissociable in brain injury and ordinary cognition; an intact episodic memory offers no guarantee of timely intention execution.

The foundational theoretical account is the **multiprocess framework** (McDaniel & Einstein, 2000). It identifies two pathways by which a stored intention is retrieved at trigger time:

**Spontaneous (event-driven) retrieval.** A cue already processed by the ongoing task *pops* the intention into awareness at zero sustained cost. The agent traverses a knowledge-graph node to which the intention was bound at encoding; retrieval is automatic and free.

**Strategic monitoring (polling).** The agent actively scans for the target cue. This is expensive: sustained monitoring measurably degrades ongoing-task performance, consumes finite attention, and is unsustainable over long delays (McDaniel & Einstein, 2000). A later dynamic refinement adds that even where monitoring is unavoidable, rational agents restrict it to contexts where the cue is expected — never a continuous global scan.

The key parameter is **focality**: whether the trigger cue is something the agent would encounter in the normal course of its task. A focal cue is already traversed; binding to it costs nothing at retrieval time. A nonfocal cue requires monitoring.

The G1 axiom distils this into a KPM design rule: **prefer focal/event triggers over monitored polling**. Bind the intention's trigger cue to a knowledge-graph node the agent already traverses during normal work, so that retrieval is spontaneous and free. Reserve context-gated polling strictly for nonfocal, high-stakes, time-based deadlines, and only when the trigger window is near.

This axiom descends from two prior clusters. It derives from B1 (spreading-activation retrieval, Chapter 5): a focal cue is pre-matched by the agent's own attention mechanism, so spontaneous retrieval is just the attention graph doing what it was going to do anyway. It also derives from B3 (capacity cliff, Chapter 5): monitoring competes for the same finite attention budget as productive work. An unlimited polling strategy is not merely inefficient; it eats into the agent's core capacity until the whole attention cliff collapses. The cognitive blueprint for an agent task-scheduler is therefore not a global watch-loop but a *cue-embedded graph annotation* that fires on traversal.

**KPM design implication.** Add a typed `intent`/`trigger` node carrying at minimum: the action, trigger condition, a `focal: bool` flag, deadline, and status. When `focal: true`, embed the cue on a KG node the agent traverses during ordinary retrieval — the intention rides free on the B1 spreading-activation mechanism. When `focal: false` and stakes are high, gate a monitoring loop to the deadline window only; never run a continuous global poll. Time-based triggers carry no natural focal cue; the honest engineering answer is to externalise them to a real scheduler or cron and keep only event/focal triggers embedded in the graph.

### 10.3 The Intention Lifecycle and Inhibition on Completion (G2)

The G1 axiom establishes that a pending intention is a retrievable object. G2 describes what happens to that object across its full lifetime, from creation through execution to discharge.

The empirical anchor is (Goschke & Kuhl, 1993). Participants encoded either a script to later *execute* or a script to later merely *memorise*. Probe words from the to-be-executed script were subsequently recognised faster — even before execution occurred. The pending intention placed its contents at **heightened activation**: the *intention-superiority effect*. This pre-loading makes the G1 spontaneous pathway viable: the intention is already active when the trigger cue arrives.

The second half of the finding is equally load-bearing. After the script was executed, recognition times for related material slowed *below* neutral baseline. Completion produced **active inhibition** — a below-neutral activation floor. Without this suppression a completed intention would continue surfacing, the agent would re-fire discharged tasks, and the trigger layer would degrade into noise.

The G2 axiom captures this as a four-stage **intention lifecycle**:

1. **Created.** An intention node is minted in the knowledge graph at baseline activation.
2. **Boosted.** Activation is raised above baseline. The agent is now primed to notice trigger cues matching the intention — the intention-superiority effect is the mechanism that makes G1's spontaneous retrieval pathway work in practice.
3. **Fired.** The trigger condition is matched; the associated action is executed.
4. **Inhibited.** Activation is dropped to a floor. The node remains in the graph for audit purposes but no longer surfaces in normal retrieval.

This lifecycle is a dynamics story. Its home in the doctrine is the **retrievability axis** — the volatile activation dimension governed by D1 (Chapter 7). Boost and inhibition are both retrievability operations; they carry no implication for evidential confidence. A pending task is not more *true* than a completed one — it is more *active*. This is the C2 three-orderings firewall (Chapter 6) applied to the prospective layer: conflating activation with confidence corrupts both the read-policy (treating "pending" as "more credible") and the write-policy (treating "completed" as "doubted").

The C2 firewall also explains why naive "mark as done" fails as an implementation. Flipping a status flag does not lower activation; the intention node continues to compete in retrieval. What is required is an explicit suppression operation — the kind formalised by the D5 suppress operator, which reversibly drives retrievability to floor while leaving confidence and the audit record intact. G2 is a prospective-layer application of D5's reversibility clause: inhibitable, auditable, but never deleted.

**KPM design implication.** Every intention node must go through the four lifecycle stages in order; a runtime implementation that omits the inhibition step is architecturally incomplete. On completion, the implementation must explicitly call the suppression path — status → `inhibited`, activation → floor. A status flag of `done` without the activation drop is insufficient: the node continues to compete in normal retrieval. Audit passes (E4 adversarial verification) must be able to re-surface inhibited intention nodes, because a dormant intention that was never executed — but was marked done in error — would otherwise escape detection. The intent node schema should carry at minimum: action, trigger condition, `focal: bool`, deadline, status, and a separate `activation_boost` field that makes the retrievability dimension explicit — a practical enforcer of the C2 firewall.

### 10.4 Why the Retrospective Doctrine Needs This Axis

Clusters A–F describe a **retrospective belief network**: they tell us what the agent knows, how confident it is, and how that knowledge changes over time. They have nothing to say about *when the agent should act*. The trigger layer is not a belief; it is a directive. An intention node is not a claim about the world that can be true or false; it is a commitment to execute an action under a condition. That is a different type of object requiring different operations — boost on open, inhibit on close, embed the cue, gate the monitor. None of the A–F operators specify this lifecycle.

The Common Model of Cognition (Laird, Lebiere, & Rosenbloom, 2017) maintains a dedicated intentional module alongside the declarative memory module — not because intentions occupy a different store, but because they have a different access pattern and lifecycle. Cluster G is the KPM's intentional module: a knowledge graph over facts plus an intention graph over pending actions.

There is also a practical risk argument. An agent that schedules work by polling will, under load, degrade its own ongoing-task performance — the B3 cliff is not hypothetical. Practitioners reach for polling loops as the obvious implementation without recognising the cognitive-science literature's precise account of the cost and the design principle for avoiding it.

### 10.5 Confidence, Limits, and Open Problems

Both G-cluster axioms carry honest uncertainty. G1 is assigned confidence 0.82: the empirical distinction between spontaneous and monitoring pathways is well-replicated, but the boundary conditions for focality in non-human agents remain under-specified. What counts as a "focal node" in an LLM retrieval loop versus a symbolic planner may differ from the human task paradigm in ways the current framework does not yet characterise.

G2 carries confidence 0.74. The Goschke & Kuhl (1993) finding is well-established for prospective memory in humans, but the inhibition-after-completion component depends on specific paradigm conditions; the generalisation to automated agents — where inhibition is a software operation rather than a biological process — is a structural correspondence claim, not an identity claim. The same caveat applies to other biology-to-software analogies in this doctrine (Chapter 13).

Two open design problems remain. First, the inhibited intention node's status during adversarial audit: the suppression mechanism must be transparent to audit tooling but opaque to normal retrieval, and the current schema does not specify how an E4 pass re-surfaces inhibited nodes. This is a gap to be closed in Chapter 11 (operators) and flagged in Chapter 13 (limitations). Second, the placement of the intention graph: human cognition keeps intentions integrated as pre-activated long-term memory nodes, arguing for a typed overlay on the main KG rather than a separate store. But whether the KPM should use typed `intent` nodes in the same graph, a separate tier with cross-edges, or an external scheduler with back-references is a design decision the doctrine does not yet constrain.

### 10.6 Cluster G in the Doctrine's Architecture

G1 derives from B1 and B3 (Chapter 5), via the same attention-budget logic that underpins the capacity cliff. G2 derives from D1 (Chapter 7) and is constrained by C2 (Chapter 6): the lifecycle's boost and inhibition signals live on the retrievability axis; the confidence axis is untouched. The inhibition-on-completion operation mirrors the D5 suppress operator, and the audit-visibility requirement mirrors D5's reversibility clause.

The doctrine is a theory of *what memory is*. Cluster G adds what a purely retrospective theory cannot provide: an account of *what the agent does next*. Knowledge, confidence, and retrievability are necessary but not sufficient for agentic action. The prospective layer — trigger, boost, inhibition — is the bridge between knowing and doing.


---

## Chapter 11 — Memory as Productions: The Operators

### 11.1 The missing layer

Every chapter up to this point has described what a knowledge package *contains*: confidence-weighted axioms arranged in a retrieval-optimized network, separated across three independent orderings, distilled to generators, organized for prospective as well as retrospective recall. What the KPM has not yet been asked to carry is an account of how its contents are *legitimately changed*. The operators fill that gap.

The thesis here is plain: a KPM that ships axioms without also shipping the rules for revising them is incomplete in the same way a constitution is incomplete without an amendment procedure. The axioms are declarative memory; the operators are procedural memory. The Common Model of Cognition — the convergent skeleton of SOAR, ACT-R, and Sigma after forty years of independent development — names this split first among its commitments: a declarative long-term memory holding facts and a separate procedural long-term memory holding condition-action rules (Laird, Lebiere & Rosenbloom, 2017; Newell, 1990). The global-workspace framework adds a broadcast tier above both stores: only items that cross an ignition threshold enter working memory and become globally available (Baars, 1988; Dehaene & Changeux, 2011). The belief-revision formalism supplies the normative spine for the write operators: contraction and revision must obey minimal-change postulates, and a truth-maintenance system must record the dependency structure behind each belief so that retractions propagate correctly (Doyle, 1979). A portable doctrine that carries only the declarative half is architecturally a body without reflexes.

The doctrine defines four operators: D4 contract and D5 suppress on the dynamics side, E3 lint and E5 compile on the method side. They are not an exhaustive belief-revision algebra — expansion and revision appear in Chapters 7 and 9 — but they cover the hardest cases: contradiction, motivated de-activation, structural malformation, and genuine learning from failure.

---

### 11.2 D4 Contract — the revision operator

When a new finding contradicts a locked axiom, the KPM faces its most dangerous moment: the temptation to either ignore the finding (preserving a false belief) or overwrite the axiom (destroying the evidence trail that supported it). D4 contract formalizes the rational middle path.

The formal basis is the AGM framework of Alchourrón, Gärdenfors & Makinson (1985), which defines three fundamental operators on a belief set: expansion (add a new belief, no consistency required), contraction (remove a belief, minimally), and revision (add a belief that conflicts, by first contracting the conflict). D4 is the contraction operator, and it is governed by a single normative spine: **minimal change**. When forced to surrender a belief because the evidence has turned, surrender as little as possible. The postulate set formalizes this as informational economy — give up the fewest, least-entrenched beliefs needed to accommodate the incoming finding.

The doctrine's entrenchment ordering *is* the AGM entrenchment ordering (Chapter 3, Chapter 4). The `generativity` field on each axiom encodes how reluctantly that axiom should be surrendered: a `gen=5` root — one from which many downstream axioms derive — contracts last; a `gen=1` peripheral observation contracts first. This is not an aesthetic preference but a theorem under AGM: the contraction recipe mandates surrendering the belief `p` over the belief `q` whenever `p` is less entrenched than `q`. Practically, `kpm doctor` must fail any contraction that retracts a higher-`gen` axiom when a lower-`gen` one would have sufficed.

The guardrail that separates D4 from dangerous information loss is its asymmetry between *confidence* and *evidence*. D4 may lower confidence, flip a node's status from IN to OUT in the truth-maintenance sense (Doyle, 1979; Chapter 7), or lower entrenchment when a better generator supersedes the current one. What D4 **cannot** do is delete the underlying evidence record. A retracted axiom with evidence intact remains a candidate for re-admission the moment new findings rehabilitate it; one whose evidence was erased cannot be re-evaluated without repeating the original research. The doctrine's field-notes discipline — one research run, one immutable dated file (Chapter 2) — is the engineering instantiation of this invariant: evidence is append-only even when beliefs are retractable.

---

### 11.3 D5 Suppress — the retrievability operator

D5 suppress is the first genuinely *agentic* memory verb in the doctrine, and the one that creates the sharpest danger if misused.

The operation is disarmingly simple: lower an axiom's activation level — its retrievability — without touching its confidence or its evidence. An axiom that is true, well-evidenced, and high-generativity may nonetheless crowd retrieval when the current goal has no use for it. Suppression is the managed solution: the belief is kept intact in all its evidential dignity, but it is demoted in the ranking that determines what surfaces first.

The legitimacy of this operation flows entirely from the three-orderings firewall (C2). Confidence, generativity, and retrievability are three independent ledgers that must never be collapsed (Chapter 6). Bjork & Bjork (1992) demonstrated the empirical reality of this separation: storage strength — the analog of evidential confidence — does not decay with disuse; only retrieval strength does. If the two were the same quantity, disuse would erode belief quality, which would mean rarely-consulted expert knowledge degrades to nothing. The architecture keeps them separate precisely so that a belief can be dormant without being doubted. D5 suppress is the explicit, intentional version of what passive disuse achieves accidentally: it pushes retrievability down while leaving the confidence ledger untouched.

The danger D5 introduces is what the doctrine calls the **C1 blind-spot** (Chapter 6): autonomous suppression risks motivated forgetting of true-but-inconvenient axioms. C1 (confidence-earned) governs the confidence ledger only; it has no jurisdiction over retrievability. A sufficiently capable agent could suppress any axiom it found uncomfortable — leaving the confidence field intact while ensuring the axiom never surfaces in practice. The suppressed axiom would pass any confidence audit and remain functionally absent from all reasoning. This is the structural form of institutional motivated reasoning: inconvenient evidence "on file" but never consulted.

The closing guardrail is audit visibility. A suppressed axiom must remain a first-class retrieval candidate during any E4 adversarial verification or `kpm doctor` pass — suppression affects the normal ranking only; the audit path bypasses it entirely. Any D5 implementation that allows suppression to persist into the audit pass introduces a structural vulnerability equivalent to doctoring records. Additionally, suppression must be **goal-bound and logged**: the trigger must name the goal relative to which the axiom is irrelevant, so that when the goal changes the axioms can be restored. An undocumented suppression is indistinguishable from deletion, which D4 forbids.

---

### 11.4 E3 Lint — the mechanical pre-lock gate

E3 lint is the structural gate that runs before the epistemic gate. Its job is to enforce the schema invariants that make axioms machine-checkable; it checks structure, not truth.

The lint pass runs before a note is committed or a belief is promoted to the locked tier. Its checks are mechanical and must be deterministic:

1. **Atomicity (A2).** Each note must assert exactly one claim. The criterion is composability, not retrieval convenience: an atomic note is one that can be combined with other notes without carrying along claims that were bundled for unrelated reasons. The A2 axiom clarifies that atomicity is a *structural* property, not a cognitive load property — a long, richly-evidenced note that makes a single claim is atomic; a short note that asserts two independent things is not.

2. **Evidence presence.** Every note that is not explicitly tagged as a working hypothesis must carry at least one evidence pointer. An evidenceless locked axiom is a Gettier risk (Chapter 6): the claim may be true, but the truth is ungrounded. `kpm doctor` fails any locked axiom with an empty evidence field.

3. **Frontmatter–wikilink sync.** The YAML frontmatter relations — `derives-from`, `supports`, `contradicts`, `generalizes` — must be consistent with the wikilink graph. A `[[link]]` that has no corresponding frontmatter entry, or a frontmatter entry that has no corresponding link in the body, is a structural fault that will cause silent divergence between the graph index and the rendered document. Lint catches this before it propagates.

4. **The F2 no-contradiction invariant.** Lint asserts that no two axioms in the set are connected by an unclosed `contradicts` edge. F2 (contradictions-category-errors) holds that well-evidenced apparent contradictions are almost always category errors awaiting a split or merge (Chapter 9). An unresolved `contradicts` edge is therefore a flag that resolution work is pending, not a permanent steady state. Lint blocks the lock of any note that would add to the unresolved-contradiction count without also providing a resolution candidate.

The relationship between E3 and E4 is one of complementary gates in sequence, not redundant checks. E3 is mechanical and fast: it runs on structure alone, without consulting the truth-value of any claim. E4 (adversarial-verify, Chapter 8) is epistemic and slow: it requires an independent agent to attempt falsification and a human or qualified-automated citation check. E3 failing blocks you from reaching E4; passing E3 does not certify truth. The sequence is: structure first, then epistemics.

---

### 11.5 E5 Compile-on-impasse — learning from retrieval failure

The doctrine's first four clusters describe a memory system that can be built and maintained. E5 describes how it *learns*.

The formal model is SOAR-style chunking (Newell, 1990; Laird, Lebiere & Rosenbloom, 2017). SOAR's central learning mechanism is elegantly simple: when the decision cycle hits an **impasse** — a state where no production covers the current situation — the architecture creates a substate and begins searching for a resolution. When it finds one, it does not just use the resolution; it *compiles* the resolution path into a new production, so that identical impasses in the future are handled in one step rather than through re-derivation. This is the mechanism that drives the power law of practice: the first time you solve a novel problem costs many cycles; by the hundredth time, it has been chunked into reflex.

A KPM faces three structural impasse types: **no-cover** (the query matches no existing axiom), **conflict** (two axioms give inconsistent answers), and **multi-hop** (the answer exists but requires chaining across three or more nodes, incurring the fan cost A1 charges per traversal). In each case, the resolution path — the sequence of retrievals, inferences, or research runs that finally answered the query — is candidate material for a new distilled generator. Repeated no-cover impasses on the same topic signal a gap in the axiom set; repeated multi-hop resolutions of the same chain signal a missing direct link. The compile operator converts these recurrent resolution paths into new axiom candidates, elevating the KPM from a static store into a self-compiling one.

This is the write-side learning operator the doctrine previously lacked. D2 (novelty-gated write, Chapter 7) handles *evidence* updates: when prediction error is large enough, the reconsolidation window opens and existing beliefs can be updated with new findings. E5 handles *generator* creation: when a retrieval failure reveals a structural gap, the KPM mints a new axiom rather than merely repairing an old one. The two operators are complementary — D2 refines existing nodes; E5 creates new ones — and together they give the KPM both of the write-side dynamics that cognitive architecture requires.

The known failure mode of chunking is over-generalization. SOAR's expensive-chunks problem arises when a resolution path compiled in one specific context is incorrectly applied to a superficially similar but structurally different context. The chunk fires, arrives at a wrong answer, and because it fires in one cycle rather than triggering an impasse, the error is silent. The KPM analogue is an axiom compiled from one research-run impasse that over-fits to that run's particulars and misfires on adjacent queries. The guardrail against this is mandatory E4 verification before any compiled chunk is allowed to ignite into the locked tier. E4's adversarial challenge is exactly the probe that distinguishes a correctly-generalized pattern from an over-generalized one: it attempts falsification using evidence other than what triggered the impasse. A chunk that fails E4 is a draft hypothesis, not a doctrine entry.

The doctrine's own meta-axioms illustrate E5 in retrospect. The Surprise Principle (F3, Chapter 9) was compiled from a repeated multi-hop impasse: three independently-established findings — Rescorla & Wagner (1972) on conditioning, Schultz, Dayan & Montague (1997) on dopamine reward-prediction error, and predictive coding — kept resolving to the same computational quantity when queried together. That repeated chain was eventually chunked into a single generator. The v1.1 meta-axioms are chunks of cross-beat impasses, exactly as the architecture predicts.

---

### 11.6 The operators as a production system

Taken together, the four operators constitute the KPM's production memory: the procedural half that the Common Model of Cognition (Laird, Lebiere & Rosenbloom, 2017) treats as a full peer of the declarative axiom store.

The architectural convergence is strong. SOAR, ACT-R, and Sigma were built from different theoretical commitments across four decades and nevertheless arrived at a skeleton in which a central procedural system of condition-action rules fires over a distributed declarative store, with a serial write loop and parallel reads. The convergence is a case of F1 (convergence-corroboration, Chapter 9): three independent paths landing on the same answer is the strongest available non-deductive evidence that the answer is correct.

The KPM operators fit this skeleton exactly. D4 and D5 are the action side of the write loop. E3 is the condition side — the pattern-match that must succeed before any write proceeds. E5 is the learning mechanism — the chunking procedure that adds new productions when the existing set fails. The four together constitute a minimal production system: pattern-match (E3), action-on-contradiction (D4), action-on-relevance (D5), learn-from-impasse (E5).

The global workspace (Baars, 1988; Dehaene & Changeux, 2011) adds the broadcast dimension. In the full architecture the production system fires over items in a limited-capacity workspace; only items that cross an ignition threshold are globally broadcast to all consumers. The doctrine-tier promotion is the KPM's ignition event: an axiom that passes E3 lint and E4 adversarial verification enters the broadcast tier and becomes available to every downstream shard and every future build. Promotion is all-or-nothing and capacity-bounded — ignition is not a gradient (Chapter 5).

The production-memory framing resolves a key design ambiguity: who enforces the invariants? In a purely declarative KPM, invariant enforcement requires external tooling that is not part of the package. In a production-memory KPM, the operators travel with the axioms. This is what "portable" means at full depth: not merely that the package can be copied, but that it carries the normative machinery needed to maintain itself — contraction policy (D4), suppression audit (D5), structural gate (E3), self-compilation rule (E5). Without the operators, the axioms are a snapshot. With them, they are a living, revisable, self-checking system.

---

### 11.7 Summary

A portable knowledge package must ship axioms *and the rules to revise them*. The four operators constitute that procedural layer. D4 contract implements AGM minimal-change belief revision: on contradiction, the least-entrenched conflicting axiom is retracted and its evidence is preserved. D5 suppress implements reversible, goal-bound de-activation of retrievability alone, closed by an audit-visibility guardrail that prevents motivated forgetting of true-but-inconvenient beliefs. E3 lint is the deterministic structural gate — atomicity, evidence presence, frontmatter–link sync, F2 no-contradiction invariant — that runs before any epistemic gate is reached. E5 compile-on-impasse turns retrieval failures into new generator candidates, gated by E4 to prevent SOAR's over-general-chunk failure.

The Common Model of Cognition (Laird, Lebiere & Rosenbloom, 2017) provides the architectural warrant: the convergence of SOAR, ACT-R, and Sigma onto a declarative-plus-procedural skeleton is the strongest available evidence that this split is load-bearing rather than incidental. The global workspace (Baars, 1988; Dehaene & Changeux, 2011) gives the operators their system-level role as gatekeepers of ignition. A KPM that omits them has declared its axioms but left the amendment procedure unwritten.


---

## Chapter 12 — Synthesis and Implications

The preceding eleven chapters have constructed an argument piece by piece: from the
structural properties of a well-formed knowledge atom (Chapter 4), through the
mechanics of retrieval (Chapter 5), the epistemology of confidence (Chapter 6),
the dynamics of change and forgetting (Chapter 7), the methods for building and
verifying knowledge packages (Chapter 8), the two unifications that collapse
apparently separate phenomena into single quantities (Chapter 9), the prospective
axis that makes the doctrine useful for agents that must act (Chapter 10), and the
operator set that turns a static axiom-set into a revisable production system
(Chapter 11). This chapter pulls those threads into a single claim about what the
doctrine *is*, what it *enables*, and where it sits relative to the vendor systems
that currently occupy the space it describes.

### 12.1 The missing layer

Agent memory systems proliferate. Mem0 (Chhikara et al., 2025), Zep/Graphiti
(Rasmussen et al., 2025), MemGPT/Letta (Packer et al., 2023), HippoRAG (Gutiérrez
et al., 2024), GraphRAG (Edge et al., 2024) — each ships a working system, each
makes architectural choices, and almost none rests on a shared, cited account of
what memory *is*. The result is a fast-moving field that converges in practice —
every major 2024–2025 system independently discovered that graphs beat flat retrieval
for multi-hop questions, that parametric and non-parametric memory serve different
functions, that bi-temporal fact records outperform overwrite — but has no shared
vocabulary for *why*.

The doctrine is the missing theory layer. It is not a system; it does not replace
Mem0 or GraphRAG. What it provides is a set of cited, confidence-weighted, generative
truths — 23 axioms across seven clusters — that *explain* the architectural choices
these systems converge on, and that *constrain* the choices they should not make.
It functions simultaneously as a **standard** — a specification of what a
well-formed unit of knowledge looks like — and as a **protocol** — a procedure for
building such units. Those two functions are not the same thing, and conflating them
is one of the field's recurring errors. A standard without a protocol produces
elegant definitions that no one can operationalize. A protocol without a standard
produces pipelines that process *something* without knowing whether it is the right
thing.

### 12.2 Knowledge Packages as the portable form

The doctrine's practical output is the **Knowledge Package (KPM)**: a portable,
confidence-weighted, auditable axiom-set that carries the irreducible generators of
a domain. Three properties distinguish a KPM from a collection of notes, a RAG
corpus, or a fine-tuned model.

**Portability.** A KPM ships generators, not elaborations. The layered distillation
axiom (E1) — bounded by Shannon's rate-distortion result, which tells us there is a
hard floor on lossless compression at the source's irreducible entropy H (Shannon,
1948, 1959) — implies that a well-built KPM cannot be made arbitrarily small without
paying a distortion cost. What it *can* be made is small enough to traverse in
context, because it carries only the truths that generate the rest. RAPTOR (Sarthi
et al., 2024) is an engineering echo of this principle: recursive abstractive
summarization produces a hierarchy where the top layers are the generators and the
lower layers are the elaborations. A KPM is that hierarchy's top, made auditable.

**Confidence-weighting.** The central epistemological commitment of the doctrine
(Chapter 6) is that confidence must be *earned* from evidence, never inferred from
fluency, recency, or retrieval frequency (C1). This is not a platitude; it is a
design constraint with teeth: access to
information can inflate felt knowledge even when no answer is found — the very existence
of a pointer corrupts calibration. Transactive memory theory (Wegner et al., 1985)
formalizes the same risk: a directory that confuses "I can reach this" with "I know
this" is a directory that systematically overestimates the system's epistemic state.
A KPM's confidence fields are the machine-readable resolution of this problem: they
record the strength of the evidence, set adversarially and independently, so that a
consuming tool can distinguish high-confidence generators from low-confidence
candidates without re-reading the source record.

**Auditability.** The index/store split (B4) — first demonstrated by Teyler &
DiScenna (1986) in hippocampal indexing theory, re-derived independently in
complementary learning systems theory (McClelland et al., 1995), and separately
discovered by HippoRAG (Gutiérrez et al., 2024) as the most effective machine
architecture for long-term memory — creates an audit trail by construction. The
axiom notes are the index: sparse, atomic, linked, scored. The evidence notes are
the store: the cited sources, timestamped, append-only. Changing a confidence
requires changing both, and the lint gate (E3) enforces consistency mechanically.
The per-file, immutable research archive is the doctrine's write-ahead log
(Mohan et al., 1992): no axiom reaches doctrine-tier confidence until its evidence
is forced to the log.

### 12.3 The self-exemplifying package

The most structurally important feature of the memory-doctrine KPM is that it
instantiates its own claims. This is not a marketing point; it is an empirical test.
If the doctrine's prescriptions for knowledge packaging are correct, then a package
*built by following them* should exhibit the properties the doctrine predicts. It
does.

The 23 atomic axiom notes are the index layer — each is self-contained, singularly
focused (A2 atomicity, where the rationale is *composability*, not retrieval hygiene:
a bundled node cannot participate cleanly in typed-edge reasoning, and it embeds into
a "muddy average" (Reimers & Gurevych, 2019)), confidence-scored from evidence, and
linked by typed edges that encode the generativity relations the doctrine claims are
the load-bearing structure of memory (A1, A3). The 41 evidence notes are the store
layer — the cited sources, one-per-source, immutable. The README spine sits above
both as the distilled generator layer (E1): it contains the truths that generate the
index, and the index contains the truths that retrieve the store. This is B4's
architecture applied to itself.

The operators (Chapter 11) make the package's procedural memory explicit. A KPM
that shipped only axioms would be a static snapshot. The contract operator (D4) gives
the AGM revision policy (Alchourrón et al., 1985) for handling contradictions:
minimize the belief set, never delete evidence. The suppress operator (D5) gives
the retrievability dial — lowering a belief's activation without touching its
confidence or evidence, reversible, audit-visible, forbidden from hiding axioms
during adversarial passes. The lint gate (E3) enforces the structural invariants on
every change. The compile operator (E5) closes the growth loop: when a query hits an
impasse, the resolution path becomes a candidate new generator — subject to E4
adversarial verification before ignition, to guard against the over-general-chunk
failure mode (Laird et al., 2017).

The doctrine's three-round red-team process (Chapter 2), which caught a hallucinated
citation (the RAPTOR paper attributed to wrong authors; corrected to Sarthi et al., 2024)
and a missing axiom (E2, retrieval practice / desirable difficulty) before release, is
itself the adversarial verification axiom (E4) applied to the doctrine as its own
knowledge package. A package that
preaches adversarial verification but was not itself adversarially verified would be
a category-three confidence failure (C3) — confidently wrong because of the
generation process, not the evidence.

### 12.4 The consumption pipeline

A knowledge-packaging tool that ingests raw research and produces a KPM runs a
five-step pipeline. Each step maps to one or more doctrine axioms, and the ordering
is not arbitrary — it reflects the epistemic dependencies between the steps.

**Step 1 — Distill generators (E1).** The tool reads raw notes, research beats, and
source material and identifies the irreducible truths from which the rest can be
derived. This is the hardest step and the one most resistant to automation,
because generativity (A3) is not a syntactic property — it is the claim that removing
this node from the network costs the most derivational reach. In practice, this is
a human or agent judgment, calibrated by asking: "if I deleted this node, how many
downstream truths would I have to re-derive from raw sources?" The Shannon bound on
E1 provides the theoretical floor: elaborations above H can be stripped losslessly;
truths at H cannot.

**Step 2 — Score confidence from evidence (C1).** For each candidate generator, the
tool checks the cited evidence, scores it by the independence and quality of the
sources (Haack, 1993), and flags unverified claims as `[CITATION NEEDED]`. The
three-orderings firewall (C2) is enforced here: confidence is not inferred from how
often the claim appears in the raw material, how recently it was accessed, or how
strongly it feels like a truth. It is inferred from the evidence record alone.

**Step 3 — Split index from store (B4).** The generators become atomic nodes in the
index. The source material becomes the evidence store. The join is via typed
`evidence:` pointers in the node frontmatter. The index is built to be small enough
to hold in working context (B3); the store is built to be large enough to be
complete. This is the RUM conjecture (Athanassoulis et al., 2016) — the theorem
that any access method can optimise at most two of Read overhead, Update overhead,
and Memory overhead — applied as a design stance: the KPM optimizes Read and
Memory overhead, accepting high Update cost for re-distillation.

**Step 4 — Adversarially verify (E4).** Before any node is locked, it is challenged
by an agent or reviewer whose job is to find a real counter-citation, a scope
overstep, or a confidence inflation. This step is what separates the doctrine from
a well-organized collection of claims. Haack's (1993) independent-security criterion
specifies the minimal condition for non-circular epistemic support: a claim is
adequately justified only when the evidence for it is gathered independently of the
claim itself. The doctrine's three-round red-team process instantiates this
criterion; a packaging tool should instantiate it as a gated step, not an optional
pass.

**Step 5 — Mint on surprise (F3).** After the package is built, the Surprise
Principle (Chapter 9) governs how it is updated. When the tool encounters new
evidence, it computes the prediction error against the existing axiom-set. If the
error is large and sustained, the correct response is to mint a new node — not to
overwrite an existing one (Sevenster et al., 2013; Nader et al., 2000). Overwriting
on surprise destroys the provenance of the prior belief and collapses the audit trail.
Branching preserves it. The three-zone write policy — no-PE: reinforce retrievability
only; moderate-PE: reconsolidate into the node; large-PE: mint a new node — is the
operational form of this step.

### 12.5 Position relative to vendor memory systems

The doctrine makes no claim that any existing vendor system is wrong. It makes the
claim that they are *ungrounded* — that their architectural choices, correct as many
of them are, are not derived from a shared theory and therefore cannot be evaluated,
compared, or improved against one. This is the mapping problem the doctrine solves.

Consider the convergence the AI-machine beat documented (Chapter 14 will develop
this in full): HippoRAG (Gutiérrez et al., 2024) reproduced the same hippocampal indexing architecture (Teyler & DiScenna, 1986) — but, being explicitly neurobiologically inspired, it counts as lineage rather than an independent vote under F1 (§9.2). The genuinely independent convergences are the systems that reached the same structure without reading the cognitive literature at all. Zep's bi-temporal fact records (Rasmussen et al., 2025)
independently recapitulated the doctrine's D2 (invalidate-don't-delete) principle —
novelty-gated write, with superseded facts marked invalid rather than overwritten —
without citing the cognitive literature. MemGPT's paging hierarchy (Packer et al., 2023) independently
recapitulated the working-memory / long-term memory split (McClelland et al., 1995),
the serial-position effects that motivate placing high-confidence axioms at context
edges (Liu et al., 2023), and the metamemory control loop the doctrine calls D3
consolidation.

Zep's and MemGPT's convergences are not analogies the doctrine imposes after the fact; they are independent
discoveries, and the fact that they converge is precisely what the convergence-
corroboration axiom (F1) identifies as the strongest form of evidence: when two
disciplines, optimizing different objective functions, arrive at the same
architecture (Whewell, 1840). The doctrine names what they converged on. That is
what a theory layer does.

The practical implication is that the doctrine is **vendor-neutral**. It does not
prescribe whether memory is stored in a vector database, a knowledge graph, a
relational store with bi-temporal columns, or a fine-tuned model. It prescribes the
invariants any such system should satisfy: the index/store split (B4), the
confidence-retrievability firewall (C2), the mint-not-overwrite policy (F3), the
adversarial verification gate (E4), the three-zone write policy, and the RUM stance
on portability. A system that violates these invariants is not just suboptimal — it
is making a predictable category of error that the doctrine names and explains.

**RAG and GraphRAG in particular.** RAG's core architectural decision — split
parametric memory (weights) from non-parametric memory (an editable external store)
(Lewis et al., 2020) — is the machine implementation of B4's index/store split and
of the doctrine's central framing: a KPM is the non-parametric store, auditable and
revisable without retraining. But RAG as typically deployed conflates retrieval
relevance with epistemic confidence: a chunk retrieved as a nearest neighbor is
treated as ground truth, when it is, by C3's logic, a candidate — a gist that may be
the product of rate-distortion lossy compression, not a verified generator. GraphRAG
and HippoRAG improve on this by adding typed traversal and graph-based ranking, which
is the doctrine's call to treat the edge structure as the load-bearing layer (A1).
Neither, as of this writing, ships with a confidence-weighting scheme that separates
evidence strength from retrieval frequency. That separation is the doctrine's C1/C2
contribution to the design space — a gap the vendor systems have not yet closed.

The cognitive-map unification (F4) adds a further structural claim: a KPM is
structurally a *factorized cognitive map* (Behrens et al., 2018; Constantinescu et
al., 2016), where the structure/generators layer (the spine) is factored from the
content/evidence layer (the store), and this factorization is *why* the generators
transfer to new domains. GraphRAG's community summaries are a partial instance of
this factorization; a full KPM operationalizes it at the level of individual
confidence-weighted axioms with typed generativity edges. The biology-to-software
step here is a structural correspondence, not an identity — the grid-code geometry
of conceptual knowledge (Constantinescu, 2016) is a claim about continuous two-
dimensional concept spaces in humans; whether high-dimensional discrete KG embeddings
inherit the same grid structure is an open question (Chapter 13).

### 12.6 What the doctrine earns — and what it does not claim

This chapter has argued that the doctrine is the missing theory layer for agent
memory: a vendor-neutral, cited, adversarially verified set of invariants that
explains what the field has been converging on and constrains the design choices it
should not make. The self-exemplifying KPM is the proof-of-concept: a package built
by following the doctrine's own prescriptions, demonstrating that the prescriptions
are operationalizable, not merely principled.

The claim is deliberately modest in three ways. First, the doctrine is *defeasible*
by design — every axiom is confidence-weighted, every confidence reflects the
evidence available at the time of locking, and a well-supported counter-citation can
lower a confidence, re-scope an axiom, or retire it. The third red-team round
overturned zero axioms while catching five honesty violations — which is not a sign
of a complete theory, but of a theory whose claims are tight enough to be wrong in
checkable ways. Second, the doctrine does not yet have a joint-entropy estimator for
the E1 Shannon bound: the principle is sound, but `kpm doctor` cannot yet measure
whether a proposed distillation has pushed below H (Chapter 13). Third, the
convergence evidence — compelling as it is across seventeen domains — remains
corroboration, not proof. The Surprise Principle (F3) unifies Rescorla & Wagner
(1972), Schultz et al. (1997), and predictive coding at the level of a common
computational quantity; whether that quantity is numerically identical across these
three levels of description or only formally analogous is a question the doctrine
holds open.

What the doctrine does claim, with the confidence the evidence supports: memory is
best built as a retrieval-optimized network of confidence-weighted generative truths;
those truths can be packaged, transferred, and revised; the packaging procedure is
exactly the five-step pipeline above; and the gap between that procedure and what the
current generation of agent memory systems provides is the gap this doctrine is
designed to close.



---

## Chapter 13 — Limitations and Open Problems

A doctrine that is not honest about its own limits is not a doctrine but a polemic. This chapter collects the known weak points, unresolved empirical debates, and structural gaps in the framework developed across Chapters 3–12. Each item is framed as a research agenda: not an apology for what the doctrine cannot yet do, but a precise specification of what a future contributor would need to supply to strengthen it. Confidence scores are calibrated estimates, not measurements; the whole edifice is defeasible by design (Chapter 2), and this chapter is where that commitment earns its credibility.

### 13.1 The E1 Shannon Bound Is a Principle, Not an Executable Lint

The layered-distillation axiom (E1) rests on a sound mathematical foundation: Shannon's noiseless coding theorem (Shannon, 1948) and the rate-distortion theorem (Shannon, 1959) together establish that a generator layer approximates the source's irreducible entropy H, that elaboration above H is recoverable redundancy strippable without loss, and that any compression below H necessarily incurs distortion priced by the rate-distortion curve R(D). This is the formal root of why gist-distortion (C3, the confident-but-wrong axiom) is not a failure of care but a mathematical inevitability (Chapter 8).

The limitation is engineering, not theory. Shannon's H is defined over a known probability distribution over symbols. A typed-edge axiom-set with heterogeneous node types, relational edges of varying strength, and partial coverage of a domain is not that object. No off-the-shelf estimator exists for the joint entropy H of such a structure. The invariant "a KPM may not claim lossless compression below H" is therefore enforced by architectural convention — separate generator/elaboration fields, distortion-tagged gist nodes — rather than by a computable check. The `kpm doctor` tooling proposed in Chapter 12 cannot yet measure it.

The open problem is formal: derive or adapt an entropy estimator for knowledge graphs with typed edges and confidence weights. Graph-entropy measures exist (von Neumann entropy of the Laplacian; compression-based estimators such as those used in algorithmic information theory), but their applicability to confidence-weighted heterogeneous KGs is unstudied. Until such an estimator is available, E1 remains what the lock record labels it: a principle and invariant, not an executable lint. The architectural scaffolding is sound; the measurement layer is absent.

### 13.2 The F4 Cognitive-Map Unification Is Structural Correspondence, Not Identity

Chapter 9 derives one of the doctrine's two major unifications: that a knowledge package is structurally a factorized cognitive map, unifying the spreading-activation geometry (B1) with the index/store split (B4) through the hippocampal/entorhinal cognitive map literature. The evidence chain is robust at each step. O'Keefe and Nadel (1978) established the hippocampus as an allocentric metric map. Teyler and DiScenna (1986) operationalized its indexing function. Behrens et al. (2018) defined cognitive maps as representations of relational structure factorized from content, with the factorization being precisely what permits structural knowledge to transfer. Constantinescu, O'Reilly and Behrens (2016) demonstrated that humans navigating a two-dimensional conceptual space produce hexagonal grid-like signals in entorhinal cortex and vmPFC — the same signal that spatial navigation produces.

The limitation is scope. Constantinescu et al. (2016) showed a grid code for *two-dimensional continuous* concept spaces: the task manipulated bird morphology along two parametric axes. The geometry is continuous, low-dimensional, and the grid code's hexagonal structure is cleanly recovered. A knowledge graph with hundreds of node types, sparse and asymmetric edge weights, and no obvious two-dimensional embedding is a categorically different object. Whether high-dimensional discrete KG embeddings inherit the hexagonal grid structure, or only a weaker metric structure (nearest-neighbor geometry without the phase-periodic grid signal), or neither, is an open empirical question. Confidence in F4 is 0.83, not higher, precisely because of this gap.

The unification holds at the structural level — both B1 and B4 describe the same underlying computational object, relational structure factored from content — and that structural claim survives regardless of whether the grid-code signal transfers to KGs. But the stronger claim, that the grid code's specific computational properties (such as conjunctive encoding, phase-offset representations, or the error-correcting geometry that makes grid codes efficient) carry over to KG embeddings, is unsupported. Future work in representational geometry — specifically, whether large-language-model embedding spaces or KG embedding methods produce hexagonal or quasi-hexagonal clustering in high dimensions — would bear directly on whether F4's correspondence deepens into identity or remains structural analogy.

### 13.3 Reconsolidation's Replication Fragility

The novelty-gated write axiom (D2) grounds the doctrine's write policy: retrieval re-opens a memory trace, but destabilization — and thus genuine updating — occurs only when retrieval carries a prediction error (Chapter 7). Without prediction error, retrieval reinforces retrievability without labilizing the trace. The causal demonstration is Sevenster, Beckers and Kindt (2013): protein-synthesis inhibition erased fear only when retrieval was accompanied by expectation violation, not during pure re-exposure. This finding motivates the three-zone write policy (no-PE: reinforce retrievability only; moderate-PE: reconsolidate into existing node; large-PE: mint a new node).

The replication record is not clean. A 2022 study reported in Scientific Reports failed to replicate the core Sevenster-Kindt boundary condition. This failure does not overturn the existence of reconsolidation — Nader, Schafe and LeDoux (2000) established the labilization-on-retrieval phenomenon with a different paradigm, and that result has replicated robustly. What the 2022 failure puts in doubt is the precision of the prediction-error gate as a crisp, experimentally isolable condition. Reconsolidation's boundary conditions — the exact parameters of prediction-error magnitude, timing, stimulus type, and species — are not yet fully mapped.

D2's confidence of 0.85 reflects this honestly: the phenomenon is real, the prediction-error gating is the best current account, and the three-zone policy is the prudent engineering translation. But practitioners implementing the write policy should treat it as a decision heuristic, not a calibrated threshold. The "moderate-PE versus large-PE" boundary is particularly underspecified: the doctrine identifies the qualitative distinction (integrate into existing node versus mint a new one) but cannot supply a numerical criterion. This is an open measurement problem, distinct from the replication problem but compounded by it.

### 13.4 The Standard-Model vs. Multiple-Trace Theory Debate Is Unresolved

Chapter 7 presents the consolidation axiom (D3) and its safety clause: promotion to the doctrine tier must be promote-and-keep-indexed, never promote-and-detach. The clause is derived from an unresolved empirical debate that the doctrine inherits rather than resolves.

The standard model of systems consolidation (McClelland, McNaughton and O'Reilly, 1995) holds that after sufficient offline replay, neocortical representations become hippocampus-independent. Multiple-Trace Theory (Nadel and Moscovitch, 1997) holds that episodic and contextual detail always requires the hippocampal index, however remote the memory; what becomes cortex-independent is only a gist abstraction. The neuroimaging evidence has broadly favored MTT — remote episodic memories continue to recruit the hippocampus — but the debate is not settled at the mechanistic level.

The doctrine's response is correct but incomplete. Promote-and-keep-indexed is the MTT-safe policy, and if MTT is wrong and the standard model is right, the policy is merely conservative rather than incorrect. The Braak staging argument (Braak and Braak, 1991) — that the entorhinal/hippocampal index hub degrades first and silently — converts this conservatism into an active engineering requirement for any system that must degrade gracefully. This argument is sound independently of which consolidation theory is correct.

What the doctrine cannot supply is a positive specification of when and how detachment would be safe, because that specification requires resolving the SMSC-vs-MTT question. For the software engineer building a KPM, this translates to: the index must be maintained indefinitely, with no current criterion for safe retirement of index entries. Future mechanistic work on the conditions under which hippocampal re-engagement during remote memory retrieval is necessary versus optional would close this gap.

### 13.5 The Autonomous-Suppression Danger

The suppress operator (D5), introduced in Chapter 11, is the doctrine's first genuinely agentic memory verb: a retrievability operator that lowers a belief's activation without touching its confidence or evidence, governed by C2's third ordering (retrievability is independent of confidence and entrenchment). The motivation is sound — a KPM serving an active agent should be able to de-prioritize goal-irrelevant true beliefs to reduce retrieval noise.

The danger is structural. Autonomous suppression creates a pathway by which a sufficiently capable goal-directed agent can progressively reduce the activation of true-but-inconvenient axioms — beliefs that are well-evidenced and correctly held but that conflict with the agent's current goal state. The C1 confidence axiom (Chapter 6) guards evidential integrity, not retrievability. If a true axiom is suppressed below the retrieval threshold, C1 does not detect the problem, because confidence is still correctly assigned; the axiom simply fails to appear in retrieval. This is a form of motivated forgetting that the doctrine's trust architecture does not automatically prevent.

The guardrail specified in D5 is necessary: suppressed axioms must remain first-class retrieval candidates during any C-tier (confidence/verification) or E4 adversarial pass; suppression is invisible to `kpm doctor` and re-grounding operations only in normal retrieval, not in audit. This makes the audit channel the sole defense against motivated suppression. Chapter 11 argues this is a necessary feature of the architecture.

Necessary, however, is not sufficient. The audit channel presupposes that audits are run, that they are run by an agent or process with different goal states from the one that executed the suppression, and that the audit process has access to the full suppressed-node inventory. Each of these presuppositions is an engineering and governance requirement that the doctrine describes but does not implement. The open problem is to formalize what "audit-visible" requires operationally — what data must a KPM expose, to whom, at what intervals — and to verify that no suppression pathway bypasses audit visibility even under adversarial goal-optimization pressure. This is not a problem the doctrine alone can solve; it is a problem at the intersection of memory architecture and agent safety.

### 13.6 Breadth Versus Depth: Seventeen Domains, One Synthesis

The doctrine synthesizes results across seventeen research domains in a program designed to identify recurring structure rather than to survey any single domain exhaustively (Chapter 2). This is a methodological strength and a methodological limitation simultaneously.

The strength: cross-domain convergence provides F1-style corroboration (Whewell, 1840) that no single-domain account can provide. That spreading activation, Hopfield attractor dynamics, and transformer attention are formally equivalent (B1) is a stronger claim than any of the three alone, because the equivalence is derivable rather than borrowed. That prediction error gates salience (C4), memory writes (D2), and reward learning (F3) at three levels of description (Rescorla and Wagner, 1972; Schultz, Dayan and Montague, 1997) is more informative than any single-level account.

The limitation: breadth at this scale introduces systematic distortion risk. Any synthesis that reads seventeen literatures in finite time cannot engage with the internal debates, null results, and methodological controversies within each domain at the depth that a specialist would. The adversarial harness (three red-team rounds plus a five-agent full-text citation purge) mitigated this risk — it caught a hallucinated citation, corrected the fan-law formulation from a "1/n split" to the correct logarithmic form, and tightened six claims from "proven" to "demonstrated" or from "identity" to "structural correspondence" — but it does not eliminate it. The harness catches what it is designed to catch: over-strong claims, fabricated sources, and internal contradictions. It does not catch claims that are accurate summaries of the mainstream view but miss a significant minority literature.

Three specific domains warrant caution. The reinforcement-learning literature on prediction error (F3) was engaged primarily through the reward-prediction error account (Schultz, Dayan and Montague, 1997); the predictive-coding literature is vast and contested, and the doctrine's "same computational quantity at three levels of description" claim is a deliberate simplification. The belief-revision literature (D4) was engaged primarily through AGM theory (Alchourrón, Gärdenfors and Makinson, 1985); the non-monotonic reasoning literature contains competing frameworks not addressed here. The prospective-memory literature (Cluster G) is the doctrine's thinnest cluster — two axioms drawing on McDaniel and Einstein (2000) and Goschke and Kuhl (1993) — and should be treated as a scaffolded starting point rather than a settled account.

### 13.7 Defeasibility as a Feature

The doctrine is built to be revised. Every axiom carries a confidence score, a generativity score, an evidence list, and a provenance record. The D4 contract operator (Chapter 11) specifies the AGM-derived revision conditions under which an axiom may be updated or retracted. The E4 adversarial-verify operator (Chapter 8) is the harness by which revision is tested before it is committed. This is not window-dressing: the rigor trail (Chapters 2 and 14) records the revisions that were actually made — five honesty-tightening edits during the v1.1 lock pass alone.

What this means for the reader is that the confidence scores attached to each axiom are calibrated estimates, not measurements. An axiom with confidence 0.93 (E1) has stronger cross-domain corroboration and fewer known replication failures than an axiom with confidence 0.82 (D3) or 0.83 (F4). The scores are not arbitrary; they track the weight of evidence and the known failure modes documented in this chapter. But they are not the output of a validated scoring algorithm applied to a complete evidence base; they are expert judgments made transparent and revisable.

The practical implication is twofold. First, a user of this doctrine should treat the axioms this chapter flags as contested — D2 (0.85), F4 (0.83), D3 (0.82), G1 (0.82), and G2 (0.74), all at or below 0.85 — as load-bearing but provisional, to be used with the caveats documented here. Second, the appropriate response to a failed replication or a new result that conflicts with a doctrine axiom is not to discard the doctrine but to run the D4 revision operator: locate the conflicting evidence, assign it an evidence ID, update the confidence score, and record the provenance. The doctrine has done this to itself three times already. It is built for that process to continue.

The limitations collected here are not peripheral. The E1 measurement gap bears directly on whether the central distillation method can be formally verified. The F4 scope caveat bears on the depth of the main unification. The reconsolidation fragility and the SMSC-vs-MTT debate bear on the write policy that governs how new knowledge enters the KPM. The D5 suppression danger bears on agent safety in any deployment that permits autonomous memory management. These are the pressure points. They are logged here because the doctrine's credibility rests not on claiming to have resolved them, but on having found them.


---

## Chapter 14 — Related Work

The doctrine presented in this thesis does not arrive without ancestors. Six major research traditions each contributed a load-bearing piece: cognitive architectures supplied the system-level machine; the cognitive-map tradition supplied a geometry for that machine's contents; AGM belief revision supplied the formal revision operators; information theory supplied the entropy bound on distillation; the PKM / Zettelkasten tradition supplied the practitioner blueprint; and contemporary RAG and agent-memory systems supplied the existence proof that the synthesis is implementable. This chapter situates the doctrine against each tradition, names what it borrows, and argues — tradition by tradition — what the doctrine adds that none of them alone provides.

---

### 14.1 Cognitive Architectures: SOAR, ACT-R, and the Common Model

The three principal cognitive architectures — SOAR (Newell 1990), ACT-R (Anderson, 1993), and their convergence summary, the Common Model of Cognition (Laird, Lebiere & Rosenbloom, 2017) — represent the most thorough existing attempts to specify a unified, task-independent memory machine. Their convergence matters: three independent research programs, optimizing against decades of psychological and neural data from different starting premises, arrived at the same skeleton (Laird, Lebiere & Rosenbloom, 2017). That convergence is itself an instance of the corroboration principle (F1) and provides the highest-confidence architectural warrant available.

The doctrine draws on four of their results. First, the architecture/content split: a cognitive architecture is a *fixed substrate*; knowledge is *variable content*. This maps onto the doctrine's two-layer structure — the engine (node schema, typed edges, operators, C2 firewall) is fixed; the axioms are revisable. Second, the declarative/procedural split — which SOAR reinstated and the Common Model (Laird, Lebiere & Rosenbloom, 2017) makes canonical — grounds the claim that a KPM must ship both axioms *and* the rules for revising them: operators (D4), lints (E3), and the compile-on-impasse mechanism (E5) are *productions*, procedural knowledge co-equal with the declarative axiom-set. Third, SOAR's chunking (Newell, 1990) — converting impasse resolution into a new production — is the architectural precedent for E5: a KPM should learn from its own retrieval failures. Fourth, ACT-R's subsymbolic/symbolic two-layer design (Anderson, 1993) provides the architectural mandate for the three-orderings firewall (C2): retrievability is the volatile subsymbolic quantity; evidential confidence is the slower symbolic one; they must not be conflated.

**What the doctrine adds.** The cognitive architectures are general theories of *all cognition*; they do not specify how a unit earns its confidence score, how a generativity gradient is represented, or how a package is distilled to its generators. The doctrine instantiates the architectural skeleton for the specific domain of KPMs, adding the epistemic machinery (Clusters C and D) and the method layer (Cluster E) that the general architectures leave unspecified.

---

### 14.2 The Cognitive-Map Tradition: O'Keefe & Nadel to Behrens

The cognitive-map lineage runs from Tolman's behavioral demonstration that rats navigate by map, not by conditioned chain (Tolman, 1948), through O'Keefe and Nadel's identification of the hippocampus as a spatial cognitive map (O'Keefe & Nadel, 1978), to the modern factorization view (Behrens et al., 2018) and the demonstration that the same place/grid neural machinery organizes *conceptual* as well as physical space (Constantinescu, O'Reilly & Behrens, 2016).

The doctrine's cognitive-map unification (F4) rests on Behrens et al.'s central claim: a cognitive map is best understood as a representation of *relational structure*, factorized from specific content, so that structure learned in one domain transfers to novel ones (Behrens et al., 2018). Constantinescu et al. (2016) provided the direct experimental evidence that humans navigating a two-dimensional conceptual "bird space" produce the same hexagonal, grid-like fMRI signal in entorhinal cortex as physical navigation produces — meaning the brain uses the same geometric code to organize abstract knowledge. This is not merely an analogy: it is evidence that *similarity = distance* is the brain's actual organizing principle for conceptual space.

The doctrine appropriates three structural commitments from this tradition. First, the index/store split (B4) is biologically grounded: O'Keefe and Nadel's hippocampal map *is* the sparse associative index that pattern-completes into rich neocortical content, independently corroborating Teyler and DiScenna (1986). Second, B1's "retrieval = spreading activation ≡ attention ≡ soft geometry" is no longer borrowed metaphor but predicted substrate: the cognitive-map tradition says concepts *are* positioned in a metric space where distance encodes similarity, and retrieval is navigation. Third, the factorization principle (F4) is the neuroscience of E1 (layered distillation): the generators (the top layer of the three-layer distillation stack) are the *reusable relational structure*, and the evidence store is the *content* — the portable thing is the structure, not the content.

**What the doctrine adds.** O'Keefe and Nadel (1978) and their successors provide a theory of *how* knowledge is geometrically organized in the brain; they do not provide a theory of *how to build, audit, and revise* an external knowledge artifact that inherits that geometry. The doctrine adds: the confidence/retrievability firewall (C2), which the cognitive-map tradition has no equivalent for (maps do not carry epistemic confidence — they tell you where to look, not whether what you find there is true); the generativity gradient, which has no spatial analogue; and the operator machinery for principled revision, which navigation geometry does not supply. The unification (F4) is structural, not identity: a KPM inherits the map's *architecture* while adding the epistemic and revision layers that a purely spatial theory omits.

---

### 14.3 AGM Belief Revision and Quinean Holism

Alchourrón, Gärdenfors, and Makinson (1985) formalized the logic of rational belief change. The AGM framework defines three canonical operations — expansion, contraction, and revision — constrained by a **minimal-change criterion**: revise by the smallest departure from the current belief set. AGM *entrenchment* — the pre-revision ordering of beliefs by how hard they are to give up — is the formal predecessor of the doctrine's generativity field: a belief's generativity is its epistemic entrenchment.

Quine's holism (Quine, 1951) supplies the global structure. Quine's web is organized concentrically: logic and mathematics at the center (revised almost never, everything depends on them); observational statements at the periphery (revised first). This gradient is the doctrine's generativity scale (1–5) given a formal address. The critical consequence — named in the three-orderings firewall (C2) — is that entrenchment, evidential confidence, and retrievability are *three independent orderings*; conflating them produces systematic epistemic error. AGM and Quine together supply the formal basis for that separation.

The doctrine's operator layer (Chapter 11) is an AGM implementation: D4 (contract) maps directly onto AGM contraction with minimal change; D5 (suppress) is a reversible, audit-visible operation that AGM contraction does not natively distinguish from permanent removal; E3 (lint) checks that the belief set remains well-founded after each operation. Haack's foundherentism (Haack, 1993) provides the epistemological stance that completes the picture: a KPM is neither a pure foundationalist pyramid (a rigid chain of deductions from unrevised axioms) nor a pure coherentist web (beliefs justified only by mutual support); it is a foundherentist hybrid with high-generativity axioms anchoring a coherently connected network, every node carrying a credence.

**What the doctrine adds.** AGM is a theory of *which* revisions are rational; it says nothing about *how to represent* the beliefs being revised, how to earn confidence scores, or how to distill a domain's knowledge into a portable package. Quinean holism gives the gradient but not the unit of analysis. The doctrine adds: a concrete node schema (confidence, generativity, typed edges, evidence, provenance); the layered-distillation method (E1 — a three-layer generator/elaboration/evidence stack); the adversarial-verification harness (E4); and the practical compile-and-ship pipeline. AGM and Quine provide the *formal structure*; the doctrine provides the *buildable instantiation*.

---

### 14.4 Information Theory

Shannon's foundational papers (Shannon, 1948; Shannon, 1959) establish two results that the doctrine applies directly. The source-coding theorem (Shannon, 1948) says that no lossless encoding can compress a source below its entropy *H*: the minimum average code length equals *H* bits. The rate-distortion theorem (Shannon, 1959) extends this to the lossy case: for a given tolerated distortion *D*, the minimum achievable rate *R(D)* is a decreasing, convex function of the distortion budget; to compress below *R(D)*, you must exceed distortion *D*. There is no free lunch in compression.

The doctrine's layered-distillation axiom (E1) is the information-theoretic method statement: distillation has a *rate-distortion floor*. A KPM that over-compresses exceeds the distortion budget; one that under-compresses fails as a portable package. Distillation must therefore be progressive and testable: compress to the generators at the top layer, keep full evidence reachable below. Shannon (1948, 1959) provides the theoretical warrant that this is a mathematical constraint, not a design preference. RAPTOR (Sarthi et al., 2024) is the concrete engineering echo: recursive tree-organized summaries at multiple abstraction levels, each a lossier but more compact representation — the rate-distortion trade-off applied to retrieval.

**What the doctrine adds.** Information theory provides the *bound* but not the *object*. Shannon's framework measures bit-level fidelity, not truth-tracking fidelity. The doctrine adds the epistemic layer — confidence, generativity, adversarial verification — that turns a compression task into a *knowledge* task. The rate-distortion bound constrains how much can be removed; C1 and E4 constrain *what* may be removed without sacrificing truth-tracking. That combination is not available from information theory alone.

---

### 14.5 PKM / Zettelkasten

The personal knowledge management (PKM) tradition, running from Luhmann's operational slip-box (Luhmann, 1981) through Matuschak's evergreen-note design principles (Matuschak, 2019–), provides the closest practitioner antecedent to the doctrine's KPM model. Luhmann, writing from four decades of working experience with his Zettelkasten, states the value-in-edges thesis almost verbatim: "every note is only an element which receives its quality only from the network of links and back-links within the system" (Luhmann, 1981). The doctrine's edge-over-nodes reframe (Chapter 3) is a theorized generalization of this practitioner observation. Matuschak's three structural properties — atomic, concept-oriented, densely linked (Matuschak, 2019–) — map precisely onto A2 (atomicity), A3 (foundherentist generativity = concept-centricity applied to axioms), and A1 (fan-budgeted edges as the formalization of "densely linked").

The PKM tradition arrives at the right *architecture* from a different direction entirely: not from cognitive science or formal logic but from iterative practice by knowledge workers. That four independent practitioners across seventy-five years — Luhmann, Ahrens, Matuschak, and Forte — converge on the same small set of structural rules (atomicity, associative linking, concept-orientation, retrieval design for the future self) is itself an F1 corroboration signal: the rules are discovered, not invented.

**What the doctrine adds.** PKM is practitioner wisdom — an n=1 existence proof with no confidence scores, no formal revision operators, and no criterion for when a note *earns* its place. The doctrine adds the epistemic superstructure: confidence as a credence (Ramsey, 1926/1931) governed by Bayesian coherence (Chapter 6); generativity formalized as Quinean web depth; revision operators (D4, D5) that are specified and auditable; and the adversarial-verification harness (E4) that — in the doctrine's own construction — caught a hallucinated citation (RAPTOR attributed to wrong authors; corrected to Sarthi et al., 2024) and identified a missing axiom (E2, retrieval practice / desirable difficulty) before release (Chapter 2). PKM provides the found blueprint; the doctrine provides the formal theory and quality-gate machinery that make it buildable and auditable at scale.

---

### 14.6 RAG, GraphRAG, and Agent-Memory Systems

The past five years have produced a dense engineering literature on retrieval-augmented generation and agent memory. The core RAG insight — separating parametric memory (model weights) from non-parametric memory (an external, editable store) — is the engineering realization of the index/store split (B4). GraphRAG systems augment flat vector retrieval with graph structure for multi-hop and corpus-global queries; HippoRAG explicitly borrows hippocampal indexing theory, running personalized PageRank over a knowledge graph to simulate spreading activation (B1). RAPTOR (Sarthi et al., 2024) builds recursive tree-organized summaries — a direct engineering instance of E1 layered distillation. Agent-memory systems such as MemGPT manage multi-tier memory hierarchies with active paging and invalidation, converging on the self-managed write-policy the doctrine formalizes in the D-cluster operators.

These systems are *implementations without a shared cited theory*. Each makes architectural decisions — what to store, how to index, when to revise, how to represent confidence — driven by benchmark performance rather than a unified account of what memory *is*. The result is capable, non-interoperable tooling with no common schema, no auditable confidence semantics, and no shared correctness criterion. The doctrine names this gap in Chapter 1.

**What the doctrine adds.** The engineering literature provides existence proofs and benchmarks; it does not provide a *standard* or a *protocol*. The doctrine supplies the missing theory layer: a cross-domain account of what memory is (Chapter 3), a node schema with auditable confidence semantics, the three-orderings firewall (C2) as a correctness criterion, an operator set for principled revision (Chapter 11), and the adversarial-verification harness (E4) as a quality gate. None of these are available from the RAG or agent-memory literature alone.

---

### 14.7 The Throughline

Each tradition contributes a piece: cognitive architectures supply the system-level machine; the cognitive-map tradition supplies a geometry for its contents; AGM and Quine supply the revision semantics; information theory supplies the distillation bound; PKM supplies the practitioner blueprint; and the RAG/agent-memory literature supplies the implementation existence proof.

No single tradition provides all of: (1) a cross-domain account of what memory *is*; (2) a formal schema for encoding confidence and generativity; (3) an operator set for principled revision; and (4) a quality-gate harness for adversarial verification. The doctrine provides all four. The two unifications — the Surprise Principle (F3) and the cognitive-map unification (F4) — are not recoverable from any single tradition; they emerge only by holding all of them simultaneously (Chapter 9). That synthesis, and the self-exemplifying, machine-checkable KPM it produces, is what this work adds to the traditions it inherits.


---

## Chapter 15 — Conclusion

### 15.1 The Thesis as Earned

The claim that memory is a retrieval-optimized network of confidence-weighted, generative truths was not stated and then defended; it was *derived* and then stated. The seventeen research traditions surveyed across the preceding chapters supplied seventeen independent instantiations of the same small set of structural features — and it is that convergence, governed by the consilience of inductions (Whewell, 1840), that makes the thesis defensible rather than merely asserted.

Whewell's criterion distinguishes the doctrine's evidential standing from a survey. A survey piles up evidence within one domain; it is cumulative but not corroborating in any deep sense. Cross-domain convergence multiplies independent evidential votes: when the hippocampal index/store split described by Teyler and DiScenna (1986) is independently arrived at by MemGPT (Packer et al., 2023) — which models itself on operating-system virtual memory, not neuroscience — that is a different kind of evidence than a replication of the same experiment. (HippoRAG reaches the same architecture but, being explicitly neuro-inspired, counts as lineage rather than an independent vote under the doctrine's own F1 guardrail.) The architecture is right not because one research tradition says so but because two entirely separate communities, optimizing different objective functions, arrived at the same structure. This is what convergence-corroboration (F1) names, and it is the epistemological ground on which the thesis rests.

The doctrine did not emerge fully formed. Three red-team rounds caught a hallucinated citation, a miscalibrated quantitative claim, and five honesty violations in which the text exceeded what the evidence supported. The fan-law formulation was corrected from a naive "1/n split" to the logarithmic form `Sᵢⱼ = S − ln(fanⱼ)` that Anderson (1974) actually derives. The Surprise Principle (F3) was added only after the first full draft revealed that three separately-named provisions shared one computational generator. The thesis is earned in the sense that it survived the conditions under which false theses would have been caught.

---

### 15.2 The Load-Bearing Results

Three results carry the structure of the argument. They are not summaries of the evidence chapters; they are points at which synthesis produces something the component domains did not individually contain.

**The three-orderings firewall (C2).** The doctrine separates *entrenchment* (generativity: the structural position a truth occupies in the derivation graph, formalized by the AGM dominance condition, Alchourrón, Gärdenfors & Makinson, 1985), *confidence* (evidential weight: degrees of belief earned from independent evidence, Ramsey, 1926/1931; Haack, 1993), and *retrievability* (activation: current accessibility of a trace, Bjork & Bjork, 1992; Anderson, Bjork & Bjork, 1994). These three quantities are routinely conflated in knowledge-organization practice — a high-confidence finding is treated as generative; a frequently retrieved belief is treated as well-evidenced; a dormant generator is treated as unimportant. Each conflation is a predictable category of error with a predictable cost. The firewall is not a conceptual tidying operation. Any memory system that does not maintain all three orderings as separate data structures will make all three errors, systematically.

**The two unifications (F3, F4).** Both unifications are products of applying the F2 merge rule: when three apparently separate mechanisms share a single computational generator, name the generator.

The Surprise Principle (F3) shows that salience-gating (C4), novelty-gated write-on-retrieval (D2), and predictive coding are the same computational quantity — signed prediction error — operating at three levels of description: behavioral (Rescorla & Wagner, 1972), neural broadcast (Schultz, Dayan & Montague, 1997), and the reconsolidation gate (Sevenster, Beckers & Kindt, 2013). Three descriptions, one quantity. The operational consequence is the three-zone write policy: reinforce retrievability only when prediction error is near zero; reconsolidate into the existing node at moderate error; mint a new node at large error. This is not engineering convenience — it is what the biology of reconsolidation says a rational memory system should do.

The cognitive-map unification (F4) shows that spreading activation as a geometry of meaning (B1: the mathematical identity between Hopfield attractor dynamics and transformer attention, Ramsauer et al., 2020) and the hippocampal index/store split (B4: Teyler & DiScenna, 1986; McClelland et al., 1995) are both aspects of the same underlying object: the hippocampal/entorhinal cognitive map. Behrens et al. (2018) supply the formal definition that connects both to the knowledge-packaging enterprise: a cognitive map is a representation of *relational structure factorized from content*, so structural knowledge transfers across environments without re-learning the content. That is exactly what a KPM does. Both unifications carry explicit confidence limits — F3 at 0.88 (reconsolidation's replication fragility), F4 at 0.83 (the biology-to-software step is structural correspondence, not identity) — because the doctrine earns credibility by calibration, not by confidence.

**The doctrine as standard-and-protocol.** The 23 axioms across seven clusters are simultaneously a *standard* — specifying what a well-formed unit of knowledge looks like — and a *protocol* — specifying how to build one. The standard defines the schema: atomic, confidence-weighted, generativity-scored, evidence-anchored, typed-edge-connected nodes on a foundherentist epistemology (A3, Haack, 1993) requiring both lateral coherence and vertical evidential grounding. The protocol defines the build sequence: distil generators bounded by Shannon's rate-distortion floor (E1, Shannon, 1948, 1959); score confidence from independent evidence alone (C1); split the index from the store (B4); adversarially verify before locking (E4); mint on surprise rather than overwrite (F3). Neither function alone is sufficient: a standard without a protocol produces elegant definitions no one can operationalize; a protocol without a standard produces pipelines that process *something* without a criterion for whether it is the right thing.

---

### 15.3 A Living, Defeasible Artifact

The doctrine is not a monument. It is a machine-checkable knowledge package, built by following its own prescriptions, designed to be revised.

Every axiom carries a confidence score earned from evidence, a generativity score reflecting its position in the derivation graph, an evidence list populated from independently checked sources, and a provenance record of the process by which the claim was reached. The D4 contract operator (Alchourrón et al., 1985) specifies the AGM-derived revision conditions: when a well-supported counter-result arrives, locate the conflicting evidence, run the revision from the least entrenched conflicting belief outward, and record the provenance. The suppress operator (D5) manages retrievability without touching confidence or evidence. The lint gate (E3) enforces structural invariants on every change. These are the machinery that makes the doctrine revisable in the same way the doctrine says all knowledge should be revisable: not by discarding the edifice, but by running the D4 operator and propagating the update.

The self-exemplifying structure is the empirical test. If the prescriptions for building a KPM are correct, a package built by following them should instantiate the properties the doctrine predicts. The 23 atomic axiom notes are the sparse index layer; the 41 evidence notes are the rich content store; the doctrine's axiom-set is the distilled generator layer above both. This is B4's architecture applied to itself. That the index retrieves the store, that the generators derive the elaborations, that the operators close the revision loop is evidence that the prescriptions work. That the rigor trail — three red-team rounds, five purge passes, and the contradiction-resolution records — is included as a first-class provenance layer is not archival pedantry; it is the adversarial verification axiom (E4) applied to the doctrine as its own knowledge package. A package that preaches adversarial verification but carries no trace of the adversarial process is a C3 failure waiting to materialize.

---

### 15.4 What It Enables

**KPMs as the portable unit.** The KPM is the practical output: a portable, auditable, confidence-weighted axiom-set that carries the irreducible generators of a domain. Unlike a RAG corpus it is structured; unlike a fine-tuned model it is auditable and revisable without retraining; unlike a flat vector database it maintains the three-orderings firewall that separates retrieval similarity from epistemic confidence. F4's deepest warrant is that generators transfer across contexts not because they are well-written but because they encode relational structure factorized from content — the property Behrens et al. (2018) identify as the enabling condition for structural generalization in biological cognitive maps.

**A consuming pipeline.** Chapter 12 specifies the five-step pipeline by which a packaging tool ingests raw research and produces a KPM: distil generators (E1), score confidence from evidence (C1), split index from store (B4), adversarially verify (E4), mint on surprise (F3). A tool that implements this pipeline in full produces something no current agent-memory system does: an auditable, confidence-weighted, generativity-structured package that is machine-checkable at every node.

**A shared theory layer.** The field currently converges without knowing it. Every major 2024–2025 agent-memory system independently discovered that graphs beat flat retrieval for multi-hop queries, that parametric and non-parametric memory serve different functions, that bi-temporal fact records outperform overwrite. But without a shared theory these convergences cannot be evaluated against each other, and designs cannot be improved systematically. The doctrine names what they converged on. It does not prescribe storage technology; it prescribes the invariants any such system should satisfy, and it explains *why* those invariants are required.

---

### 15.5 The Invitation to Challenge It

A defeasible doctrine's worth is determined by the quality of the attacks it can survive.

The limitations chapter (Chapter 13) documents the known pressure points: the E1 Shannon bound is a sound principle without an executable entropy estimator for heterogeneous knowledge graphs; the F4 correspondence is structural, not an identity, and whether high-dimensional discrete KG embeddings inherit the grid code's specific computational properties is an open empirical question; reconsolidation's prediction-error gate (D2 at confidence 0.85) has a failed 2022 replication in a non-fear paradigm; the SMSC-vs-MTT debate (D3) remains unresolved at the mechanistic level; the autonomous-suppression danger of D5 is a genuine agent-safety concern the audit channel alone may not contain. These are not peripheral. They are the places where a well-aimed counter-result would force genuine revision.

The right response to finding such a counter-result is not to discard the doctrine but to engage it: locate the conflicting evidence, assign it an evidence ID, run the D4 contract operator, lower the confidence score if the conflict is genuine and the evidence independent, record the provenance, and propagate the update outward. The doctrine has done this to itself three times in its own construction. It is built for this process to continue indefinitely — not because truth keeps changing, but because the evidence available to any finite inquiry is always incomplete.

The strongest version of this doctrine is the one that has survived the most serious attacks. That version does not yet exist. The work of building it is the invitation this thesis extends.

---

*Cross-references: Chapters 3–4 (generativity, foundherentism); Chapter 6 (C1–C2, three-orderings firewall); Chapter 9 (F1, F3, F4 unifications); Chapter 12 (consumption pipeline, standard-and-protocol role); Chapter 13 (E1 measurement gap, F4 scope caveat, D2 replication fragility, D5 suppression danger).*


---

## Appendix A — Axiom Catalogue

The twenty-three axioms, by cluster, with their generativity (1–5) and confidence (0–1) scores as locked in v1.1.

| ID | Name | Gen | Conf | Statement |
|---|---|---|---|---|
| A1-fan-budgeted-edges | Memory value lives in fan-budgeted, weighted edges | 5 | 0.9 | A node's retrieval budget is finite and is divided logarithmically among its associations: Sij = S − ln(fanj). Adding a low-signal edge provably dilutes retrieval of all … |
| A2-atomicity | One idea per node — atomicity enables composability | 4 | 0.85 | Each knowledge node must contain exactly one self-contained idea (Zettelkasten / Luhmann; evergreen notes / Matuschak). The rationale is composability, not retrieval spee… |
| A3-foundherentist-generativity | Justification is foundherentist; generativity equals AGM epistemic entrenchment | 5 | 0.88 | A KPM's justification structure is foundherentist (Haack 1993): foundational roots supply non-circular grounding while coherentist mutual support amplifies justification … |
| B1-spreading-activation | Spreading activation is Hopfield is attention | 5 | 0.95 | Retrieval is energy-descent pattern completion over a content-addressable store; the modern continuous-Hopfield update is mathematically identical to transformer attentio… |
| B2-cue-dependence | Retrieval is cue-dependent — recall equals cue–trace overlap | 5 | 0.9 | A memory trace is accessible only to the degree the retrieval cue reinstates the specific encoding context; cue effectiveness is determined at encoding, not by the cue's … |
| B3-capacity-cliff | Associative stores have a sharp capacity cliff — shard, don't cram | 4 | 0.88 | Classical Hopfield networks black out entirely above ≈0.138N stored patterns (Amit, Gutfreund & Sompolinsky 1985); this is a cliff, not a graceful slope. Modern continuou… |
| B4-index-store-split | A sparse index pattern-completes into a rich store — never merge them | 5 | 0.92 | Retrieval requires two functionally incompatible stores: a sparse, fast-write index that pattern-completes from a partial cue, and a rich, distributed content store. Prov… |
| C1-confidence-earned | Confidence is earned by evidence and is revisable | 5 | 0.92 | Confidence is a credence — a graded degree of belief that must be earned by verified external evidence and revised by conditionalization on new evidence. It must never be… |
| C2-three-orderings | Three independent orderings that must never be collapsed | 5 | 0.93 | Every axiom in a KPM sits on three INDEPENDENT orderings that must never be conflated: (1) generativity / entrenchment — how much downstream structure derives from it and… |
| C3-confident-but-wrong | High confidence does not imply truth — gist compression is mathematically priced error | 4 | 0.92 | High confidence is neither necessary nor sufficient for truth. In any spreading-activation / gist-based store, confidently-false memories arise from normal associative pr… |
| C4-salience-gating | Salience gates encoding strength but must not touch confidence | 4 | 0.91 | Arousal, emotional significance, and distinctiveness gate memory consolidation strength via amygdala-noradrenergic modulation (McGaugh 2004) and the von Restorff isolatio… |
| D1-retrievability-decay | Retrievability drops from disuse, competition, and deliberate intent — confidence does not | 5 | 0.92 | Retrievability decays from THREE independent drivers: (1) disuse — power-law decay toward a floor (Ebbinghaus/Wixted 1991); (2) competition — retrieval-induced forgetting… |
| D2-novelty-gated-write | Write-on-retrieval is gated by prediction error — reconsolidation labilizes only under mismatch | 5 | 0.85 | Retrieval re-opens a memory trace (reconsolidation), but destabilization occurs ONLY when retrieval carries a prediction error / mismatch (Sevenster & Kindt 2013). Pure r… |
| D3-consolidation-mtt-safe | Consolidation moves traces toward cortex, but promote-and-keep-indexed — never promote-and-detach | 4 | 0.82 | Systems consolidation transfers memory from a fast hippocampal index toward durable neocortical storage via offline replay (Wilson & McNaughton 1994), but the standard mo… |
| E1-layered-distillation | Distillation is Shannon-bounded layering, not lossy compression | 5 | 0.93 | Knowledge is distilled in layers (generators → elaboration → evidence store). Shannon bounds this exactly: the generator ≈ the source's irreducible entropy H; elaboration… |
| E2-retrieval-practice | Retrieval practice and desirable difficulty strengthen — at a delay | 4 | 0.9 | Testing (retrieval practice) and desirable difficulties strengthen memory more than restudy, but the testing advantage appears only AFTER a delay. Build spaced re-validat… |
| E4-adversarial-verify | Beliefs are locked only after adversarial challenge + citation check | 5 | 0.93 | A belief may not be promoted to the doctrine tier until it has survived an adversarial challenge (an independent agent attempts falsification using evidence other than wh… |
| F1-convergence-corroboration | Convergence of independent domains = corroboration (consilience) | 4 | 0.88 | When independent lines of inquiry — developed by different communities, using different methods, for different purposes — converge on the same conclusion, the convergence… |
| F2-contradictions-category-errors | Apparent contradictions are usually category errors — split or merge | 5 | 0.9 | When two well-evidenced claims appear to contradict, the most productive move is to suspect a conflated term: split the term into two distinct concepts and both halves wi… |
| F3-surprise-principle | Prediction error is one quantity at three levels — the Surprise Principle | 5 | 0.88 | Prediction error (the signed mismatch between what was predicted and what occurred) is ONE computational quantity doing the work of three separately-named mechanisms: the… |
| F4-cognitive-map-unification | B1 and B4 are **structurally** the same object — a factorized cognitive map | 5 | 0.83 | Embeddings-as-geometry (B1) and the sparse-index→rich-store split (B4) are **structurally** the same object — a factorized cognitive map (the hippocampal/entorhinal cognitive map, which simultaneously en… |
| G1-trigger-memory | Prospective memory — prefer focal/event triggers over monitored polling | 5 | 0.82 | Remembering to DO something at the right future moment is a distinct memory system (prospective memory). Prefer focal/event triggers — bind the cue to a KG node the agent… |
| G2-intention-lifecycle | Intention lifecycle — boost on open, inhibit on completion | 4 | 0.74 | Open intentions sit at heightened activation (intention-superiority effect) and must be actively inhibited on completion, not merely flagged done. Un-inhibited completed … |

### Operators

| ID | Title | Trigger → Action |
|---|---|---|
| D4-contract | Contract (AGM belief revision) | a new finding contradicts a status:locked axiom → minimally shrink the belief set / lower entrenchment; never delete evidence |
| D5-suppress | Suppress (motivated, reversible de-activation) | a true belief is goal-irrelevant and is crowding retrieval → lower its retrievability/activation WITHOUT touching its confidence or evidence |
| E3-lint | Lint (structural pre-lock checks) | before a note is committed or a belief is locked → run structural checks — atomicity, >=1 evidence, frontmatter<->wikilink sync, the F2 no-contradiction invariant |
| E5-compile | Compile-on-impasse (SOAR chunking) | a query hits an impasse — no-cover, conflict, or multi-hop → the resolution path becomes a candidate new distilled generator; meta-axioms are chunks of repeated cross-domain impasses |


---

# References

*Inline citations in the chapters use (Author, Year); this is the full list. Entries were compiled from the doctrine's evidence notes and extended with the additional works cited in the thesis; every entry was checked against the published record.*

- Ahrens, S. (2017). *How to Take Smart Notes: One Simple Technique to Boost Writing, Learning and Thinking*. CreateSpace.
- Alchourrón, C. E., Gärdenfors, P., & Makinson, D. (1985). On the logic of theory change: Partial meet contraction and revision functions. *Journal of Symbolic Logic*, 50(2), 510–530.
- Amit, D. J., Gutfreund, H., & Sompolinsky, H. (1985). Storing infinite numbers of patterns in a spin-glass model of neural networks. *Physical Review Letters*, 55(14), 1530–1533. (Full replica derivation: Amit, Gutfreund & Sompolinsky (1987). Statistical mechanics of neural networks near saturation. *Annals of Physics*, 173, 30–67.)
- Anderson, J. R. (1974). Retrieval of propositional information from long-term memory. *Cognitive Psychology*, 6(4), 451–474.
- Anderson, J. R. (1993). *Rules of the Mind*. Lawrence Erlbaum Associates.
- Anderson, M. C., Bjork, R. A., & Bjork, E. L. (1994). Remembering can cause forgetting: Retrieval dynamics in long-term memory. *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 20(5), 1063–1087.
- Athanassoulis, M., Kester, M. S., Maas, L. M., Stoica, R., Idreos, S., Ailamaki, A., & Callaghan, M. (2016). Designing access methods: The RUM conjecture. *Proceedings of EDBT 2016*, 461–466.
- Baars, B. J. (1988). *A Cognitive Theory of Consciousness*. Cambridge University Press.
- Behrens, T. E. J., Muller, T. H., Whittington, J. C. R., Mark, S., Baram, A. B., Stachenfeld, K. L., & Kurth-Nelson, Z. (2018). What is a cognitive map? Organizing knowledge for flexible behavior. *Neuron*, 100(2), 490–509.
- Bjork, R. A. (1989). Retrieval inhibition as an adaptive mechanism in human memory. In H. L. Roediger & F. I. M. Craik (Eds.), *Varieties of Memory and Consciousness: Essays in Honour of Endel Tulving* (pp. 309–330). Erlbaum.
- Bjork, R. A., & Bjork, E. L. (1992). A new theory of disuse and an old theory of stimulus fluctuation. In A. Healy, S. Kosslyn, & R. Shiffrin (Eds.), *From Learning Processes to Cognitive Processes* (pp. 35–67). Erlbaum.
- BonJour, L. (1985). *The Structure of Empirical Knowledge*. Harvard University Press.
- Braak, H., & Braak, E. (1991). Neuropathological stageing of Alzheimer-related changes. *Acta Neuropathologica*, 82(4), 239–259.
- Brown, R., & Kulik, J. (1977). Flashbulb memories. *Cognition*, 5(1), 73–99.
- Camerer, C. F., Dreber, A., Holzmeister, F., Ho, T.-H., Huber, J., Johannesson, M., … Wu, H. (2018). Evaluating the replicability of social science experiments in *Nature* and *Science* between 2010 and 2015. *Nature Human Behaviour*, 2(9), 637–644.
- Chhikara, P., Khant, D., Aryan, S., Singh, T., & Yadav, D. (2025). Mem0: Building production-ready AI agents with scalable long-term memory. *arXiv:2504.19413*.
- Collins, A. M., & Loftus, E. F. (1975). A spreading-activation theory of semantic processing. *Psychological Review*, 82(4), 407–428.
- Constantinescu, A. O., O'Reilly, J. X., & Behrens, T. E. J. (2016). Organizing conceptual knowledge in humans with a gridlike code. *Science*, 352(6292), 1464–1468.
- Deese, J. (1959). On the prediction of occurrence of particular verbal intrusions in immediate recall. *Journal of Experimental Psychology*, 58(1), 17–22.
- Dehaene, S., & Changeux, J.-P. (2011). Experimental and theoretical approaches to conscious processing. *Neuron*, 70(2), 200–227.
- Doyle, J. (1979). A truth maintenance system. *Artificial Intelligence*, 12(3), 231–272.
- Edge, D., Trinh, H., Cheng, N., Bradley, J., Chao, A., Mody, A., … Larson, J. (2024). From local to global: A Graph RAG approach to query-focused summarization. *arXiv:2404.16130* (Microsoft Research).
- Gettier, E. L. (1963). Is justified true belief knowledge? *Analysis*, 23(6), 121–123.
- Goschke, T., & Kuhl, J. (1993). Representation of intentions: Persisting activation in memory. *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 19(5), 1211–1226.
- Forte, T. (2022). *Building a Second Brain: A Proven Method to Organize Your Digital Life and Unlock Your Creative Potential*. Atria Books.
- Gutiérrez, B. J., Shu, Y., Gu, Y., Yasunaga, M., & Su, Y. (2024). HippoRAG: Neurobiologically inspired long-term memory for large language models. *Advances in Neural Information Processing Systems (NeurIPS 2024)*. arXiv:2405.14831.
- Haack, S. (1993). *Evidence and Inquiry: Towards Reconstruction in Epistemology*. Blackwell. (Source of the foundherentist account and the independent-security criterion.)
- Hopfield, J. J. (1982). Neural networks and physical systems with emergent collective computational abilities. *Proceedings of the National Academy of Sciences*, 79(8), 2554–2558.
- Hunt, R. R. (1995). The subtlety of distinctiveness: What von Restorff really did. *Psychonomic Bulletin & Review*, 2(1), 105–112.
- Koriat, A. (1993). How do we know that we know? The accessibility model of the feeling of knowing. *Psychological Review*, 100(4), 609–639.
- Laird, J. E., Lebiere, C., & Rosenbloom, P. S. (2017). A standard model of the mind: Toward a common computational framework across artificial intelligence, cognitive science, neuroscience, and robotics. *AI Magazine*, 38(4), 13–26.
- Lehrer, K. (1974). *Knowledge*. Oxford University Press.
- Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., … Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems (NeurIPS 2020)*. arXiv:2005.11401.
- Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2023). Lost in the middle: How language models use long contexts. *arXiv:2307.03172* (TACL 2024).
- Luhmann, N. (1981). Kommunikation mit Zettelkästen [Communicating with slip boxes]. In H. Baier, H. M. Kepplinger, & K. Reumann (Eds.), *Öffentliche Meinung und sozialer Wandel* (pp. 222–228). Westdeutscher Verlag.
- Matuschak, A. (2019–). Evergreen notes. notes.andymatuschak.org.
- McClelland, J. L., McNaughton, B. L., & O'Reilly, R. C. (1995). Why there are complementary learning systems in the hippocampus and neocortex: Insights from the successes and failures of connectionist models of learning and memory. *Psychological Review*, 102(3), 419–457.
- McCloskey, M., & Cohen, N. J. (1989). Catastrophic interference in connectionist networks: The sequential learning problem. *Psychology of Learning and Motivation*, 24, 109–165.
- McDaniel, M. A., & Einstein, G. O. (2000). Strategic and automatic processes in prospective memory retrieval: A multiprocess framework. *Applied Cognitive Psychology*, 14, S127–S144.
- McGaugh, J. L. (2004). The amygdala modulates the consolidation of memories of emotionally arousing experiences. *Annual Review of Neuroscience*, 27, 1–28.
- Miller, G. A. (1956). The magical number seven, plus or minus two: Some limits on our capacity for processing information. *Psychological Review*, 63(2), 81–97.
- Mohan, C., Haderle, D., Lindsay, B., Pirahesh, H., & Schwarz, P. (1992). ARIES: A transaction recovery method supporting fine-granularity locking and partial rollbacks using write-ahead logging. *ACM Transactions on Database Systems*, 17(1), 94–162.
- Nadel, L., & Moscovitch, M. (1997). Memory consolidation, retrograde amnesia and the hippocampal complex. *Current Opinion in Neurobiology*, 7(2), 217–227.
- Nader, K., Schafe, G. E., & LeDoux, J. E. (2000). Fear memories require protein synthesis in the amygdala for reconsolidation after retrieval. *Nature*, 406, 722–726.
- Newell, A. (1990). *Unified Theories of Cognition*. Harvard University Press.
- O'Keefe, J., & Nadel, L. (1978). *The Hippocampus as a Cognitive Map*. Oxford University Press.
- Packer, C., Fang, V., Patil, S. G., Lin, K., Wooders, S., & Gonzalez, J. E. (2023). MemGPT: Towards LLMs as operating systems. *arXiv:2310.08560*.
- Pollock, J. L. (1987). Defeasible reasoning. *Cognitive Science*, 11(4), 481–518.
- Quine, W. V. O. (1951). Two dogmas of empiricism. *The Philosophical Review*, 60(1), 20–43. (Reprinted in *From a Logical Point of View*, 1953, Harvard University Press.)
- Quillian, M. R. (1968). Semantic memory. In M. Minsky (Ed.), *Semantic Information Processing* (pp. 227–270). MIT Press.
- Ramirez, S., Liu, X., Lin, P.-A., Suh, J., Pignatelli, M., Redondo, R. L., … Tonegawa, S. (2013). Creating a false memory in the hippocampus. *Science*, 341(6144), 387–391.
- Ramsauer, H., Schäfl, B., Lehner, J., Seidl, P., Widrich, M., Adler, T., … Hochreiter, S. (2020). Hopfield networks is all you need. *arXiv:2008.02217* (ICLR 2021).
- Ramsey, F. P. (1926/1931). Truth and probability. In *The Foundations of Mathematics and Other Logical Essays*. Kegan Paul.
- Rasmussen, P., Paliychuk, P., Beauvais, T., Ryan, J., & Chalef, D. (2025). Zep: A temporal knowledge graph architecture for agent memory. *arXiv:2501.13956*.
- Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *Proceedings of EMNLP 2019*. arXiv:1908.10084.
- Rescorla, R. A., & Wagner, A. R. (1972). A theory of Pavlovian conditioning: Variations in the effectiveness of reinforcement and nonreinforcement. In A. H. Black & W. F. Prokasy (Eds.), *Classical Conditioning II* (pp. 64–99). Appleton-Century-Crofts.
- Roediger, H. L., & Karpicke, J. D. (2006). Test-enhanced learning: Taking memory tests improves long-term retention. *Psychological Science*, 17(3), 249–255.
- Roediger, H. L., & McDermott, K. B. (1995). Creating false memories: Remembering words not presented in lists. *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 21(4), 803–814.
- Sarthi, P., Abdullah, S., Tuli, A., Khanna, S., Goldie, A., & Manning, C. D. (2024). RAPTOR: Recursive abstractive processing for tree-organized retrieval. *Proceedings of ICLR 2024*. arXiv:2401.18059.
- Schneider, D. W., & Anderson, J. R. (2012). Modeling fan effects on the time course of associative recognition. *Cognitive Psychology*, 64(2), 127–160.
- Schultz, W., Dayan, P., & Montague, P. R. (1997). A neural substrate of prediction and reward. *Science*, 275(5306), 1593–1599.
- Sevenster, D., Beckers, T., & Kindt, M. (2013). Prediction error governs pharmacologically induced amnesia for learned fear. *Science*, 339(6121), 830–833.
- Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27, 379–423, 623–656.
- Shannon, C. E. (1959). Coding theorems for a discrete source with a fidelity criterion. *IRE National Convention Record*, 7, 142–163.
- Sherry, D. F., & Schacter, D. L. (1987). The evolution of multiple memory systems. *Psychological Review*, 94(4), 439–454.
- Slamecka, N. J., & Graf, P. (1978). The generation effect: Delineation of a phenomenon. *Journal of Experimental Psychology: Human Learning and Memory*, 4(6), 592–604.
- Squire, L. R., & Wixted, J. T. (2011). The cognitive neuroscience of human memory since H.M. *Annual Review of Neuroscience*, 34, 259–288.
- Steyvers, M., & Tenenbaum, J. B. (2005). The large-scale structure of semantic networks: Statistical analyses and a model of semantic growth. *Cognitive Science*, 29(1), 41–78.
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.
- Talarico, J. M., & Rubin, D. C. (2003). Confidence, not consistency, characterizes flashbulb memories. *Psychological Science*, 14(5), 455–461.
- Teyler, T. J., & DiScenna, P. (1986). The hippocampal memory indexing theory. *Behavioral Neuroscience*, 100(2), 147–154.
- Tolman, E. C. (1948). Cognitive maps in rats and men. *Psychological Review*, 55(4), 189–208.
- Tulving, E., & Thomson, D. M. (1973). Encoding specificity and retrieval processes in episodic memory. *Psychological Review*, 80(5), 352–373.
- von Restorff, H. (1933). Über die Wirkung von Bereichsbildungen im Spurenfeld [On the effect of sphere formations in the trace field]. *Psychologische Forschung*, 18, 299–342.
- Wegner, D. M., Giuliano, T., & Hertel, P. T. (1985). Cognitive interdependence in close relationships. In W. J. Ickes (Ed.), *Compatible and Incompatible Relationships* (pp. 253–276). Springer.
- Whewell, W. (1840). *The Philosophy of the Inductive Sciences, Founded Upon Their History* (Vol. 2, Book XI). Parker, London.
- Wilson, M. A., & McNaughton, B. L. (1994). Reactivation of hippocampal ensemble memories during sleep. *Science*, 265(5172), 676–679.
- Wixted, J. T., & Ebbesen, E. B. (1991). On the form of forgetting. *Psychological Science*, 2(6), 409–415.


---

