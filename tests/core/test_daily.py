from datetime import datetime

from ofsc import OFSC
from ofsc.models import DailyExtractFiles, DailyExtractFolders

# FOR TESTING THIS GROUP WE NEED A PROD INSTANCE THAT HAS DAILY EXTRACTS ENABLED

test_instance = OFSC(
    companyName="<instance>.test",
    clientID="readonly",
    secret="<SECRET>",
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
        files: DailyExtractFiles = test_instance.core.get_daily_extract_files(
            first_folder.name
        )
        assert files is not None
        assert files.files is not None
        assert isinstance(files, DailyExtractFiles)
        for file in files.files.items:
            assert file.name is not None


def test_daily_extract_file():
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
        files: DailyExtractFiles = test_instance.core.get_daily_extract_files(
            first_folder.name
        )
        assert files is not None
        assert files.files is not None
        assert isinstance(files, DailyExtractFiles)
        if files.files and len(files.files.items) > 0:
            file = files.files.items[0]
            assert file.name is not None
            # get file details for that file
            file_content = test_instance.core.get_daily_extract_file(
                first_folder.name, file.name
            )
            assert file_content is not None
            # write the file to disk
            with open(file.name, "wb") as f:
                f.write(file_content)
