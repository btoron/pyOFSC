# REQUIREMENTS TO TEST MAPPING

**Project:** pyOFSC - Python wrapper for Oracle Field Service Cloud (OFSC) REST API
**Version:** 2.24.0
**Report Date:** 2026-03-04
**Derived from:** ENDPOINTS.md, source code inspection, and test suite analysis

---

## Overview

This document maps functional requirements (derived from the OFSC API endpoint coverage in `docs/ENDPOINTS.md`) to specific test functions in the test suite.

Requirements are organized by OFSC API module and use the Endpoint ID format from ENDPOINTS.md (e.g., `CO001G` = Core, endpoint 001, GET method).

**Legend:**
- MOCKED = Test uses AsyncMock/Mock, no API credentials needed
- LIVE = Test marked `@pytest.mark.uses_real_data`, requires API credentials
- INTEGRATION = Test marked `@pytest.mark.integration`, requires API credentials (but lacks `uses_real_data` marker)
- SKIP = Test exists but calls `pytest.skip()` unconditionally
- NONE = No test exists for this requirement

---

## Module: Metadata API (`/rest/ofscMetadata/v1/`)

### Workzones

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| ME055G | GET /workZones (list) | `TestAsyncGetWorkzones::test_get_workzones_with_model` | MOCKED | `tests/async/test_async_workzones.py` |
| ME055G | GET /workZones (list) | `TestAsyncGetWorkzones::test_get_workzones_pagination` | MOCKED | `tests/async/test_async_workzones.py` |
| ME055G | GET /workZones (list) | `TestAsyncGetWorkzones::test_get_workzones_total_results` | MOCKED | `tests/async/test_async_workzones.py` |
| ME055G | GET /workZones (list) | `TestAsyncGetWorkzonesLive::test_get_workzones` | LIVE | `tests/async/test_async_workzones.py` |
| ME056G | GET /workZones/{label} | `TestAsyncGetWorkzone::test_get_workzone` | MOCKED | `tests/async/test_async_workzones.py` |
| ME056G | GET /workZones/{label} | `TestAsyncGetWorkzone::test_get_workzone_details` | MOCKED | `tests/async/test_async_workzones.py` |
| ME056U | PUT /workZones/{label} | `TestUpdateWorkzones::test_update_returns_list_response` | MOCKED | `tests/async/test_async_metadata_write.py` |
| ME056U | PUT /workZones/{label} | `TestUpdateWorkzones::test_update_uses_patch_method` | MOCKED | `tests/async/test_async_metadata_write.py` |
| ME055P | POST /workZones | `TestReplaceWorkzones::test_replace_sends_items_body` | MOCKED | `tests/async/test_async_metadata_write.py` |
| ME055U | PUT /workZones | `TestReplaceWorkzones::test_replace_workzones_returns_list_response` | MOCKED | `tests/async/test_async_metadata_write.py` |
| ME059G | GET /workZoneKey | `TestAsyncGetWorkzoneKey::test_returns_correct_model` | MOCKED | `tests/async/test_async_workzones.py` |
| ME059G | GET /workZoneKey | `TestAsyncGetWorkzoneKey::test_with_pending_key` | MOCKED | `tests/async/test_async_workzones.py` |
| ME059G | GET /workZoneKey | `TestAsyncGetWorkzoneKey::test_without_pending` | MOCKED | `tests/async/test_async_workzones.py` |
| ME059G | GET /workZoneKey | `TestAsyncGetWorkzoneKey::test_optional_fields` | MOCKED | `tests/async/test_async_workzones.py` |

