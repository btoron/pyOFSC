# OFSC API Endpoints Reference

This document provides a comprehensive reference of all Oracle Field Service Cloud (OFSC) API endpoints available in the pyOFSC Python Wrapper v3.0.

**Total Endpoints:** 242  
**Implemented in v3.0:** 158 (65.3%)

## Implementation Coverage by Module

- **metadata**: 49/86 endpoints (57.0%) ✅
- **core**: 102/127 endpoints (80.3%) ✅  
- **capacity**: 7/11 endpoints (63.6%) ✅
- **statistics**: 0/6 endpoints (0%) ❌
- **partscatalog**: 0/3 endpoints (0%) ❌
- **collaboration**: 0/7 endpoints (0%) ❌
- **auth**: 0/2 endpoints (0%) ❌

## Endpoints Table

| ID | Endpoint Path | Method | Module | Implemented In Version | Signature |
|----|---------------|--------|---------|---------------|-----------|
| 1 | `/rest/ofscMetadata/v1/activityTypeGroups` | GET | metadata | v3.0.0-dev | `async def get_activity_type_groups(self, offset: int = 0, limit: int = 100) -> ActivityTypeGroupListResponse` |
| 2 | `/rest/ofscMetadata/v1/activityTypeGroups/{label}` | GET | metadata | v3.0.0-dev | `async def get_activity_type_group(self, label: str) -> ActivityTypeGroup` |
| 3 | `/rest/ofscMetadata/v1/activityTypeGroups/{label}` | PUT | metadata | v3.0.0-dev | `async def create_or_replace_activity_type_group(self, label: str, translations: Optional[TranslationList] = None) -> ActivityTypeGroup` |
| 4 | `/rest/ofscMetadata/v1/activityTypes` | GET | metadata | v3.0.0-dev | `async def get_activity_types(self, offset: int = 0, limit: int = 100) -> ActivityTypeListResponse` |
| 5 | `/rest/ofscMetadata/v1/activityTypes/{label}` | GET | metadata | v3.0.0-dev | `async def get_activity_type(self, label: str) -> ActivityType` |
| 6 | `/rest/ofscMetadata/v1/activityTypes/{label}` | PUT | metadata | | |
| 7 | `/rest/ofscMetadata/v1/applications` | GET | metadata | v3.0.0-dev | `async def get_applications(self) -> ApplicationListResponse` |
| 8 | `/rest/ofscMetadata/v1/applications/{label}` | GET | metadata | v3.0.0-dev | `async def get_application(self, label: str) -> Application` |
| 9 | `/rest/ofscMetadata/v1/applications/{label}` | PUT | metadata | | |
| 10 | `/rest/ofscMetadata/v1/applications/{label}/apiAccess` | GET | metadata | v3.0.0-dev | `async def get_application_api_accesses(self, label: str) -> ApplicationApiAccessListResponse` |
| 11 | `/rest/ofscMetadata/v1/applications/{label}/apiAccess/{apiLabel}` | GET | metadata | v3.0.0-dev | `async def get_application_api_access(self, label: str, api_label: str) -> ApplicationApiAccess` |
| 12 | `/rest/ofscMetadata/v1/applications/{label}/apiAccess/{apiLabel}` | PATCH | metadata | | |
| 13 | `/rest/ofscMetadata/v1/applications/{label}/custom-actions/generateClientSecret` | POST | metadata | | |
| 14 | `/rest/ofscMetadata/v1/capacityAreas` | GET | metadata | v3.0.0-dev | `async def get_capacity_areas(self, expandParent: bool = False, fields: List[str] = ["label"], activeOnly: bool = False, areasOnly: bool = False) -> CapacityAreaListResponse` |
| 15 | `/rest/ofscMetadata/v1/capacityAreas/{label}` | GET | metadata | v3.0.0-dev | `async def get_capacity_area(self, label: str) -> CapacityArea` |
| 16 | `/rest/ofscMetadata/v1/capacityAreas/{label}/capacityCategories` | GET | metadata | v3.0.0-dev | `async def get_capacity_area_categories(self, area_label: str, offset: int = 0, limit: int = 100) -> CapacityAreaCategoryListResponse` |
| 17 | `/rest/ofscMetadata/v2/capacityAreas/{label}/workZones` | GET | metadata | v3.0.0-dev | `async def get_capacity_area_workzones(self, area_label: str, offset: int = 0, limit: int = 100) -> CapacityAreaWorkzoneListResponse` |
| 18 | `/rest/ofscMetadata/v1/capacityAreas/{label}/workZones` | GET | metadata | DEPRECATED | |
| 19 | `/rest/ofscMetadata/v1/capacityAreas/{label}/timeSlots` | GET | metadata | v3.0.0-dev | `async def get_capacity_area_timeslots(self, area_label: str, offset: int = 0, limit: int = 100) -> CapacityAreaTimeSlotListResponse` |
| 20 | `/rest/ofscMetadata/v1/capacityAreas/{label}/timeIntervals` | GET | metadata | v3.0.0-dev | `async def get_capacity_area_timeintervals(self, area_label: str, offset: int = 0, limit: int = 100) -> CapacityAreaTimeIntervalListResponse` |
| 21 | `/rest/ofscMetadata/v1/capacityAreas/{label}/organizations` | GET | metadata | v3.0.0-dev | `async def get_capacity_area_organizations(self, area_label: str, offset: int = 0, limit: int = 100) -> CapacityAreaOrganizationListResponse` |
| 22 | `/rest/ofscMetadata/v1/capacityAreas/{label}/children` | GET | metadata | | |
| 23 | `/rest/ofscMetadata/v1/capacityCategories` | GET | metadata | v3.0.0-dev | `async def get_capacity_categories(self, offset: int = 0, limit: int = 100) -> CapacityCategoryListResponse` |
| 24 | `/rest/ofscMetadata/v1/capacityCategories/{label}` | GET | metadata | v3.0.0-dev | `async def get_capacity_category(self, label: str) -> CapacityCategoryResponse` |
| 25 | `/rest/ofscMetadata/v1/capacityCategories/{label}` | PUT | metadata | v3.0.0-dev | `async def create_or_replace_capacity_category(self, label: str, capacity_category: CapacityCategoryRequest) -> CapacityCategoryResponse` |
| 26 | `/rest/ofscMetadata/v1/capacityCategories/{label}` | DELETE | metadata | v3.0.0-dev | `async def delete_capacity_category(self, label: str) -> None` |
| 27 | `/rest/ofscMetadata/v1/forms` | GET | metadata | v3.0.0-dev | `async def get_forms(self, offset: int = 0, limit: int = 100) -> FormListResponse` |
| 28 | `/rest/ofscMetadata/v1/forms/{label}` | GET | metadata | v3.0.0-dev | `async def get_form(self, label: str) -> Form` |
| 29 | `/rest/ofscMetadata/v1/forms/{label}` | PUT | metadata | | |
| 30 | `/rest/ofscMetadata/v1/forms/{label}` | DELETE | metadata | | |
| 31 | `/rest/ofscMetadata/v1/inventoryTypes` | GET | metadata | v3.0.0-dev | `async def get_inventory_types(self) -> InventoryTypeListResponse` |
| 32 | `/rest/ofscMetadata/v1/inventoryTypes/{label}` | GET | metadata | v3.0.0-dev | `async def get_inventory_type(self, label: str) -> InventoryType` |
| 33 | `/rest/ofscMetadata/v1/inventoryTypes/{label}` | PUT | metadata | | |
| 34 | `/rest/ofscMetadata/v1/languages` | GET | metadata | v3.0.0-dev | `async def get_languages(self, offset: int = 0, limit: int = 100) -> LanguageListResponse` |
| 35 | `/rest/ofscMetadata/v1/linkTemplates` | GET | metadata | v3.0.0-dev | `async def get_link_templates(self, offset: int = 0, limit: int = 100) -> LinkTemplateListResponse` |
| 36 | `/rest/ofscMetadata/v1/linkTemplates/{label}` | GET | metadata | v3.0.0-dev | `async def get_link_template(self, label: str) -> LinkTemplate` |
| 37 | `/rest/ofscMetadata/v1/linkTemplates/{label}` | POST | metadata | | |
| 38 | `/rest/ofscMetadata/v1/linkTemplates/{label}` | PATCH | metadata | | |
| 39 | `/rest/ofscMetadata/v1/mapLayers` | GET | metadata | | |
| 40 | `/rest/ofscMetadata/v1/mapLayers` | POST | metadata | | |
| 41 | `/rest/ofscMetadata/v1/mapLayers/{label}` | GET | metadata | | |
| 42 | `/rest/ofscMetadata/v1/mapLayers/{label}` | PUT | metadata | | |
| 43 | `/rest/ofscMetadata/v1/mapLayers/custom-actions/populateLayers/{downloadId}` | GET | metadata | | |
| 44 | `/rest/ofscMetadata/v1/mapLayers/custom-actions/populateLayers` | POST | metadata | | |
| 45 | `/rest/ofscMetadata/v1/nonWorkingReasons` | GET | metadata | v3.0.0-dev | `async def get_non_working_reasons(self, offset: int = 0, limit: int = 100) -> NonWorkingReasonListResponse` |
| 46 | `/rest/ofscMetadata/v1/organizations` | GET | metadata | v3.0.0-dev | `async def get_organizations(self) -> OrganizationListResponse` |
| 47 | `/rest/ofscMetadata/v1/organizations/{label}` | GET | metadata | v3.0.0-dev | `async def get_organization(self, label: str) -> Organization` |
| 48 | `/rest/ofscMetadata/v1/plugins/custom-actions/import` | POST | metadata | | |
| 49 | `/rest/ofscMetadata/v1/plugins/{pluginLabel}/custom-actions/install` | POST | metadata | | |
| 50 | `/rest/ofscMetadata/v1/properties` | GET | metadata | v3.0.0-dev | `async def get_properties(self, offset: int = 0, limit: int = 100) -> PropertyListResponse` |
| 51 | `/rest/ofscMetadata/v1/properties/{label}` | GET | metadata | v3.0.0-dev | `async def get_property(self, label: str) -> PropertyResponse` |
| 52 | `/rest/ofscMetadata/v1/properties/{label}` | PUT | metadata | v3.0.0-dev | `async def create_or_replace_property(self, label: str, property_request: PropertyRequest) -> PropertyResponse` |
| 53 | `/rest/ofscMetadata/v1/properties/{label}` | PATCH | metadata | | |
| 54 | `/rest/ofscMetadata/v1/properties/{label}/enumerationList` | GET | metadata | v3.0.0-dev | `async def get_enumeration_values(self, label: str, offset: int = 0, limit: int = 100) -> EnumerationValueList` |
| 55 | `/rest/ofscMetadata/v1/properties/{label}/enumerationList` | PUT | metadata | | |
| 56 | `/rest/ofscMetadata/v1/resourceTypes` | GET | metadata | v3.0.0-dev | `async def get_resource_types(self) -> ResourceTypeListResponse` |
| 57 | `/rest/ofscMetadata/v1/routingProfiles` | GET | metadata | v3.0.0-dev | `async def get_routing_profiles(self, offset: int = 0, limit: int = 100) -> RoutingProfileListResponse` |
| 58 | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans` | GET | metadata | v3.0.0-dev | `async def get_routing_profile_plans(self, profile_label: str, offset: int = 0, limit: int = 100) -> RoutingPlanListResponse` |
| 59 | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/{planLabel}/custom-actions/export` | GET | metadata | v3.0.0-dev | `async def get_routing_profile_plan_export(self, profile_label: str, plan_label: str, media_type: Optional[str] = "application/octet-stream") -> RoutingPlanExportResponse` |
| 60 | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/custom-actions/import` | PUT | metadata | | |
| 61 | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/custom-actions/forceImport` | PUT | metadata | | |
| 62 | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/{planLabel}/{resourceExternalId}/{date}/custom-actions/start` | POST | metadata | | |
| 63 | `/rest/ofscMetadata/v1/shifts` | GET | metadata | v3.0.0-dev | `async def get_shifts(self, offset: int = 0, limit: int = 100) -> ShiftListResponse` |
| 64 | `/rest/ofscMetadata/v1/shifts/{label}` | GET | metadata | v3.0.0-dev | `async def get_shift(self, label: str) -> Shift` |
| 65 | `/rest/ofscMetadata/v1/shifts/{label}` | DELETE | metadata | | |
| 66 | `/rest/ofscMetadata/v1/shifts/{label}` | PUT | metadata | | |
| 67 | `/rest/ofscMetadata/v1/timeSlots` | GET | metadata | v3.0.0-dev | `async def get_timeslots(self, offset: int = 0, limit: int = 100) -> TimeSlotListResponse` |
| 68 | `/rest/ofscMetadata/v1/workSkillConditions` | GET | metadata | v3.0.0-dev | `async def get_workskill_conditions(self) -> WorkskillConditionListResponse` |
| 69 | `/rest/ofscMetadata/v1/workSkillConditions` | PUT | metadata | | |
| 70 | `/rest/ofscMetadata/v1/workSkillGroups` | GET | metadata | v3.0.0-dev | `async def get_workskill_groups(self) -> WorkSkillGroupListResponse` |
| 71 | `/rest/ofscMetadata/v1/workSkillGroups/{label}` | GET | metadata | v3.0.0-dev | `async def get_workskill_group(self, label: str) -> WorkSkillGroup` |
| 72 | `/rest/ofscMetadata/v1/workSkillGroups/{label}` | PUT | metadata | | |
| 73 | `/rest/ofscMetadata/v1/workSkillGroups/{label}` | DELETE | metadata | | |
| 74 | `/rest/ofscMetadata/v1/workSkills` | GET | metadata | v3.0.0-dev | `async def get_workskills(self, offset: int = 0, limit: int = 100) -> WorkskillListResponse` |
| 75 | `/rest/ofscMetadata/v1/workSkills/{label}` | GET | metadata | v3.0.0-dev | `async def get_workskill(self, label: str) -> Workskill` |
| 76 | `/rest/ofscMetadata/v1/workSkills/{label}` | PUT | metadata | | |
| 77 | `/rest/ofscMetadata/v1/workSkills/{label}` | DELETE | metadata | | |
| 78 | `/rest/ofscMetadata/v1/workZones` | GET | metadata | v3.0.0-dev | `async def get_workzones(self, offset: int = 0, limit: int = 100) -> WorkzoneListResponse` |
| 79 | `/rest/ofscMetadata/v1/workZones` | POST | metadata | | |
| 80 | `/rest/ofscMetadata/v1/workZones` | PUT | metadata | | |
| 81 | `/rest/ofscMetadata/v1/workZones` | PATCH | metadata | | |
| 82 | `/rest/ofscMetadata/v1/workZones/{label}` | GET | metadata | v3.0.0-dev | `async def get_workzone(self, label: str) -> Workzone` |
| 83 | `/rest/ofscMetadata/v1/workZones/{label}` | PUT | metadata | | |
| 84 | `/rest/ofscMetadata/v1/workZones/custom-actions/populateShapes/{downloadId}` | GET | metadata | | |
| 85 | `/rest/ofscMetadata/v1/workZones/custom-actions/populateShapes` | POST | metadata | | |
| 86 | `/rest/ofscMetadata/v1/workZoneKey` | GET | metadata | v3.0.0-dev | `async def get_work_zone_key(self) -> WorkZoneKeyResponse` |
| 87 | `/rest/ofscStatistics/v1/activityDurationStats` | GET | statistics | | |
| 88 | `/rest/ofscStatistics/v1/activityDurationStats` | PATCH | statistics | | |
| 89 | `/rest/ofscStatistics/v1/activityTravelStats` | GET | statistics | | |
| 90 | `/rest/ofscStatistics/v1/activityTravelStats` | PATCH | statistics | | |
| 91 | `/rest/ofscStatistics/v1/airlineDistanceBasedTravel` | GET | statistics | | |
| 92 | `/rest/ofscStatistics/v1/airlineDistanceBasedTravel` | PATCH | statistics | | |
| 93 | `/rest/ofscPartsCatalog/v1/catalogs/{catalog}/{language}` | PUT | partscatalog | | |
| 94 | `/rest/ofscPartsCatalog/v1/catalogs/{catalog}/{language}/{itemLabel}` | PUT | partscatalog | | |
| 95 | `/rest/ofscPartsCatalog/v1/catalogs/{catalog}/{language}/{itemLabel}` | DELETE | partscatalog | | |
| 96 | `/rest/ofscCollaboration/v1/addressBook` | GET | collaboration | | |
| 97 | `/rest/ofscCollaboration/v1/chats` | POST | collaboration | | |
| 98 | `/rest/ofscCollaboration/v1/chats/{chatId}/leave` | POST | collaboration | | |
| 99 | `/rest/ofscCollaboration/v1/chats/{chatId}/messages` | GET | collaboration | | |
| 100 | `/rest/ofscCollaboration/v1/chats/{chatId}/messages` | POST | collaboration | | |
| 101 | `/rest/ofscCollaboration/v1/chats/{chatId}/participants` | GET | collaboration | | |
| 102 | `/rest/ofscCollaboration/v1/chats/{chatId}/participants/invite` | POST | collaboration | | |
| 103 | `/rest/ofscCore/v1/activities` | POST | core | v3.0.0-dev | `async def create_activity(self, activity_data: dict) -> Activity` |
| 104 | `/rest/ofscCore/v1/activities` | GET | core | v3.0.0-dev | `async def get_activities(self, resources: List[str], dateFrom: Optional[date] = None, dateTo: Optional[date] = None, includeChildren: str = "all", q: Optional[str] = None, fields: Optional[List[str]] = None, includeNonScheduled: bool = False, offset: int = 0, limit: int = 100) -> ActivityListResponse` |
| 105 | `/rest/ofscCore/v1/activities/{activityId}` | PATCH | core | v3.0.0-dev | `async def update_activity(self, activity_id: int, activity_data: dict) -> Activity` |
| 106 | `/rest/ofscCore/v1/activities/{activityId}` | DELETE | core | v3.0.0-dev | `async def delete_activity(self, activity_id: int) -> None` |
| 107 | `/rest/ofscCore/v1/activities/{activityId}` | GET | core | v3.0.0-dev | `async def get_activity(self, activity_id: int) -> Activity` |
| 108 | `/rest/ofscCore/v1/activities/{activityId}/multidaySegments` | GET | core | v3.0.0-dev | `async def get_activity_multiday_segments(self, activity_id: int) -> ActivityMultidaySegmentListResponse` |
| 109 | `/rest/ofscCore/v1/activities/{activityId}/{propertyLabel}` | PUT | core | v3.0.0-dev | `async def set_activity_property(self, activity_id: int, property_label: str, property_value: Any) -> ActivityProperty` |
| 110 | `/rest/ofscCore/v1/activities/{activityId}/{propertyLabel}` | GET | core | v3.0.0-dev | `async def get_activity_property(self, activity_id: int, property_label: str) -> ActivityProperty` |
| 111 | `/rest/ofscCore/v1/activities/{activityId}/{propertyLabel}` | DELETE | core | v3.0.0-dev | `async def delete_activity_property(self, activity_id: int, property_label: str) -> None` |
| 112 | `/rest/ofscCore/v1/activities/{activityId}/submittedForms` | GET | core | v3.0.0-dev | `async def get_activity_submitted_forms(self, activity_id: int) -> ActivitySubmittedFormListResponse` |
| 113 | `/rest/ofscCore/v1/activities/{activityId}/resourcePreferences` | PUT | core | v3.0.0-dev | `async def set_activity_resource_preferences(self, activity_id: int, preferences_data: List[dict]) -> ActivityResourcePreferenceListResponse` |
| 114 | `/rest/ofscCore/v1/activities/{activityId}/resourcePreferences` | GET | core | v3.0.0-dev | `async def get_activity_resource_preferences(self, activity_id: int) -> ActivityResourcePreferenceListResponse` |
| 115 | `/rest/ofscCore/v1/activities/{activityId}/resourcePreferences` | DELETE | core | v3.0.0-dev | `async def delete_activity_resource_preferences(self, activity_id: int) -> None` |
| 116 | `/rest/ofscCore/v1/activities/{activityId}/requiredInventories` | PUT | core | v3.0.0-dev | `async def set_activity_required_inventories(self, activity_id: int, inventories_data: List[dict]) -> ActivityRequiredInventoryListResponse` |
| 117 | `/rest/ofscCore/v1/activities/{activityId}/requiredInventories` | GET | core | v3.0.0-dev | `async def get_activity_required_inventories(self, activity_id: int) -> ActivityRequiredInventoryListResponse` |
| 118 | `/rest/ofscCore/v1/activities/{activityId}/requiredInventories` | DELETE | core | v3.0.0-dev | `async def delete_activity_required_inventories(self, activity_id: int) -> None` |
| 119 | `/rest/ofscCore/v1/activities/{activityId}/customerInventories` | POST | core | v3.0.0-dev | `async def add_activity_customer_inventory(self, activity_id: int, inventory_data: dict) -> ActivityCustomerInventory` |
| 120 | `/rest/ofscCore/v1/activities/{activityId}/customerInventories` | GET | core | v3.0.0-dev | `async def get_activity_customer_inventories(self, activity_id: int) -> ActivityCustomerInventoryListResponse` |
| 121 | `/rest/ofscCore/v1/activities/{activityId}/installedInventories` | GET | core | v3.0.0-dev | `async def get_activity_installed_inventories(self, activity_id: int) -> ActivityInstalledInventoryListResponse` |
| 122 | `/rest/ofscCore/v1/activities/{activityId}/deinstalledInventories` | GET | core | v3.0.0-dev | `async def get_activity_deinstalled_inventories(self, activity_id: int) -> ActivityDeinstalledInventoryListResponse` |
| 123 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities` | GET | core | v3.0.0-dev | `async def get_activity_linked_activities(self, activity_id: int) -> ActivityLinkListResponse` |
| 124 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities` | DELETE | core | v3.0.0-dev | `async def delete_activity_linked_activities(self, activity_id: int) -> None` |
| 125 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities` | POST | core | v3.0.0-dev | `async def add_activity_linked_activities(self, activity_id: int, linked_activities_data: List[dict]) -> ActivityLinkListResponse` |
| 126 | `/rest/ofscCore/v1/activities/{activityId}/capacityCategories` | GET | core | v3.0.0-dev | `async def get_activity_capacity_categories(self, activity_id: int) -> ActivityCapacityCategoryListResponse` |
| 127 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities/{linkedActivityId}/linkTypes/{linkType}` | DELETE | core | v3.0.0-dev | `async def delete_activity_link(self, activity_id: int, linked_activity_id: int, link_type: str) -> None` |
| 128 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities/{linkedActivityId}/linkTypes/{linkType}` | GET | core | v3.0.0-dev | `async def get_activity_link(self, activity_id: int, linked_activity_id: int, link_type: str) -> ActivityLink` |
| 129 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities/{linkedActivityId}/linkTypes/{linkType}` | PUT | core | v3.0.0-dev | `async def set_activity_link(self, activity_id: int, linked_activity_id: int, link_type: str, link_data: Optional[dict] = None) -> ActivityLink` |
| 130 | `/rest/ofscCore/v1/activities/custom-actions/search` | GET | core | v3.0.0-dev | `async def search_activities(self, **params) -> ActivityListResponse` |
| 131 | `/rest/ofscCore/v1/activities/custom-actions/bulkUpdate` | POST | core | v3.0.0-dev | `async def bulk_update_activities(self, bulk_data: BulkUpdateRequest) -> BulkUpdateResponse` |
| 132 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/startPrework` | POST | core | v3.0.0-dev | `async def start_activity_prework(self, activity_id: int) -> Activity` |
| 133 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/reopen` | POST | core | v3.0.0-dev | `async def reopen_activity(self, activity_id: int) -> Activity` |
| 134 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/delay` | POST | core | v3.0.0-dev | `async def delay_activity(self, activity_id: int, delay_data: Optional[dict] = None) -> Activity` |
| 135 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/cancel` | POST | core | v3.0.0-dev | `async def cancel_activity(self, activity_id: int) -> Activity` |
| 136 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/start` | POST | core | v3.0.0-dev | `async def start_activity(self, activity_id: int) -> Activity` |
| 137 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/enroute` | POST | core | v3.0.0-dev | `async def set_activity_enroute(self, activity_id: int) -> Activity` |
| 138 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/stopTravel` | POST | core | v3.0.0-dev | `async def stop_activity_travel(self, activity_id: int) -> Activity` |
| 139 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/suspend` | POST | core | v3.0.0-dev | `async def suspend_activity(self, activity_id: int, suspend_data: Optional[dict] = None) -> Activity` |
| 140 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/move` | POST | core | v3.0.0-dev | `async def move_activity(self, activity_id: int, move_data: dict) -> ActivityMoveResponse` |
| 141 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/complete` | POST | core | v3.0.0-dev | `async def complete_activity(self, activity_id: int) -> Activity` |
| 142 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/notDone` | POST | core | v3.0.0-dev | `async def mark_activity_not_done(self, activity_id: int, not_done_data: Optional[dict] = None) -> Activity` |
| 143 | `/rest/ofscCore/v1/whereIsMyTech` | GET | core | | |
| 144 | `/rest/ofscCore/v1/folders/dailyExtract/folders` | GET | core | v3.0.0-dev | `async def get_daily_extract_dates(self) -> DailyExtractFolders` |
| 145 | `/rest/ofscCore/v1/folders/dailyExtract/folders/{dailyExtractDate}/files` | GET | core | v3.0.0-dev | `async def get_daily_extract_files(self, extract_date: str) -> DailyExtractFiles` |
| 146 | `/rest/ofscCore/v1/folders/dailyExtract/folders/{dailyExtractDate}/files/{dailyExtractFilename}` | GET | core | v3.0.0-dev | `async def get_daily_extract_file(self, extract_date: str, filename: str, media_type: str = "application/octet-stream") -> bytes` |
| 147 | `/rest/ofscCore/v1/events/subscriptions/{subscriptionId}` | DELETE | core | | |
| 148 | `/rest/ofscCore/v1/events/subscriptions/{subscriptionId}` | GET | core | | |
| 149 | `/rest/ofscCore/v1/events/subscriptions` | GET | core | v3.0.0-dev | `async def get_subscriptions(self, allSubscriptions: bool = False) -> SubscriptionList` |
| 150 | `/rest/ofscCore/v1/events/subscriptions` | POST | core | | |
| 151 | `/rest/ofscCore/v1/events` | GET | core | | |
| 152 | `/rest/ofscCore/v1/inventories` | POST | core | v3.0.0-dev | `async def create_inventory(self, inventory_data: dict) -> Inventory` |
| 153 | `/rest/ofscCore/v1/inventories/{inventoryId}` | PATCH | core | v3.0.0-dev | `async def update_inventory(self, inventory_id: int, inventory_data: dict) -> Inventory` |
| 154 | `/rest/ofscCore/v1/inventories/{inventoryId}` | GET | core | v3.0.0-dev | `async def get_inventory(self, inventory_id: int) -> Inventory` |
| 155 | `/rest/ofscCore/v1/inventories/{inventoryId}` | DELETE | core | | |
| 156 | `/rest/ofscCore/v1/inventories/{inventoryId}/{propertyLabel}` | PUT | core | | |
| 157 | `/rest/ofscCore/v1/inventories/{inventoryId}/{propertyLabel}` | GET | core | | |
| 158 | `/rest/ofscCore/v1/inventories/{inventoryId}/{propertyLabel}` | DELETE | core | | |
| 159 | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/undoInstall` | POST | core | | |
| 160 | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/undoDeinstall` | POST | core | | |
| 161 | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/install` | POST | core | | |
| 162 | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/deinstall` | POST | core | | |
| 163 | `/rest/ofscCore/v1/resources` | GET | core | v3.0.0-dev | `async def get_resources(self, offset: int = 0, limit: int = 100, fields: Optional[List[str]] = None) -> ResourceListResponse` |
| 164 | `/rest/ofscCore/v1/resources/{resourceId}/children` | GET | core | | |
| 165 | `/rest/ofscCore/v1/resources/{resourceId}/descendants` | GET | core | v3.0.0-dev | `async def get_resource_descendants(self, resource_id: str, resource_fields: Optional[List[str]] = None, offset: int = 0, limit: int = 100, inventories: bool = False, work_skills: bool = False, work_zones: bool = False, work_schedules: bool = False) -> ResourceListResponse` |
| 166 | `/rest/ofscCore/v1/resources/{resourceId}/assistants` | GET | core | | |
| 167 | `/rest/ofscCore/v1/resources/{resourceId}` | GET | core | v3.0.0-dev | `async def get_resource(self, resource_id: str, inventories: bool = False, workSkills: bool = False, workZones: bool = False, workSchedules: bool = False) -> Resource` |
| 168 | `/rest/ofscCore/v1/resources/{resourceId}` | PUT | core | v3.0.0-dev | `async def create_resource(self, resource_id: str, resource_data: dict) -> Resource` |
| 169 | `/rest/ofscCore/v1/resources/{resourceId}` | PATCH | core | v3.0.0-dev | `async def update_resource(self, resource_id: str, resource_data: dict) -> Resource` |
| 170 | `/rest/ofscCore/v1/resources/{resourceId}/users` | GET | core | v3.0.0-dev | `async def get_resource_users(self, resource_id: str) -> ResourceUsersListResponse` |
| 171 | `/rest/ofscCore/v1/resources/{resourceId}/users` | PUT | core | v3.0.0-dev | `async def set_resource_users(self, resource_id: str, user_logins: List[str]) -> ResourceUsersListResponse` |
| 172 | `/rest/ofscCore/v1/resources/{resourceId}/users` | DELETE | core | v3.0.0-dev | `async def delete_resource_users(self, resource_id: str) -> None` |
| 173 | `/rest/ofscCore/v1/resources/{resourceId}/inventories` | POST | core | v3.0.0-dev | `async def assign_inventory_to_resource(self, resource_id: str, inventory_data: dict) -> ResourceInventory` |
| 174 | `/rest/ofscCore/v1/resources/{resourceId}/inventories` | GET | core | v3.0.0-dev | `async def get_resource_inventories(self, resource_id: str) -> ResourceInventoryListResponse` |
| 175 | `/rest/ofscCore/v1/resources/{resourceId}/inventories/{inventoryId}/custom-actions/install` | POST | core | | |
| 176 | `/rest/ofscCore/v1/resources/{resourceId}/workSkills` | POST | core | v3.0.0-dev | `async def add_resource_work_skills(self, resource_id: str, work_skills_data: List[dict]) -> ResourceWorkSkillListResponse` |
| 177 | `/rest/ofscCore/v1/resources/{resourceId}/workSkills` | GET | core | v3.0.0-dev | `async def get_resource_work_skills(self, resource_id: str) -> ResourceWorkSkillListResponse` |
| 178 | `/rest/ofscCore/v1/resources/{resourceId}/workSkills/{workSkill}` | DELETE | core | | |
| 179 | `/rest/ofscCore/v1/resources/{resourceId}/workZones` | POST | core | v3.0.0-dev | `async def assign_resource_work_zones(self, resource_id: str, work_zones_data: List[dict]) -> ResourceWorkZoneListResponse` |
| 180 | `/rest/ofscCore/v1/resources/{resourceId}/workZones` | GET | core | v3.0.0-dev | `async def get_resource_work_zones(self, resource_id: str) -> ResourceWorkZoneListResponse` |
| 181 | `/rest/ofscCore/v1/resources/{resourceId}/workZones/{workZoneItemId}` | DELETE | core | | |
| 182 | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules` | GET | core | v3.0.0-dev | `async def get_resource_work_schedules(self, resource_id: str, actual_date: Optional[date] = None) -> ResourceWorkScheduleResponse` |
| 183 | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules` | POST | core | v3.0.0-dev | `async def create_resource_work_schedule(self, resource_id: str, schedule_data: dict) -> ResourceWorkScheduleResponse` |
| 184 | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules/{scheduleItemId}` | DELETE | core | v3.0.0-dev | `async def delete_resource_work_schedule_item(self, resource_id: str, schedule_item_id: int) -> None` |
| 185 | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules/calendarView` | GET | core | v3.0.0-dev | `async def get_resource_calendar_view(self, resource_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> CalendarView` |
| 186 | `/rest/ofscCore/v1/calendars` | GET | core | v3.0.0-dev | `async def get_calendars(self, offset: int = 0, limit: int = 100) -> CalendarListResponse` |
| 187 | `/rest/ofscCore/v1/resources/{resourceId}/{propertyLabel}` | PUT | core | v3.0.0-dev | `async def set_resource_property(self, resource_id: str, property_label: str, property_value: Any) -> ResourcePropertyValue` |
| 188 | `/rest/ofscCore/v1/resources/{resourceId}/{propertyLabel}` | GET | core | v3.0.0-dev | `async def get_resource_property(self, resource_id: str, property_label: str) -> ResourcePropertyValue` |
| 189 | `/rest/ofscCore/v1/resources/{resourceId}/{propertyLabel}` | DELETE | core | v3.0.0-dev | `async def delete_resource_property(self, resource_id: str, property_label: str) -> None` |
| 190 | `/rest/ofscCore/v1/resources/{resourceId}/locations` | POST | core | v3.0.0-dev | `async def create_resource_location(self, resource_id: str, location_data: dict) -> LocationListResponse` |
| 191 | `/rest/ofscCore/v1/resources/{resourceId}/locations` | GET | core | v3.0.0-dev | `async def get_resource_locations(self, resource_id: str, offset: int = 0, limit: int = 100) -> LocationListResponse` |
| 192 | `/rest/ofscCore/v1/resources/{resourceId}/locations/{locationId}` | GET | core | v3.0.0-dev | `async def get_resource_location(self, resource_id: str, location_id: int) -> Location` |
| 193 | `/rest/ofscCore/v1/resources/{resourceId}/locations/{locationId}` | PATCH | core | v3.0.0-dev | `async def update_resource_location(self, resource_id: str, location_id: int, location_data: dict) -> LocationListResponse` |
| 194 | `/rest/ofscCore/v1/resources/{resourceId}/locations/{locationId}` | DELETE | core | v3.0.0-dev | `async def delete_resource_location(self, resource_id: str, location_id: int) -> None` |
| 195 | `/rest/ofscCore/v1/resources/{resourceId}/positionHistory` | GET | core | v3.0.0-dev | `async def get_resource_position_history(self, resource_id: str, start_time: Optional[str] = None, end_time: Optional[str] = None) -> PositionHistory` |
| 196 | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations` | PUT | core | v3.0.0-dev | `async def set_resource_assigned_locations(self, resource_id: str, assigned_locations_data: dict) -> AssignedLocationsResponse` |
| 197 | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations` | GET | core | v3.0.0-dev | `async def get_resource_assigned_locations(self, resource_id: str) -> AssignedLocationsResponse` |
| 198 | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations` | PATCH | core | v3.0.0-dev | `async def update_resource_assigned_locations(self, resource_id: str, assigned_locations_data: dict) -> AssignedLocationsResponse` |
| 199 | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations/{date}` | DELETE | core | v3.0.0-dev | `async def delete_resource_assigned_location_date(self, resource_id: str, date: str) -> None` |
| 200 | `/rest/ofscCore/v1/resources/{resourceId}/plans` | POST | core | v3.0.0-dev | `async def create_resource_plan(self, resource_id: str, plan_data: dict) -> ResourcePlanListResponse` |
| 201 | `/rest/ofscCore/v1/resources/{resourceId}/plans` | GET | core | v3.0.0-dev | `async def get_resource_plans(self, resource_id: str) -> ResourcePlanListResponse` |
| 202 | `/rest/ofscCore/v1/resources/{resourceId}/plans` | DELETE | core | v3.0.0-dev | `async def delete_resource_plans(self, resource_id: str) -> None` |
| 203 | `/rest/ofscCore/v1/resources/{resourceId}/routes/{date}` | GET | core | v3.0.0-dev | `async def get_resource_route(self, resource_id: str, date: str) -> RouteInfoResponse` |
| 204 | `/rest/ofscCore/v1/resources/{resourceId}/routes/{date}/custom-actions/activate` | POST | core | v3.0.0-dev | `async def activate_resource_route(self, resource_id: str, date: str, activation_data: Optional[dict] = None) -> RouteActivationResponse` |
| 205 | `/rest/ofscCore/v1/resources/{resourceId}/routes/{date}/custom-actions/deactivate` | POST | core | v3.0.0-dev | `async def deactivate_resource_route(self, resource_id: str, date: str, deactivation_data: Optional[dict] = None) -> RouteActivationResponse` |
| 206 | `/rest/ofscCore/v1/resources/{resourceId}/findNearbyActivities` | GET | core | v3.0.0-dev | `async def find_nearby_activities(self, resource_id: str, latitude: Optional[float] = None, longitude: Optional[float] = None, radius: Optional[float] = None) -> NearbyActivityListResponse` |
| 207 | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkSchedules` | POST | core | v3.0.0-dev | `async def bulk_update_work_schedules(self, bulk_data: dict) -> BulkScheduleUpdateResponse` |
| 208 | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkSkills` | POST | core | v3.0.0-dev | `async def bulk_update_work_skills(self, bulk_data: dict) -> BulkSkillUpdateResponse` |
| 209 | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkZones` | POST | core | v3.0.0-dev | `async def bulk_update_work_zones(self, bulk_data: dict) -> BulkZoneUpdateResponse` |
| 210 | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateInventories` | POST | core | v3.0.0-dev | `async def bulk_update_inventories(self, bulk_data: dict) -> BulkInventoryUpdateResponse` |
| 211 | `/rest/ofscCore/v1/resources/custom-actions/findMatchingResources` | POST | core | v3.0.0-dev | `async def find_matching_resources(self, search_criteria: dict) -> ResourceMatchResponse` |
| 212 | `/rest/ofscCore/v1/resources/custom-actions/findResourcesForUrgentAssignment` | POST | core | v3.0.0-dev | `async def find_resources_for_urgent_assignment(self, urgent_data: dict) -> UrgentAssignmentResponse` |
| 213 | `/rest/ofscCore/v1/resources/custom-actions/setPositions` | POST | core | v3.0.0-dev | `async def set_resource_positions(self, positions_data: dict) -> SetPositionsResponse` |
| 214 | `/rest/ofscCore/v1/resources/custom-actions/lastKnownPositions` | GET | core | v3.0.0-dev | `async def get_last_known_positions(self, resource_ids: Optional[List[str]] = None) -> LastKnownPositionListResponse` |
| 215 | `/rest/ofscCore/v1/resources/custom-actions/resourcesInArea` | GET | core | v3.0.0-dev | `async def get_resources_in_area(self, latitude: float, longitude: float, radius: float, resource_types: Optional[List[str]] = None) -> ResourcesInAreaResponse` |
| 216 | `/rest/ofscCore/v1/serviceRequests/{requestId}` | GET | core | v3.0.0-dev | `async def get_service_request(self, request_id: str) -> ServiceRequest` |
| 217 | `/rest/ofscCore/v1/serviceRequests` | POST | core | v3.0.0-dev | `async def create_service_request(self, request_data: dict) -> ServiceRequest` |
| 218 | `/rest/ofscCore/v1/serviceRequests/{requestId}/{propertyLabel}` | GET | core | v3.0.0-dev | `async def get_service_request_property(self, request_id: str, property_label: str) -> ServiceRequestProperty` |
| 219 | `/rest/ofscCore/v1/users` | GET | core | v3.0.0-dev | `async def get_users(self, offset: int = 0, limit: int = 100) -> UserListResponse` |
| 220 | `/rest/ofscCore/v1/users/{login}` | GET | core | v3.0.0-dev | `async def get_user(self, login: str) -> User` |
| 221 | `/rest/ofscCore/v1/users/{login}` | PUT | core | v3.0.0-dev | `async def create_user(self, login: str, user_data: dict) -> User` |
| 222 | `/rest/ofscCore/v1/users/{login}` | PATCH | core | v3.0.0-dev | `async def update_user(self, login: str, user_data: dict) -> User` |
| 223 | `/rest/ofscCore/v1/users/{login}` | DELETE | core | v3.0.0-dev | `async def delete_user(self, login: str) -> None` |
| 224 | `/rest/ofscCore/v1/users/{login}/{propertyLabel}` | PUT | core | | |
| 225 | `/rest/ofscCore/v1/users/{login}/{propertyLabel}` | GET | core | | |
| 226 | `/rest/ofscCore/v1/users/{login}/{propertyLabel}` | DELETE | core | | |
| 227 | `/rest/ofscCore/v1/users/{login}/collaborationGroups` | GET | core | | |
| 228 | `/rest/ofscCore/v1/users/{login}/collaborationGroups` | POST | core | | |
| 229 | `/rest/ofscCore/v1/users/{login}/collaborationGroups` | DELETE | core | | |
| 230 | `/rest/oauthTokenService/v1/token` | POST | auth | | |
| 231 | `/rest/oauthTokenService/v2/token` | POST | auth | | |
| 232 | `/rest/ofscCapacity/v1/activityBookingOptions` | GET | capacity | v3.0.0-dev | `async def get_activity_booking_options(self, activity_id: str, date: str, duration: Optional[int] = None, travel_time: Optional[int] = None) -> ActivityBookingOptionsResponse` |
| 233 | `/rest/ofscCapacity/v1/bookingClosingSchedule` | GET | capacity | v3.0.0-dev | `async def get_booking_closing_schedule(self, areas: Optional[List[str]] = None) -> BookingClosingScheduleListResponse` |
| 234 | `/rest/ofscCapacity/v1/bookingClosingSchedule` | PATCH | capacity | | |
| 235 | `/rest/ofscCapacity/v1/bookingStatuses` | GET | capacity | v3.0.0-dev | `async def get_booking_statuses(self, dates: List[str], areas: Optional[List[str]] = None) -> BookingStatusListResponse` |
| 236 | `/rest/ofscCapacity/v1/bookingStatuses` | PATCH | capacity | | |
| 237 | `/rest/ofscCapacity/v1/capacity` | GET | capacity | v3.0.0-dev | `async def get_capacity(self, dates: List[str], areas: Optional[List[str]] = None, categories: Optional[List[str]] = None, fields: Optional[List[str]] = None, aggregateResults: bool = False, availableTimeIntervals: str = "all", calendarTimeIntervals: str = "all") -> GetCapacityResponse` |
| 238 | `/rest/ofscCapacity/v1/quota` | GET | capacity | v3.0.0-dev | `async def get_quota(self, dates: List[str], areas: Optional[List[str]] = None, categories: Optional[List[str]] = None, aggregateResults: Optional[bool] = None, categoryLevel: Optional[bool] = None, intervalLevel: Optional[bool] = None, returnStatuses: Optional[bool] = None, timeSlotLevel: Optional[bool] = None) -> GetQuotaResponse` |
| 239 | `/rest/ofscCapacity/v1/quota` | PATCH | capacity | v3.0.0-dev | `async def patch_quota(self, dates: List[str], areas: Optional[List[str]] = None, categories: Optional[List[str]] = None, aggregateResults: Optional[bool] = None, categoryLevel: Optional[bool] = None, intervalLevel: Optional[bool] = None, returnStatuses: Optional[bool] = None, timeSlotLevel: Optional[bool] = None) -> GetQuotaResponse` |
| 240 | `/rest/ofscCapacity/v2/quota` | GET | capacity | v3.0.0-dev | `async def get_quota_v2(self, dates: List[str], areas: Optional[List[str]] = None, categories: Optional[List[str]] = None, aggregateResults: Optional[bool] = None, categoryLevel: Optional[bool] = None, intervalLevel: Optional[bool] = None, returnStatuses: Optional[bool] = None, timeSlotLevel: Optional[bool] = None) -> GetQuotaV2Response` |
| 241 | `/rest/ofscCapacity/v2/quota` | PATCH | capacity | | |
| 242 | `/rest/ofscCapacity/v1/showBookingGrid` | POST | capacity | | |

