## Setup
You are a knowledge engineer working on a project involving patients living with dementia (PLWD). Think carefully and logically, explaining the reasoning behind your answers.
Available Information

Your team has collected information from the Lifespace Assessment (LSA) conducted over a month for different patients. The data include lifespace scores, daily diaries, and demographic information about patients and their caregivers. Using this data, you computed the following variables for each patient. These variables will be used for Logistic Regression Model construction.

The variables collected are as follows:

    1. sex_cg: The sex of the caregiver. The value is either male or female.
    2. educ_cg: The education level of the caregiver. This is a boolean variable with a value of 1 for some college or more, and 0 for high school or less.
    3. sex_plwd: The sex of the patient. The value is either male or female.
    4. educ_plwd: The education level of the patient. This is a boolean variable with a value of 1 for some college or more, and 0 for high school or less.
    5. lifespace_score: A boolean variable indicating a high Lifespace Assessment score. The LSA measures an individual’s mobility and independence; a higher score indicates better mobility and independence.
    6. non_routine_days: A boolean variable indicating whether the patient had a high number of days in a month where their routine deviated from normal.
    7. challenging_days: A boolean variable indicating whether the patient had a high number of days in a month when they were not feeling well or not having a good day.
    8. total_burden: A boolean variable indicating whether the caregiver experienced significant difficulty in caring for the patient.
    9. community_type: The type of community the patient lives in. The value is either rural or indigenous.

## Task

Make a list of direct association relationships between these variables and provide a score from [-2, -1, 0, 1, 2], where -2 indicates a strong negative association, -1 indicates a negative association, 0 indicates no association, 1 indicates a positive association, and 2 indicates a strong positive association with the lifespace_score.