### Properties

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| ME037G | GET /properties (list) | `TestAsyncGetProperties::test_get_properties_with_model` | MOCKED | `tests/async/test_async_properties.py` |
| ME037G | GET /properties (list) | `TestAsyncGetProperties::test_get_properties_pagination` | MOCKED | `tests/async/test_async_properties.py` |
| ME038G | GET /properties/{label} | `TestAsyncGetProperty::test_get_property` | MOCKED | `tests/async/test_async_properties.py` |
| ME038G | GET /properties/{label} | `TestAsyncGetProperty::test_get_property_details` | MOCKED | `tests/async/test_async_properties.py` |
| ME038G | GET /properties/{label} | `TestAsyncGetProperty::test_get_property_not_found` | MOCKED | `tests/async/test_async_properties.py` |
| ME038U | PUT /properties/{label} | `TestUpdateProperty::test_update_returns_model` | MOCKED | `tests/async/test_async_metadata_write.py` |
| ME038U | PUT /properties/{label} | `TestUpdateProperty::test_update_uses_patch_method` | MOCKED | `tests/async/test_async_metadata_write.py` |
| ME039G | GET /properties/{label}/enumerationList | `TestAsyncGetEnumerationValues::test_get_enumeration_values` | MOCKED | `tests/async/test_async_properties.py` |
| ME039G | GET /properties/{label}/enumerationList | `TestAsyncGetEnumerationValues::test_get_enumeration_values_pagination` | MOCKED | `tests/async/test_async_properties.py` |
| ME039U | PUT /properties/{label}/enumerationList | `TestAsyncCreateOrUpdateEnumerationValue::test_country_code_property_cannot_be_updated` | MOCKED | `tests/async/test_async_properties.py` |

### Activity Types

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| ME003G | GET /activityTypes (list) | `TestAsyncGetActivityTypes::test_get_activity_types_with_model` | MOCKED | `tests/async/test_async_activity_types.py` |
| ME003G | GET /activityTypes (list) | `TestAsyncGetActivityTypes::test_get_activity_types_pagination` | MOCKED | `tests/async/test_async_activity_types.py` |
| ME003G | GET /activityTypes (list) | `TestAsyncGetActivityTypes::test_get_activity_types_total_results` | MOCKED | `tests/async/test_async_activity_types.py` |
| ME003G | GET /activityTypes (list) | `TestAsyncGetActivityTypes::test_get_activity_types_field_types` | MOCKED | `tests/async/test_async_activity_types.py` |
| ME004G | GET /activityTypes/{label} | `TestAsyncActivityTypeSavedResponses::test_activity_type_single_response_validation` | MOCKED | `tests/async/test_async_activity_types.py` |
| ME004U | PUT /activityTypes/{label} | NONE | - | - |

### Activity Type Groups

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| ME001G | GET /activityTypeGroups (list) | `TestAsyncGetActivityTypeGroups::test_get_activity_type_groups_with_model` | MOCKED | `tests/async/test_async_activity_type_groups.py` |
| ME001G | GET /activityTypeGroups (list) | `TestAsyncGetActivityTypeGroups::test_get_activity_type_groups_pagination` | MOCKED | `tests/async/test_async_activity_type_groups.py` |
| ME002G | GET /activityTypeGroups/{label} | `TestAsyncActivityTypeGroupSavedResponses::test_activity_type_group_list_response_validation` | MOCKED | `tests/async/test_async_activity_type_groups.py` |
| ME002U | PUT /activityTypeGroups/{label} | NONE | - | - |

### Capacity Areas

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| ME010G | GET /capacityAreas (list) | `TestAsyncGetCapacityAreas::test_get_capacity_areas_returns_model` | MOCKED | `tests/async/test_async_capacity_areas.py` |
| ME010G | GET /capacityAreas (list) | `TestAsyncGetCapacityAreas::test_get_capacity_areas_pagination` | MOCKED | `tests/async/test_async_capacity_areas.py` |
| ME011G | GET /capacityAreas/{label} | `TestAsyncGetCapacityArea::test_get_capacity_area_returns_model` | MOCKED | `tests/async/test_async_capacity_areas.py` |
| ME012G | GET /capacityAreas/{label}/capacityCategories | `TestAsyncGetCapacityAreaCapacityCategories::test_returns_correct_model` | MOCKED | `tests/async/test_async_capacity_areas.py` |
| ME013G | GET /capacityAreas/{label}/workZones (v2) | `TestAsyncGetCapacityAreaWorkzonesV2::test_iterable` | MOCKED | `tests/async/test_async_capacity_areas.py` |
| ME014G | GET /capacityAreas/{label}/workZones (v1) | `TestAsyncGetCapacityAreaWorkzonesV1::test_iterable` | MOCKED | `tests/async/test_async_capacity_areas.py` |
| ME015G | GET /capacityAreas/{label}/timeSlots | `TestAsyncGetCapacityAreaTimeSlots::test_returns_correct_model` | MOCKED | `tests/async/test_async_capacity_areas.py` |
| ME016G | GET /capacityAreas/{label}/timeIntervals | `TestAsyncGetCapacityAreaTimeIntervals::test_iterable` | MOCKED | `tests/async/test_async_capacity_areas.py` |
| ME017G | GET /capacityAreas/{label}/organizations | `TestAsyncGetCapacityAreaOrganizations::test_returns_correct_model` | MOCKED | `tests/async/test_async_capacity_areas.py` |
| ME018G | GET /capacityAreas/{label}/children | `TestAsyncGetCapacityAreaChildren::test_returns_correct_model` | MOCKED | `tests/async/test_async_capacity_areas.py` |

