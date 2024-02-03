import pandas as pd
from whelper.textual_helper import display_table


data = pd.DataFrame({"a": [1, 2, 3], "b": ["a", "b", "c"], "c": [0.1, 0.2, 0.3]})
app_to_test = display_table(data=data, is_dev_for_pytest=True)
