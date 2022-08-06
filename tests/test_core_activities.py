import logging

from ofsc.common import FULL_RESPONSE


def test_search_activities_001(instance):
    logging.info("...103: Search Activities (activity exists)")
    params = {
        "searchInField": "customerPhone",
        "searchForValue": "555760757294",
        "dateFrom": "2021-01-01",
        "dateTo": "2099-01-01",
    }
    response = instance.core.search_activities(params, response_type=FULL_RESPONSE)
    logging.info(response.json())
    assert response.status_code == 200
    assert response.json()["totalResults"] == 2  # 202206 Modified in demo 22B