### Capacity Categories

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| ME019G | GET /capacityCategories (list) | `TestAsyncGetCapacityCategories::test_get_capacity_categories_with_model` | MOCKED | `tests/async/test_async_capacity_categories.py` |
| ME020G | GET /capacityCategories/{label} | `TestAsyncGetCapacityCategory::test_get_capacity_category_returns_model` | MOCKED | `tests/async/test_async_capacity_categories.py` |
| ME020U | PUT /capacityCategories/{label} | `TestAsyncUpdateCapacityCategory::test_update_returns_model` | MOCKED | `tests/async/test_async_capacity_categories.py` |
| ME020D | DELETE /capacityCategories/{label} | `TestAsyncDeleteCapacityCategory::test_delete_returns_none` | MOCKED | `tests/async/test_async_capacity_categories.py` |

### Organizations

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| ME033G | GET /organizations (list) | `TestAsyncGetOrganizations::test_get_organizations_with_model` | MOCKED | `tests/async/test_async_organizations.py` |
| ME033G | GET /organizations (list) | `TestAsyncGetOrganizations::test_get_organizations_pagination` | MOCKED | `tests/async/test_async_organizations.py` |
| ME034G | GET /organizations/{label} | `TestAsyncOrganizationSavedResponses::test_organization_single_response_validation` | MOCKED | `tests/async/test_async_organizations.py` |

### Applications

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| ME005G | GET /applications (list) | `TestAsyncGetApplicationsModel::test_get_applications_returns_model` | MOCKED | `tests/async/test_async_applications.py` |
| ME006G | GET /applications/{label} | `TestAsyncGetApplicationModel::test_get_application_returns_model` | MOCKED | `tests/async/test_async_applications.py` |
| ME007G | GET /applications/{label}/apiAccess | `TestAsyncGetApplicationApiAccesses::test_get_api_accesses_returns_model` | MOCKED | `tests/async/test_async_applications.py` |
| ME008G | GET /applications/{label}/apiAccess/{apiLabel} | `TestAsyncGetApplicationApiAccess::test_get_api_access_returns_model` | MOCKED | `tests/async/test_async_applications.py` |
| ME006U | PUT /applications/{label} | NONE | - | - |
| ME008A | PATCH /applications/{label}/apiAccess/{apiLabel} | NONE | - | - |
| ME009P | POST /applications/{label}/custom-actions/generateClientSecret | NONE | - | - |

### Routing Profiles

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| ME041G | GET /routingProfiles (list) | `TestAsyncGetRoutingProfiles::test_get_routing_profiles_with_model` | MOCKED | `tests/async/test_async_routing_profiles.py` |
| ME042G | GET /routingProfiles/{label}/plans | `TestAsyncGetRoutingProfilePlans::test_get_routing_profile_plans_with_model` | MOCKED | `tests/async/test_async_routing_profiles.py` |
| ME043G | GET /routingProfiles/{label}/plans/{planLabel}/export | `TestAsyncExportRoutingPlan::test_export_routing_plan_returns_bytes` | MOCKED | `tests/async/test_async_routing_profiles.py` |
| ME044U | PUT /routingProfiles/{label}/plans/import | `TestAsyncRoutingProfileSavedResponses::test_import_routing_plan_validation` | MOCKED | `tests/async/test_async_routing_profiles.py` |
| ME045U | PUT /routingProfiles/{label}/plans/forceImport | `TestAsyncRoutingProfileSavedResponses::test_force_import_routing_plan_validation` | MOCKED | `tests/async/test_async_routing_profiles.py` |
| ME046P | POST .../start | LIVE tests only | LIVE | `tests/async/test_async_routing_profiles.py` |

