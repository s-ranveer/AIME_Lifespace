### Project Description
1. The repository contains Python scripts used for processing the LLM graphs, refining them using data, plotting them, computing their BIC scores, and computing their CI independencies.
2. The dataset, containing about 10 rural and 10 Indigenous examples each, for the code is not available at the moment, and there is no timeframe for its availability.
3. For the project, we had our clinical experts provide us with the causal graph. As for the LLMs, we used Claude 4.5 Sonnet, GPT 5.2, and Gemini 3 (thinking) to prompt and get the weighted causal graphs as outputs. Each LLM was prompted five times, with the outputs pooled together in the end. During prompting, if a cyclic graph was returned, we prompted again (once each for Claude and Gemini)
4. The non-boolean (or categorical values with two categories) were binarized as per the thresholds
    1. non_routine_days = 1 if # of non-routine days > 14 else 0
    2. challenging_days = 1 if # of challenging days > 10 else 0
    3. total_burden = 1 if max total burden > sample mean else 0
    4. life_space_score = 1 if life_space_score > sample mean else 0
5. For the data-driven causal discovery, FCI was used.

### Repository Details
1. /graphs: Folder containing the responses from the LLMs and experts. Each corresponding LLM folder contains the different prompt responses, extracted edges as well as plots. For the expert, there is only a single response and graph.
2. /prompts: Folder containing the prompts used (causal.md) for the different LLMs
3. /refinement: Folder containing the refinement code and results
    1. plots: The plots for subtractive refinement for the combination of different LLM responses, as well as expert ones
    2. refinement: The refined results in the form of .bif files for subtractive refinement for the combination of different LLM responses, as well as expert ones
    3. blacklist.csv: The list containing impossible edges
    4. hill_climb.py: Pgmpy code Hill Climb Search modified to work with subtractive refinement.
    5. structure_learning_subtractive.py: File containing the methods and classes for learning the refinement structure.
    6. subtractive_refinement.py: File to run for starting the subtractive refinement process. Uses the structure learning classes for refinement
    7. plot_and_evaluate_bif.py: Method to plot and evaluate the log_likelihood of the refined model.
4. compute_ci.py: File for computing the conditional independence metrics for the manuscript
5. merge_graphs.py: File for merging the different LLM responses.
6. plot_graphs.py: File for plotting the edge lists to a graphviz plot

### Code Dependencies:
The code was tested on a Linux System with python 3.10 . The code has the following dependencies
```
pandas~=2.3.3
networkx~=3.5
matplotlib~=3.10.7
scikit-learn~=1.7.2
numpy~=2.3.4
pgmpy~=1.0.0
causal-learn
```
**Note**: One may need to make changes to pgmpy library files in BayesianEsttimator code line 34 onwards to be something 
along these lines
```python
if isinstance(model, DAG):
    if len(model.edges()) == 0:
        temp = DiscreteBayesianNetwork()
        temp.add_nodes_from(model.nodes())
        model = temp
    else:
        model = DiscreteBayesianNetwork(model.edges())
```
This is due to the fact that BayesianEstimator fails for graphs with no edges
