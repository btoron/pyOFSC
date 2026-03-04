"""Live data round-trip tests for async metadata write operations (issue #138).

Tests cover create → read → update → read → delete cycles for all metadata
entities that support write operations. All test labels are prefixed with TST_
for easy identification and cleanup of test artifacts.

Entities with DELETE support use try/finally for guaranteed cleanup.
Entities without DELETE accumulate TST_ prefixed entries in the instance.
"""

import datetime

import pytest

MINIMAL_FORM_CONTENT = '{"formatVersion":"1.1","items":[]}'

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCAuthorizationError, OFSCNotFoundError
from ofsc.models import (
    ActivityType,
    ActivityTypeGroup,
    CapacityCategory,
    Form,
    InventoryType,
    LinkTemplate,
    MapLayer,
    Property,
    Shift,
    ShiftUpdate,
    Translation,
    TranslationList,
    Workskill,
    WorkskillGroup,
)
from ofsc.models._base import EntityEnum, SharingEnum
from ofsc.models.metadata import LinkTemplateType, ShiftType


def _unique_label(faker, prefix: str, max_len: int = 40) -> str:
    """Generate a unique test label with TST_ prefix."""
    random_part = faker.pystr(min_chars=6, max_chars=8).upper()
    random_part = "".join(c for c in random_part if c.isalnum())[:8]
    label = f"TST_{prefix}_{random_part}"
    return label[:max_len]


def _translation(name: str, language: str = "en") -> TranslationList:
    return TranslationList([Translation(name=name, language=language)])


# ============================================================
# 1. Workskill — PUT create, GET, PUT update, DELETE
# ============================================================


