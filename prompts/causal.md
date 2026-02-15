## Setup
You are a knowledge engineer working to build a causal model regarding patients living with Dementia (plwd). Think carefully and logically, explaining the reasons for your answer.

## Available information
Your team has collected information regarding the Lifespace assessment (LSA) over a month for different patients, including the lifespace scores, daily diaries as well as the demographic information about patients and their caregivers. The following variables were collected using the information and will be used for Causal Bayesian Network construction. 

    1. sex_cg: The sex of the caregiver which is either male or female.
    2. educ_cg: The education level of the caregiver. The value is either: "some college or more" or "high school or less".
    3. sex_plwd: The sex of the patient which is either male or female.
    4. educ_plwd: The education level of the patient. The value is either: "some college or more" or "high school or less".
    5. community_type: The type of community the patient lives in. The value is either rural or indigenous.
    6. lifespace_score:  The lifespace score measures an individual’s mobility and independence; a higher score indicates better mobility and independence. It is measured by the caregiver.
    7. non_routine_days: Indicates whether the patient had a high number of days in a month where their routine deviated from normal.
    8. challenging_days: Indicates whether the patient had a high number of days in a month when they were not feeling well or not having a good day.
    9. total_burden: Indicates whether the caregiver experienced significant difficulty in caring for the patient.

## Task
Make a list of direct causal relations between these variables and explain the rationale behind each decision. Additionally, provided a weight for each causal relation from 1 to 10, where 1 is a weak causal relation and 10 is a strong causal relation.
