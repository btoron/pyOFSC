# OFSC API Endpoints Reference

**Version:** 2.20.0
**Last Updated:** 2025-12-26

This document provides a comprehensive reference of all Oracle Field Service Cloud (OFSC) API endpoints and their implementation status in pyOFSC.

**Total Endpoints:** 242

## Implementation Status

- `sync` - Implemented in synchronous client only
- `async` - Implemented in asynchronous client only
- `both` - Implemented in both sync and async clients
- `-` - Not implemented

## Endpoints Table

| ID | Endpoint | Module | Method | Status |
|----|----------|--------|--------|--------|
| 1 | `/rest/ofscMetadata/v1/activityTypeGroups` | metadata | GET | both |
| 2 | `/rest/ofscMetadata/v1/activityTypeGroups/{label}` | metadata | GET | both |
| 3 | `/rest/ofscMetadata/v1/activityTypeGroups/{label}` | metadata | PUT | - |
| 4 | `/rest/ofscMetadata/v1/activityTypes` | metadata | GET | both |
| 5 | `/rest/ofscMetadata/v1/activityTypes/{label}` | metadata | GET | both |
| 6 | `/rest/ofscMetadata/v1/activityTypes/{label}` | metadata | PUT | - |
| 7 | `/rest/ofscMetadata/v1/applications` | metadata | GET | sync |
| 8 | `/rest/ofscMetadata/v1/applications/{label}` | metadata | GET | sync |
| 9 | `/rest/ofscMetadata/v1/applications/{label}` | metadata | PUT | - |
| 10 | `/rest/ofscMetadata/v1/applications/{label}/apiAccess` | metadata | GET | sync |
| 11 | `/rest/ofscMetadata/v1/applications/{label}/apiAccess/{apiLabel}` | metadata | GET | sync |
| 12 | `/rest/ofscMetadata/v1/applications/{label}/apiAccess/{apiLabel}` | metadata | PATCH | - |
| 13 | `/rest/ofscMetadata/v1/applications/{label}/custom-actions/generateClientSecret` | metadata | POST | - |
| 14 | `/rest/ofscMetadata/v1/capacityAreas` | metadata | GET | sync |
| 15 | `/rest/ofscMetadata/v1/capacityAreas/{label}` | metadata | GET | sync |
| 16 | `/rest/ofscMetadata/v1/capacityAreas/{label}/capacityCategories` | metadata | GET | - |
| 17 | `/rest/ofscMetadata/v2/capacityAreas/{label}/workZones` | metadata | GET | - |
| 18 | `/rest/ofscMetadata/v1/capacityAreas/{label}/workZones` | metadata | GET | - |
| 19 | `/rest/ofscMetadata/v1/capacityAreas/{label}/timeSlots` | metadata | GET | - |
| 20 | `/rest/ofscMetadata/v1/capacityAreas/{label}/timeIntervals` | metadata | GET | - |
| 21 | `/rest/ofscMetadata/v1/capacityAreas/{label}/organizations` | metadata | GET | - |
| 22 | `/rest/ofscMetadata/v1/capacityAreas/{label}/children` | metadata | GET | - |
| 23 | `/rest/ofscMetadata/v1/capacityCategories` | metadata | GET | sync |
| 24 | `/rest/ofscMetadata/v1/capacityCategories/{label}` | metadata | GET | sync |
| 25 | `/rest/ofscMetadata/v1/capacityCategories/{label}` | metadata | PUT | - |
| 26 | `/rest/ofscMetadata/v1/capacityCategories/{label}` | metadata | DELETE | - |
| 27 | `/rest/ofscMetadata/v1/forms` | metadata | GET | - |
| 28 | `/rest/ofscMetadata/v1/forms/{label}` | metadata | GET | - |
| 29 | `/rest/ofscMetadata/v1/forms/{label}` | metadata | PUT | - |
| 30 | `/rest/ofscMetadata/v1/forms/{label}` | metadata | DELETE | - |
| 31 | `/rest/ofscMetadata/v1/inventoryTypes` | metadata | GET | both |
| 32 | `/rest/ofscMetadata/v1/inventoryTypes/{label}` | metadata | GET | both |
| 33 | `/rest/ofscMetadata/v1/inventoryTypes/{label}` | metadata | PUT | - |
| 34 | `/rest/ofscMetadata/v1/languages` | metadata | GET | async |
| 35 | `/rest/ofscMetadata/v1/linkTemplates` | metadata | GET | async |
| 36 | `/rest/ofscMetadata/v1/linkTemplates/{label}` | metadata | GET | async |
| 37 | `/rest/ofscMetadata/v1/linkTemplates/{label}` | metadata | POST | - |
| 38 | `/rest/ofscMetadata/v1/linkTemplates/{label}` | metadata | PATCH | - |
| 39 | `/rest/ofscMetadata/v1/mapLayers` | metadata | GET | - |
| 40 | `/rest/ofscMetadata/v1/mapLayers` | metadata | POST | - |
| 41 | `/rest/ofscMetadata/v1/mapLayers/{label}` | metadata | GET | - |
| 42 | `/rest/ofscMetadata/v1/mapLayers/{label}` | metadata | PUT | - |
| 43 | `/rest/ofscMetadata/v1/mapLayers/custom-actions/populateLayers/{downloadId}` | metadata | GET | - |
| 44 | `/rest/ofscMetadata/v1/mapLayers/custom-actions/populateLayers` | metadata | POST | - |
| 45 | `/rest/ofscMetadata/v1/nonWorkingReasons` | metadata | GET | async |
| 46 | `/rest/ofscMetadata/v1/organizations` | metadata | GET | both |
| 47 | `/rest/ofscMetadata/v1/organizations/{label}` | metadata | GET | both |
| 48 | `/rest/ofscMetadata/v1/plugins/custom-actions/import` | metadata | POST | sync |
| 49 | `/rest/ofscMetadata/v1/plugins/{pluginLabel}/custom-actions/install` | metadata | POST | - |
| 50 | `/rest/ofscMetadata/v1/properties` | metadata | GET | both |
| 51 | `/rest/ofscMetadata/v1/properties/{label}` | metadata | GET | both |
| 52 | `/rest/ofscMetadata/v1/properties/{label}` | metadata | PUT | both |
| 53 | `/rest/ofscMetadata/v1/properties/{label}` | metadata | PATCH | - |
| 54 | `/rest/ofscMetadata/v1/properties/{label}/enumerationList` | metadata | GET | both |
| 55 | `/rest/ofscMetadata/v1/properties/{label}/enumerationList` | metadata | PUT | both |
| 56 | `/rest/ofscMetadata/v1/resourceTypes` | metadata | GET | both |
| 57 | `/rest/ofscMetadata/v1/routingProfiles` | metadata | GET | sync |
| 58 | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans` | metadata | GET | sync |
| 59 | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/{planLabel}/custom-actions/export` | metadata | GET | sync |
| 60 | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/custom-actions/import` | metadata | PUT | sync |
| 61 | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/custom-actions/forceImport` | metadata | PUT | sync |
| 62 | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/{planLabel}/{resourceExternalId}/{date}/custom-actions/start` | metadata | POST | sync |
| 63 | `/rest/ofscMetadata/v1/shifts` | metadata | GET | - |
| 64 | `/rest/ofscMetadata/v1/shifts/{label}` | metadata | GET | - |
| 65 | `/rest/ofscMetadata/v1/shifts/{label}` | metadata | DELETE | - |
| 66 | `/rest/ofscMetadata/v1/shifts/{label}` | metadata | PUT | - |
| 67 | `/rest/ofscMetadata/v1/timeSlots` | metadata | GET | async |
| 68 | `/rest/ofscMetadata/v1/workSkillConditions` | metadata | GET | sync |
| 69 | `/rest/ofscMetadata/v1/workSkillConditions` | metadata | PUT | sync |
| 70 | `/rest/ofscMetadata/v1/workSkillGroups` | metadata | GET | sync |
| 71 | `/rest/ofscMetadata/v1/workSkillGroups/{label}` | metadata | GET | sync |
| 72 | `/rest/ofscMetadata/v1/workSkillGroups/{label}` | metadata | PUT | sync |
| 73 | `/rest/ofscMetadata/v1/workSkillGroups/{label}` | metadata | DELETE | sync |
| 74 | `/rest/ofscMetadata/v1/workSkills` | metadata | GET | sync |
| 75 | `/rest/ofscMetadata/v1/workSkills/{label}` | metadata | GET | sync |
| 76 | `/rest/ofscMetadata/v1/workSkills/{label}` | metadata | PUT | sync |
| 77 | `/rest/ofscMetadata/v1/workSkills/{label}` | metadata | DELETE | sync |
| 78 | `/rest/ofscMetadata/v1/workZones` | metadata | GET | both |
| 79 | `/rest/ofscMetadata/v1/workZones` | metadata | POST | async |
| 80 | `/rest/ofscMetadata/v1/workZones` | metadata | PUT | - |
| 81 | `/rest/ofscMetadata/v1/workZones` | metadata | PATCH | - |
| 82 | `/rest/ofscMetadata/v1/workZones/{label}` | metadata | GET | both |
| 83 | `/rest/ofscMetadata/v1/workZones/{label}` | metadata | PUT | both |
| 84 | `/rest/ofscMetadata/v1/workZones/custom-actions/populateShapes/{downloadId}` | metadata | GET | - |
| 85 | `/rest/ofscMetadata/v1/workZones/custom-actions/populateShapes` | metadata | POST | - |
| 86 | `/rest/ofscMetadata/v1/workZoneKey` | metadata | GET | - |
| 87 | `/rest/ofscStatistics/v1/activityDurationStats` | statistics | GET | - |
| 88 | `/rest/ofscStatistics/v1/activityDurationStats` | statistics | PATCH | - |
| 89 | `/rest/ofscStatistics/v1/activityTravelStats` | statistics | GET | - |
| 90 | `/rest/ofscStatistics/v1/activityTravelStats` | statistics | PATCH | - |
| 91 | `/rest/ofscStatistics/v1/airlineDistanceBasedTravel` | statistics | GET | - |
| 92 | `/rest/ofscStatistics/v1/airlineDistanceBasedTravel` | statistics | PATCH | - |
| 93 | `/rest/ofscPartsCatalog/v1/catalogs/{catalog}/{language}` | partscatalog | PUT | - |
| 94 | `/rest/ofscPartsCatalog/v1/catalogs/{catalog}/{language}/{itemLabel}` | partscatalog | PUT | - |
| 95 | `/rest/ofscPartsCatalog/v1/catalogs/{catalog}/{language}/{itemLabel}` | partscatalog | DELETE | - |
| 96 | `/rest/ofscCollaboration/v1/addressBook` | collaboration | GET | - |
| 97 | `/rest/ofscCollaboration/v1/chats` | collaboration | POST | - |
| 98 | `/rest/ofscCollaboration/v1/chats/{chatId}/leave` | collaboration | POST | - |
| 99 | `/rest/ofscCollaboration/v1/chats/{chatId}/messages` | collaboration | GET | - |
| 100 | `/rest/ofscCollaboration/v1/chats/{chatId}/messages` | collaboration | POST | - |
| 101 | `/rest/ofscCollaboration/v1/chats/{chatId}/participants` | collaboration | GET | - |
| 102 | `/rest/ofscCollaboration/v1/chats/{chatId}/participants/invite` | collaboration | POST | - |
| 103 | `/rest/ofscCore/v1/activities` | core | POST | - |
| 104 | `/rest/ofscCore/v1/activities` | core | GET | sync |
| 105 | `/rest/ofscCore/v1/activities/{activityId}` | core | PATCH | sync |
| 106 | `/rest/ofscCore/v1/activities/{activityId}` | core | DELETE | sync |
| 107 | `/rest/ofscCore/v1/activities/{activityId}` | core | GET | sync |
| 108 | `/rest/ofscCore/v1/activities/{activityId}/multidaySegments` | core | GET | - |
| 109 | `/rest/ofscCore/v1/activities/{activityId}/{propertyLabel}` | core | PUT | - |
| 110 | `/rest/ofscCore/v1/activities/{activityId}/{propertyLabel}` | core | GET | sync |
| 111 | `/rest/ofscCore/v1/activities/{activityId}/{propertyLabel}` | core | DELETE | - |
| 112 | `/rest/ofscCore/v1/activities/{activityId}/submittedForms` | core | GET | - |
| 113 | `/rest/ofscCore/v1/activities/{activityId}/resourcePreferences` | core | PUT | - |
| 114 | `/rest/ofscCore/v1/activities/{activityId}/resourcePreferences` | core | GET | - |
| 115 | `/rest/ofscCore/v1/activities/{activityId}/resourcePreferences` | core | DELETE | - |
| 116 | `/rest/ofscCore/v1/activities/{activityId}/requiredInventories` | core | PUT | - |
| 117 | `/rest/ofscCore/v1/activities/{activityId}/requiredInventories` | core | GET | - |
| 118 | `/rest/ofscCore/v1/activities/{activityId}/requiredInventories` | core | DELETE | - |
| 119 | `/rest/ofscCore/v1/activities/{activityId}/customerInventories` | core | POST | - |
| 120 | `/rest/ofscCore/v1/activities/{activityId}/customerInventories` | core | GET | - |
| 121 | `/rest/ofscCore/v1/activities/{activityId}/installedInventories` | core | GET | - |
| 122 | `/rest/ofscCore/v1/activities/{activityId}/deinstalledInventories` | core | GET | - |
| 123 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities` | core | GET | - |
| 124 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities` | core | DELETE | - |
| 125 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities` | core | POST | - |
| 126 | `/rest/ofscCore/v1/activities/{activityId}/capacityCategories` | core | GET | - |
| 127 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities/{linkedActivityId}/linkTypes/{linkType}` | core | DELETE | - |
| 128 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities/{linkedActivityId}/linkTypes/{linkType}` | core | GET | - |
| 129 | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities/{linkedActivityId}/linkTypes/{linkType}` | core | PUT | - |
| 130 | `/rest/ofscCore/v1/activities/custom-actions/search` | core | GET | sync |
| 131 | `/rest/ofscCore/v1/activities/custom-actions/bulkUpdate` | core | POST | sync |
| 132 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/startPrework` | core | POST | - |
| 133 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/reopen` | core | POST | - |
| 134 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/delay` | core | POST | - |
| 135 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/cancel` | core | POST | - |
| 136 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/start` | core | POST | - |
| 137 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/enroute` | core | POST | - |
| 138 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/stopTravel` | core | POST | - |
| 139 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/suspend` | core | POST | - |
| 140 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/move` | core | POST | sync |
| 141 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/complete` | core | POST | - |
| 142 | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/notDone` | core | POST | - |
| 143 | `/rest/ofscCore/v1/whereIsMyTech` | core | GET | - |
| 144 | `/rest/ofscCore/v1/folders/dailyExtract/folders` | core | GET | sync |
| 145 | `/rest/ofscCore/v1/folders/dailyExtract/folders/{dailyExtractDate}/files` | core | GET | sync |
| 146 | `/rest/ofscCore/v1/folders/dailyExtract/folders/{dailyExtractDate}/files/{dailyExtractFilename}` | core | GET | sync |
| 147 | `/rest/ofscCore/v1/events/subscriptions/{subscriptionId}` | core | DELETE | sync |
| 148 | `/rest/ofscCore/v1/events/subscriptions/{subscriptionId}` | core | GET | sync |
| 149 | `/rest/ofscCore/v1/events/subscriptions` | core | GET | sync |
| 150 | `/rest/ofscCore/v1/events/subscriptions` | core | POST | sync |
| 151 | `/rest/ofscCore/v1/events` | core | GET | sync |
| 152 | `/rest/ofscCore/v1/inventories` | core | POST | - |
| 153 | `/rest/ofscCore/v1/inventories/{inventoryId}` | core | PATCH | - |
| 154 | `/rest/ofscCore/v1/inventories/{inventoryId}` | core | GET | - |
| 155 | `/rest/ofscCore/v1/inventories/{inventoryId}` | core | DELETE | - |
| 156 | `/rest/ofscCore/v1/inventories/{inventoryId}/{propertyLabel}` | core | PUT | - |
| 157 | `/rest/ofscCore/v1/inventories/{inventoryId}/{propertyLabel}` | core | GET | - |
| 158 | `/rest/ofscCore/v1/inventories/{inventoryId}/{propertyLabel}` | core | DELETE | - |
| 159 | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/undoInstall` | core | POST | - |
| 160 | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/undoDeinstall` | core | POST | - |
| 161 | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/install` | core | POST | - |
| 162 | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/deinstall` | core | POST | - |
| 163 | `/rest/ofscCore/v1/resources` | core | GET | sync |
| 164 | `/rest/ofscCore/v1/resources/{resourceId}/children` | core | GET | - |
| 165 | `/rest/ofscCore/v1/resources/{resourceId}/descendants` | core | GET | sync |
| 166 | `/rest/ofscCore/v1/resources/{resourceId}/assistants` | core | GET | - |
| 167 | `/rest/ofscCore/v1/resources/{resourceId}` | core | GET | sync |
| 168 | `/rest/ofscCore/v1/resources/{resourceId}` | core | PUT | sync |
| 169 | `/rest/ofscCore/v1/resources/{resourceId}` | core | PATCH | sync |
| 170 | `/rest/ofscCore/v1/resources/{resourceId}/users` | core | GET | sync |
| 171 | `/rest/ofscCore/v1/resources/{resourceId}/users` | core | PUT | sync |
| 172 | `/rest/ofscCore/v1/resources/{resourceId}/users` | core | DELETE | sync |
| 173 | `/rest/ofscCore/v1/resources/{resourceId}/inventories` | core | POST | - |
| 174 | `/rest/ofscCore/v1/resources/{resourceId}/inventories` | core | GET | sync |
| 175 | `/rest/ofscCore/v1/resources/{resourceId}/inventories/{inventoryId}/custom-actions/install` | core | POST | - |
| 176 | `/rest/ofscCore/v1/resources/{resourceId}/workSkills` | core | POST | - |
| 177 | `/rest/ofscCore/v1/resources/{resourceId}/workSkills` | core | GET | sync |
| 178 | `/rest/ofscCore/v1/resources/{resourceId}/workSkills/{workSkill}` | core | DELETE | - |
| 179 | `/rest/ofscCore/v1/resources/{resourceId}/workZones` | core | POST | - |
| 180 | `/rest/ofscCore/v1/resources/{resourceId}/workZones` | core | GET | sync |
| 181 | `/rest/ofscCore/v1/resources/{resourceId}/workZones/{workZoneItemId}` | core | DELETE | - |
| 182 | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules` | core | GET | sync |
| 183 | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules` | core | POST | sync |
| 184 | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules/{scheduleItemId}` | core | DELETE | - |
| 185 | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules/calendarView` | core | GET | sync |
| 186 | `/rest/ofscCore/v1/calendars` | core | GET | - |
| 187 | `/rest/ofscCore/v1/resources/{resourceId}/{propertyLabel}` | core | PUT | - |
| 188 | `/rest/ofscCore/v1/resources/{resourceId}/{propertyLabel}` | core | GET | - |
| 189 | `/rest/ofscCore/v1/resources/{resourceId}/{propertyLabel}` | core | DELETE | - |
| 190 | `/rest/ofscCore/v1/resources/{resourceId}/locations` | core | POST | sync |
| 191 | `/rest/ofscCore/v1/resources/{resourceId}/locations` | core | GET | sync |
| 192 | `/rest/ofscCore/v1/resources/{resourceId}/locations/{locationId}` | core | GET | - |
| 193 | `/rest/ofscCore/v1/resources/{resourceId}/locations/{locationId}` | core | PATCH | - |
| 194 | `/rest/ofscCore/v1/resources/{resourceId}/locations/{locationId}` | core | DELETE | sync |
| 195 | `/rest/ofscCore/v1/resources/{resourceId}/positionHistory` | core | GET | sync |
| 196 | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations` | core | PUT | sync |
| 197 | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations` | core | GET | sync |
| 198 | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations` | core | PATCH | - |
| 199 | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations/{date}` | core | DELETE | - |
| 200 | `/rest/ofscCore/v1/resources/{resourceId}/plans` | core | POST | - |
| 201 | `/rest/ofscCore/v1/resources/{resourceId}/plans` | core | GET | - |
| 202 | `/rest/ofscCore/v1/resources/{resourceId}/plans` | core | DELETE | - |
| 203 | `/rest/ofscCore/v1/resources/{resourceId}/routes/{date}` | core | GET | sync |
| 204 | `/rest/ofscCore/v1/resources/{resourceId}/routes/{date}/custom-actions/activate` | core | POST | - |
| 205 | `/rest/ofscCore/v1/resources/{resourceId}/routes/{date}/custom-actions/deactivate` | core | POST | - |
| 206 | `/rest/ofscCore/v1/resources/{resourceId}/findNearbyActivities` | core | GET | - |
| 207 | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkSchedules` | core | POST | sync |
| 208 | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkSkills` | core | POST | sync |
| 209 | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkZones` | core | POST | sync |
| 210 | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateInventories` | core | POST | - |
| 211 | `/rest/ofscCore/v1/resources/custom-actions/findMatchingResources` | core | POST | - |
| 212 | `/rest/ofscCore/v1/resources/custom-actions/findResourcesForUrgentAssignment` | core | POST | - |
| 213 | `/rest/ofscCore/v1/resources/custom-actions/setPositions` | core | POST | - |
| 214 | `/rest/ofscCore/v1/resources/custom-actions/lastKnownPositions` | core | GET | - |
| 215 | `/rest/ofscCore/v1/resources/custom-actions/resourcesInArea` | core | GET | - |
| 216 | `/rest/ofscCore/v1/serviceRequests/{requestId}` | core | GET | - |
| 217 | `/rest/ofscCore/v1/serviceRequests` | core | POST | - |
| 218 | `/rest/ofscCore/v1/serviceRequests/{requestId}/{propertyLabel}` | core | GET | - |
| 219 | `/rest/ofscCore/v1/users` | core | GET | sync |
| 220 | `/rest/ofscCore/v1/users/{login}` | core | GET | sync |
| 221 | `/rest/ofscCore/v1/users/{login}` | core | PUT | sync |
| 222 | `/rest/ofscCore/v1/users/{login}` | core | PATCH | sync |
| 223 | `/rest/ofscCore/v1/users/{login}` | core | DELETE | sync |
| 224 | `/rest/ofscCore/v1/users/{login}/{propertyLabel}` | core | PUT | - |
| 225 | `/rest/ofscCore/v1/users/{login}/{propertyLabel}` | core | GET | - |
| 226 | `/rest/ofscCore/v1/users/{login}/{propertyLabel}` | core | DELETE | - |
| 227 | `/rest/ofscCore/v1/users/{login}/collaborationGroups` | core | GET | - |
| 228 | `/rest/ofscCore/v1/users/{login}/collaborationGroups` | core | POST | - |
| 229 | `/rest/ofscCore/v1/users/{login}/collaborationGroups` | core | DELETE | - |
| 230 | `/rest/oauthTokenService/v1/token` | auth | POST | - |
| 231 | `/rest/oauthTokenService/v2/token` | auth | POST | - |
| 232 | `/rest/ofscCapacity/v1/activityBookingOptions` | capacity | GET | - |
| 233 | `/rest/ofscCapacity/v1/bookingClosingSchedule` | capacity | GET | - |
| 234 | `/rest/ofscCapacity/v1/bookingClosingSchedule` | capacity | PATCH | - |
| 235 | `/rest/ofscCapacity/v1/bookingStatuses` | capacity | GET | - |
| 236 | `/rest/ofscCapacity/v1/bookingStatuses` | capacity | PATCH | - |
| 237 | `/rest/ofscCapacity/v1/capacity` | capacity | GET | sync |
| 238 | `/rest/ofscCapacity/v1/quota` | capacity | GET | - |
| 239 | `/rest/ofscCapacity/v1/quota` | capacity | PATCH | - |
| 240 | `/rest/ofscCapacity/v2/quota` | capacity | GET | sync |
| 241 | `/rest/ofscCapacity/v2/quota` | capacity | PATCH | - |
| 242 | `/rest/ofscCapacity/v1/showBookingGrid` | capacity | POST | - |



