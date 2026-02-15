Building a Causal Bayesian Network (CBN) for patients living with dementia (PLWD) requires distinguishing between **exogenous variables** (fixed demographic traits) and **endogenous variables** (dynamic states like health and mobility). In this model, we treat the caregiver's experience and the patient's mobility as the primary sinks for causal influence.

Below are the direct causal relations proposed for the model based on the variables provided.

---

## Direct Causal Relations

| Cause (Parent) | Effect (Child) | Weight (1-10) | Rationale |
| --- | --- | --- | --- |
| `challenging_days` | `total_burden` | **9** | **Primary Stressor:** Days when the patient is not feeling well or is having a "bad day" often involve behavioral symptoms or acute physical distress, which are the strongest predictors of caregiver burnout and perceived difficulty. |
| `lifespace_score` | `total_burden` | **8** | **Functional Dependency:** A lower lifespace score indicates reduced mobility and independence. This requires the caregiver to provide more physical assistance (transfers, transportation, constant supervision), directly increasing the labor and burden. |
| `challenging_days` | `non_routine_days` | **7** | **Routine Disruption:** If a patient is feeling unwell or agitated, scheduled activities (like walks or social visits) are typically cancelled, leading to a deviation from the normal routine. |
| `non_routine_days` | `lifespace_score` | **7** | **Mobility Restriction:** Non-routine days in dementia care often involve staying home due to illness or weather. Frequent disruptions to a routine usually shrink the patient’s active environment, lowering the lifespace score. |
| `community_type` | `lifespace_score` | **6** | **Environmental Access:** Whether a community is rural or indigenous significantly impacts the available infrastructure, transportation, and geographic "lifespace" reachable by the patient. |
| `sex_cg` | `total_burden` | **5** | **Gendered Caregiving Roles:** Statistical evidence often suggests that the sex of the caregiver can influence the *perception* of burden and the types of tasks performed, though the effect is moderated by other factors. |
| `educ_cg` | `total_burden` | **5** | **Resource Navigation:** Higher education levels may provide caregivers with better health literacy and coping strategies, potentially mitigating the perceived "total burden" through more efficient care management. |
| `educ_plwd` | `lifespace_score` | **4** | **Cognitive Reserve:** Higher patient education is often a proxy for higher socioeconomic status or cognitive reserve, which can correlate with maintaining independence and mobility (lifespace) for longer periods. |
| `sex_plwd` | `lifespace_score` | **4** | **Behavioral Patterns:** Biological and social factors related to the patient's sex can influence their baseline mobility levels and the types of social engagement they seek. |

---

### Structural Considerations

* **The Hub of Burden:** In this network, `total_burden` acts as the ultimate outcome variable. It is influenced by both the caregiver's internal state (`sex_cg`, `educ_cg`) and the patient's externalized state (`lifespace_score`, `challenging_days`).
* **The Mobility Loop:** There is a strong interplay between the patient's wellness (`challenging_days`), the stability of their environment (`non_routine_days`), and their actual movement (`lifespace_score`). While `non_routine_days` can cause a low `lifespace_score`, a chronically low `lifespace_score` can also contribute to more `non_routine_days`. For the sake of a Directed Acyclic Graph (DAG), we prioritize health/wellness as the root cause of routine disruption.

Would you like me to generate a DOT script for this network so you can visualize the DAG structure?