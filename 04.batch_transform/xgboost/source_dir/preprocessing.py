
import sys
import subprocess
import logging

# 로그 생성
logger = logging.getLogger()

# 로그의 출력 기준 설정
logger.setLevel(logging.INFO)

# log 출력 형식
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# log 출력
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'xgboost'])

import pandas as pd
import tarfile
import xgboost as xgb

if __name__=='__main__':
    logger.info('Starting preprocessing...')
    
    input_file = '/opt/ml/processing/input/boston.csv'
    input = pd.read_csv(input_file)
    
    logger.info('Input data')
    logger.info(input.head())
    
    logger.info('Loading trained XGBoost model...')
    
    model_artifacts = '/opt/ml/processing/model/model.tar.gz'
    with tarfile.open(model_artifacts) as model:
        model.extractall('/opt/ml/processing/model')
    
    loaded_model = xgb.Booster()
    loaded_model.load_model('/opt/ml/processing/model/model.json')
    
    logger.info('Starting batch prefiction...')
    predictions = loaded_model.inplace_predict(input.loc[:, input.columns != 'PRICE'])
    input['PREDICTED'] = predictions
    
    input.to_csv('/opt/ml/processing/results/results.csv', index=False)
    logger.info('Output data')
    logger.info(input.head())
