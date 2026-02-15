# This is the file for plotting the different graphs generated after refinement
import os
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from pgmpy.readwrite import BIFReader
from pgmpy.metrics import log_likelihood_score
from pathlib import Path

tld = Path(__file__).parent.parent
bif_dir = os.path.join(tld, "refinement", "results")
output_dir = os.path.join(tld, "refinement", "plots")
data_dir = "../data/processed_data.csv"

if __name__ == "__main__":
    data = pd.read_csv(data_dir)
    data = data.drop(columns=["id"]).dropna().astype(int).astype(str)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    log_df = pd.DataFrame(columns=["model", "log_likelihood"])
    for cur, dirs, files in os.walk(bif_dir):
        for file in files:
            if file.endswith(".bif"):
                print("Evaluating model " + file)
                reader = BIFReader(os.path.join(cur, file))
                model = reader.get_model()
                ll_score = log_likelihood_score(model, data)
                log_df.loc[len(log_df.index)] = [file.replace(".bif", ""), ll_score]
                model_gv = model.to_graphviz()
                subdirs = cur.replace(bif_dir, "")
                os.makedirs(f"{output_dir}{subdirs}", exist_ok=True)
                model_gv.draw(f"{output_dir}{subdirs}/{file.replace(".bif", ".png")}", prog="dot")

    log_df.to_csv("refined_log_likelihood.csv")
