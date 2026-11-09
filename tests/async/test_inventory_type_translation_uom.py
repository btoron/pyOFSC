"""Inventory type translations keep their unit of measure (#211)."""

from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.models import EnumerationValue, InventoryType, InventoryTypeTranslation, Translation


# Raw GET /rest/ofscMetadata/v1/inventoryTypes/{label} reply for a non-serialized type, from the issue.
NON_SERIALIZED = {
    "label": "EC_SLMC",
    "name": "Slump Cones",
    "unitOfMeasurement": "EA",
    "nonSerialized": True,
    "translations": [{"language": "en", "name": "Slump Cones", "unitOfMeasurement": "EA", "languageISO": "en-US"}],
}


def _response(payload: dict) -> Mock:
    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = payload
    return response


def test_issue_repro_keeps_the_translation_unit_of_measure() -> None:
    inventory_type = InventoryType.model_validate(
        {
            "label": "X",
            "nonSerialized": True,
            "unitOfMeasurement": "EA",
            "translations": [{"language": "en", "name": "X", "unitOfMeasurement": "EA"}],
        }
    )
    dumped = inventory_type.model_dump(by_alias=True, exclude_none=True)["translations"]
    assert dumped == [{"language": "en", "name": "X", "unitOfMeasurement": "EA"}]


def test_translation_without_unit_of_measure_omits_the_key() -> None:
    inventory_type = InventoryType.model_validate({"label": "CABLE", "translations": [{"language": "en", "name": "Cable"}]})
    assert inventory_type.translations is not None
    assert inventory_type.translations[0].unitOfMeasurement is None
    dumped = inventory_type.model_dump(by_alias=True, exclude_none=True)["translations"]
    assert dumped == [{"language": "en", "name": "Cable"}]


def test_inventory_type_translations_are_still_translations() -> None:
    inventory_type = InventoryType.model_validate(NON_SERIALIZED)
    assert inventory_type.translations is not None
    translation = inventory_type.translations[0]
    assert isinstance(translation, InventoryTypeTranslation)
    assert isinstance(translation, Translation)
    assert inventory_type.translations.map()["en"].unitOfMeasurement == "EA"
    assert [t.languageISO for t in inventory_type.translations] == ["en-US"]


def test_shared_translation_model_is_unchanged() -> None:
    # Enumeration values are written with model_dump() and no exclude_none, so
    # the shared model must not gain a null unitOfMeasurement key.
    value = EnumerationValue.model_validate({"active": True, "label": "A", "translations": [{"language": "en", "name": "A"}]})
    assert "unitOfMeasurement" not in value.model_dump()["translations"][0]
    assert "unitOfMeasurement" not in Translation.model_fields


@pytest.mark.asyncio
async def test_get_inventory_type_reads_the_translation_unit(mock_instance: AsyncOFSC) -> None:
    mock_instance.metadata._client.get = AsyncMock(return_value=_response(NON_SERIALIZED.copy()))
    inventory_type = await mock_instance.metadata.get_inventory_type("EC_SLMC")
    assert inventory_type.translations is not None
    assert inventory_type.translations[0].unitOfMeasurement == "EA"


@pytest.mark.asyncio
async def test_create_or_replace_sends_the_translation_unit(mock_instance: AsyncOFSC) -> None:
    mock_instance.metadata._client.put = AsyncMock(return_value=_response(NON_SERIALIZED.copy()))
    data = InventoryType.model_validate(NON_SERIALIZED)
    result = await mock_instance.metadata.create_or_replace_inventory_type(data)
    body = mock_instance.metadata._client.put.call_args.kwargs["json"]
    assert body["unitOfMeasurement"] == "EA"
    assert body["translations"] == [{"language": "en", "name": "Slump Cones", "unitOfMeasurement": "EA", "languageISO": "en-US"}]
    assert result.translations is not None
    assert result.translations[0].unitOfMeasurement == "EA"