class TestWorkskillRoundtrip:
    """Full CRUD round-trip test for Workskill entity."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_workskill_crud(self, async_instance: AsyncOFSC, faker):
        label = _unique_label(faker, "WS")
        name = faker.sentence(nb_words=3)[:50]
        try:
            # CREATE
            skill = Workskill.model_validate(
                {
                    "label": label,
                    "name": name,
                    "active": True,
                    "sharing": SharingEnum.no_sharing,
                }
            )
            created = await async_instance.metadata.create_or_update_workskill(skill)
            assert isinstance(created, Workskill)
            assert created.label == label

            # READ
            fetched = await async_instance.metadata.get_workskill(label)
            assert fetched.label == label
            assert fetched.name == name

            # UPDATE
            new_name = faker.sentence(nb_words=3)[:50]
            updated_skill = Workskill.model_validate(
                {
                    "label": label,
                    "name": new_name,
                    "active": True,
                    "sharing": SharingEnum.maximal,
                }
            )
            updated = await async_instance.metadata.create_or_update_workskill(
                updated_skill
            )
            assert isinstance(updated, Workskill)

            # READ to verify update
            refetched = await async_instance.metadata.get_workskill(label)
            assert refetched.name == new_name
            assert refetched.sharing == SharingEnum.maximal

        finally:
            try:
                await async_instance.metadata.delete_workskill(label)
            except OFSCNotFoundError:
                pass
            with pytest.raises(OFSCNotFoundError):
                await async_instance.metadata.get_workskill(label)


# ============================================================
# 2. Workskill Group — PUT create, GET, PUT update, DELETE
# ============================================================


class TestWorkskillGroupRoundtrip:
    """Full CRUD round-trip test for WorkskillGroup entity.

    Creates its own dependency workskill inline and cleans up both
    (group first, then workskill) in finally.
    """

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_workskill_group_crud(self, async_instance: AsyncOFSC, faker):
        ws_label = _unique_label(faker, "WS")
        group_label = _unique_label(faker, "WSG")
        group_name = faker.sentence(nb_words=3)[:50]

        # Create dependency workskill first
        dep_skill = Workskill.model_validate(
            {
                "label": ws_label,
                "name": faker.word(),
                "active": True,
                "sharing": SharingEnum.no_sharing,
            }
        )
        await async_instance.metadata.create_or_update_workskill(dep_skill)

        try:
            # CREATE group
            group = WorkskillGroup.model_validate(
                {
                    "label": group_label,
                    "name": group_name,
                    "active": True,
                    "assignToResource": True,
                    "addToCapacityCategory": False,
                    "workSkills": [{"label": ws_label, "ratio": 100}],
                    "translations": [{"language": "en", "name": group_name}],
                }
            )
            created = await async_instance.metadata.create_or_update_workskill_group(
                group
            )
            assert isinstance(created, WorkskillGroup)
            assert created.label == group_label

            # READ
            fetched = await async_instance.metadata.get_workskill_group(group_label)
            assert fetched.label == group_label
            assert fetched.name == group_name

            # UPDATE — change name
            new_name = faker.sentence(nb_words=3)[:50]
            updated_group = WorkskillGroup.model_validate(
                {
                    "label": group_label,
                    "name": new_name,
                    "active": True,
                    "assignToResource": False,
                    "addToCapacityCategory": True,
                    "workSkills": [{"label": ws_label, "ratio": 50}],
                    "translations": [{"language": "en", "name": new_name}],
                }
            )
            updated = await async_instance.metadata.create_or_update_workskill_group(
                updated_group
            )
            assert isinstance(updated, WorkskillGroup)

            # READ to verify update
            refetched = await async_instance.metadata.get_workskill_group(group_label)
            assert refetched.name == new_name

        finally:
            # Delete group first, then dependency workskill
            try:
                await async_instance.metadata.delete_workskill_group(group_label)
            except OFSCNotFoundError:
                pass
            try:
                await async_instance.metadata.delete_workskill(ws_label)
            except OFSCNotFoundError:
                pass
            with pytest.raises(OFSCNotFoundError):
                await async_instance.metadata.get_workskill_group(group_label)
            with pytest.raises(OFSCNotFoundError):
                await async_instance.metadata.get_workskill(ws_label)


# ============================================================
# 3. Capacity Category — PUT create, GET, PUT replace, DELETE
# ============================================================


class TestCapacityCategoryRoundtrip:
    """Full CRUD round-trip test for CapacityCategory entity."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_capacity_category_crud(self, async_instance: AsyncOFSC, faker):
        label = _unique_label(faker, "CC")
        name = faker.sentence(nb_words=3)[:50]
        try:
            # CREATE
            category = CapacityCategory.model_validate(
                {
                    "label": label,
                    "name": name,
                    "active": True,
                    "translations": [{"language": "en", "name": name}],
                }
            )
            created = await async_instance.metadata.create_or_replace_capacity_category(
                category
            )
            assert isinstance(created, CapacityCategory)
            assert created.label == label

            # READ
            fetched = await async_instance.metadata.get_capacity_category(label)
            assert fetched.label == label
            assert fetched.name == name

            # UPDATE (replace)
            new_name = faker.sentence(nb_words=3)[:50]
            replaced = CapacityCategory.model_validate(
                {
                    "label": label,
                    "name": new_name,
                    "active": False,
                    "translations": [{"language": "en", "name": new_name}],
                }
            )
            updated = await async_instance.metadata.create_or_replace_capacity_category(
                replaced
            )
            assert isinstance(updated, CapacityCategory)

            # READ to verify
            refetched = await async_instance.metadata.get_capacity_category(label)
            assert refetched.name == new_name

        finally:
            try:
                await async_instance.metadata.delete_capacity_category(label)
            except OFSCNotFoundError:
                pass
            with pytest.raises(OFSCNotFoundError):
                await async_instance.metadata.get_capacity_category(label)


# ============================================================
# 4. Form — PUT create, GET, PUT replace, DELETE
# ============================================================


