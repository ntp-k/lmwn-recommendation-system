from fastapi import FastAPI
from app.services.data_services import DataService
from app.services.ml_services import MLServices

app = FastAPI()

data_services = DataService()
restaurant_id_list = data_services.get_restaurant_id_list()
user_id_list = data_services.get_user_id_list()
top_10_hot_restaurant_id_list = data_services.get_top_n_restaurant_id(10)

ml_services = MLServices()
ml_services.load_model()

def is_first_time_user(
        uid
    ) -> bool:

    if uid in user_id_list: # user has transaction history
        return False
    else: # user doesn't have transaction history
        return True


@app.get("/recommend/{uid}")
def get_recommendation_by_uid(uid: str):
    if is_first_time_user(uid):
        recommended_list = top_10_hot_restaurant_id_list
    else:
        recommended_list = ml_services.predict_recommendation_list_by_uid(10, uid, restaurant_id_list)

    return {"uid": uid, "rid_lsit": recommended_list}


# EOF