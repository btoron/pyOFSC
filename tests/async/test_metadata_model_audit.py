"""Audit tests for metadata Pydantic models vs real API responses.

These tests call the live API and check whether any fields returned by the API
are being silently captured in __pydantic_extra__ instead of mapped model fields.

This detects:
- Missing fields in model definitions
- Typos in field names (model vs API)
- API changes that added new fields we should handle

Reference: GitHub Issue #149
"""

import json
import logging
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC

logger = logging.getLogger(__name__)

# Directory to save audit results for later analysis
AUDIT_DIR = Path(__file__).parent.parent / "audit_results" / "metadata"


def _collect_extras(instance, path="") -> list[dict]:
    """Recursively collect __pydantic_extra__ from a model and its nested models.

    Returns a list of dicts with:
        - model: the model class name
        - path: dotted path to the field
        - extra_fields: dict of field_name -> value
    """
    from pydantic import BaseModel

    results = []

    # Check if this instance has extra fields
    if hasattr(instance, "__pydantic_extra__") and instance.__pydantic_extra__:
        results.append(
            {
                "model": type(instance).__name__,
                "path": path or "(root)",
                "extra_fields": {
                    k: _summarize_value(v)
                    for k, v in instance.__pydantic_extra__.items()
                },
            }
        )

    # Recurse into fields that are BaseModel instances
    if hasattr(instance, "model_fields"):
        for field_name in instance.model_fields:
            value = getattr(instance, field_name, None)
            child_path = f"{path}.{field_name}" if path else field_name
            if isinstance(value, BaseModel):
                results.extend(_collect_extras(value, child_path))
            elif isinstance(value, list):
                for i, item in enumerate(value[:3]):  # Check first 3 items
                    if isinstance(item, BaseModel):
                        results.extend(_collect_extras(item, f"{child_path}[{i}]"))

    return results


def _summarize_value(v) -> str:
    """Summarize a value for reporting (type and truncated repr)."""
    if v is None:
        return "None"
    type_name = type(v).__name__
    repr_v = repr(v)
    if len(repr_v) > 80:
        repr_v = repr_v[:77] + "..."
    return f"{type_name}: {repr_v}"


def _save_audit_result(name: str, data: dict):
    """Save audit result to JSON for offline analysis."""
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = AUDIT_DIR / f"{name}.json"
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)


