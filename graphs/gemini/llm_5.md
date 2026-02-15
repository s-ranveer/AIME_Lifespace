To construct an effective Causal Bayesian Network (CBN) for patients living with dementia (PLWD), we must identify the directional dependencies where one variable directly influences the state of another.

The following list outlines the proposed direct causal relations, the underlying mechanisms, and their associated weights based on clinical literature and social determinants of health.

---

### Patient Health & Mobility Dynamics

* **`challenging_days`  `lifespace_score**`
* **Rationale:** On days when a patient is not feeling well or is experiencing high symptoms, their physical activity and willingness to move beyond their immediate environment naturally decrease. This is a direct biological and psychological constraint on mobility.
* **Weight:** 8/10


* **`challenging_days`  `non_routine_days**`
* **Rationale:** Frequent "bad days" disrupt established patterns. If a patient is unwell, scheduled outings or social visits are often canceled, leading to a deviation from the standard monthly routine.
* **Weight:** 7/10


* **`lifespace_score`  `total_burden**`
* **Rationale:** Independence is inversely related to caregiver workload. A higher lifespace score implies the patient is more mobile and independent, which generally reduces the constant supervision and physical assistance required from the caregiver.
* **Weight:** 8/10



### Environmental & Demographic Influences

* **`community_type`  `lifespace_score**`
* **Rationale:** The physical environment dictates mobility potential. Rural or indigenous communities may have different levels of infrastructure, public transit, or proximity to community centers compared to urban areas, directly impacting how far a patient can travel.
* **Weight:** 6/10


* **`educ_plwd`  `lifespace_score**`
* **Rationale:** Education levels are frequently a proxy for socioeconomic status and health literacy. Higher education may correlate with better access to mobility aids, physical therapy, or environments that encourage safe exploration.
* **Weight:** 5/10


* **`sex_plwd`  `lifespace_score**`
* **Rationale:** Studies often indicate gender-based differences in dementia progression and community engagement. Socialized behaviors and biological factors can influence the range of movement in older age.
* **Weight:** 4/10



### Caregiver Strain Mechanisms

* **`challenging_days`  `total_burden**`
* **Rationale:** This is arguably the strongest causal link. When the patient experiences high symptomatic days, the caregiver must provide more emotional support, manage behavioral issues, and increase physical care, directly driving up perceived burden.
* **Weight:** 9/10


* **`non_routine_days`  `total_burden**`
* **Rationale:** Caregiving is often sustainable only through rigid routines. Frequent deviations and "non-routine" events require the caregiver to constantly adapt and problem-solve, which increases cognitive and emotional fatigue.
* **Weight:** 6/10


* **`educ_cg`  `total_burden**`
* **Rationale:** Education level can influence a caregiver's access to coping resources, their ability to navigate the healthcare system, and their financial stability, all of which mitigate or exacerbate the experience of "total burden."
* **Weight:** 5/10


* **`sex_cg`  `total_burden**`
* **Rationale:** Sociological research suggests that male and female caregivers often report different levels of burden even when providing similar levels of care, due to differing social expectations and coping styles.
* **Weight:** 5/10



---

### Summary Table for CBN Construction

| Cause (Parent) | Effect (Child) | Weight (1-10) |
| --- | --- | --- |
| `challenging_days` | `total_burden` | 9 |
| `challenging_days` | `lifespace_score` | 8 |
| `lifespace_score` | `total_burden` | 8 |
| `challenging_days` | `non_routine_days` | 7 |
| `community_type` | `lifespace_score` | 6 |
| `non_routine_days` | `total_burden` | 6 |
| `educ_cg` | `total_burden` | 5 |
| `educ_plwd` | `lifespace_score` | 5 |

Would you like me to help you define the **Conditional Probability Tables (CPTs)** for these nodes to begin quantifying the model?