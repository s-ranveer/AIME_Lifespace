Building a Causal Bayesian Network (CBN) for dementia care involves distinguishing between fixed demographic traits (exogenous variables) and the dynamic behavioral or environmental factors that influence patient outcomes and caregiver wellbeing.

Here is a proposed structure of direct causal relations based on the variables provided in `causal.md`.

---

## Direct Causal Relations

| Causal Relation (Cause  Effect) | Weight (1-10) | Rationale |
| --- | --- | --- |
| **challenging_days**  **lifespace_score** | 9 | If a patient has many days where they are "not feeling well", their physical mobility and willingness to leave their immediate environment (lifespace) will naturally decrease. |
| **challenging_days**  **total_burden** | 9 | Frequent "bad days" for a patient create immediate emotional and physical strain on the caregiver, directly escalating the perceived burden. |
| **lifespace_score**  **total_burden** | 8 | Lower mobility and independence require the caregiver to provide more hands-on assistance for daily activities, which is a primary driver of caregiver exhaustion. |
| **community_type**  **lifespace_score** | 7 | Rural or indigenous settings often have different infrastructure, transportation options, and geographical spreads that dictate how far a patient can realistically travel independently. |
| **non_routine_days**  **total_burden** | 7 | High unpredictability in a patient's schedule prevents caregivers from planning their own lives, leading to higher stress and a sense of being "on call" constantly. |
| **educ_plwd**  **lifespace_score** | 5 | Education level is often a proxy for socioeconomic resources or health literacy, which can influence a patient's ability to maintain an active, mobile lifestyle. |
| **sex_cg**  **total_burden** | 5 | Sociological studies frequently show that the sex of the caregiver can influence the types of tasks performed and the internal reporting of "burden" due to varying societal expectations and coping mechanisms. |
| **educ_cg**  **total_burden** | 4 | Higher caregiver education may correlate with better access to external support systems or more effective coping strategies, potentially mitigating the feeling of total burden. |
| **lifespace_score**  **non_routine_days** | 4 | When independence is high, the patient may be more likely to engage in spontaneous activities that deviate from a strict routine. |

---

## Logic and Structural Assumptions

### 1. The Burden Sink

In this model, **total_burden** is the primary "sink" (an endogenous variable with many parents). It is the cumulative result of the patient's physical state, the environment, and the caregiver's own demographic profile.

### 2. Independence and Mobility

The **lifespace_score** acts as a critical mediator. While demographic factors like **community_type** and **educ_plwd** influence it, its primary driver in a dementia context is the patient's daily health status (**challenging_days**).

### 3. Demographic Exogeneity

Variables such as **sex_plwd**, **sex_cg**, and **educ_cg** are treated as root nodes. They influence other variables but are not influenced by them within the scope of this model.

> **Note on Weights:** The weights assigned (1–10) reflect the expected strength of the conditional probability . For instance, the link between a patient's daily health and their caregiver's burden (9) is modeled as a much stronger causal driver than the caregiver's education level (4).

---

Would you like me to help you define the **Conditional Probability Tables (CPTs)** for these relations, or perhaps suggest which variables might be **confounders** in this network?