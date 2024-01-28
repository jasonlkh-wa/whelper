import pandas as pd

# CR-soon: This is not optimal to import the package, as the package must be deployed
# or else the test is running on the stale package, consider:
# 1. add a [-dev] flag to release-whelper to publish the change to a dev venv and then test
#    it -> This is the right way
# 2. check the standardized way to work on package and how others import and test
from whelper.textual_helper import display_table


def test_display_table():
    data = pd.DataFrame({"a": [1, 2, 3], "b": [2, 3, 4]})
    data_lst = [["c", "d"], ["1", "2"], ["2", "3"], ["3", "4"]]

    assert display_table(data=data) is None
    assert display_table(data=data_lst) is None