### Workskills

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| ME053G | GET /workSkills (list) | `TestAsyncGetWorkskills::test_get_workskills_with_model` | MOCKED | `tests/async/test_async_workskills.py` |
| ME054G | GET /workSkills/{label} | `TestAsyncGetWorkskill::test_get_workskill_returns_model` | MOCKED | `tests/async/test_async_workskills.py` |
| ME054U | PUT /workSkills/{label} | `TestAsyncUpdateWorkskill::test_update_workskill_returns_model` | MOCKED | `tests/async/test_async_workskills.py` |
| ME054D | DELETE /workSkills/{label} | `TestAsyncDeleteWorkskill::test_delete_workskill_returns_none` | MOCKED | `tests/async/test_async_workskills.py` |
| ME051G | GET /workSkillGroups (list) | `TestAsyncGetWorkskillGroups::test_get_workskill_groups_with_model` | MOCKED | `tests/async/test_async_workskills.py` |
| ME052G | GET /workSkillGroups/{label} | `TestAsyncGetWorkskillGroup::test_get_workskill_group_returns_model` | MOCKED | `tests/async/test_async_workskills.py` |
| ME052U | PUT /workSkillGroups/{label} | `TestAsyncUpdateWorkskillGroup::test_update_workskill_group_returns_model` | MOCKED | `tests/async/test_async_workskills.py` |
| ME052D | DELETE /workSkillGroups/{label} | `TestAsyncDeleteWorkskillGroup::test_delete_workskill_group_returns_none` | MOCKED | `tests/async/test_async_workskills.py` |

### Plugins, Forms, Shifts, Time Slots, Languages, Link Templates, Map Layers, Non-Working Reasons

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| ME035P | POST /plugins/import | `TestAsyncImportPluginFileMock::test_import_plugin_file_success` | MOCKED | `tests/async/test_async_plugins.py` |
| ME021G | GET /forms (list) | `TestAsyncGetForms::test_get_forms_with_model` | MOCKED | `tests/async/test_async_forms.py` |
| ME022G | GET /forms/{label} | `TestAsyncGetForm::test_get_form_returns_model` | MOCKED | `tests/async/test_async_forms.py` |
| ME022U | PUT /forms/{label} | `TestAsyncUpdateForm::test_update_returns_model` | MOCKED | `tests/async/test_async_forms.py` |
| ME022D | DELETE /forms/{label} | `TestAsyncDeleteForm::test_delete_returns_none` | MOCKED | `tests/async/test_async_forms.py` |
| ME047G | GET /shifts (list) | `TestAsyncGetShiftsModel::test_get_shifts_returns_model` | MOCKED | `tests/async/test_async_shifts.py` |
| ME048G | GET /shifts/{label} | LIVE tests only | LIVE | `tests/async/test_async_shifts.py` |
| ME048U | PUT /shifts/{label} | LIVE tests only | LIVE | `tests/async/test_async_shifts.py` |
| ME048D | DELETE /shifts/{label} | LIVE tests only | LIVE | `tests/async/test_async_shifts.py` |
| ME049G | GET /timeSlots (list) | `TestAsyncGetTimeSlots::test_get_time_slots_with_model` | MOCKED | `tests/async/test_async_time_slots.py` |
| ME025G | GET /languages (list) | `TestAsyncGetLanguages::test_get_languages_with_model` | MOCKED | `tests/async/test_async_languages.py` |
| ME026G | GET /linkTemplates (list) | `TestAsyncGetLinkTemplates::test_get_link_templates_with_model` | MOCKED | `tests/async/test_async_link_templates.py` |
| ME027G | GET /linkTemplates/{label} | LIVE tests only | LIVE | `tests/async/test_async_link_templates.py` |
| ME028G | GET /mapLayers (list) | `TestAsyncGetMapLayers::test_get_map_layers_with_model` | MOCKED | `tests/async/test_async_map_layers.py` |
| ME030G | GET /mapLayers/populateLayers/{downloadId} | `TestAsyncGetPopulateMapLayersStatus::test_returns_correct_model` | MOCKED | `tests/async/test_async_populate_status.py` |
| ME031P | POST /mapLayers/populateLayers | `TestAsyncPopulateLayers::test_returns_model` | MOCKED | `tests/async/test_async_map_layers.py` |
| ME032G | GET /nonWorkingReasons (list) | `TestAsyncGetNonWorkingReasons::test_get_non_working_reasons_with_model` | MOCKED | `tests/async/test_async_non_working_reasons.py` |

