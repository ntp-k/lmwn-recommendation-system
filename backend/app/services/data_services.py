import pandas as pd
import os

cur_dir = os.getcwd()
path_to_data = os.path.join(cur_dir, 'app', 'transaction')


class DataService:
    def __init__(self) -> None:
        self.path_to_data = path_to_data
        self.df = None

    def create_pd_df(
            self,
            path_to_data = None
        ):

        df = None
        if path_to_data is None:
            path_to_data = self.path_to_data

        if os.path.isfile(path_to_data):
            try:
                df = pd.read_csv(path_to_data)
            except Exception as e:
                print('Error:', e)

        else:
            raise Exception(f'{path_to_data} not found')
        
        self.df = df


    def get_restaurant_id_list(self) -> list:
        
        if self.df is None:
            self.create_pd_df()

        unique_res_id = self.df.restaurant_id.unique().tolist()

        return unique_res_id


    def get_user_id_list(self) -> list:
        
        if self.df is None:
            self.create_pd_df()

        unique_user_id = self.df.user_id.unique().tolist()

        return unique_user_id


    def get_top_n_restaurant_id(
            self,
            n: int = 10
        ) -> list:
        
        if self.df is None:
            self.create_pd_df()

        df = self.df[['user_id', 'restaurant_id']]
        df_frequency = self.df.groupby(df.columns.tolist(), as_index=False).size()
        top_n_res_id = df_frequency.nlargest(n, 'size').restaurant_id.tolist()

        return top_n_res_id


if __name__ == "__main__":
    file_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(file_dir)
    os.chdir('..')
    data_path = os.path.join(os.getcwd(), 'transaction')

    ds = DataService()
    ds.create_pd_df(data_path)
    res_id = ds.get_restaurant_id_list()
    print(len(res_id))
    print(res_id[:5])

    top_N = ds.get_top_n_restaurant_id(10)
    print(type(top_N))
    print(len(top_N))
    print(top_N)

# EOF