class TestFormRoundtrip:
    """Full CRUD round-trip test for Form entity."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_form_crud(self, async_instance: AsyncOFSC, faker):
        label = _unique_label(faker, "FORM")
        name = faker.sentence(nb_words=3)[:50]
        try:
            # CREATE
            form = Form.model_validate(
                {
                    "label": label,
                    "name": name,
                    "content": MINIMAL_FORM_CONTENT,
                    "translations": [{"language": "en", "name": name}],
                }
            )
            created = await async_instance.metadata.create_or_replace_form(form)
            assert isinstance(created, Form)
            assert created.label == label

            # READ
            fetched = await async_instance.metadata.get_form(label)
            assert fetched.label == label
            assert fetched.name == name

            # UPDATE (replace)
            new_name = faker.sentence(nb_words=3)[:50]
            replaced = Form.model_validate(
                {
                    "label": label,
                    "name": new_name,
                    "content": MINIMAL_FORM_CONTENT,
                    "translations": [{"language": "en", "name": new_name}],
                }
            )
            updated = await async_instance.metadata.create_or_replace_form(replaced)
            assert isinstance(updated, Form)

            # READ to verify
            refetched = await async_instance.metadata.get_form(label)
            assert refetched.name == new_name

        finally:
            try:
                await async_instance.metadata.delete_form(label)
            except OFSCNotFoundError:
                pass
            with pytest.raises(OFSCNotFoundError):
                await async_instance.metadata.get_form(label)


# ============================================================
# 5. Shift — PUT create, GET, PUT replace, DELETE
# ============================================================


class TestShiftRoundtrip:
    """Full CRUD round-trip test for Shift entity."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_shift_crud(self, async_instance: AsyncOFSC, faker):
        label = _unique_label(faker, "SHF")
        name = faker.sentence(nb_words=3)[:50]
        try:
            # CREATE
            shift = Shift.model_validate(
                {
                    "label": label,
                    "name": name,
                    "active": True,
                    "type": ShiftType.regular,
                    "workTimeStart": "08:00:00",
                    "workTimeEnd": "17:00:00",
                }
            )
            created = await async_instance.metadata.create_or_replace_shift(shift)
            assert isinstance(created, Shift)
            assert created.label == label

            # READ
            fetched = await async_instance.metadata.get_shift(label)
            assert fetched.label == label
            assert fetched.name == name
            assert fetched.workTimeStart == datetime.time(8, 0, 0)
            assert fetched.workTimeEnd == datetime.time(17, 0, 0)

            # UPDATE (replace with new times) — omit 'type' as it cannot be changed
            new_name = faker.sentence(nb_words=3)[:50]
            replaced = ShiftUpdate.model_validate(
                {
                    "label": label,
                    "name": new_name,
                    "active": True,
                    "workTimeStart": "09:00:00",
                    "workTimeEnd": "18:00:00",
                }
            )
            updated = await async_instance.metadata.create_or_replace_shift(replaced)
            assert isinstance(updated, Shift)

            # READ to verify
            refetched = await async_instance.metadata.get_shift(label)
            assert refetched.name == new_name
            assert refetched.workTimeStart == datetime.time(9, 0, 0)

        finally:
            try:
                await async_instance.metadata.delete_shift(label)
            except OFSCNotFoundError:
                pass
            with pytest.raises(OFSCNotFoundError):
                await async_instance.metadata.get_shift(label)


# ============================================================
# 6. Activity Type Group — PUT create, GET, PUT replace
#    (no delete endpoint)
# ============================================================


