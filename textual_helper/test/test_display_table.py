# CR-soon: This is not optimal to import the package, as the package must be deployed
# or else the test is running on the stale package, consider:
# ++1. add a [-dev] flag to release-whelper to publish the change to a dev venv and then test
#    it -> This is the right way
# --2. check the standardized way to work on package and how others import and test
import os

PWD = os.path.dirname(os.path.abspath(__file__))


# CR: consider putting all textual test here
def test_display_table_for_pandas_dataframe(snap_compare):
    assert snap_compare(
        os.path.join(PWD, "display_table_app_for_pandas_df.py:app_to_test")
    )


def test_display_table_for_nested_list(snap_compare):
    assert snap_compare(
        os.path.join(PWD, "display_table_app_for_nested_list.py:app_to_test")
    )
