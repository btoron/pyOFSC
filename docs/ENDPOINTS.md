# OFSC API Endpoints Reference

This document provides a comprehensive reference of all Oracle Field Service Cloud (OFSC) API endpoints available in the pyOFSC Python Wrapper v3.0.

**Total Endpoints:** 242  
**Implemented in v3.0:** 27 (11.2%)

## Implementation Coverage by Module

- **metadata**: 25/86 endpoints (29.1%) ✅
- **core**: 2/127 endpoints (1.6%) ⚠️  
- **capacity**: 0/11 endpoints (0%) ❌
- **statistics**: 0/6 endpoints (0%) ❌
- **partscatalog**: 0/3 endpoints (0%) ❌
- **collaboration**: 0/7 endpoints (0%) ❌
- **auth**: 0/2 endpoints (0%) ❌

## Endpoints Table

| ID | Endpoint Path | Method | Module | Implemented In | Signature |
|----|---------------|--------|---------|---------------|-----------|
| 1 | `/rest/ofscMetadata/v1/activityTypeGroups` | GET | metadata | v3.0.0-dev | `async def get_activity_type_groups(self, offset: int = 0, limit: int = 100) -> ActivityTypeGroupListResponse` |
| 2 | `/rest/ofscMetadata/v1/activityTypeGroups/{label}` | GET | metadata | v3.0.0-dev | `async def get_activity_type_group(self, label: str) -> ActivityTypeGroup` |
| 3 | `/rest/ofscMetadata/v1/activityTypeGroups/{label}` | PUT | metadata | | |
| 4 | `/rest/ofscMetadata/v1/activityTypes` | GET | metadata | v3.0.0-dev | `async def get_activity_types(self, offset: int = 0, limit: int = 100) -> ActivityTypeListResponse` |
| 5 | `/rest/ofscMetadata/v1/activityTypes/{label}` | GET | metadata | v3.0.0-dev | `async def get_activity_type(self, label: str) -> ActivityType` |
| 6 | `/rest/ofscMetadata/v1/activityTypes/{label}` | PUT | metadata | | |
| 7 | `/rest/ofscMetadata/v1/applications` | GET | metadata | v3.0.0-dev | `async def get_applications(self) -> ApplicationListResponse` |
| 8 | `/rest/ofscMetadata/v1/applications/{label}` | GET | metadata | v3.0.0-dev | `async def get_application(self, label: str) -> Application` |
| 9 | `/rest/ofscMetadata/v1/applications/{label}` | PUT | metadata | | |
| 10 | `/rest/ofscMetadata/v1/applications/{label}/apiAccess` | GET | metadata | v3.0.0-dev | `async def get_application_api_accesses(self, label: str) -> dict` |
| 11 | `/rest/ofscMetadata/v1/applications/{label}/apiAccess/{apiLabel}` | GET | metadata | v3.0.0-dev | `async def get_application_api_access(self, label: str, accessId: str) -> dict` |
| 12 | `/rest/ofscMetadata/v1/applications/{label}/apiAccess/{apiLabel}` | PATCH | metadata | | |
| 13 | `/rest/ofscMetadata/v1/applications/{label}/custom-actions/generateClientSecret` | POST | metadata | | |
| 14 | `/rest/ofscMetadata/v1/capacityAreas` | GET | metadata | v3.0.0-dev | `async def get_capacity_areas(self, expandParent: bool = False, fields: List[str] = ["label"], activeOnly: bool = False, areasOnly: bool = False) -> CapacityAreaListResponse` |
| 15 | `/rest/ofscMetadata/v1/capacityAreas/{label}` | GET | metadata | v3.0.0-dev | `async def get_capacity_area(self, label: str) -> CapacityArea` |
| 16 | `/rest/ofscMetadata/v1/capacityAreas/{label}/capacityCategories` | GET | metadata | | |
| 17 | `/rest/ofscMetadata/v2/capacityAreas/{label}/workZones` | GET | metadata | | |
| 18 | `/rest/ofscMetadata/v1/capacityAreas/{label}/workZones` | GET | metadata | | |
| 19 | `/rest/ofscMetadata/v1/capacityAreas/{label}/timeSlots` | GET | metadata | | |
| 20 | `/rest/ofscMetadata/v1/capacityAreas/{label}/timeIntervals` | GET | metadata | | |
| 21 | `/rest/ofscMetadata/v1/capacityAreas/{label}/organizations` | GET | metadata | | |
| 22 | `/rest/ofscMetadata/v1/capacityAreas/{label}/children` | GET | metadata | | |
| 23 | `/rest/ofscMetadata/v1/capacityCategories` | GET | metadata | v3.0.0-dev | `async def get_capacity_categories(self, offset: int = 0, limit: int = 100) -> CapacityCategoryListResponse` |
| 24 | `/rest/ofscMetadata/v1/capacityCategories/{label}` | GET | metadata | v3.0.0-dev | `async def get_capacity_category(self, label: str) -> CapacityCategory` |
| 25 | `/rest/ofscMetadata/v1/capacityCategories/{label}` | PUT | metadata | | |
| 26 | `/rest/ofscMetadata/v1/capacityCategories/{label}` | DELETE | metadata | | |
| 27 | `/rest/ofscMetadata/v1/forms` | GET | metadata | | |
| 28 | `/rest/ofscMetadata/v1/forms/{label}` | GET | metadata | | |
| 29 | `/rest/ofscMetadata/v1/forms/{label}` | PUT | metadata | | |
| 30 | `/rest/ofscMetadata/v1/forms/{label}` | DELETE | metadata | | |
| 31 | `/rest/ofscMetadata/v1/inventoryTypes` | GET | metadata | v3.0.0-dev | `async def get_inventory_types(self) -> InventoryTypeListResponse` |
| 32 | `/rest/ofscMetadata/v1/inventoryTypes/{label}` | GET | metadata | v3.0.0-dev | `async def get_inventory_type(self, label: str) -> InventoryType` |
| 33 | `/rest/ofscMetadata/v1/inventoryTypes/{label}` | PUT | metadata | | |
| 34 | `/rest/ofscMetadata/v1/languages` | GET | metadata | | |
| 35 | `/rest/ofscMetadata/v1/linkTemplates` | GET | metadata | | |
| 36 | `/rest/ofscMetadata/v1/linkTemplates/{label}` | GET | metadata | | |
| 37 | `/rest/ofscMetadata/v1/linkTemplates/{label}` | POST | metadata | | |
| 38 | `/rest/ofscMetadata/v1/linkTemplates/{label}` | PATCH | metadata | | |
| 39 | `/rest/ofscMetadata/v1/mapLayers` | GET | metadata | | |
| 40 | `/rest/ofscMetadata/v1/mapLayers` | POST | metadata | | |
| 41 | `/rest/ofscMetadata/v1/mapLayers/{label}` | GET | metadata | | |
| 42 | `/rest/ofscMetadata/v1/mapLayers/{label}` | PUT | metadata | | |
| 43 | `/rest/ofscMetadata/v1/mapLayers/custom-actions/populateLayers/{downloadId}` | GET | metadata | | |
| 44 | `/rest/ofscMetadata/v1/mapLayers/custom-actions/populateLayers` | POST | metadata | | |
| 45 | `/rest/ofscMetadata/v1/nonWorkingReasons` | GET | metadata | | |
| 46 | `/rest/ofscMetadata/v1/organizations` | GET | metadata | v3.0.0-dev | `async def get_organizations(self) -> OrganizationListResponse` |
| 47 | `/rest/ofscMetadata/v1/organizations/{label}` | GET | metadata | v3.0.0-dev | `async def get_organization(self, label: str) -> Organization` |
| 48 | `/rest/ofscMetadata/v1/plugins/custom-actions/import` | POST | metadata | | |
| 49 | `/rest/ofscMetadata/v1/plugins/{pluginLabel}/custom-actions/install` | POST | metadata | | |
| 50 | `/rest/ofscMetadata/v1/properties` | GET | metadata | v3.0.0-dev | `async def get_properties(self, offset: int = 0, limit: int = 100) -> PropertyListResponse` |
| 51 | `/rest/ofscMetadata/v1/properties/{label}` | GET | metadata | v3.0.0-dev | `async def get_property(self, label: str) -> Property` |
| 52 | `/rest/ofscMetadata/v1/properties/{label}` | PUT | metadata | | |
| 53 | `/rest/ofscMetadata/v1/properties/{label}` | PATCH | metadata | | |
| 54 | `/rest/ofscMetadata/v1/properties/{label}/enumerationList` | GET | metadata | v3.0.0-dev | `async def get_enumeration_values(self, label: str, offset: int = 0, limit: int = 100) -> EnumerationValueList` |
| 55 | `/rest/ofscMetadata/v1/properties/{label}/enumerationList` | PUT | metadata | | |
| 56 | `/rest/ofscMetadata/v1/resourceTypes` | GET | metadata | v3.0.0-dev | `async def get_resource_types(self) -> ResourceTypeListResponse` |
| 57 | `/rest/ofscMetadata/v1/routingProfiles` | GET | metadata | | |
| 58 | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans` | GET | metadata | | |
| 59 | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/{planLabel}/custom-actions/export` | GET | metadata | | |
| 60 | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/custom-actions/import` | PUT | metadata | | |
| 61 | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/custom-actions/forceImport` | PUT | metadata | | |
| 62 | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/{planLabel}/{resourceExternalId}/{date}/custom-actions/start` | POST | metadata | | |
| 63 | `/rest/ofscMetadata/v1/shifts` | GET | metadata | | |
| 64 | `/rest/ofscMetadata/v1/shifts/{label}` | GET | metadata | | |
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
| 82 | `/rest/ofscMetadata/v1/workZones/{label}` | GET | metadata | | |
| 83 | `/rest/ofscMetadata/v1/workZones/{label}` | PUT | metadata | | |
| 84 | `/rest/ofscMetadata/v1/workZones/custom-actions/populateShapes/{downloadId}` | GET | metadata | | |
| 85 | `/rest/ofscMetadata/v1/workZones/custom-actions/populateShapes` | POST | metadata | | |
| 86 | `/rest/ofscMetadata/v1/workZoneKey` | GET | metadata | | |
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
| 103 | `/rest/ofscCore/v1/activities` | POST | core | | |
| 104 | `/rest/ofscCore/v1/activities` | GET | core | | |
| 105 | `/rest/ofscCore/v1/activities/{activityId}` | PATCH | core | | |
| 106 | `/rest/ofscCore/v1/activities/{activityId}` | DELETE | core | | |
| 107 | `/rest/ofscCore/v1/activities/{activityId}` | GET | core | | |
| 108 | `/rest/ofscCore/v1/activities/{activityId}/multidaySegments` | GET | core | | |
| 109 | `/rest/ofscCore/v1/activities/{activityId}/{propertyLabel}` | PUT | core | | |
| 110 | `/rest/ofscCore/v1/activities/{activityId}/{propertyLabel}` | GET | core | | |
| 111 | `/rest/ofscCore/v1/activities/{activityId}/{propertyLabel}` | DELETE | core | | |
| 112 | `/rest/ofscCore/v1/activities/{activityId}/submittedForms` | GET | core | | |
| 113 | `/rest/ofscCore/v1/activities/{activityId}/resourcePreferences` | PUT | core | | |
| 114 | `/rest/ofscCore/v1/activities/{activityId}/resourcePreferences` | GET | core | | |
| 115 | `/rest/ofscCore/v1/activities/{activityId}/resourcePreferences` | DELETE | core | | |
| 116 | `/rest/ofscCore/v1/activities/{activityId}/requiredInventories` | PUT | core | | |
| 117 | `/rest/ofscCore/v1/activities/{activityId}/requiredInventories` | GET | core | | |
| 118 | `/rest/ofscCore/v1/activities/{activityId}/requiredInventories` | DELETE | core | | |
| 119 | `/rest/ofscCore/v1/activities/{activityId}/customerInventories` | POST | core | | |
| 120 | `/rest/ofscCore/v1/activities/{activityId}/customerInventories` | GET | core | | |
| 121 | `/rest/ofscCore/v1/activities/{activityId}/installedInventories` | GET | core | | |
| 122 | `/rest/ofscCore/v1/activities/{activityId}/deinstalledInventories` | GET | core | | |
| 123 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities` | GET | core | | |
| 124 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities` | DELETE | core | | |
| 125 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities` | POST | core | | |
| 126 | `/rest/ofscCore/v1/activities/{activityId}/capacityCategories` | GET | core | | |
| 127 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities/{linkedActivityId}/linkTypes/{linkType}` | DELETE | core | | |
| 128 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities/{linkedActivityId}/linkTypes/{linkType}` | GET | core | | |
| 129 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities/{linkedActivityId}/linkTypes/{linkType}` | PUT | core | | |
| 130 | `/rest/ofscCore/v1/activities/custom-actions/search` | GET | core | | |
| 131 | `/rest/ofscCore/v1/activities/custom-actions/bulkUpdate` | POST | core | | |
| 132 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/startPrework` | POST | core | | |
| 133 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/reopen` | POST | core | | |
| 134 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/delay` | POST | core | | |
| 135 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/cancel` | POST | core | | |
| 136 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/start` | POST | core | | |
| 137 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/enroute` | POST | core | | |
| 138 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/stopTravel` | POST | core | | |
| 139 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/suspend` | POST | core | | |
| 140 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/move` | POST | core | | |
| 141 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/complete` | POST | core | | |
| 142 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/notDone` | POST | core | | |
| 143 | `/rest/ofscCore/v1/whereIsMyTech` | GET | core | | |
| 144 | `/rest/ofscCore/v1/folders/dailyExtract/folders` | GET | core | | |
| 145 | `/rest/ofscCore/v1/folders/dailyExtract/folders/{dailyExtractDate}/files` | GET | core | | |
| 146 | `/rest/ofscCore/v1/folders/dailyExtract/folders/{dailyExtractDate}/files/{dailyExtractFilename}` | GET | core | | |
| 147 | `/rest/ofscCore/v1/events/subscriptions/{subscriptionId}` | DELETE | core | | |
| 148 | `/rest/ofscCore/v1/events/subscriptions/{subscriptionId}` | GET | core | | |
| 149 | `/rest/ofscCore/v1/events/subscriptions` | GET | core | v3.0.0-dev | `async def get_subscriptions(self, allSubscriptions: bool = False) -> SubscriptionList` |
| 150 | `/rest/ofscCore/v1/events/subscriptions` | POST | core | | |
| 151 | `/rest/ofscCore/v1/events` | GET | core | | |
| 152 | `/rest/ofscCore/v1/inventories` | POST | core | | |
| 153 | `/rest/ofscCore/v1/inventories/{inventoryId}` | PATCH | core | | |
| 154 | `/rest/ofscCore/v1/inventories/{inventoryId}` | GET | core | | |
| 155 | `/rest/ofscCore/v1/inventories/{inventoryId}` | DELETE | core | | |
| 156 | `/rest/ofscCore/v1/inventories/{inventoryId}/{propertyLabel}` | PUT | core | | |
| 157 | `/rest/ofscCore/v1/inventories/{inventoryId}/{propertyLabel}` | GET | core | | |
| 158 | `/rest/ofscCore/v1/inventories/{inventoryId}/{propertyLabel}` | DELETE | core | | |
| 159 | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/undoInstall` | POST | core | | |
| 160 | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/undoDeinstall` | POST | core | | |
| 161 | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/install` | POST | core | | |
| 162 | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/deinstall` | POST | core | | |
| 163 | `/rest/ofscCore/v1/resources` | GET | core | | |
| 164 | `/rest/ofscCore/v1/resources/{resourceId}/children` | GET | core | | |
| 165 | `/rest/ofscCore/v1/resources/{resourceId}/descendants` | GET | core | | |
| 166 | `/rest/ofscCore/v1/resources/{resourceId}/assistants` | GET | core | | |
| 167 | `/rest/ofscCore/v1/resources/{resourceId}` | GET | core | | |
| 168 | `/rest/ofscCore/v1/resources/{resourceId}` | PUT | core | | |
| 169 | `/rest/ofscCore/v1/resources/{resourceId}` | PATCH | core | | |
| 170 | `/rest/ofscCore/v1/resources/{resourceId}/users` | GET | core | | |
| 171 | `/rest/ofscCore/v1/resources/{resourceId}/users` | PUT | core | | |
| 172 | `/rest/ofscCore/v1/resources/{resourceId}/users` | DELETE | core | | |
| 173 | `/rest/ofscCore/v1/resources/{resourceId}/inventories` | POST | core | | |
| 174 | `/rest/ofscCore/v1/resources/{resourceId}/inventories` | GET | core | | |
| 175 | `/rest/ofscCore/v1/resources/{resourceId}/inventories/{inventoryId}/custom-actions/install` | POST | core | | |
| 176 | `/rest/ofscCore/v1/resources/{resourceId}/workSkills` | POST | core | | |
| 177 | `/rest/ofscCore/v1/resources/{resourceId}/workSkills` | GET | core | | |
| 178 | `/rest/ofscCore/v1/resources/{resourceId}/workSkills/{workSkill}` | DELETE | core | | |
| 179 | `/rest/ofscCore/v1/resources/{resourceId}/workZones` | POST | core | | |
| 180 | `/rest/ofscCore/v1/resources/{resourceId}/workZones` | GET | core | | |
| 181 | `/rest/ofscCore/v1/resources/{resourceId}/workZones/{workZoneItemId}` | DELETE | core | | |
| 182 | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules` | GET | core | | |
| 183 | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules` | POST | core | | |
| 184 | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules/{scheduleItemId}` | DELETE | core | | |
| 185 | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules/calendarView` | GET | core | | |
| 186 | `/rest/ofscCore/v1/calendars` | GET | core | | |
| 187 | `/rest/ofscCore/v1/resources/{resourceId}/{propertyLabel}` | PUT | core | | |
| 188 | `/rest/ofscCore/v1/resources/{resourceId}/{propertyLabel}` | GET | core | | |
| 189 | `/rest/ofscCore/v1/resources/{resourceId}/{propertyLabel}` | DELETE | core | | |
| 190 | `/rest/ofscCore/v1/resources/{resourceId}/locations` | POST | core | | |
| 191 | `/rest/ofscCore/v1/resources/{resourceId}/locations` | GET | core | | |
| 192 | `/rest/ofscCore/v1/resources/{resourceId}/locations/{locationId}` | GET | core | | |
| 193 | `/rest/ofscCore/v1/resources/{resourceId}/locations/{locationId}` | PATCH | core | | |
| 194 | `/rest/ofscCore/v1/resources/{resourceId}/locations/{locationId}` | DELETE | core | | |
| 195 | `/rest/ofscCore/v1/resources/{resourceId}/positionHistory` | GET | core | | |
| 196 | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations` | PUT | core | | |
| 197 | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations` | GET | core | | |
| 198 | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations` | PATCH | core | | |
| 199 | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations/{date}` | DELETE | core | | |
| 200 | `/rest/ofscCore/v1/resources/{resourceId}/plans` | POST | core | | |
| 201 | `/rest/ofscCore/v1/resources/{resourceId}/plans` | GET | core | | |
| 202 | `/rest/ofscCore/v1/resources/{resourceId}/plans` | DELETE | core | | |
| 203 | `/rest/ofscCore/v1/resources/{resourceId}/routes/{date}` | GET | core | | |
| 204 | `/rest/ofscCore/v1/resources/{resourceId}/routes/{date}/custom-actions/activate` | POST | core | | |
| 205 | `/rest/ofscCore/v1/resources/{resourceId}/routes/{date}/custom-actions/deactivate` | POST | core | | |
| 206 | `/rest/ofscCore/v1/resources/{resourceId}/findNearbyActivities` | GET | core | | |
| 207 | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkSchedules` | POST | core | | |
| 208 | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkSkills` | POST | core | | |
| 209 | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkZones` | POST | core | | |
| 210 | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateInventories` | POST | core | | |
| 211 | `/rest/ofscCore/v1/resources/custom-actions/findMatchingResources` | POST | core | | |
| 212 | `/rest/ofscCore/v1/resources/custom-actions/findResourcesForUrgentAssignment` | POST | core | | |
| 213 | `/rest/ofscCore/v1/resources/custom-actions/setPositions` | POST | core | | |
| 214 | `/rest/ofscCore/v1/resources/custom-actions/lastKnownPositions` | GET | core | | |
| 215 | `/rest/ofscCore/v1/resources/custom-actions/resourcesInArea` | GET | core | | |
| 216 | `/rest/ofscCore/v1/serviceRequests/{requestId}` | GET | core | | |
| 217 | `/rest/ofscCore/v1/serviceRequests` | POST | core | | |
| 218 | `/rest/ofscCore/v1/serviceRequests/{requestId}/{propertyLabel}` | GET | core | | |
| 219 | `/rest/ofscCore/v1/users` | GET | core | v3.0.0-dev | `async def get_users(self, offset: int = 0, limit: int = 100) -> UserListResponse` |
| 220 | `/rest/ofscCore/v1/users/{login}` | GET | core | | |
| 221 | `/rest/ofscCore/v1/users/{login}` | PUT | core | | |
| 222 | `/rest/ofscCore/v1/users/{login}` | PATCH | core | | |
| 223 | `/rest/ofscCore/v1/users/{login}` | DELETE | core | | |
| 224 | `/rest/ofscCore/v1/users/{login}/{propertyLabel}` | PUT | core | | |
| 225 | `/rest/ofscCore/v1/users/{login}/{propertyLabel}` | GET | core | | |
| 226 | `/rest/ofscCore/v1/users/{login}/{propertyLabel}` | DELETE | core | | |
| 227 | `/rest/ofscCore/v1/users/{login}/collaborationGroups` | GET | core | | |
| 228 | `/rest/ofscCore/v1/users/{login}/collaborationGroups` | POST | core | | |
| 229 | `/rest/ofscCore/v1/users/{login}/collaborationGroups` | DELETE | core | | |
| 230 | `/rest/oauthTokenService/v1/token` | POST | auth | | |
| 231 | `/rest/oauthTokenService/v2/token` | POST | auth | | |
| 232 | `/rest/ofscCapacity/v1/activityBookingOptions` | GET | capacity | | |
| 233 | `/rest/ofscCapacity/v1/bookingClosingSchedule` | GET | capacity | | |
| 234 | `/rest/ofscCapacity/v1/bookingClosingSchedule` | PATCH | capacity | | |
| 235 | `/rest/ofscCapacity/v1/bookingStatuses` | GET | capacity | | |
| 236 | `/rest/ofscCapacity/v1/bookingStatuses` | PATCH | capacity | | |
| 237 | `/rest/ofscCapacity/v1/capacity` | GET | capacity | | |
| 238 | `/rest/ofscCapacity/v1/quota` | GET | capacity | | |
| 239 | `/rest/ofscCapacity/v1/quota` | PATCH | capacity | | |
| 240 | `/rest/ofscCapacity/v2/quota` | GET | capacity | | |
| 241 | `/rest/ofscCapacity/v2/quota` | PATCH | capacity | | |
| 242 | `/rest/ofscCapacity/v1/showBookingGrid` | POST | capacity | | |

