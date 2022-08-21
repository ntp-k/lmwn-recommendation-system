import argparse
import os
import pandas as pd
import surprise
from surprise import Reader, Dataset, SVD, dump
from surprise.model_selection import  GridSearchCV
import numpy as np
import json
from datetime import datetime


def create_pd_df(
        path_to_data: str = None
    ) -> pd.DataFrame:

    df = None

    if os.path.isfile(path_to_data):
        try:
            df = pd.read_csv(path_to_data)
        except Exception as e:
            print('Error:', e)

    else:
        raise Exception(f'{path_to_data} not found')
    
    return df
    

def create_user_ratings_df(
        pd_df: pd.DataFrame = None
    ) -> pd.DataFrame:

    user_ratings_df = None

    if pd_df is not None:
        try:
            pd_df = pd_df[['user_id', 'restaurant_id']]
            user_ratings_df = pd_df.groupby(pd_df.columns.tolist(), as_index=False).size().reset_index()
            user_ratings_df = user_ratings_df.rename({'size':'freq'}, axis=1)

        except Exception as e:
            print(e)

    else:
        raise ValueError('pd_df is None')
    
    return user_ratings_df


def surprise_df(
        user_ratings_df: pd.DataFrame = None
    ) -> surprise.dataset.DatasetAutoFolds:

    user_ratings_matrix = None

    if user_ratings_df is not None:
        try:
            scale = (user_ratings_df.freq.min(), user_ratings_df.freq.max())
            reader = Reader(rating_scale=scale)

            user_ratings_matrix = Dataset.load_from_df(user_ratings_df[['user_id',
                                            'restaurant_id',
                                            'freq']], reader)

        except Exception as e:
            print('Error:', e)
    
    else:
        raise ValueError('pd_df is None')
    
    return user_ratings_matrix


def gridsearch(
        model,
        data
    ):

    svd_param_grid = {'n_factors': [5, 15, 25, 35, 50],
                        'n_epochs': [5, 15, 25, 35, 50],       
                        'lr_all': [0.001, 0.002, 0.005, 0.01],
                        'reg_all':[0.02, 0.1, 0.4]
                    }

    gs = GridSearchCV(model, svd_param_grid, measures=['rmse'], cv=5)
    gs.fit(data)

    best_params = gs.best_params['rmse']
    best_score = gs.best_score['rmse']

    return best_params, best_score


def set_model_params(
        user_ratings_matrix,
        config
    ):

    svd_params = {}
    path_to_model_params = config['path_to_model_params']

    if path_to_model_params == '' or not os.path.isfile(path_to_model_params):
        print('searching for best model parameters...')

        try:
            svd_params, svd_score = gridsearch(SVD, user_ratings_matrix)
            print("best score:", svd_score)
            print("best params:", svd_params)

            svd_params['grid_search'] = True
            svd_params['best_score'] = svd_score

        except Exception as e:
            print('Error:', e)
    
    else:
        print('loading model parameters...')
        with open(path_to_model_params, 'r') as fin:
            svd_params = json.load(fin)

        svd_params['grid_search'] = False
        svd_params['best_score'] = 0.0
    
    output_dir = config['output_directory']
    os.makedirs(output_dir, exist_ok=True)
    model_params_filename = config['output_model_name'].split('.')[0] + '_params.json'
    output_model_params_path = os.path.join(output_dir, model_params_filename)

    with open(output_model_params_path, 'w') as fout:
        string_svd_params = json.dumps(svd_params, indent=4)
        fout.write(string_svd_params)

    print('model parameters:')
    print(json.dumps(svd_params, indent=4))
    print('model parameters saved:', output_model_params_path)
    
    return svd_params


def create_svd_model(
        params: dict
    ) -> surprise.prediction_algorithms.matrix_factorization.SVD:

    model = None

    try:
        if params is not None:
            model = SVD(n_factors=params['n_factors'], 
                        n_epochs=params['n_epochs'],
                        lr_all=params['lr_all'], 
                        reg_all=params['reg_all'])
        else:
            model = SVD()

    except Exception as e:
        print('Error:', e)
    
    return model


def train_model(
        model,
        user_ratings_matrix
    ):

    if user_ratings_matrix is not None:
        training_data = user_ratings_matrix.build_full_trainset()

        try:
            model.fit(training_data)
        except Exception as e:
            print('Error:', e)
    
    else:
        raise Exception('training data is None')
    
    return model


def test_predict(
        model,
        uid,
        iid
    ):
    result = {}

    try:
        result = model.predict(uid, iid)
    except Exception as e:
        print('Error:', e)

    if len(result) == 0:
        return False
    else:
        return True


def save_model(
        config,
        final_model
    ):

    output_dir = config['output_directory']
    os.makedirs(output_dir, exist_ok=True)
    model_name = config['output_model_name']
    output_model_path = os.path.join(output_dir, model_name)

    if os.path.isfile(output_model_path):
        print(f'output model path: {output_model_path} already exist')
        print('replaceing...')
        os.remove(output_model_path)

    try:
        dump.dump(output_model_path, None, final_model)
    except Exception as e:
        print('Error:', e)

    print('model saved:', output_model_path)


def main(
        config: dict
    ) -> None:

    # create data
    print('creating data...')
    pd_df = create_pd_df(config['path_to_data'])
    user_ratings_df = create_user_ratings_df(pd_df)
    user_ratings_matrix = surprise_df(user_ratings_df)
    
    # setting model params
    print('setting model parameters...')
    svd_params = set_model_params(user_ratings_matrix,
                                    config
                                )

    # create model
    print('creating model...')
    svd = create_svd_model(svd_params)

    # train model
    print('training model...')
    final_model = train_model(svd, user_ratings_matrix)

    # test predict output, check if model works properly
    print('testing prediction...')
    if pd_df.shape[0] > 0:
        if not test_predict(final_model, pd_df['user_id'][0], pd_df['restaurant_id'][0]):
            raise Exception('prediction rasult is empty')

    # save model
    print('saving model...')
    save_model(config, final_model)

    print('DONE')


if __name__ == '__main__':
    start_time = datetime.now()
    print(f'\nStart Time:', start_time, '\n')

    # set variables
    root_dir = os.path.dirname(os.path.realpath(__file__))
    path_to_data = os.path.join(root_dir, 'transaction')
    datetime_str = start_time.strftime("%Y%m%d_%H%M%S")
    saved_model_dir = os.path.join(root_dir, 'models', f'model_{datetime_str}')
    model_name = f'model_{datetime_str}.pickle'

    ap = argparse.ArgumentParser()
    ap.add_argument("-data", "--path_to_data", type=str, default=path_to_data,
                    help="path to training data (.csv) ex: /home/user/assignment/data.csv")
    ap.add_argument("-params", "--path_to_model_params", type=str, default='',
                    help="path to model parameters (.json) ex: /home/user/assignment/models/model_params.json")
    ap.add_argument("-dir", "--output_directory", type=str, default=saved_model_dir,
                    help="directory that model will be saved at ex: /home/user/assignment/models")
    ap.add_argument("-model", "--output_model_name", type=str, default=model_name,
                    help="name of output model (.pickle) ex: model.pickle")
    config = vars(ap.parse_args())

    if config['output_directory'].endswith('/') or config['output_directory'].endswith('\\'):
        config['output_directory'] = config['output_directory'][:-1]

    print('config:')
    print(json.dumps(config, indent=4))

    # main
    main(config)

    end_time = datetime.now()
    print(f'\nEnd Time:', end_time)
    print(f'Duration: {end_time - start_time}\n')

# EOF