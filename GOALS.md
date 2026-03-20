# GOALS.md — Business, Agent, and System Goals

This is the **source of truth** for what the system is trying to achieve. Other agents read this file to understand priorities, constraints, and success criteria.

Fill in every **bold placeholder** below. Search for `**[` to find them all.

---

## 1. Business Outcomes

These are the top-level outcomes the agentic system exists to drive.

### Primary Objective

**[Describe what "self-improve" means for your system (e.g., better output quality, fewer bugs, faster throughput, higher KPIs like leads or revenue).]**

### Key Business KPIs

| KPI | Current Baseline | Target | Measurement Frequency |
|---|---|---|---|
| **[Your primary KPI, e.g., MRR]** | **[Current value]** | **[Target value]** | **[Weekly / Monthly]** |
| **[Secondary KPI, e.g., qualified leads per week]** | **[Current value]** | **[Target value]** | **[Weekly / Monthly]** |
| **[Tertiary KPI, e.g., churn rate]** | **[Current value]** | **[Target value]** | **[Weekly / Monthly]** |

### Business Constraints

- **[Maximum acceptable cost per agent cycle (e.g., $X per 1000 tasks)]**
- **[Latency requirements (e.g., response within N seconds for user-facing tasks)]**
- **[Compliance or regulatory constraints]**

---

## 2. Agent-Level Goals

Each department has specific goals that roll up into the business outcomes above.

### Per-Department Goals

| Department | Primary Goal | Quality Metric | Target |
|---|---|---|---|
| Research | **[e.g., Produce accurate, sourced briefs]** | **[e.g., Factual accuracy rate]** | **[e.g., > 95%]** |
| Architect | **[e.g., Deliver coherent system designs]** | **[e.g., Design review approval rate]** | **[e.g., > 90%]** |
| Build | **[e.g., Ship working code with tests]** | **[e.g., Code defect rate, test pass rate]** | **[e.g., < 5% defect rate]** |
| Design | **[e.g., Create usable, accessible UX]** | **[e.g., UX satisfaction score]** | **[e.g., > 4.2 / 5]** |
| QA | **[e.g., Catch defects before release]** | **[e.g., Defect escape rate]** | **[e.g., < 2%]** |
| Growth | **[e.g., Increase signups and engagement]** | **[e.g., CTR, conversion rate]** | **[e.g., > 3% CTR]** |
| Reporter | **[e.g., Accurate, timely status reports]** | **[e.g., Report accuracy, delivery time]** | **[e.g., < 5 min latency]** |
| PM-Sync | **[e.g., Keep external tools in sync]** | **[e.g., Sync lag time]** | **[e.g., < 1 hour lag]** |

### Cross-Cutting Agent Goals

These apply to every agent in the system:

- **Complete tasks within the cycle budget** — **[Define your cycle budget, e.g., max 5 LLM calls per sub-task]**
- **Emit accurate completion signals** — no false `done` signals; `blocked` must include actionable context.
- **Log every episode** — every task execution produces a structured log entry (see `docs/logging_and_episodes.md`).
- **Self-evaluate before signaling `done`** — every agent runs a reflection check on its output.

---

## 3. System-Level Quality Metrics

These measure the health of the agentic system itself, independent of business outcomes.

| Metric | Description | Target | Alert Threshold |
|---|---|---|---|
| Task completion rate | % of tasks that reach `done` without human intervention | **[e.g., > 85%]** | **[e.g., < 70%]** |
| Escalation rate | % of tasks escalated to Foreman or human | **[e.g., < 15%]** | **[e.g., > 30%]** |
| Mean cycles to completion | Average LLM calls per task | **[e.g., < 8]** | **[e.g., > 15]** |
| Episode log coverage | % of tasks with complete episode logs | > 99% | < 95% |
| Reflection loop compliance | % of agents that self-evaluate before `done` | 100% | < 90% |
| Policy update proposal rate | Number of meta-agent proposals per week | **[e.g., 2-5]** | **[e.g., > 10 suggests instability]** |
| Human review turnaround | Time from `needs-review` to human response | **[e.g., < 4 hours]** | **[e.g., > 24 hours]** |

---

## 4. Self-Improvement Goals

What does "getting better" look like for this system?

### Short-Term (Weeks 1)

- [ ] All agents emit completion signals consistently.
- [ ] Episode logs are captured for > 95% of tasks.
- [ ] Reflection loops are active for at least **[N departments]**.
- [ ] Baseline quality scores are established per department.

### Medium-Term (Month 1)

- [ ] Evaluation rubrics are calibrated against human judgment.
- [ ] Quality trends are visible in dashboards.
- [ ] Meta-agent is proposing prompt improvements (human-reviewed).
- [ ] **[Define your medium-term self-improvement milestone]**

### Long-Term (Months 2+)

- [ ] System demonstrates measurable improvement on business KPIs.
- [ ] Policy updates are semi-automated with high human approval rate (> 80%).
- [ ] New departments can be added and reach baseline quality within **[N days]**.
- [ ] **[Define your long-term vision for autonomous improvement]**

---

## How Agents Use This File

1. **Foreman** reads Sections 1 and 3 to prioritize tasks and assess system health.
2. **Department heads** read their row in Section 2 to understand their quality targets.
3. **Meta-agent** reads Sections 3 and 4 to know what "improvement" means when proposing policy changes.
4. **Reporter** reads all sections to generate accurate status reports.
