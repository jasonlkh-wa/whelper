from whelper.textual_helper import display_table


data = [["c1", "c2", "c3"], [1, "a", 0.1], [2, "b", 0.2], [3, "c", 0.3]]
app_to_test = display_table(data_or_path=data, is_dev_for_pytest=True)