### Inventory Types

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| ME023G | GET /inventoryTypes (list) | `TestAsyncGetInventoryTypes::test_get_inventory_types_with_model` | MOCKED | `tests/async/test_async_inventory_types.py` |
| ME024G | GET /inventoryTypes/{label} | `TestAsyncInventoryTypeSavedResponses::test_inventory_type_single_response_validation` | MOCKED | `tests/async/test_async_inventory_types.py` |
| ME024U | PUT /inventoryTypes/{label} | LIVE tests only | LIVE | `tests/async/test_async_inventory_types.py` |

### Resource Types

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| ME040G | GET /resourceTypes (list) | `TestAsyncGetResourceTypes::test_get_resource_types_returns_model` | MOCKED | `tests/async/test_async_resource_types.py` |

---

## Module: Core API (`/rest/ofscCore/v1/`)

### Activities

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| CO001G | GET /activities (list) | `TestAsyncGetActivities::test_get_activities_returns_model` | SKIP | `tests/async/test_async_activities.py` |
| CO001G | GET /activities (list) | `TestAsyncGetActivities::test_get_activities_pagination` | SKIP | `tests/async/test_async_activities.py` |
| CO001G | GET /activities (list) | `TestAsyncGetActivitiesLive::test_get_activities` | LIVE | `tests/async/test_async_activities.py` |
| CO001P | POST /activities | `TestAsyncCreateActivity::test_create_and_delete_activity` | LIVE | `tests/async/test_async_activities.py` |
| CO001P | POST /activities | `TestAsyncCreateActivity::test_create_activity_returns_activity_model` | LIVE | `tests/async/test_async_activities.py` |
| CO002G | GET /activities/{activityId} | `TestAsyncGetActivityLive::test_get_activity` | LIVE | `tests/async/test_async_activities.py` |
| CO002A | PATCH /activities/{activityId} | `TestAsyncUpdateActivity::test_update_activity` | LIVE | `tests/async/test_async_activities.py` |
| CO002A | PATCH /activities/{activityId} | `TestAsyncUpdateActivity::test_update_activity_not_found` | LIVE | `tests/async/test_async_activities.py` |
| CO002D | DELETE /activities/{activityId} | `TestAsyncDeleteActivity::test_delete_activity_not_found` | LIVE | `tests/async/test_async_activities.py` |
| CO003G | GET /activities/{activityId}/multidaySegments | `test_get_multiday_segments` | MOCKED | `tests/async/test_async_activities.py` |
| CO005G | GET /activities/{activityId}/submittedForms | `TestAsyncGetSubmittedFormsLive::test_get_submitted_forms` | LIVE | `tests/async/test_async_activities.py` |
| CO006G | GET /activities/{activityId}/resourcePreferences | `TestAsyncGetResourcePreferencesLive::test_get_resource_preferences` | LIVE | `tests/async/test_async_activities.py` |
| CO007G | GET /activities/{activityId}/requiredInventories | `TestAsyncGetRequiredInventoriesLive::test_get_required_inventories` | LIVE | `tests/async/test_async_activities.py` |
| CO008G | GET /activities/{activityId}/customerInventories | `TestAsyncGetCustomerInventoriesLive::test_get_customer_inventories` | LIVE | `tests/async/test_async_activities.py` |
| CO009G | GET /activities/{activityId}/installedInventories | `TestAsyncGetInstalledInventoriesLive::test_get_installed_inventories` | LIVE | `tests/async/test_async_activities.py` |
| CO010G | GET /activities/{activityId}/deinstalledInventories | `TestAsyncGetDeinstalledInventoriesLive::test_get_deinstalled_inventories` | LIVE | `tests/async/test_async_activities.py` |
| CO011G | GET /activities/{activityId}/linkedActivities | `TestAsyncLinkedActivities::test_get_linked_activities` | MOCKED | `tests/async/test_async_activities.py` |
| CO012G | GET /activities/{activityId}/capacityCategories | `TestAsyncGetCapacityCategoriesLive::test_get_capacity_categories` | LIVE | `tests/async/test_async_activities.py` |
| CO014G | GET /activities/search | NONE | - | - |
| CO015P | POST /activities/bulkUpdate | NONE | - | - |
| CO024P | POST /activities/{id}/move | NONE | - | - |