class TestActivityTypeGroupRoundtrip:
    """Round-trip test for ActivityTypeGroup entity (no delete available)."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_activity_type_group_create_read_update(
        self, async_instance: AsyncOFSC, faker
    ):
        label = _unique_label(faker, "ATG")
        name = faker.sentence(nb_words=3)[:50]

        # CREATE
        atg = ActivityTypeGroup.model_validate(
            {
                "label": label,
                "name": name,
                "translations": [{"language": "en", "name": name}],
            }
        )
        created = await async_instance.metadata.create_or_replace_activity_type_group(
            atg
        )
        assert isinstance(created, ActivityTypeGroup)
        assert created.label == label

        # READ
        fetched = await async_instance.metadata.get_activity_type_group(label)
        assert fetched.label == label
        assert fetched.name == name

        # UPDATE (replace)
        new_name = faker.sentence(nb_words=3)[:50]
        replaced = ActivityTypeGroup.model_validate(
            {
                "label": label,
                "name": new_name,
                "translations": [{"language": "en", "name": new_name}],
            }
        )
        updated = await async_instance.metadata.create_or_replace_activity_type_group(
            replaced
        )
        assert isinstance(updated, ActivityTypeGroup)

        # READ to verify
        refetched = await async_instance.metadata.get_activity_type_group(label)
        assert refetched.name == new_name


# ============================================================
# 7. Activity Type — PUT create, GET, PUT replace
#    (no delete endpoint; requires groupLabel)
# ============================================================


class TestActivityTypeRoundtrip:
    """Round-trip test for ActivityType entity (no delete available).

    Creates an inline ActivityTypeGroup dependency to satisfy the mandatory
    groupLabel field.
    """

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_activity_type_create_read_update(
        self, async_instance: AsyncOFSC, faker
    ):
        atg_label = _unique_label(faker, "ATG")
        label = _unique_label(faker, "AT")
        name = faker.sentence(nb_words=3)[:50]

        # Create dependency ActivityTypeGroup inline
        atg = ActivityTypeGroup.model_validate(
            {
                "label": atg_label,
                "name": faker.sentence(nb_words=3)[:50],
                "translations": [{"language": "en", "name": faker.word()}],
            }
        )
        await async_instance.metadata.create_or_replace_activity_type_group(atg)

        # CREATE
        at = ActivityType.model_validate(
            {
                "label": label,
                "name": name,
                "active": True,
                "defaultDuration": 60,
                "groupLabel": atg_label,
                "translations": [{"language": "en", "name": name}],
            }
        )
        created = await async_instance.metadata.create_or_replace_activity_type(at)
        assert isinstance(created, ActivityType)
        assert created.label == label

        # READ
        fetched = await async_instance.metadata.get_activity_type(label)
        assert fetched.label == label
        assert fetched.name == name
        assert fetched.defaultDuration == 60

        # UPDATE (replace)
        new_name = faker.sentence(nb_words=3)[:50]
        replaced = ActivityType.model_validate(
            {
                "label": label,
                "name": new_name,
                "active": True,
                "defaultDuration": 90,
                "groupLabel": atg_label,
                "translations": [{"language": "en", "name": new_name}],
            }
        )
        updated = await async_instance.metadata.create_or_replace_activity_type(
            replaced
        )
        assert isinstance(updated, ActivityType)

        # READ to verify
        refetched = await async_instance.metadata.get_activity_type(label)
        assert refetched.name == new_name
        assert refetched.defaultDuration == 90


# ============================================================
# 8. Inventory Type — PUT create, GET, PUT replace
#    (no delete endpoint; may require elevated permissions)
# ============================================================


class TestInventoryTypeRoundtrip:
    """Round-trip test for InventoryType entity (no delete available)."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_inventory_type_create_read_update(
        self, async_instance: AsyncOFSC, faker
    ):
        label = _unique_label(faker, "IT")
        name = faker.word()[:30]

        # CREATE — may fail with 403 if account lacks write permissions
        try:
            inv_type = InventoryType.model_validate(
                {
                    "label": label,
                    "active": True,
                    "translations": [{"language": "en", "name": name}],
                }
            )
            created = await async_instance.metadata.create_or_replace_inventory_type(
                inv_type
            )
        except OFSCAuthorizationError:
            pytest.skip("Test account lacks write permissions for inventory types")

        assert isinstance(created, InventoryType)
        assert created.label == label

        # READ
        fetched = await async_instance.metadata.get_inventory_type(label)
        assert fetched.label == label
        assert fetched.active is True

        # UPDATE (replace — change active status)
        new_name = faker.word()[:30]
        replaced = InventoryType.model_validate(
            {
                "label": label,
                "active": False,
                "translations": [{"language": "en", "name": new_name}],
            }
        )
        updated = await async_instance.metadata.create_or_replace_inventory_type(
            replaced
        )
        assert isinstance(updated, InventoryType)

        # READ to verify
        refetched = await async_instance.metadata.get_inventory_type(label)
        assert refetched.active is False


# ============================================================
# 9. Map Layer — POST create, GET, PUT replace
#    (no delete endpoint; label max 24 chars, ^[A-Za-z0-9_]+$)
# ============================================================


