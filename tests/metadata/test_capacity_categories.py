import pytest

from ofsc.models import CapacityCategory, CapacityCategoryListResponse


@pytest.mark.uses_real_data
def test_get_capacity_categories_model_no_parameters(instance, pp, demo_data):
    capacity_categories = demo_data.get("metadata").get("expected_capacity_categories")
    metadata_response = instance.metadata.get_capacity_categories()
    assert isinstance(metadata_response, CapacityCategoryListResponse), (
        f"Expected a CapacityCategoryListResponse received {type(metadata_response)}"
    )
    assert len(metadata_response.items) == len(capacity_categories.keys()), (
        f"Expected {len(capacity_categories.keys())} received {metadata_response.totalResults}"
    )
    assert metadata_response.hasMore is False
    assert metadata_response.totalResults == len(capacity_categories.keys())
    for category in metadata_response.items:
        assert isinstance(category, CapacityCategory)
        assert category.label in capacity_categories.keys()


@pytest.mark.uses_real_data
def test_get_capacity_category(instance, pp, demo_data):
    capacity_categories = demo_data.get("metadata").get("expected_capacity_categories")
    for category in capacity_categories.keys():
        metadata_response = instance.metadata.get_capacity_category(category)
        assert isinstance(metadata_response, CapacityCategory), (
            f"Expected a CapacityCategory received {type(metadata_response)}"
        )
        assert metadata_response.label == category
        assert metadata_response.name == capacity_categories[category].get("name")


def test_capacity_category_nested_fields_are_preserved():
    """Nested workSkills/workSkillGroups fields must not be silently dropped.

    Mirrors the real OFS API shape (synthetic labels). Regression test for #175.
    """
    from ofsc.models import (
        CapacityCategory,
        CapacityCategoryWorkSkill,
        CapacityCategoryWorkSkillGroup,
    )

    payload = {
        "label": "DEMO_CAT",
        "name": "Demo Category",
        "active": True,
        "workSkills": [
            {
                "label": "S_DEMO",
                "ratio": 100,
                "startDate": "2023-01-06",
                "end_date": "2025-01-04",
                "created_by": "alice",
                "creation_date": "2023-01-06 10:00:00",
                "last_updated_by": "bob",
                "last_update_date": "2024-01-01 12:00:00",
                "last_update_login": "bob_login",
            }
        ],
        "workSkillGroups": [
            {
                "label": "Demo Group",
                "startDate": "2025-01-05",
                "end_date": "",
                "created_by": "carol",
                "creation_date": "2025-01-05 09:00:00",
                "last_updated_by": "carol",
                "last_update_date": "2025-01-05 09:00:00",
                "last_update_login": "carol_login",
                "links": [
                    {
                        "rel": "canonical",
                        "href": "https://x.example/rest/ofscMetadata/v1/workSkillGroups/Demo%20Group",
                    }
                ],
            }
        ],
        "timeSlots": [{"label": "AM"}, {"label": "PM"}],
        "translations": [{"language": "en", "name": "Demo Category", "languageISO": "en-US"}],
        "links": [{"rel": "canonical", "href": "https://x.example/cat/DEMO_CAT"}],
    }

    cat = CapacityCategory.model_validate(payload)

    # workSkills: declared fields are typed and populated
    skill = cat.workSkills[0]
    assert isinstance(skill, CapacityCategoryWorkSkill)
    assert skill.label == "S_DEMO"
    assert skill.ratio == 100
    assert skill.startDate == "2023-01-06"
    assert skill.end_date == "2025-01-04"

    # workSkills: undeclared audit fields preserved via extra="allow"
    assert skill.model_extra["created_by"] == "alice"
    assert skill.model_extra["last_update_login"] == "bob_login"

    # workSkillGroups: declared fields + links typed and populated
    group = cat.workSkillGroups[0]
    assert isinstance(group, CapacityCategoryWorkSkillGroup)
    assert group.label == "Demo Group"
    assert group.startDate == "2025-01-05"
    assert group.end_date == ""
    assert group.links[0].rel == "canonical"
    assert group.model_extra["created_by"] == "carol"

    # timeSlots unchanged (label only)
    assert cat.timeSlots[0].label == "AM"

    # round-trip: extras survive model_dump()
    dumped = cat.model_dump()
    assert dumped["workSkills"][0]["created_by"] == "alice"
    assert dumped["workSkills"][0]["ratio"] == 100


def test_capacity_category_with_empty_nested_lists():
    """A category with no skills/groups (the COPPER shape) parses cleanly."""
    from ofsc.models import CapacityCategory

    cat = CapacityCategory.model_validate(
        {
            "label": "COPPER",
            "name": "Copper",
            "active": True,
            "workSkills": [],
            "workSkillGroups": [],
            "timeSlots": [{"label": "AM"}],
            "translations": [{"language": "en", "name": "Copper"}],
            "links": [],
        }
    )
    assert cat.workSkills == []
    assert cat.workSkillGroups == []
    assert cat.label == "COPPER"
