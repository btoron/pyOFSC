from datetime import datetime

from ofsc import OFSC
from ofsc.models import DailyExtractFolders

# FOR TESTING THIS GROUP WE NEED A PROD INSTANCE THAT HAS DAILY EXTRACTS ENABLED

test_instance = OFSC(
    companyName="fairpoint.test",
    clientID="readonly",
    secret="bfebfd543c962b08717907397eed3e2783f0efba4f02716ef07e8617e1f6",
)


def test_daily_extract_dates():
    folders: DailyExtractFolders = test_instance.core.get_daily_extract_dates()
    assert folders is not None
    assert folders.folders is not None
    assert isinstance(folders, DailyExtractFolders)
    for folder in folders.folders.items:
        assert folder.name is not None


def test_daily_extract_files_with_date():
    folders: DailyExtractFolders = test_instance.core.get_daily_extract_dates()
    assert folders is not None
    assert folders.folders is not None
    assert isinstance(folders, DailyExtractFolders)
    if folders.folders and len(folders.folders.items) > 0:
        assert folders.folders.items[0].name is not None
        first_folder = folders.folders.items[0]
        assert first_folder.name is not None
        # Assert that the name is parseable as a date
        assert first_folder.name == first_folder.name[:10]
        # Parse the date
        date = datetime.strptime(first_folder.name, "%Y-%m-%d")
        assert date is not None
        # get files for that date