class TestMapLayerRoundtrip:
    """Round-trip test for MapLayer entity (no delete available).

    Label constraint: max 24 chars, pattern ^[A-Za-z0-9_]+$.
    Uses POST create_map_layer for initial creation, then PUT for update.
    """

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_map_layer_create_read_update(self, async_instance: AsyncOFSC, faker):
        label = _unique_label(faker, "ML", max_len=24)
        name = faker.sentence(nb_words=3)[:50]

        # CREATE via PUT (idempotent — no DELETE endpoint exists)
        layer = MapLayer.model_validate(
            {
                "label": label,
                "status": "active",
                "translations": [{"language": "en", "name": name}],
            }
        )
        created = await async_instance.metadata.create_map_layer(layer)
        assert isinstance(created, MapLayer)
        assert created.label == label

        # READ
        fetched = await async_instance.metadata.get_map_layer(label)
        assert fetched.label == label

        # UPDATE via PUT (replace)
        new_name = faker.sentence(nb_words=3)[:50]
        replaced = MapLayer.model_validate(
            {
                "label": label,
                "status": "inactive",
                "translations": [{"language": "en", "name": new_name}],
            }
        )
        updated = await async_instance.metadata.create_or_replace_map_layer(replaced)
        assert isinstance(updated, MapLayer)

        # READ to verify
        refetched = await async_instance.metadata.get_map_layer(label)
        assert refetched.label == label


# ============================================================
# 10. Property — PUT create, GET, PATCH update
#     (no delete endpoint)
# ============================================================


class TestPropertyRoundtrip:
    """Round-trip test for Property entity (no delete available).

    Uses PUT create_or_replace_property and PATCH update_property.
    """

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_property_create_read_update(self, async_instance: AsyncOFSC, faker):
        label = _unique_label(faker, "PROP")
        name = faker.sentence(nb_words=3)[:50]

        # CREATE
        prop = Property.model_validate(
            {
                "label": label,
                "name": name,
                "type": "string",
                "entity": EntityEnum.activity,
                "gui": "text",
            }
        )
        created = await async_instance.metadata.create_or_replace_property(prop)
        assert isinstance(created, Property)
        assert created.label == label

        # READ
        fetched = await async_instance.metadata.get_property(label)
        assert fetched.label == label
        assert fetched.name == name
        assert fetched.type == "string"

        # UPDATE via PATCH
        new_name = faker.sentence(nb_words=3)[:50]
        patch_prop = Property.model_validate(
            {
                "label": label,
                "name": new_name,
                "type": "string",
                "entity": EntityEnum.activity,
                "gui": "text",
            }
        )
        updated = await async_instance.metadata.update_property(patch_prop)
        assert isinstance(updated, Property)

        # READ to verify
        refetched = await async_instance.metadata.get_property(label)
        assert refetched.name == new_name


# ============================================================
# 11. Link Template — POST create, GET, PATCH update
#     (no delete endpoint; POST is not idempotent)
# ============================================================


class TestLinkTemplateRoundtrip:
    """Round-trip test for LinkTemplate entity (no delete available).

    Uses POST create_link_template and PATCH update_link_template.
    """

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_link_template_create_read_update(
        self, async_instance: AsyncOFSC, faker
    ):
        label = _unique_label(faker, "LT")
        name = faker.sentence(nb_words=3)[:50]

        # CREATE
        link = LinkTemplate.model_validate(
            {
                "label": label,
                "active": True,
                "linkType": LinkTemplateType.related,
                "translations": [{"language": "en", "name": name}],
            }
        )
        created = await async_instance.metadata.create_link_template(link)
        assert isinstance(created, LinkTemplate)
        assert created.label == label
        assert created.linkType == LinkTemplateType.related

        # READ
        fetched = await async_instance.metadata.get_link_template(label)
        assert fetched.label == label
        assert fetched.active is True

        # UPDATE via PATCH
        new_name = faker.sentence(nb_words=3)[:50]
        patch_link = LinkTemplate.model_validate(
            {
                "label": label,
                "active": False,
                "linkType": LinkTemplateType.related,
                "translations": [{"language": "en", "name": new_name}],
            }
        )
        updated = await async_instance.metadata.update_link_template(patch_link)
        assert isinstance(updated, LinkTemplate)

        # READ to verify
        refetched = await async_instance.metadata.get_link_template(label)
        assert refetched.active is False