### Resources

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| CO041G | GET /resources (list) | `TestAsyncGetResources::test_get_resources_returns_model` | MOCKED | `tests/async/test_async_resources_get.py` |
| CO041G | GET /resources (list) | `TestAsyncGetResources::test_get_resources_returns_model` | MOCKED | `tests/async/test_async_resources_get.py` |
| CO045G | GET /resources/{resourceId} | `TestAsyncGetResource::test_get_resource_returns_model` | MOCKED | `tests/async/test_async_resources_get.py` |
| CO042G | GET /resources/{id}/children | `TestAsyncGetResourceChildren::test_get_resource_children_returns_model` | MOCKED | `tests/async/test_async_resources_get.py` |
| CO043G | GET /resources/{id}/descendants | `TestAsyncGetResourceDescendants::test_get_resource_descendants_returns_model` | MOCKED | `tests/async/test_async_resources_get.py` |
| CO044G | GET /resources/{id}/assistants | `TestAsyncGetResourceAssistants::test_get_resource_assistants_returns_model` | MOCKED | `tests/async/test_async_resources_get.py` |
| CO046G | GET /resources/{id}/users | `TestAsyncGetResourceUsers::test_get_resource_users_returns_model` | MOCKED | `tests/async/test_async_resources_get.py` |
| CO049G | GET /resources/{id}/workSkills | `TestAsyncGetResourceWorkskills::test_get_resource_workskills_returns_model` | MOCKED | `tests/async/test_async_resources_get.py` |
| CO051G | GET /resources/{id}/workZones | `TestAsyncGetResourceWorkzones::test_get_resource_workzones_returns_model` | MOCKED | `tests/async/test_async_resources_get.py` |
| CO053G | GET /resources/{id}/workSchedules | `TestAsyncGetResourceWorkschedules::test_get_resource_workschedules_returns_model` | MOCKED | `tests/async/test_async_resources_get.py` |
| CO055G | GET /resources/{id}/workSchedules/calendarView | `TestAsyncGetResourceCalendar::test_get_resource_calendar_returns_model` | MOCKED | `tests/async/test_async_resources_get.py` |
| CO045U | PUT /resources/{id} | `TestAsyncUpdateResource::test_update_resource_returns_resource` | MOCKED | `tests/async/test_async_resources_write.py` |
| CO045A | PATCH /resources/{id} | LIVE tests only | LIVE | `tests/async/test_async_resources_write.py` |
| CO046U | PUT /resources/{id}/users | `TestAsyncSetResourceUsers::test_set_resource_users_returns_response` | MOCKED | `tests/async/test_async_resources_write.py` |
| CO046D | DELETE /resources/{id}/users | `TestAsyncSetDeleteResourceUsers::test_delete_resource_users_returns_none` | MOCKED | `tests/async/test_async_resources_write.py` |
| CO053P | POST /resources/{id}/workSchedules | `TestAsyncSetResourceWorkschedules::test_set_resource_workschedules_returns_response` | MOCKED | `tests/async/test_async_resources_write.py` |
| CO068P | POST /resources/bulkUpdateWorkSchedules | `TestAsyncBulkUpdateResourceWorkschedules::test_bulk_update_returns_response` | MOCKED | `tests/async/test_async_resources_write.py` |
| CO069P | POST /resources/bulkUpdateWorkSkills | `TestAsyncBulkUpdateResourceWorkskills::test_bulk_update_returns_response` | MOCKED | `tests/async/test_async_resources_write.py` |
| CO070P | POST /resources/bulkUpdateWorkZones | `TestAsyncBulkUpdateResourceWorkzones::test_bulk_update_returns_response` | MOCKED | `tests/async/test_async_resources_write.py` |

