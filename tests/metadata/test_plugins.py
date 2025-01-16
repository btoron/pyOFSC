from pathlib import Path

from ofsc import OFSC
from ofsc.common import FULL_RESPONSE


def test_import_plugin_file(instance: OFSC):
    metadata_response = instance.metadata.import_plugin_file(
        Path("tests/test.xml"), response_type=FULL_RESPONSE
    )
    assert metadata_response.status_code == 204


def test_import_plugin(instance: OFSC):
    metadata_response = instance.metadata.import_plugin(
        Path("tests/test.xml").read_text(), response_type=FULL_RESPONSE
    )
    assert metadata_response.status_code == 204