class TestMetadataModelAudit:
    """Audit metadata models against real API responses to detect unmapped fields."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_activity_type_groups_extras(self, async_instance: AsyncOFSC):
        """Audit ActivityTypeGroup and ActivityTypeGroupListResponse."""
        response = await async_instance.metadata.get_activity_type_groups()
        extras = _collect_extras(response)

        _save_audit_result(
            "activity_type_groups",
            {
                "total_items": len(response.items),
                "response_extra": extras,
                "response_model_fields": list(type(response).model_fields.keys()),
            },
        )

        if extras:
            logger.warning(
                f"ActivityTypeGroupListResponse has unmapped fields: {extras}"
            )
        # Check individual items too
        if response.items:
            group = response.items[0]
            item_extras = _collect_extras(group)
            if item_extras:
                logger.warning(f"ActivityTypeGroup has unmapped fields: {item_extras}")

        assert not extras, (
            f"ActivityTypeGroupListResponse has unmapped extra fields: {extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_activity_type_group_single_extras(self, async_instance: AsyncOFSC):
        """Audit single ActivityTypeGroup model."""
        groups = await async_instance.metadata.get_activity_type_groups()
        if not groups.items:
            pytest.skip("No activity type groups available")

        group = await async_instance.metadata.get_activity_type_group(
            groups.items[0].label
        )
        extras = _collect_extras(group)

        _save_audit_result(
            "activity_type_group_single",
            {
                "label": group.label,
                "model_fields": list(type(group).model_fields.keys()),
                "extras": extras,
            },
        )

        if extras:
            logger.warning(f"ActivityTypeGroup has unmapped fields: {extras}")
        assert not extras, f"ActivityTypeGroup has unmapped extra fields: {extras}"

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_activity_types_extras(self, async_instance: AsyncOFSC):
        """Audit ActivityType and ActivityTypeListResponse."""
        response = await async_instance.metadata.get_activity_types()
        extras = _collect_extras(response)

        item_extras = []
        for at in response.items[:5]:
            ie = _collect_extras(at)
            if ie:
                item_extras.extend(ie)

        _save_audit_result(
            "activity_types",
            {
                "total_items": len(response.items),
                "response_extras": extras,
                "item_extras": item_extras,
            },
        )

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"ActivityType models have unmapped fields: {all_extras}")
        assert not all_extras, (
            f"ActivityType models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_activity_type_single_extras(self, async_instance: AsyncOFSC):
        """Audit single ActivityType model (has more fields than list)."""
        types = await async_instance.metadata.get_activity_types()
        if not types.items:
            pytest.skip("No activity types available")

        at = await async_instance.metadata.get_activity_type(types.items[0].label)
        extras = _collect_extras(at)

        _save_audit_result(
            "activity_type_single",
            {
                "label": at.label,
                "model_fields": list(type(at).model_fields.keys()),
                "extras": extras,
            },
        )

        if extras:
            logger.warning(f"ActivityType single has unmapped fields: {extras}")
        assert not extras, f"ActivityType single has unmapped extra fields: {extras}"

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_capacity_categories_extras(self, async_instance: AsyncOFSC):
        """Audit CapacityCategory model."""
        response = await async_instance.metadata.get_capacity_categories()
        extras = _collect_extras(response)

        item_extras = []
        for cc in response.items[:5]:
            ie = _collect_extras(cc)
            if ie:
                item_extras.extend(ie)

        _save_audit_result(
            "capacity_categories",
            {
                "total_items": len(response.items),
                "response_extras": extras,
                "item_extras": item_extras,
            },
        )

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(
                f"CapacityCategory models have unmapped fields: {all_extras}"
            )
        assert not all_extras, (
            f"CapacityCategory models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_capacity_category_single_extras(self, async_instance: AsyncOFSC):
        """Audit single CapacityCategory model."""
        cats = await async_instance.metadata.get_capacity_categories()
        if not cats.items:
            pytest.skip("No capacity categories available")

        cc = await async_instance.metadata.get_capacity_category(cats.items[0].label)
        extras = _collect_extras(cc)

        _save_audit_result(
            "capacity_category_single",
            {
                "label": cc.label,
                "model_fields": list(type(cc).model_fields.keys()),
                "extras": extras,
            },
        )

        if extras:
            logger.warning(f"CapacityCategory single has unmapped fields: {extras}")
        assert not extras, (
            f"CapacityCategory single has unmapped extra fields: {extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_forms_extras(self, async_instance: AsyncOFSC):
        """Audit Form model."""
        response = await async_instance.metadata.get_forms()
        extras = _collect_extras(response)

        item_extras = []
        for form in response.items[:5]:
            ie = _collect_extras(form)
            if ie:
                item_extras.extend(ie)

        _save_audit_result(
            "forms",
            {
                "total_items": len(response.items),
                "response_extras": extras,
                "item_extras": item_extras,
            },
        )

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"Form models have unmapped fields: {all_extras}")
        assert not all_extras, f"Form models have unmapped extra fields: {all_extras}"

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_inventory_types_extras(self, async_instance: AsyncOFSC):
        """Audit InventoryType model."""
        response = await async_instance.metadata.get_inventory_types()
        extras = _collect_extras(response)

        item_extras = []
        for it in response.items[:5]:
            ie = _collect_extras(it)
            if ie:
                item_extras.extend(ie)

        _save_audit_result(
            "inventory_types",
            {
                "total_items": len(response.items),
                "response_extras": extras,
                "item_extras": item_extras,
            },
        )

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"InventoryType models have unmapped fields: {all_extras}")
        assert not all_extras, (
            f"InventoryType models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_languages_extras(self, async_instance: AsyncOFSC):
        """Audit Language model."""
        response = await async_instance.metadata.get_languages()
        extras = _collect_extras(response)

        item_extras = []
        for lang in response.items[:5]:
            ie = _collect_extras(lang)
            if ie:
                item_extras.extend(ie)

        _save_audit_result(
            "languages",
            {
                "total_items": len(response.items),
                "response_extras": extras,
                "item_extras": item_extras,
            },
        )

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"Language models have unmapped fields: {all_extras}")
        assert not all_extras, (
            f"Language models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_map_layers_extras(self, async_instance: AsyncOFSC):
        """Audit MapLayer model."""
        response = await async_instance.metadata.get_map_layers()
        extras = _collect_extras(response)

        item_extras = []
        for ml in response.items[:5]:
            ie = _collect_extras(ml)
            if ie:
                item_extras.extend(ie)

        _save_audit_result(
            "map_layers",
            {
                "total_items": len(response.items),
                "response_extras": extras,
                "item_extras": item_extras,
            },
        )

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"MapLayer models have unmapped fields: {all_extras}")
        assert not all_extras, (
            f"MapLayer models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_non_working_reasons_extras(self, async_instance: AsyncOFSC):
        """Audit NonWorkingReason model."""
        response = await async_instance.metadata.get_non_working_reasons()
        extras = _collect_extras(response)

        item_extras = []
        for nwr in response.items[:5]:
            ie = _collect_extras(nwr)
            if ie:
                item_extras.extend(ie)

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(
                f"NonWorkingReason models have unmapped fields: {all_extras}"
            )
        assert not all_extras, (
            f"NonWorkingReason models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_properties_extras(self, async_instance: AsyncOFSC):
        """Audit Property model (uses extra='ignore' - verify no data loss)."""
        response = await async_instance.metadata.get_properties()
        extras = _collect_extras(response)

        _save_audit_result(
            "properties",
            {
                "total_items": len(response.items),
                "response_extras": extras,
            },
        )

        # Property model uses extra="ignore" so response-level extras are
        # from OFSResponseList which uses extra="allow"
        if extras:
            logger.warning(f"PropertyListResponse has unmapped fields: {extras}")
        assert not extras, f"PropertyListResponse has unmapped extra fields: {extras}"

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_resource_types_extras(self, async_instance: AsyncOFSC):
        """Audit ResourceType model."""
        response = await async_instance.metadata.get_resource_types()
        extras = _collect_extras(response)

        item_extras = []
        for rt in response.items[:5]:
            ie = _collect_extras(rt)
            if ie:
                item_extras.extend(ie)

        _save_audit_result(
            "resource_types",
            {
                "total_items": len(response.items),
                "response_extras": extras,
                "item_extras": item_extras,
            },
        )

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"ResourceType models have unmapped fields: {all_extras}")
        assert not all_extras, (
            f"ResourceType models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_routing_profiles_extras(self, async_instance: AsyncOFSC):
        """Audit RoutingProfile model (only has profileLabel!)."""
        response = await async_instance.metadata.get_routing_profiles()
        extras = _collect_extras(response)

        item_extras = []
        for rp in response.items[:5]:
            ie = _collect_extras(rp)
            if ie:
                item_extras.extend(ie)

        _save_audit_result(
            "routing_profiles",
            {
                "total_items": len(response.items),
                "response_extras": extras,
                "item_extras": item_extras,
                "sample_item_dict": (
                    response.items[0].model_dump() if response.items else {}
                ),
                "sample_item_extra": (
                    dict(response.items[0].__pydantic_extra__)
                    if response.items and response.items[0].__pydantic_extra__
                    else {}
                ),
            },
        )

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"RoutingProfile models have unmapped fields: {all_extras}")
        # This is expected to fail - RoutingProfile only has profileLabel
        assert not all_extras, (
            f"RoutingProfile models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_shifts_extras(self, async_instance: AsyncOFSC):
        """Audit Shift model."""
        response = await async_instance.metadata.get_shifts()
        extras = _collect_extras(response)

        item_extras = []
        for s in response.items[:5]:
            ie = _collect_extras(s)
            if ie:
                item_extras.extend(ie)

        _save_audit_result(
            "shifts",
            {
                "total_items": len(response.items),
                "response_extras": extras,
                "item_extras": item_extras,
            },
        )

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"Shift models have unmapped fields: {all_extras}")
        assert not all_extras, f"Shift models have unmapped extra fields: {all_extras}"

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_time_slots_extras(self, async_instance: AsyncOFSC):
        """Audit TimeSlot model."""
        response = await async_instance.metadata.get_time_slots()
        extras = _collect_extras(response)

        item_extras = []
        for ts in response.items[:5]:
            ie = _collect_extras(ts)
            if ie:
                item_extras.extend(ie)

        _save_audit_result(
            "time_slots",
            {
                "total_items": len(response.items),
                "response_extras": extras,
                "item_extras": item_extras,
            },
        )

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"TimeSlot models have unmapped fields: {all_extras}")
        assert not all_extras, (
            f"TimeSlot models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_workskills_extras(self, async_instance: AsyncOFSC):
        """Audit Workskill model."""
        response = await async_instance.metadata.get_workskills()
        extras = _collect_extras(response)

        item_extras = []
        for ws in response.items[:5]:
            ie = _collect_extras(ws)
            if ie:
                item_extras.extend(ie)

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"Workskill models have unmapped fields: {all_extras}")
        assert not all_extras, (
            f"Workskill models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_workskill_groups_extras(self, async_instance: AsyncOFSC):
        """Audit WorkskillGroup model (uses extra='ignore')."""
        response = await async_instance.metadata.get_workskill_groups()
        extras = _collect_extras(response)

        item_extras = []
        for wsg in response.items[:5]:
            ie = _collect_extras(wsg)
            if ie:
                item_extras.extend(ie)

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"WorkskillGroup models have unmapped fields: {all_extras}")
        assert not all_extras, (
            f"WorkskillGroup models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_workzones_extras(self, async_instance: AsyncOFSC):
        """Audit Workzone model."""
        response = await async_instance.metadata.get_workzones()
        extras = _collect_extras(response)

        item_extras = []
        for wz in response.items[:5]:
            ie = _collect_extras(wz)
            if ie:
                item_extras.extend(ie)

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"Workzone models have unmapped fields: {all_extras}")
        assert not all_extras, (
            f"Workzone models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_capacity_areas_extras(self, async_instance: AsyncOFSC):
        """Audit CapacityArea model."""
        response = await async_instance.metadata.get_capacity_areas()
        extras = _collect_extras(response)

        item_extras = []
        for ca in response.items[:5]:
            ie = _collect_extras(ca)
            if ie:
                item_extras.extend(ie)

        _save_audit_result(
            "capacity_areas",
            {
                "total_items": len(response.items),
                "response_extras": extras,
                "item_extras": item_extras,
            },
        )

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"CapacityArea models have unmapped fields: {all_extras}")
        assert not all_extras, (
            f"CapacityArea models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_organizations_extras(self, async_instance: AsyncOFSC):
        """Audit Organization model."""
        response = await async_instance.metadata.get_organizations()
        extras = _collect_extras(response)

        item_extras = []
        for org in response.items[:5]:
            ie = _collect_extras(org)
            if ie:
                item_extras.extend(ie)

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"Organization models have unmapped fields: {all_extras}")
        assert not all_extras, (
            f"Organization models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_applications_extras(self, async_instance: AsyncOFSC):
        """Audit Application model."""
        response = await async_instance.metadata.get_applications()
        extras = _collect_extras(response)

        item_extras = []
        for app in response.items[:5]:
            ie = _collect_extras(app)
            if ie:
                item_extras.extend(ie)

        _save_audit_result(
            "applications",
            {
                "total_items": len(response.items),
                "response_extras": extras,
                "item_extras": item_extras,
            },
        )

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"Application models have unmapped fields: {all_extras}")
        assert not all_extras, (
            f"Application models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_link_templates_extras(self, async_instance: AsyncOFSC):
        """Audit LinkTemplate model."""
        response = await async_instance.metadata.get_link_templates()
        extras = _collect_extras(response)

        item_extras = []
        for lt in response.items[:5]:
            ie = _collect_extras(lt)
            if ie:
                item_extras.extend(ie)

        _save_audit_result(
            "link_templates",
            {
                "total_items": len(response.items),
                "response_extras": extras,
                "item_extras": item_extras,
            },
        )

        all_extras = extras + item_extras
        if all_extras:
            logger.warning(f"LinkTemplate models have unmapped fields: {all_extras}")
        assert not all_extras, (
            f"LinkTemplate models have unmapped extra fields: {all_extras}"
        )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_activity_type_features_extras(self, async_instance: AsyncOFSC):
        """Audit ActivityTypeFeatures model specifically.

        This model has 27 boolean fields with extra='allow'.
        The API may return additional feature flags not yet in the model.
        """
        types = await async_instance.metadata.get_activity_types()
        feature_extras = []
        for at in types.items[:10]:
            if at.features:
                ie = _collect_extras(at.features)
                if ie:
                    for entry in ie:
                        entry["activity_type_label"] = at.label
                    feature_extras.extend(ie)

        _save_audit_result(
            "activity_type_features",
            {
                "total_checked": min(10, len(types.items)),
                "extras": feature_extras,
                "defined_fields": list(
                    __import__(
                        "ofsc.models.metadata", fromlist=["ActivityTypeFeatures"]
                    ).ActivityTypeFeatures.model_fields.keys()
                ),
            },
        )

        if feature_extras:
            logger.warning(
                f"ActivityTypeFeatures has unmapped fields: {feature_extras}"
            )
        assert not feature_extras, (
            f"ActivityTypeFeatures has unmapped extra fields: {feature_extras}"
        )