### Users

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| CO080G | GET /users (list) | `TestAsyncGetUsers::test_get_users_returns_model` | MOCKED | `tests/async/test_async_users.py` |
| CO081G | GET /users/{login} | `TestAsyncGetUser::test_get_user_returns_model` | MOCKED | `tests/async/test_async_users.py` |
| CO081U | PUT /users/{login} | LIVE tests only | LIVE | `tests/async/test_async_users.py` |
| CO081A | PATCH /users/{login} | LIVE tests only | LIVE | `tests/async/test_async_users.py` |
| CO081D | DELETE /users/{login} | LIVE tests only | LIVE | `tests/async/test_async_users.py` |
| CO082G | GET /users/{login}/{propertyLabel} | `TestAsyncUserFileProperty::test_get_user_property_returns_bytes` | MOCKED | `tests/async/test_async_users.py` |
| CO082U | PUT /users/{login}/{propertyLabel} | `TestAsyncUserFileProperty::test_set_user_property_returns_none` | MOCKED | `tests/async/test_async_users.py` |
| CO082D | DELETE /users/{login}/{propertyLabel} | `TestAsyncUserFileProperty::test_delete_user_property_returns_none` | MOCKED | `tests/async/test_async_users.py` |
| CO083G | GET /users/{login}/collaborationGroups | `TestAsyncUserCollabGroups::test_get_user_collab_groups_returns_model` | MOCKED | `tests/async/test_async_users.py` |
| CO083P | POST /users/{login}/collaborationGroups | NONE | - | - |
| CO083D | DELETE /users/{login}/collaborationGroups | NONE | - | - |

### Inventories

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| CO034P | POST /inventories | `TestAsyncCreateInventory::test_create_inventory_with_model` | MOCKED | `tests/async/test_async_inventories.py` |
| CO035G | GET /inventories/{inventoryId} | `TestAsyncGetInventory::test_get_inventory_with_model` | MOCKED | `tests/async/test_async_inventories.py` |
| CO035A | PATCH /inventories/{inventoryId} | `TestAsyncUpdateInventory::test_update_inventory_returns_model` | MOCKED | `tests/async/test_async_inventories.py` |
| CO035D | DELETE /inventories/{inventoryId} | `TestAsyncDeleteInventory::test_delete_inventory_returns_none` | MOCKED | `tests/async/test_async_inventories.py` |

### Events & Subscriptions

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| CO033G | GET /events | `TestAsyncGetEvents::test_get_events_with_params` | MOCKED | `tests/async/test_async_subscriptions.py` |
| CO032G | GET /events/subscriptions (list) | `TestAsyncGetSubscriptions::test_get_subscriptions_returns_model` | MOCKED | `tests/async/test_async_subscriptions.py` |
| CO032P | POST /events/subscriptions | `TestAsyncCreateSubscription::test_create_subscription_returns_model` | MOCKED | `tests/async/test_async_subscriptions.py` |
| CO031G | GET /events/subscriptions/{id} | `TestAsyncGetSubscription::test_get_subscription_returns_model` | MOCKED | `tests/async/test_async_subscriptions.py` |
| CO031D | DELETE /events/subscriptions/{id} | `TestAsyncDeleteSubscription::test_delete_subscription_returns_none` | MOCKED | `tests/async/test_async_subscriptions.py` |

### Daily Extract

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| CO028G | GET /folders/dailyExtract/folders | `TestAsyncGetDailyExtract::test_get_daily_extract_dates_returns_model` | MOCKED | `tests/async/test_async_daily_extract.py` |
| CO029G | GET /folders/dailyExtract/folders/{date}/files | LIVE tests only | LIVE | `tests/async/test_async_daily_extract.py` |
| CO030G | GET /folders/dailyExtract/folders/{date}/files/{filename} | LIVE tests only | LIVE | `tests/async/test_async_daily_extract.py` |

---

