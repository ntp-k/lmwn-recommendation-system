from fastapi import FastAPI
from app.services.data_services import DataService
from app.services.ml_services import MLServices

app = FastAPI()
user_recom_list = dict()

data_services = DataService()
app.restaurant_id_list = data_services.get_restaurant_id_list()
app.user_id_list = data_services.get_user_id_list()
app.top_10_hot_restaurant_id_list = data_services.get_top_n_restaurant_id(10)

app.ml_services = MLServices()
app.ml_services.load_model()


def is_first_time_user(
        uid
    ) -> bool:

    if uid in app.user_id_list: # user has transaction history
        return False
    else: # user doesn't have transaction history
        return True


@app.get("/recommend")
def get_recommendation_by_uid(uid: str):
    recommended_list = []
    first_time_user = is_first_time_user(uid)

    if first_time_user:
        recommended_list = app.top_10_hot_restaurant_id_list
    else:
        # check for cache
        if uid in user_recom_list:
            recommended_list = user_recom_list[uid]
        else:
            recommended_list = app.ml_services.predict_recommendation_list_by_uid(n=10, 
                                                                                user_id=uid, 
                                                                                restaurant_id_list=app.restaurant_id_list
                                                                                )
            user_recom_list[uid] = recommended_list        

    return {"uid": uid, "new_user": first_time_user, "rid_lsit": recommended_list}


@app.get("/")
def hello_world():
    return {'msg': 'hello world!'}
# EOF