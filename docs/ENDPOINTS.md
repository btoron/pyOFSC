# OFSC API Endpoints Reference

**Version:** 2.20.0
**Last Updated:** 2025-12-26

This document provides a comprehensive reference of all Oracle Field Service Cloud (OFSC) API endpoints and their implementation status in pyOFSC.

**Total Endpoints:** 243

## Implementation Status

- `sync` - Implemented in synchronous client only
- `async` - Implemented in asynchronous client only
- `both` - Implemented in both sync and async clients
- `-` - Not implemented

## Endpoints Table

| ID | Endpoint | Module | Method | Status |
|----|----------|--------|--------|--------|
| ME001G | `/rest/ofscMetadata/v1/activityTypeGroups` | metadata | GET | both |
| ME002G | `/rest/ofscMetadata/v1/activityTypeGroups/{label}` | metadata | GET | both |
| ME002U | `/rest/ofscMetadata/v1/activityTypeGroups/{label}` | metadata | PUT | - |
| ME003G | `/rest/ofscMetadata/v1/activityTypes` | metadata | GET | both |
| ME004G | `/rest/ofscMetadata/v1/activityTypes/{label}` | metadata | GET | both |
| ME004U | `/rest/ofscMetadata/v1/activityTypes/{label}` | metadata | PUT | - |
| ME005G | `/rest/ofscMetadata/v1/applications` | metadata | GET | sync |
| ME006G | `/rest/ofscMetadata/v1/applications/{label}` | metadata | GET | sync |
| ME006U | `/rest/ofscMetadata/v1/applications/{label}` | metadata | PUT | - |
| ME007G | `/rest/ofscMetadata/v1/applications/{label}/apiAccess` | metadata | GET | sync |
| ME008G | `/rest/ofscMetadata/v1/applications/{label}/apiAccess/{apiLabel}` | metadata | GET | sync |
| ME008A | `/rest/ofscMetadata/v1/applications/{label}/apiAccess/{apiLabel}` | metadata | PATCH | - |
| ME009P | `/rest/ofscMetadata/v1/applications/{label}/custom-actions/generateClientSecret` | metadata | POST | - |
| ME010G | `/rest/ofscMetadata/v1/capacityAreas` | metadata | GET | sync |
| ME011G | `/rest/ofscMetadata/v1/capacityAreas/{label}` | metadata | GET | sync |
| ME012G | `/rest/ofscMetadata/v1/capacityAreas/{label}/capacityCategories` | metadata | GET | - |
| ME013G | `/rest/ofscMetadata/v2/capacityAreas/{label}/workZones` | metadata | GET | - |
| ME014G | `/rest/ofscMetadata/v1/capacityAreas/{label}/workZones` | metadata | GET | - |
| ME015G | `/rest/ofscMetadata/v1/capacityAreas/{label}/timeSlots` | metadata | GET | - |
| ME016G | `/rest/ofscMetadata/v1/capacityAreas/{label}/timeIntervals` | metadata | GET | - |
| ME017G | `/rest/ofscMetadata/v1/capacityAreas/{label}/organizations` | metadata | GET | - |
| ME018G | `/rest/ofscMetadata/v1/capacityAreas/{label}/children` | metadata | GET | - |
| ME019G | `/rest/ofscMetadata/v1/capacityCategories` | metadata | GET | sync |
| ME020G | `/rest/ofscMetadata/v1/capacityCategories/{label}` | metadata | GET | sync |
| ME020U | `/rest/ofscMetadata/v1/capacityCategories/{label}` | metadata | PUT | - |
| ME020D | `/rest/ofscMetadata/v1/capacityCategories/{label}` | metadata | DELETE | - |
| ME021G | `/rest/ofscMetadata/v1/forms` | metadata | GET | - |
| ME022G | `/rest/ofscMetadata/v1/forms/{label}` | metadata | GET | - |
| ME022U | `/rest/ofscMetadata/v1/forms/{label}` | metadata | PUT | - |
| ME022D | `/rest/ofscMetadata/v1/forms/{label}` | metadata | DELETE | - |
| ME023G | `/rest/ofscMetadata/v1/inventoryTypes` | metadata | GET | both |
| ME024G | `/rest/ofscMetadata/v1/inventoryTypes/{label}` | metadata | GET | both |
| ME024U | `/rest/ofscMetadata/v1/inventoryTypes/{label}` | metadata | PUT | - |
| ME025G | `/rest/ofscMetadata/v1/languages` | metadata | GET | async |
| ME026G | `/rest/ofscMetadata/v1/linkTemplates` | metadata | GET | async |
| ME027G | `/rest/ofscMetadata/v1/linkTemplates/{label}` | metadata | GET | async |
| ME027P | `/rest/ofscMetadata/v1/linkTemplates/{label}` | metadata | POST | - |
| ME027A | `/rest/ofscMetadata/v1/linkTemplates/{label}` | metadata | PATCH | - |
| ME028G | `/rest/ofscMetadata/v1/mapLayers` | metadata | GET | - |
| ME028P | `/rest/ofscMetadata/v1/mapLayers` | metadata | POST | - |
| ME029G | `/rest/ofscMetadata/v1/mapLayers/{label}` | metadata | GET | - |
| ME029U | `/rest/ofscMetadata/v1/mapLayers/{label}` | metadata | PUT | - |
| ME030G | `/rest/ofscMetadata/v1/mapLayers/custom-actions/populateLayers/{downloadId}` | metadata | GET | - |
| ME031P | `/rest/ofscMetadata/v1/mapLayers/custom-actions/populateLayers` | metadata | POST | - |
| ME032G | `/rest/ofscMetadata/v1/nonWorkingReasons` | metadata | GET | async |
| ME033G | `/rest/ofscMetadata/v1/organizations` | metadata | GET | both |
| ME034G | `/rest/ofscMetadata/v1/organizations/{label}` | metadata | GET | both |
| ME035P | `/rest/ofscMetadata/v1/plugins/custom-actions/import` | metadata | POST | sync |
| ME036P | `/rest/ofscMetadata/v1/plugins/{pluginLabel}/custom-actions/install` | metadata | POST | - |
| ME037G | `/rest/ofscMetadata/v1/properties` | metadata | GET | both |
| ME038G | `/rest/ofscMetadata/v1/properties/{label}` | metadata | GET | both |
| ME038U | `/rest/ofscMetadata/v1/properties/{label}` | metadata | PUT | both |
| ME038A | `/rest/ofscMetadata/v1/properties/{label}` | metadata | PATCH | - |
| ME039G | `/rest/ofscMetadata/v1/properties/{label}/enumerationList` | metadata | GET | both |
| ME039U | `/rest/ofscMetadata/v1/properties/{label}/enumerationList` | metadata | PUT | both |
| ME040G | `/rest/ofscMetadata/v1/resourceTypes` | metadata | GET | both |
| ME041G | `/rest/ofscMetadata/v1/routingProfiles` | metadata | GET | sync |
| ME042G | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans` | metadata | GET | sync |
| ME043G | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/{planLabel}/custom-actions/export` | metadata | GET | sync |
| ME044U | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/custom-actions/import` | metadata | PUT | sync |
| ME045U | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/custom-actions/forceImport` | metadata | PUT | sync |
| ME046P | `/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/{planLabel}/{resourceExternalId}/{date}/custom-actions/start` | metadata | POST | sync |
| ME047G | `/rest/ofscMetadata/v1/shifts` | metadata | GET | - |
| ME048G | `/rest/ofscMetadata/v1/shifts/{label}` | metadata | GET | - |
| ME048D | `/rest/ofscMetadata/v1/shifts/{label}` | metadata | DELETE | - |
| ME048U | `/rest/ofscMetadata/v1/shifts/{label}` | metadata | PUT | - |
| ME049G | `/rest/ofscMetadata/v1/timeSlots` | metadata | GET | async |
| ME050G | `/rest/ofscMetadata/v1/workSkillConditions` | metadata | GET | sync |
| ME050U | `/rest/ofscMetadata/v1/workSkillConditions` | metadata | PUT | sync |
| ME051G | `/rest/ofscMetadata/v1/workSkillGroups` | metadata | GET | sync |
| ME052G | `/rest/ofscMetadata/v1/workSkillGroups/{label}` | metadata | GET | sync |
| ME052U | `/rest/ofscMetadata/v1/workSkillGroups/{label}` | metadata | PUT | sync |
| ME052D | `/rest/ofscMetadata/v1/workSkillGroups/{label}` | metadata | DELETE | sync |
| ME053G | `/rest/ofscMetadata/v1/workSkills` | metadata | GET | sync |
| ME054G | `/rest/ofscMetadata/v1/workSkills/{label}` | metadata | GET | sync |
| ME054U | `/rest/ofscMetadata/v1/workSkills/{label}` | metadata | PUT | sync |
| ME054D | `/rest/ofscMetadata/v1/workSkills/{label}` | metadata | DELETE | sync |
| ME055G | `/rest/ofscMetadata/v1/workZones` | metadata | GET | both |
| ME055P | `/rest/ofscMetadata/v1/workZones` | metadata | POST | async |
| ME055U | `/rest/ofscMetadata/v1/workZones` | metadata | PUT | - |
| ME055A | `/rest/ofscMetadata/v1/workZones` | metadata | PATCH | - |
| ME056G | `/rest/ofscMetadata/v1/workZones/{label}` | metadata | GET | both |
| ME056U | `/rest/ofscMetadata/v1/workZones/{label}` | metadata | PUT | both |
| ME057G | `/rest/ofscMetadata/v1/workZones/custom-actions/populateShapes/{downloadId}` | metadata | GET | - |
| ME058P | `/rest/ofscMetadata/v1/workZones/custom-actions/populateShapes` | metadata | POST | - |
| ME059G | `/rest/ofscMetadata/v1/workZoneKey` | metadata | GET | - |
| ST001G | `/rest/ofscStatistics/v1/activityDurationStats` | statistics | GET | - |
| ST001A | `/rest/ofscStatistics/v1/activityDurationStats` | statistics | PATCH | - |
| ST002G | `/rest/ofscStatistics/v1/activityTravelStats` | statistics | GET | - |
| ST002A | `/rest/ofscStatistics/v1/activityTravelStats` | statistics | PATCH | - |
| ST003G | `/rest/ofscStatistics/v1/airlineDistanceBasedTravel` | statistics | GET | - |
| ST003A | `/rest/ofscStatistics/v1/airlineDistanceBasedTravel` | statistics | PATCH | - |
| PC001U | `/rest/ofscPartsCatalog/v1/catalogs/{catalog}/{language}` | partscatalog | PUT | - |
| PC002U | `/rest/ofscPartsCatalog/v1/catalogs/{catalog}/{language}/{itemLabel}` | partscatalog | PUT | - |
| PC002D | `/rest/ofscPartsCatalog/v1/catalogs/{catalog}/{language}/{itemLabel}` | partscatalog | DELETE | - |
| CB001G | `/rest/ofscCollaboration/v1/addressBook` | collaboration | GET | - |
| CB002P | `/rest/ofscCollaboration/v1/chats` | collaboration | POST | - |
| CB003P | `/rest/ofscCollaboration/v1/chats/{chatId}/leave` | collaboration | POST | - |
| CB004G | `/rest/ofscCollaboration/v1/chats/{chatId}/messages` | collaboration | GET | - |
| CB004P | `/rest/ofscCollaboration/v1/chats/{chatId}/messages` | collaboration | POST | - |
| CB005G | `/rest/ofscCollaboration/v1/chats/{chatId}/participants` | collaboration | GET | - |
| CB006P | `/rest/ofscCollaboration/v1/chats/{chatId}/participants/invite` | collaboration | POST | - |
| CO001P | `/rest/ofscCore/v1/activities` | core | POST | - |
| CO001G | `/rest/ofscCore/v1/activities` | core | GET | sync |
| CO002A | `/rest/ofscCore/v1/activities/{activityId}` | core | PATCH | sync |
| CO002D | `/rest/ofscCore/v1/activities/{activityId}` | core | DELETE | sync |
| CO002G | `/rest/ofscCore/v1/activities/{activityId}` | core | GET | sync |
| CO003G | `/rest/ofscCore/v1/activities/{activityId}/multidaySegments` | core | GET | - |
| CO004U | `/rest/ofscCore/v1/activities/{activityId}/{propertyLabel}` | core | PUT | - |
| CO004G | `/rest/ofscCore/v1/activities/{activityId}/{propertyLabel}` | core | GET | sync |
| CO004D | `/rest/ofscCore/v1/activities/{activityId}/{propertyLabel}` | core | DELETE | - |
| CO005G | `/rest/ofscCore/v1/activities/{activityId}/submittedForms` | core | GET | - |
| CO006U | `/rest/ofscCore/v1/activities/{activityId}/resourcePreferences` | core | PUT | - |
| CO006G | `/rest/ofscCore/v1/activities/{activityId}/resourcePreferences` | core | GET | - |
| CO006D | `/rest/ofscCore/v1/activities/{activityId}/resourcePreferences` | core | DELETE | - |
| CO007U | `/rest/ofscCore/v1/activities/{activityId}/requiredInventories` | core | PUT | - |
| CO007G | `/rest/ofscCore/v1/activities/{activityId}/requiredInventories` | core | GET | - |
| CO007D | `/rest/ofscCore/v1/activities/{activityId}/requiredInventories` | core | DELETE | - |
| CO008P | `/rest/ofscCore/v1/activities/{activityId}/customerInventories` | core | POST | - |
| CO008G | `/rest/ofscCore/v1/activities/{activityId}/customerInventories` | core | GET | - |
| CO009G | `/rest/ofscCore/v1/activities/{activityId}/installedInventories` | core | GET | - |
| CO010G | `/rest/ofscCore/v1/activities/{activityId}/deinstalledInventories` | core | GET | - |
| CO011G | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities` | core | GET | - |
| CO011D | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities` | core | DELETE | - |
| CO011P | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities` | core | POST | - |
| CO012G | `/rest/ofscCore/v1/activities/{activityId}/capacityCategories` | core | GET | - |
| CO013D | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities/{linkedActivityId}/linkTypes/{linkType}` | core | DELETE | - |
| CO013G | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities/{linkedActivityId}/linkTypes/{linkType}` | core | GET | - |
| CO013U | `/rest/ofscCore/v1/activities/{activityId}/linkedActivities/{linkedActivityId}/linkTypes/{linkType}` | core | PUT | - |
| CO014G | `/rest/ofscCore/v1/activities/custom-actions/search` | core | GET | sync |
| CO015P | `/rest/ofscCore/v1/activities/custom-actions/bulkUpdate` | core | POST | sync |
| CO016P | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/startPrework` | core | POST | - |
| CO017P | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/reopen` | core | POST | - |
| CO018P | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/delay` | core | POST | - |
| CO019P | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/cancel` | core | POST | - |
| CO020P | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/start` | core | POST | - |
| CO021P | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/enroute` | core | POST | - |
| CO022P | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/stopTravel` | core | POST | - |
| CO023P | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/suspend` | core | POST | - |
| CO024P | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/move` | core | POST | sync |
| CO025P | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/complete` | core | POST | - |
| CO026P | `/rest/ofscCore/v1/activities/{activityId}/custom-actions/notDone` | core | POST | - |
| CO027G | `/rest/ofscCore/v1/whereIsMyTech` | core | GET | - |
| CO028G | `/rest/ofscCore/v1/folders/dailyExtract/folders` | core | GET | sync |
| CO029G | `/rest/ofscCore/v1/folders/dailyExtract/folders/{dailyExtractDate}/files` | core | GET | sync |
| CO030G | `/rest/ofscCore/v1/folders/dailyExtract/folders/{dailyExtractDate}/files/{dailyExtractFilename}` | core | GET | sync |
| CO031D | `/rest/ofscCore/v1/events/subscriptions/{subscriptionId}` | core | DELETE | sync |
| CO031G | `/rest/ofscCore/v1/events/subscriptions/{subscriptionId}` | core | GET | sync |
| CO032G | `/rest/ofscCore/v1/events/subscriptions` | core | GET | sync |
| CO032P | `/rest/ofscCore/v1/events/subscriptions` | core | POST | sync |
| CO033G | `/rest/ofscCore/v1/events` | core | GET | sync |
| CO034P | `/rest/ofscCore/v1/inventories` | core | POST | - |
| CO035A | `/rest/ofscCore/v1/inventories/{inventoryId}` | core | PATCH | - |
| CO035G | `/rest/ofscCore/v1/inventories/{inventoryId}` | core | GET | - |
| CO035D | `/rest/ofscCore/v1/inventories/{inventoryId}` | core | DELETE | - |
| CO036U | `/rest/ofscCore/v1/inventories/{inventoryId}/{propertyLabel}` | core | PUT | - |
| CO036G | `/rest/ofscCore/v1/inventories/{inventoryId}/{propertyLabel}` | core | GET | - |
| CO036D | `/rest/ofscCore/v1/inventories/{inventoryId}/{propertyLabel}` | core | DELETE | - |
| CO037P | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/undoInstall` | core | POST | - |
| CO038P | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/undoDeinstall` | core | POST | - |
| CO039P | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/install` | core | POST | - |
| CO040P | `/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/deinstall` | core | POST | - |
| CO041G | `/rest/ofscCore/v1/resources` | core | GET | sync |
| CO042G | `/rest/ofscCore/v1/resources/{resourceId}/children` | core | GET | - |
| CO043G | `/rest/ofscCore/v1/resources/{resourceId}/descendants` | core | GET | sync |
| CO044G | `/rest/ofscCore/v1/resources/{resourceId}/assistants` | core | GET | - |
| CO045G | `/rest/ofscCore/v1/resources/{resourceId}` | core | GET | sync |
| CO045U | `/rest/ofscCore/v1/resources/{resourceId}` | core | PUT | sync |
| CO045A | `/rest/ofscCore/v1/resources/{resourceId}` | core | PATCH | sync |
| CO046G | `/rest/ofscCore/v1/resources/{resourceId}/users` | core | GET | sync |
| CO046U | `/rest/ofscCore/v1/resources/{resourceId}/users` | core | PUT | sync |
| CO046D | `/rest/ofscCore/v1/resources/{resourceId}/users` | core | DELETE | sync |
| CO047P | `/rest/ofscCore/v1/resources/{resourceId}/inventories` | core | POST | - |
| CO047G | `/rest/ofscCore/v1/resources/{resourceId}/inventories` | core | GET | sync |
| CO048P | `/rest/ofscCore/v1/resources/{resourceId}/inventories/{inventoryId}/custom-actions/install` | core | POST | - |
| CO049P | `/rest/ofscCore/v1/resources/{resourceId}/workSkills` | core | POST | - |
| CO049G | `/rest/ofscCore/v1/resources/{resourceId}/workSkills` | core | GET | sync |
| CO050D | `/rest/ofscCore/v1/resources/{resourceId}/workSkills/{workSkill}` | core | DELETE | - |
| CO051P | `/rest/ofscCore/v1/resources/{resourceId}/workZones` | core | POST | - |
| CO051G | `/rest/ofscCore/v1/resources/{resourceId}/workZones` | core | GET | sync |
| CO052D | `/rest/ofscCore/v1/resources/{resourceId}/workZones/{workZoneItemId}` | core | DELETE | - |
| CO053G | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules` | core | GET | sync |
| CO053P | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules` | core | POST | sync |
| CO054D | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules/{scheduleItemId}` | core | DELETE | - |
| CO055G | `/rest/ofscCore/v1/resources/{resourceId}/workSchedules/calendarView` | core | GET | sync |
| CO056G | `/rest/ofscCore/v1/calendars` | core | GET | - |
| CO057U | `/rest/ofscCore/v1/resources/{resourceId}/{propertyLabel}` | core | PUT | - |
| CO057G | `/rest/ofscCore/v1/resources/{resourceId}/{propertyLabel}` | core | GET | - |
| CO057D | `/rest/ofscCore/v1/resources/{resourceId}/{propertyLabel}` | core | DELETE | - |
| CO058P | `/rest/ofscCore/v1/resources/{resourceId}/locations` | core | POST | sync |
| CO058G | `/rest/ofscCore/v1/resources/{resourceId}/locations` | core | GET | sync |
| CO059G | `/rest/ofscCore/v1/resources/{resourceId}/locations/{locationId}` | core | GET | - |
| CO059A | `/rest/ofscCore/v1/resources/{resourceId}/locations/{locationId}` | core | PATCH | - |
| CO059D | `/rest/ofscCore/v1/resources/{resourceId}/locations/{locationId}` | core | DELETE | sync |
| CO060G | `/rest/ofscCore/v1/resources/{resourceId}/positionHistory` | core | GET | sync |
| CO061U | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations` | core | PUT | sync |
| CO061G | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations` | core | GET | sync |
| CO061A | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations` | core | PATCH | - |
| CO062D | `/rest/ofscCore/v1/resources/{resourceId}/assignedLocations/{date}` | core | DELETE | - |
| CO063P | `/rest/ofscCore/v1/resources/{resourceId}/plans` | core | POST | - |
| CO063G | `/rest/ofscCore/v1/resources/{resourceId}/plans` | core | GET | - |
| CO063D | `/rest/ofscCore/v1/resources/{resourceId}/plans` | core | DELETE | - |
| CO064G | `/rest/ofscCore/v1/resources/{resourceId}/routes/{date}` | core | GET | sync |
| CO065P | `/rest/ofscCore/v1/resources/{resourceId}/routes/{date}/custom-actions/activate` | core | POST | - |
| CO066P | `/rest/ofscCore/v1/resources/{resourceId}/routes/{date}/custom-actions/deactivate` | core | POST | - |
| CO067G | `/rest/ofscCore/v1/resources/{resourceId}/findNearbyActivities` | core | GET | - |
| CO068P | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkSchedules` | core | POST | sync |
| CO069P | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkSkills` | core | POST | sync |
| CO070P | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkZones` | core | POST | sync |
| CO071P | `/rest/ofscCore/v1/resources/custom-actions/bulkUpdateInventories` | core | POST | - |
| CO072P | `/rest/ofscCore/v1/resources/custom-actions/findMatchingResources` | core | POST | - |
| CO073P | `/rest/ofscCore/v1/resources/custom-actions/findResourcesForUrgentAssignment` | core | POST | - |
| CO074P | `/rest/ofscCore/v1/resources/custom-actions/setPositions` | core | POST | - |
| CO075G | `/rest/ofscCore/v1/resources/custom-actions/lastKnownPositions` | core | GET | - |
| CO076G | `/rest/ofscCore/v1/resources/custom-actions/resourcesInArea` | core | GET | - |
| CO077G | `/rest/ofscCore/v1/serviceRequests/{requestId}` | core | GET | - |
| CO078P | `/rest/ofscCore/v1/serviceRequests` | core | POST | - |
| CO079G | `/rest/ofscCore/v1/serviceRequests/{requestId}/{propertyLabel}` | core | GET | - |
| CO080G | `/rest/ofscCore/v1/users` | core | GET | sync |
| CO081G | `/rest/ofscCore/v1/users/{login}` | core | GET | sync |
| CO081U | `/rest/ofscCore/v1/users/{login}` | core | PUT | sync |
| CO081A | `/rest/ofscCore/v1/users/{login}` | core | PATCH | sync |
| CO081D | `/rest/ofscCore/v1/users/{login}` | core | DELETE | sync |
| CO082U | `/rest/ofscCore/v1/users/{login}/{propertyLabel}` | core | PUT | - |
| CO082G | `/rest/ofscCore/v1/users/{login}/{propertyLabel}` | core | GET | - |
| CO082D | `/rest/ofscCore/v1/users/{login}/{propertyLabel}` | core | DELETE | - |
| CO083G | `/rest/ofscCore/v1/users/{login}/collaborationGroups` | core | GET | - |
| CO083P | `/rest/ofscCore/v1/users/{login}/collaborationGroups` | core | POST | - |
| CO083D | `/rest/ofscCore/v1/users/{login}/collaborationGroups` | core | DELETE | - |
| AU001P | `/rest/oauthTokenService/v1/token` | auth | POST | - |
| AU002P | `/rest/oauthTokenService/v2/token` | auth | POST | - |
| CA001G | `/rest/ofscCapacity/v1/activityBookingOptions` | capacity | GET | - |
| CA002G | `/rest/ofscCapacity/v1/bookingClosingSchedule` | capacity | GET | - |
| CA002A | `/rest/ofscCapacity/v1/bookingClosingSchedule` | capacity | PATCH | - |
| CA003G | `/rest/ofscCapacity/v1/bookingStatuses` | capacity | GET | - |
| CA003A | `/rest/ofscCapacity/v1/bookingStatuses` | capacity | PATCH | - |
| CA004G | `/rest/ofscCapacity/v1/capacity` | capacity | GET | sync |
| CA005G | `/rest/ofscCapacity/v1/quota` | capacity | GET | - |
| CA005A | `/rest/ofscCapacity/v1/quota` | capacity | PATCH | - |
| CA006G | `/rest/ofscCapacity/v2/quota` | capacity | GET | sync |
| CA006A | `/rest/ofscCapacity/v2/quota` | capacity | PATCH | - |
| CA007P | `/rest/ofscCapacity/v1/showBookingGrid` | capacity | POST | - |
| CA008G | `/rest/ofscCapacity/v1/bookingFieldsDependencies` | capacity | GET | - |



## Implementation Summary

- **Sync only**: 72 endpoints
- **Async only**: 6 endpoints
- **Both**: 17 endpoints
- **Not implemented**: 148 endpoints
- **Total sync**: 89 endpoints
- **Total async**: 23 endpoints

## Implementation Statistics by Module and Method

### Synchronous Client

| Module | GET | Write (POST/PUT/PATCH) | DELETE | Total |
|:-------|----:|-----------------------:|-------:|------:|
| metadata | 30/51 (58.8%) | 10/30 (33.3%) | 2/5 (40.0%) | 42/86 (48.8%) |
| core | 25/51 (49.0%) | 15/56 (26.8%) | 5/20 (25.0%) | 45/127 (35.4%) |
| capacity | 2/7 (28.6%) | 0/5 (0.0%) | 0/0 (0%) | 2/12 (16.7%) |
| statistics | 0/3 (0.0%) | 0/3 (0.0%) | 0/0 (0%) | 0/6 (0.0%) |
| partscatalog | 0/0 (0%) | 0/2 (0.0%) | 0/1 (0.0%) | 0/3 (0.0%) |
| collaboration | 0/3 (0.0%) | 0/4 (0.0%) | 0/0 (0%) | 0/7 (0.0%) |
| auth | 0/0 (0%) | 0/2 (0.0%) | 0/0 (0%) | 0/2 (0.0%) |
| **Total** | **57/115 (49.6%)** | **25/102 (24.5%)** | **7/26 (26.9%)** | **89/243 (36.6%)** |

### Asynchronous Client

| Module | GET | Write (POST/PUT/PATCH) | DELETE | Total |
|:-------|----:|-----------------------:|-------:|------:|
| metadata | 19/51 (37.3%) | 4/30 (13.3%) | 0/5 (0.0%) | 23/86 (26.7%) |
| core | 0/51 (0.0%) | 0/56 (0.0%) | 0/20 (0.0%) | 0/127 (0.0%) |
| capacity | 0/7 (0.0%) | 0/5 (0.0%) | 0/0 (0%) | 0/12 (0.0%) |
| statistics | 0/3 (0.0%) | 0/3 (0.0%) | 0/0 (0%) | 0/6 (0.0%) |
| partscatalog | 0/0 (0%) | 0/2 (0.0%) | 0/1 (0.0%) | 0/3 (0.0%) |
| collaboration | 0/3 (0.0%) | 0/4 (0.0%) | 0/0 (0%) | 0/7 (0.0%) |
| auth | 0/0 (0%) | 0/2 (0.0%) | 0/0 (0%) | 0/2 (0.0%) |
| **Total** | **19/115 (16.5%)** | **4/102 (3.9%)** | **0/26 (0.0%)** | **23/243 (9.5%)** |

## Endpoint ID Reference

### ID Format: `XXYYYM`

Endpoint IDs are structured 6-character codes where:

- **XX** = 2-character module code
- **YYY** = 3-digit zero-padded serial number (unique per endpoint path within module)
- **M** = 1-character HTTP method code

### Module Codes

| Code | Module |
|------|--------|
| `CO` | core |
| `ME` | metadata |
| `CA` | capacity |
| `CB` | collaboration |
| `ST` | statistics |
| `PC` | partscatalog |
| `AU` | auth |

### Method Codes

| Code | HTTP Method |
|------|-------------|
| `G` | GET |
| `P` | POST |
| `U` | PUT |
| `A` | PATCH |
| `D` | DELETE |

### Examples

- `CO001G` = Core module, first endpoint (GET method)
- `ME003P` = Metadata module, third endpoint (POST method)
- `CA002A` = Capacity module, second endpoint (PATCH method)
- `AU001P` = Auth module, first endpoint (POST method)

### Adding New Endpoints

When adding new endpoints:

1. **New endpoint path**: Use the next available serial number for that module
2. **Existing path with new method**: Use the same serial number as the existing endpoint(s) for that path, with the appropriate method code

**Example:** If `/rest/ofscCore/v1/activities` has `CO015G` (GET), adding POST would be `CO015P` (same serial number, different method letter).