## Implementation Summary

- **Sync only**: 72 endpoints
- **Async only**: 6 endpoints
- **Both**: 17 endpoints
- **Not implemented**: 147 endpoints
- **Total sync**: 89 endpoints
- **Total async**: 23 endpoints

## Implementation Statistics by Module and Method

### Synchronous Client

| Module | GET | Write (POST/PUT/PATCH) | DELETE | Total |
|:-------|----:|-----------------------:|-------:|------:|
| metadata | 30/51 (58.8%) | 10/30 (33.3%) | 2/5 (40.0%) | 42/86 (48.8%) |
| core | 25/51 (49.0%) | 15/56 (26.8%) | 5/20 (25.0%) | 45/127 (35.4%) |
| capacity | 2/6 (33.3%) | 0/5 (0.0%) | 0/0 (0%) | 2/11 (18.2%) |
| statistics | 0/3 (0.0%) | 0/3 (0.0%) | 0/0 (0%) | 0/6 (0.0%) |
| partscatalog | 0/0 (0%) | 0/2 (0.0%) | 0/1 (0.0%) | 0/3 (0.0%) |
| collaboration | 0/3 (0.0%) | 0/4 (0.0%) | 0/0 (0%) | 0/7 (0.0%) |
| auth | 0/0 (0%) | 0/2 (0.0%) | 0/0 (0%) | 0/2 (0.0%) |
| **Total** | **57/114 (50.0%)** | **25/102 (24.5%)** | **7/26 (26.9%)** | **89/242 (36.8%)** |

### Asynchronous Client

| Module | GET | Write (POST/PUT/PATCH) | DELETE | Total |
|:-------|----:|-----------------------:|-------:|------:|
| metadata | 19/51 (37.3%) | 4/30 (13.3%) | 0/5 (0.0%) | 23/86 (26.7%) |
| core | 0/51 (0.0%) | 0/56 (0.0%) | 0/20 (0.0%) | 0/127 (0.0%) |
| capacity | 0/6 (0.0%) | 0/5 (0.0%) | 0/0 (0%) | 0/11 (0.0%) |
| statistics | 0/3 (0.0%) | 0/3 (0.0%) | 0/0 (0%) | 0/6 (0.0%) |
| partscatalog | 0/0 (0%) | 0/2 (0.0%) | 0/1 (0.0%) | 0/3 (0.0%) |
| collaboration | 0/3 (0.0%) | 0/4 (0.0%) | 0/0 (0%) | 0/7 (0.0%) |
| auth | 0/0 (0%) | 0/2 (0.0%) | 0/0 (0%) | 0/2 (0.0%) |
| **Total** | **19/114 (16.7%)** | **4/102 (3.9%)** | **0/26 (0.0%)** | **23/242 (9.5%)** |
