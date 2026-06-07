# Godon Extensions and Advancements

Ordered by priority and dependency chain.

## 1. Interference (Pollination) Detection

**Status:** Validated. FFT + Rayleigh watermark detection working at 6-breeder scale.

Watermark-based active probing replaces passive statistical detection. Each breeder
injects a unique multi-frequency composite watermark into its parameter suggestions.
Pairwise detection via FFT power spectrum analysis + Rayleigh phase coherence test.

Previously validated for 2 breeders. Now confirmed at 6 independent optimizers
(coupling_factor=0.9, microgrid bench scenario). 5/6 breeders produced 450+ trials,
20 pairwise detection tests with high specificity. See
`watermarking-and-causal-discovery.md` for full results.

**Terminology:**
- **Coupling** — intentional, configured cooperation between breeders
- **Interference** — unintended, discovered interaction between breeders
- **Probing** — deliberate perturbation to confirm suspected interference

**Files:** `examples/bench/scenario-microgrid-6breeder/`, `examples/bench/scenario-microgrid/`
**Related:** `docs/watermarking-and-causal-discovery.md`, `docs/coupling-detection-statistical-methods.md`

## 2. Online Surrogate Breeder

A breeder that never effectuates — only observes. Builds a predictive model of the system from other breeders' trial data.

- Gaussian process or lightweight regression on (parameters → metrics) pairs
- Queryable: "if I set X=5, what do you predict?"
- Serves as shared knowledge layer across all breeders
- Uncovers parameter sensitivity, anomaly detection, what-if exploration

**Enables:**
- Parameter importance without fANOVA (breed-agnostic)
- Anomaly scoring ("this trial's result is 3σ from predicted")
- Change point attribution ("performance dropped because temperature rose past 28")
- Active learning ("explore where the model is least confident")

## 3. RAG + LLM Conversational Optimization

Retrieval-augmented generation over trial history with an LLM interface.

**RAG layer (lightweight):**
- Encode trial records (params, metrics, timestamp, target) as vectors
- Simple index (numpy + cosine similarity) — godon's data is small and structured
- No need for enterprise RAG infrastructure

**LLM interface:**
- Natural language queries against trial data
- Anomaly explanation ("why did growth_rate drop last Tuesday?")
- Cross-breeder pattern discovery
- Auto-generated dashboard narration
- Config change recommendations grounded in real data

**Key insight:** The LLM never does math. Pre-compute analysis (importance, interference, anomalies), store results, let the LLM retrieve and explain.

**Building blocks:**
- Small embedding model for trial context (runs locally)
- LLM API for generation
- Pre-computed analysis feeds (interference scores, importance rankings, anomaly flags)

## 4. Interference Detection in the Observer

Automated, continuous interference detection built into the observer.

- Runs Granger/transfer entropy continuously on incoming trial data
- Flags suspected interference pairs in real-time
- Dashboard: interference heatmap (breeder pairs × strength)
- Triggers "run a probe?" suggestion for confirmation

## 5. Dashboard Advancements

**Breeder overview page:**
- List all breeders with status, trial count, health
- Click into breeder detail view
- Multi-select for overlay/comparison

**Multi-breeder views:**
- Heatmap strip (time × breeder, color = metric value) — the interference detection view
- Faceted small multiples for detailed comparison
- Difference/divergence chart between breeder pairs
- Trajectory similarity overlay

**Config management:**
- Config diff view (old vs new on update)
- Rollback button (one-click restore from config history)

## 6. Additional Exploration Strategies

Beyond optimization (TPE/NSGA2), add orthogonal exploration:

- **Regression testing** — periodically replay known configurations, compare results. Drift detection via `replay_interval` config. Easy to implement in existing breeder loop.
- **Passive observation** — a breeder that monitors without perturbing. Establishes the unperturbed baseline. Surrogate-based.
- **Random walk** — explore uniformly, catch regions the optimizer would skip. Full landscape mapping.

**Not pursuing:**
- Adversarial perturbation (chaos engineering) — different product, different safety profile

## 7. Convergence → Adaptation Quality Monitoring

Reframe from static convergence to continuous adaptation tracking:

- **Tracking fidelity** — is the breeder keeping up with the moving optimum?
- **Regime change detection** — "it was tracking fine, then it stopped improving"
- **Drift detection** — system changed, breeder needs to re-explore

Not "did it converge?" but "is it adapting well enough?"

## 8. Cross-Target Transfer Learning

- Breeder A optimized greenhouse-1 for 500 trials
- Breeder B starts on greenhouse-2
- Bootstrap B from A's knowledge (surrogate warm-start)
- Share parameter importance rankings, search space priors, failure patterns

## 9. Federated Knowledge

Multiple godon instances, each at different customer deployments:
- Share surrogate insights without sharing raw trial data
- Privacy-preserving collective learning
- Customer A's insights improve Customer B's optimization

## 10. Probing (Confirmation Layer)

After passive detection flags suspected interference:
- Deliberate perturbation experiments
- "Freeze breeder A, let breeder B run alone, compare trajectory"
- Confirms causation, not just correlation
- Measures coupling magnitude, direction, and channels

**Layers:**
1. Passive observation → flag suspects
2. Probing → confirm and characterize
3. Action → isolate, compensate, or coordinate

## Conceptual Framing

Godon is simultaneously:
- **Data gathering engine** — structured trial data is the core asset
- **Knowledge derivation engine** — extract insight from every trial
- **Homeostat** — continuously maintains the system in good operating regions
- **Flock of simple algorithms** — emergent intelligence through diversity and interaction, not individual sophistication
- **System discovery tool** — the optimization process itself reveals hidden structure

The trial data compounds. The longer it runs, the more valuable it becomes. Every feature is a different lens for extracting value from the same data.

## Dependency Chain

```
Interference detection (now)
    ↓
Surrogate breeder (offline model)
    ↓
RAG + LLM interface (queryable knowledge)
    ↓
Dashboard advancements (visualization)
    ↓
Transfer learning / Federated knowledge (scale)
```

Each layer builds on the previous. Interference detection is validated (6 breeders, FFT+Rayleigh). The surrogate makes the data queryable. The LLM makes it accessible. The dashboard makes it visible. Federated knowledge scales it.