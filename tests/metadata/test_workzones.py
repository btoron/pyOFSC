from ofsc.common import FULL_RESPONSE


def test_get_workzones(instance):
    metadata_response = instance.metadata.get_workzones(
        offset=0, limit=1000, response_type=FULL_RESPONSE
    )
    response = metadata_response.json()
    assert response["totalResults"] is not None
    assert response["totalResults"] == 18  # 22.B
    assert response["items"][0]["workZoneLabel"] == "ALTAMONTE_SPRINGS"
    assert response["items"][1]["workZoneName"] == "CASSELBERRY"
