import pandas as pd
from whelper import display_table

if __name__ == "__main__":
    data = pd.DataFrame({"a": [1, 2, 3], "b": [2, 3, 4]})
    data_lst = [["c", "d"], ["1", "2"], ["2", "3"], ["3", "4"]]

    display_table(data=data)
    display_table(data=data_lst)