## Implementation Notes

### v3.0 Architecture
- **Async-Only**: All v3.0 implementations use `async def` and must be awaited
- **Type Safety**: Full type annotations with Pydantic model return types
- **Client Location**: v3.0 implementations are in `/ofsc/client/` directory
  - `metadata_api.py`: Metadata API endpoints (49 endpoints)
  - `core_api.py`: Core API endpoints (2 endpoints)
  - `capacity_api.py`: Capacity API endpoints (7 endpoints)
  - No v3.0 implementations for statistics, collaboration, auth, or partscatalog modules yet

### Method Signatures
- All methods follow async/await pattern: `async def method_name(...) -> ReturnType`
- Parameters include proper type hints and default values
- Return types use specific Pydantic models (e.g., `PropertyListResponse`, `UserListResponse`)

### Legacy Support
- v2.x implementations still exist in root `/ofsc/` directory for backward compatibility
- v3.0 development is ongoing - most endpoints are not yet implemented in the new architecture

## Recent Additions

### July 23, 2025
- **Core API Activities and Resources Implementation**: Added 13 new Core API endpoints
  - **Activities API (10 endpoints)**: Complete CRUD operations plus state transitions
    - `get_activities` - Search and list activities with filtering
    - `create_activity` - Create new activities
    - `get_activity` - Get specific activity by ID
    - `update_activity` - Update activity properties (PATCH)
    - `delete_activity` - Delete activities
    - `search_activities` - Advanced activity search
    - `start_activity` - Change activity status to started
    - `complete_activity` - Change activity status to completed
    - `cancel_activity` - Change activity status to cancelled
    - `bulk_update_activities` - Bulk update multiple activities
  - **Resources API (3 endpoints)**: Basic resource management
    - `get_resources` - List resources with pagination
    - `get_resource` - Get specific resource with optional related data
    - `update_resource` - Update resource properties
  - All endpoints include parameter validation and return typed Pydantic models
  - Follows established async-only architecture patterns
