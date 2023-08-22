import time
import glob
import joblib
import numpy as np
import pandas as pd
import multiprocessing as mp
from sklearn.impute import KNNImputer
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
from bayes_opt import BayesianOptimization
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

# read covariate table with CVI
all_df=pd.read_csv('...')

# take X and y
X = all_df.drop(['FID', 'gridid', 'VI', 'SVI', 'CVI'], axis=1)
y = all_df['CVI']

# split train and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, shuffle=True, random_state=1)

# train base model
rf_base = RandomForestClassifier(random_state=10, oob_score=True, n_jobs=8)
final_start_time = time.time()
rf_base.fit(X_train, y_train)
final_train_time = time.time() - final_start_time
final_oob = rf_base.oob_score_

# save model
joblib.dump(rf_base, '...')

# accuracy of the trained model on test set
pred_y_test = rf_base.predict(X_test)
X_test['pred_CVI'] = pred_y_test
X_test = pd.concat([X_test, y_test], axis=1)
X_test=X_test[['pred_CVI','CVI']]
X_test['CVI']=X_test['CVI'].map(lambda x:int(x))
f1_test = f1_score(X_test['CVI'], X_test['pred_CVI'], average='macro')
kappa_test = cohen_kappa_score(X_test['CVI'], X_test['pred_CVI'])
classify_report_dict = classification_report(X_test['CVI'], X_test['pred_CVI'])