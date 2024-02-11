from whelper.textual_helper import display_table


data = {
    "key_1": {"c1": 1, "c2": "a", "c3": 0.1},
    "key_2": {"c1": 2, "c2": "b", "c3": 0.2},
    "key_3": {"c1": 3, "c2": "c", "c3": 0.3},
}

app_to_test = display_table(data_or_path=data, is_dev_for_pytest=True)