- **Extended Core API Implementation**: Added 12 more essential endpoints
  - **Daily Extract API (3 endpoints)**: Complete daily extract functionality
    - `get_daily_extract_dates` - Get available extract dates
    - `get_daily_extract_files` - Get files for specific date
    - `get_daily_extract_file` - Download specific extract file
  - **Extended User Management (4 endpoints)**: Complete user lifecycle
    - `get_user` - Get specific user by login
    - `create_user` - Create new users
    - `update_user` - Update user properties
    - `delete_user` - Delete users
  - **Extended Resource Management (5 endpoints)**: Resource relationships and schedules
    - `get_resource_users` - Get users associated with resource
    - `set_resource_users` - Associate users with resource
    - `delete_resource_users` - Remove user associations
    - `get_resource_work_schedules` - Get resource work schedules
    - `get_resource_descendants` - Get descendant resources in hierarchy

### January 15, 2025
- **get_timeslots** (Endpoint #67): Added support for retrieving time slot definitions from `/rest/ofscMetadata/v1/timeSlots`
  - Supports both timed slots (with `timeStart`/`timeEnd`) and all-day slots (`isAllDay=True`)
  - Includes pagination parameters (`offset`, `limit`) with validation
  - Returns `TimeSlotListResponse` with proper model validation
  - Full test coverage including unit tests and model validation against response examples

### January 16, 2025
- **Capacity Area Sub-Resource Endpoints (Endpoints #16, #17, #19, #20, #21)**: Added complete implementation for capacity area sub-resource management
  - **get_capacity_area_categories** (Endpoint #16): Retrieve capacity categories for specific capacity areas
  - **get_capacity_area_workzones** (Endpoint #17): Retrieve work zones for capacity areas using v2 endpoint with detailed information
  - **get_capacity_area_timeslots** (Endpoint #19): Retrieve time slots configured for specific capacity areas
  - **get_capacity_area_timeintervals** (Endpoint #20): Retrieve time intervals for capacity areas
  - **get_capacity_area_organizations** (Endpoint #21): Retrieve organizations associated with capacity areas
  - All endpoints include proper parameter validation, pagination support, and URL encoding for area labels
  - Complete test coverage including end-to-end tests, unit tests, and model validation
  - Removed deprecated v1 workZones endpoint implementation while maintaining DEPRECATED status in documentation

---

*Generated from endpoints.json data for pyOFSC Python Wrapper v3.0  
Last updated: July 23, 2025 - Added 25 Core API endpoints with complete signatures*