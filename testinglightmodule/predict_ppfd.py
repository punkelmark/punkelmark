"""
    Title: PPFD Prediction Module
    Author: Elmark Corpus
    Latest Update: 1/4/23    
    Description: This module is tasked for loading the Multiple Regression Model (MLRmodel.pkl) for predicting PPFD values based on provided spectral data
                 Module uses joblib library to export MLR model object for deployment
                 MLR model is developed in Jupyter Notebook, refer to it for more details on model development

"""

import joblib as joblib

# Load MLR model
dir_workspace = "MLRmodel.pkl"
dir_rpi = "automain/automodules/MLRmodel.pkl"
dir_standalone = "automodules/MLRmodel.pkl"

try:
    model, ref_cols, target = joblib.load(dir_standalone)
except:
    try:
        model, ref_cols, target = joblib.load(dir_workspace)
    except:
        model, ref_cols, target = joblib.load(dir_rpi)

# Create function call for prediction

def get_PPFD(X):
    # Pass spectral data from AS7341
    ppfd = model.predict([X])
    if ppfd < 0: 
        return 0
    return ppfd

def main():

    return True

if __name__=="__main__":
    main()    
