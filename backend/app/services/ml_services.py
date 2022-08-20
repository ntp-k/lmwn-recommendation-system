from surprise import dump
import os
import pandas as pd

cur_dir = os.getcwd()
model_dir = os.path.join(cur_dir, 'app', 'models')


def get_model_path(
        model_dir: str = model_dir
    ) -> str:

    model = [ f for f in os.listdir(model_dir) if f.endswith('.pickle')]
    path_to_model = os.path.join(model_dir, model[0])
    
    return path_to_model


class MLServices:
    def __init__(self) -> None:
        self.model_path = get_model_path()
        self.model = None
    
    def load_model(self):
        pred, loaded_model = dump.load(self.model_path)
        self.pred = pred
        self.model = loaded_model

    def predict(
            self,
            user_id,
            restaurant_id,
        ):

        if self.model is None:
            self.load_model()

        predict_result = self.model.predict(user_id, restaurant_id)

        return predict_result
    
    def predict_recommendation_list_by_uid(
            self,
            n,
            user_id,
            restaurant_id_list
        ):

        user_interest = dict()
        user_interest['restaurant_id'] = []
        user_interest['est'] = []

        for res_id in restaurant_id_list:
            predict_result = self.predict(user_id, res_id)
            user_interest['restaurant_id'].append(predict_result.iid)
            user_interest['est'].append(predict_result.est)
        
        user_interest_df = pd.DataFrame(user_interest)
        top_n_res_id = user_interest_df.nlargest(n, 'est').restaurant_id.tolist()
    
        return top_n_res_id
    

if __name__ == "__main__":
    ml_service = MLServices()
    ml_service.get_recommendation_list


# EOF