## Module: Capacity API (`/rest/ofscCapacity/`)

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| CA004G | GET /capacity | `TestCapacityAPIMocked::test_available_capacity_request` | MOCKED | `tests/capacity/test_capacity_mocked.py` |
| CA006G | GET /quota (v2) | `TestQuotaAPIMocked::test_quota_with_areas` | MOCKED | `tests/capacity/test_quota_mocked.py` |
| CA006A | PATCH /quota (v2) | `TestAsyncUpdateQuota::test_update_quota_with_model` | MOCKED | `tests/async/test_async_capacity.py` |
| CA001G | GET /activityBookingOptions | `TestAsyncGetActivityBookingOptions::test_returns_model` | MOCKED | `tests/async/test_async_capacity.py` |
| CA002G | GET /bookingClosingSchedule | `TestAsyncGetBookingClosingSchedule::test_get_booking_closing_schedule_returns_model` | MOCKED | `tests/async/test_async_capacity.py` |
| CA002A | PATCH /bookingClosingSchedule | `TestAsyncUpdateBookingClosingSchedule::test_update_booking_closing_schedule_with_model` | MOCKED | `tests/async/test_async_capacity.py` |
| CA003G | GET /bookingStatuses | `TestAsyncGetBookingStatuses::test_get_booking_statuses_returns_model` | MOCKED | `tests/async/test_async_capacity.py` |
| CA003A | PATCH /bookingStatuses | `TestAsyncUpdateBookingStatuses::test_update_returns_model` | MOCKED | `tests/async/test_async_capacity.py` |
| CA007P | POST /showBookingGrid | NONE | - | - |
| CA008G | GET /bookingFieldsDependencies | NONE | - | - |
| CA005G | GET /quota (v1) | NONE | - | - |
| CA005A | PATCH /quota (v1) | NONE | - | - |

---

## Module: Statistics API (`/rest/ofscStatistics/v1/`)

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| ST001G | GET /activityDurationStats | `TestAsyncGetActivityDurationStats::test_returns_model` | MOCKED | `tests/async/test_async_statistics.py` |
| ST001A | PATCH /activityDurationStats | `TestAsyncUpdateActivityDurationStats::test_returns_model` | MOCKED | `tests/async/test_async_statistics.py` |
| ST002G | GET /activityTravelStats | `TestAsyncGetActivityTravelStats::test_returns_model` | MOCKED | `tests/async/test_async_statistics.py` |
| ST002A | PATCH /activityTravelStats | `TestAsyncUpdateActivityTravelStats::test_returns_model` | MOCKED | `tests/async/test_async_statistics.py` |
| ST003G | GET /airlineDistanceBasedTravel | `TestAsyncGetAirlineDistanceBasedTravel::test_returns_model` | MOCKED | `tests/async/test_async_statistics.py` |
| ST003A | PATCH /airlineDistanceBasedTravel | `TestAsyncUpdateAirlineDistanceBasedTravel::test_returns_model` | MOCKED | `tests/async/test_async_statistics.py` |

---

## Module: OAuth2 API (`/rest/oauthTokenService/`)

| Endpoint ID | Description | Test Function | Type | File |
|-------------|-------------|---------------|------|------|
| AU002P | POST /v2/token | `TestAsyncOAuth::test_get_oauth_token` | MOCKED | `tests/async/test_async_oauth.py` |
| AU001P | POST /v1/token | NONE | - | - |

---

## Unimplemented APIs (No Tests or Implementation)

| Module | Endpoints | Status |
|--------|-----------|--------|
| Collaboration API | CO001-CB006 (7 endpoints) | Not implemented, no tests |
| Parts Catalog API | PC001-PC002 (3 endpoints) | Not implemented, no tests |
| Activity lifecycle actions | CO016-CO026 (9 endpoints) | Not implemented, no tests |
| `whereIsMyTech` (CO027G) | 1 endpoint | Not implemented, no tests |
| `findNearbyActivities` (CO067G) | 1 endpoint | Not implemented, no tests |
| Resource bulk inventories (CO071P) | 1 endpoint | Not implemented, no tests |
| Service Requests (CO077-CO079) | 3 endpoints | Not implemented, no tests |

---

## Coverage Summary by Module

| Module | Endpoints Implemented | Mocked Tests Exist | LIVE Only | No Tests |
|--------|----------------------|-------------------|-----------|----------|
| Metadata (Async) | 85/86 (99%) | ~65% of methods | ~25% of methods | ~10% of methods |
| Core (Async) | 93/127 (73%) | ~40% of methods | ~50% of methods | ~10% of methods |
| Capacity (Async) | 10/12 (83%) | ~70% of methods | ~20% of methods | ~10% of methods |
| Statistics (Async) | 6/6 (100%) | 100% of methods | 0% | 0% |
| Auth (Async) | 1/2 (50%) | 100% of implemented | - | 0% |

---

*Last updated: 2026-03-04*
*Methodology: Test files were inspected programmatically and cross-referenced against ENDPOINTS.md. Tests marked as `pytest.skip()` unconditionally are classified as SKIP.*
