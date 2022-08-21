import time
from locust import HttpUser, task, between
import pandas as pd
import os
from backend.app.services.data_services import DataService
import random


data_service = DataService()
data_service.create_pd_df('transaction')
uid_list = data_service.get_user_id_list()


def get_random_uid(
        uid_list: list = uid_list,
        percent_new_user: int = 10
    ) -> str:

    uid = ''
    num = random.randint(1, 100)

    if num <= percent_new_user:
        uid = 'FAKE_USER_ID'
    else:
        uid = random.choice(uid_list)
    
    return uid


class QuickstartUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def recommend(self):
        uid = get_random_uid(percent_new_user = 10)
        self.client.get(f"/recommend?uid={uid}")