## Implementation Notes

### v3.0 Architecture
- **Async-Only**: All v3.0 implementations use `async def` and must be awaited
- **Type Safety**: Full type annotations with Pydantic model return types
- **Client Location**: v3.0 implementations are in `/ofsc/client/` directory
  - `metadata_api.py`: Metadata API endpoints
  - `core_api.py`: Core API endpoints
  - No v3.0 implementations for capacity, statistics, collaboration, auth, or partscatalog modules yet

### Method Signatures
- All methods follow async/await pattern: `async def method_name(...) -> ReturnType`
- Parameters include proper type hints and default values
- Return types use specific Pydantic models (e.g., `PropertyListResponse`, `UserListResponse`)

### Legacy Support
- v2.x implementations still exist in root `/ofsc/` directory for backward compatibility
- v3.0 development is ongoing - most endpoints are not yet implemented in the new architecture

## Recent Additions

### June 28, 2025
- **get_timeslots** (Endpoint #67): Added support for retrieving time slot definitions from `/rest/ofscMetadata/v1/timeSlots`
  - Supports both timed slots (with `timeStart`/`timeEnd`) and all-day slots (`isAllDay=True`)
  - Includes pagination parameters (`offset`, `limit`) with validation
  - Returns `TimeSlotListResponse` with proper model validation
  - Full test coverage including unit tests and model validation against response examples

---

*Generated from endpoints.json data for pyOFSC Python Wrapper v3.0  
Last updated: June 28, 2025 - Added get_timeslots endpoint*