# OFSC API Endpoints Reference

**Version:** 2.24.3
**Last Updated:** 2026-03-05

This document provides a comprehensive reference of all Oracle Field Service Cloud (OFSC) API endpoints and their implementation status in pyOFSC.

**Total Endpoints:** 243

## Implementation Status

- `sync` - Implemented in synchronous client only
- `async` - Implemented in asynchronous client only
- `both` - Implemented in both sync and async clients
- `-` - Not implemented

## Endpoints Table

|  ID  |                                                        Endpoint                                                         |   Module    |Method|Status|
|------|-------------------------------------------------------------------------------------------------------------------------|-------------|------|------|
|ME001G|`/rest/ofscMetadata/v1/activityTypeGroups`                                                                               |metadata     |GET   |both  |
|ME002G|`/rest/ofscMetadata/v1/activityTypeGroups/{label}`                                                                       |metadata     |GET   |both  |
|ME002U|`/rest/ofscMetadata/v1/activityTypeGroups/{label}`                                                                       |metadata     |PUT   |async |
|ME003G|`/rest/ofscMetadata/v1/activityTypes`                                                                                    |metadata     |GET   |both  |
|ME004G|`/rest/ofscMetadata/v1/activityTypes/{label}`                                                                            |metadata     |GET   |both  |
|ME004U|`/rest/ofscMetadata/v1/activityTypes/{label}`                                                                            |metadata     |PUT   |async |
|ME005G|`/rest/ofscMetadata/v1/applications`                                                                                     |metadata     |GET   |both  |
|ME006G|`/rest/ofscMetadata/v1/applications/{label}`                                                                             |metadata     |GET   |both  |
|ME006U|`/rest/ofscMetadata/v1/applications/{label}`                                                                             |metadata     |PUT   |async |
|ME007G|`/rest/ofscMetadata/v1/applications/{label}/apiAccess`                                                                   |metadata     |GET   |both  |
|ME008G|`/rest/ofscMetadata/v1/applications/{label}/apiAccess/{apiLabel}`                                                        |metadata     |GET   |both  |
|ME008A|`/rest/ofscMetadata/v1/applications/{label}/apiAccess/{apiLabel}`                                                        |metadata     |PATCH |async |
|ME009P|`/rest/ofscMetadata/v1/applications/{label}/custom-actions/generateClientSecret`                                         |metadata     |POST  |async |
|ME010G|`/rest/ofscMetadata/v1/capacityAreas`                                                                                    |metadata     |GET   |both  |
|ME011G|`/rest/ofscMetadata/v1/capacityAreas/{label}`                                                                            |metadata     |GET   |both  |
|ME012G|`/rest/ofscMetadata/v1/capacityAreas/{label}/capacityCategories`                                                         |metadata     |GET   |async |
|ME013G|`/rest/ofscMetadata/v2/capacityAreas/{label}/workZones`                                                                  |metadata     |GET   |async |
|ME014G|`/rest/ofscMetadata/v1/capacityAreas/{label}/workZones`                                                                  |metadata     |GET   |async |
|ME015G|`/rest/ofscMetadata/v1/capacityAreas/{label}/timeSlots`                                                                  |metadata     |GET   |async |
|ME016G|`/rest/ofscMetadata/v1/capacityAreas/{label}/timeIntervals`                                                              |metadata     |GET   |async |
|ME017G|`/rest/ofscMetadata/v1/capacityAreas/{label}/organizations`                                                              |metadata     |GET   |async |
|ME018G|`/rest/ofscMetadata/v1/capacityAreas/{label}/children`                                                                   |metadata     |GET   |async |
|ME019G|`/rest/ofscMetadata/v1/capacityCategories`                                                                               |metadata     |GET   |both  |
|ME020G|`/rest/ofscMetadata/v1/capacityCategories/{label}`                                                                       |metadata     |GET   |both  |
|ME020U|`/rest/ofscMetadata/v1/capacityCategories/{label}`                                                                       |metadata     |PUT   |async |
|ME020D|`/rest/ofscMetadata/v1/capacityCategories/{label}`                                                                       |metadata     |DELETE|async |
|ME021G|`/rest/ofscMetadata/v1/forms`                                                                                            |metadata     |GET   |async |
|ME022G|`/rest/ofscMetadata/v1/forms/{label}`                                                                                    |metadata     |GET   |async |
|ME022U|`/rest/ofscMetadata/v1/forms/{label}`                                                                                    |metadata     |PUT   |async |
|ME022D|`/rest/ofscMetadata/v1/forms/{label}`                                                                                    |metadata     |DELETE|async |
|ME023G|`/rest/ofscMetadata/v1/inventoryTypes`                                                                                   |metadata     |GET   |both  |
|ME024G|`/rest/ofscMetadata/v1/inventoryTypes/{label}`                                                                           |metadata     |GET   |both  |
|ME024U|`/rest/ofscMetadata/v1/inventoryTypes/{label}`                                                                           |metadata     |PUT   |async |
|ME025G|`/rest/ofscMetadata/v1/languages`                                                                                        |metadata     |GET   |async |
|ME026G|`/rest/ofscMetadata/v1/linkTemplates`                                                                                    |metadata     |GET   |async |
|ME027G|`/rest/ofscMetadata/v1/linkTemplates/{label}`                                                                            |metadata     |GET   |async |
|ME027P|`/rest/ofscMetadata/v1/linkTemplates/{label}`                                                                            |metadata     |POST  |-     |
|ME027A|`/rest/ofscMetadata/v1/linkTemplates/{label}`                                                                            |metadata     |PATCH |async |
|ME028G|`/rest/ofscMetadata/v1/mapLayers`                                                                                        |metadata     |GET   |async |
|ME028P|`/rest/ofscMetadata/v1/mapLayers`                                                                                        |metadata     |POST  |async |
|ME029G|`/rest/ofscMetadata/v1/mapLayers/{label}`                                                                                |metadata     |GET   |async |
|ME029U|`/rest/ofscMetadata/v1/mapLayers/{label}`                                                                                |metadata     |PUT   |async |
|ME030G|`/rest/ofscMetadata/v1/mapLayers/custom-actions/populateLayers/{downloadId}`                                             |metadata     |GET   |async |
|ME031P|`/rest/ofscMetadata/v1/mapLayers/custom-actions/populateLayers`                                                          |metadata     |POST  |async |
|ME032G|`/rest/ofscMetadata/v1/nonWorkingReasons`                                                                                |metadata     |GET   |async |
|ME033G|`/rest/ofscMetadata/v1/organizations`                                                                                    |metadata     |GET   |both  |
|ME034G|`/rest/ofscMetadata/v1/organizations/{label}`                                                                            |metadata     |GET   |both  |
|ME035P|`/rest/ofscMetadata/v1/plugins/custom-actions/import`                                                                    |metadata     |POST  |both  |
|ME036P|`/rest/ofscMetadata/v1/plugins/{pluginLabel}/custom-actions/install`                                                     |metadata     |POST  |async |
|ME037G|`/rest/ofscMetadata/v1/properties`                                                                                       |metadata     |GET   |both  |
|ME038G|`/rest/ofscMetadata/v1/properties/{label}`                                                                               |metadata     |GET   |both  |
|ME038U|`/rest/ofscMetadata/v1/properties/{label}`                                                                               |metadata     |PUT   |both  |
|ME038A|`/rest/ofscMetadata/v1/properties/{label}`                                                                               |metadata     |PATCH |async |
|ME039G|`/rest/ofscMetadata/v1/properties/{label}/enumerationList`                                                               |metadata     |GET   |both  |
|ME039U|`/rest/ofscMetadata/v1/properties/{label}/enumerationList`                                                               |metadata     |PUT   |both  |
|ME040G|`/rest/ofscMetadata/v1/resourceTypes`                                                                                    |metadata     |GET   |both  |
|ME041G|`/rest/ofscMetadata/v1/routingProfiles`                                                                                  |metadata     |GET   |both  |
|ME042G|`/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans`                                                             |metadata     |GET   |both  |
|ME043G|`/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/{planLabel}/custom-actions/export`                           |metadata     |GET   |both  |
|ME044U|`/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/custom-actions/import`                                       |metadata     |PUT   |both  |
|ME045U|`/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/custom-actions/forceImport`                                  |metadata     |PUT   |both  |
|ME046P|`/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/{planLabel}/{resourceExternalId}/{date}/custom-actions/start`|metadata     |POST  |both  |
|ME047G|`/rest/ofscMetadata/v1/shifts`                                                                                           |metadata     |GET   |async |
|ME048G|`/rest/ofscMetadata/v1/shifts/{label}`                                                                                   |metadata     |GET   |async |
|ME048D|`/rest/ofscMetadata/v1/shifts/{label}`                                                                                   |metadata     |DELETE|async |
|ME048U|`/rest/ofscMetadata/v1/shifts/{label}`                                                                                   |metadata     |PUT   |async |
|ME049G|`/rest/ofscMetadata/v1/timeSlots`                                                                                        |metadata     |GET   |async |
|ME050G|`/rest/ofscMetadata/v1/workSkillConditions`                                                                              |metadata     |GET   |both  |
|ME050U|`/rest/ofscMetadata/v1/workSkillConditions`                                                                              |metadata     |PUT   |sync  |
|ME051G|`/rest/ofscMetadata/v1/workSkillGroups`                                                                                  |metadata     |GET   |both  |
|ME052G|`/rest/ofscMetadata/v1/workSkillGroups/{label}`                                                                          |metadata     |GET   |both  |
|ME052U|`/rest/ofscMetadata/v1/workSkillGroups/{label}`                                                                          |metadata     |PUT   |both  |
|ME052D|`/rest/ofscMetadata/v1/workSkillGroups/{label}`                                                                          |metadata     |DELETE|both  |
|ME053G|`/rest/ofscMetadata/v1/workSkills`                                                                                       |metadata     |GET   |both  |
|ME054G|`/rest/ofscMetadata/v1/workSkills/{label}`                                                                               |metadata     |GET   |both  |
|ME054U|`/rest/ofscMetadata/v1/workSkills/{label}`                                                                               |metadata     |PUT   |both  |
|ME054D|`/rest/ofscMetadata/v1/workSkills/{label}`                                                                               |metadata     |DELETE|both  |
|ME055G|`/rest/ofscMetadata/v1/workZones`                                                                                        |metadata     |GET   |both  |
|ME055P|`/rest/ofscMetadata/v1/workZones`                                                                                        |metadata     |POST  |async |
|ME055U|`/rest/ofscMetadata/v1/workZones`                                                                                        |metadata     |PUT   |async |
|ME055A|`/rest/ofscMetadata/v1/workZones`                                                                                        |metadata     |PATCH |async |
|ME056G|`/rest/ofscMetadata/v1/workZones/{label}`                                                                                |metadata     |GET   |both  |
|ME056U|`/rest/ofscMetadata/v1/workZones/{label}`                                                                                |metadata     |PUT   |both  |
|ME057G|`/rest/ofscMetadata/v1/workZones/custom-actions/populateShapes/{downloadId}`                                             |metadata     |GET   |async |
|ME058P|`/rest/ofscMetadata/v1/workZones/custom-actions/populateShapes`                                                          |metadata     |POST  |async |
|ME059G|`/rest/ofscMetadata/v1/workZoneKey`                                                                                      |metadata     |GET   |async |
|ST001G|`/rest/ofscStatistics/v1/activityDurationStats`                                                                          |statistics   |GET   |async |
|ST001A|`/rest/ofscStatistics/v1/activityDurationStats`                                                                          |statistics   |PATCH |async |
|ST002G|`/rest/ofscStatistics/v1/activityTravelStats`                                                                            |statistics   |GET   |async |
|ST002A|`/rest/ofscStatistics/v1/activityTravelStats`                                                                            |statistics   |PATCH |async |
|ST003G|`/rest/ofscStatistics/v1/airlineDistanceBasedTravel`                                                                     |statistics   |GET   |async |
|ST003A|`/rest/ofscStatistics/v1/airlineDistanceBasedTravel`                                                                     |statistics   |PATCH |async |
|PC001U|`/rest/ofscPartsCatalog/v1/catalogs/{catalog}/{language}`                                                                |partscatalog |PUT   |-     |
|PC002U|`/rest/ofscPartsCatalog/v1/catalogs/{catalog}/{language}/{itemLabel}`                                                    |partscatalog |PUT   |-     |
|PC002D|`/rest/ofscPartsCatalog/v1/catalogs/{catalog}/{language}/{itemLabel}`                                                    |partscatalog |DELETE|-     |
|CB001G|`/rest/ofscCollaboration/v1/addressBook`                                                                                 |collaboration|GET   |-     |
|CB002P|`/rest/ofscCollaboration/v1/chats`                                                                                       |collaboration|POST  |-     |
|CB003P|`/rest/ofscCollaboration/v1/chats/{chatId}/leave`                                                                        |collaboration|POST  |-     |
|CB004G|`/rest/ofscCollaboration/v1/chats/{chatId}/messages`                                                                     |collaboration|GET   |-     |
|CB004P|`/rest/ofscCollaboration/v1/chats/{chatId}/messages`                                                                     |collaboration|POST  |-     |
|CB005G|`/rest/ofscCollaboration/v1/chats/{chatId}/participants`                                                                 |collaboration|GET   |-     |
|CB006P|`/rest/ofscCollaboration/v1/chats/{chatId}/participants/invite`                                                          |collaboration|POST  |-     |
|CO001P|`/rest/ofscCore/v1/activities`                                                                                           |core         |POST  |async |
|CO001G|`/rest/ofscCore/v1/activities`                                                                                           |core         |GET   |both  |
|CO002A|`/rest/ofscCore/v1/activities/{activityId}`                                                                              |core         |PATCH |both  |
|CO002D|`/rest/ofscCore/v1/activities/{activityId}`                                                                              |core         |DELETE|both  |
|CO002G|`/rest/ofscCore/v1/activities/{activityId}`                                                                              |core         |GET   |both  |
|CO003G|`/rest/ofscCore/v1/activities/{activityId}/multidaySegments`                                                             |core         |GET   |async |
|CO004U|`/rest/ofscCore/v1/activities/{activityId}/{propertyLabel}`                                                              |core         |PUT   |async |
|CO004G|`/rest/ofscCore/v1/activities/{activityId}/{propertyLabel}`                                                              |core         |GET   |both  |
|CO004D|`/rest/ofscCore/v1/activities/{activityId}/{propertyLabel}`                                                              |core         |DELETE|async |
|CO005G|`/rest/ofscCore/v1/activities/{activityId}/submittedForms`                                                               |core         |GET   |async |
|CO006U|`/rest/ofscCore/v1/activities/{activityId}/resourcePreferences`                                                          |core         |PUT   |async |
|CO006G|`/rest/ofscCore/v1/activities/{activityId}/resourcePreferences`                                                          |core         |GET   |async |
|CO006D|`/rest/ofscCore/v1/activities/{activityId}/resourcePreferences`                                                          |core         |DELETE|async |
|CO007U|`/rest/ofscCore/v1/activities/{activityId}/requiredInventories`                                                          |core         |PUT   |async |
|CO007G|`/rest/ofscCore/v1/activities/{activityId}/requiredInventories`                                                          |core         |GET   |async |
|CO007D|`/rest/ofscCore/v1/activities/{activityId}/requiredInventories`                                                          |core         |DELETE|async |
|CO008P|`/rest/ofscCore/v1/activities/{activityId}/customerInventories`                                                          |core         |POST  |async |
|CO008G|`/rest/ofscCore/v1/activities/{activityId}/customerInventories`                                                          |core         |GET   |async |
|CO009G|`/rest/ofscCore/v1/activities/{activityId}/installedInventories`                                                         |core         |GET   |async |
|CO010G|`/rest/ofscCore/v1/activities/{activityId}/deinstalledInventories`                                                       |core         |GET   |async |
|CO011G|`/rest/ofscCore/v1/activities/{activityId}/linkedActivities`                                                             |core         |GET   |async |
|CO011D|`/rest/ofscCore/v1/activities/{activityId}/linkedActivities`                                                             |core         |DELETE|async |
|CO011P|`/rest/ofscCore/v1/activities/{activityId}/linkedActivities`                                                             |core         |POST  |async |
|CO012G|`/rest/ofscCore/v1/activities/{activityId}/capacityCategories`                                                           |core         |GET   |async |
|CO013D|`/rest/ofscCore/v1/activities/{activityId}/linkedActivities/{linkedActivityId}/linkTypes/{linkType}`                     |core         |DELETE|async |
|CO013G|`/rest/ofscCore/v1/activities/{activityId}/linkedActivities/{linkedActivityId}/linkTypes/{linkType}`                     |core         |GET   |async |
|CO013U|`/rest/ofscCore/v1/activities/{activityId}/linkedActivities/{linkedActivityId}/linkTypes/{linkType}`                     |core         |PUT   |async |
|CO014G|`/rest/ofscCore/v1/activities/custom-actions/search`                                                                     |core         |GET   |sync  |
|CO015P|`/rest/ofscCore/v1/activities/custom-actions/bulkUpdate`                                                                 |core         |POST  |sync  |
|CO016P|`/rest/ofscCore/v1/activities/{activityId}/custom-actions/startPrework`                                                  |core         |POST  |-     |
|CO017P|`/rest/ofscCore/v1/activities/{activityId}/custom-actions/reopen`                                                        |core         |POST  |-     |
|CO018P|`/rest/ofscCore/v1/activities/{activityId}/custom-actions/delay`                                                         |core         |POST  |-     |
|CO019P|`/rest/ofscCore/v1/activities/{activityId}/custom-actions/cancel`                                                        |core         |POST  |-     |
|CO020P|`/rest/ofscCore/v1/activities/{activityId}/custom-actions/start`                                                         |core         |POST  |-     |
|CO021P|`/rest/ofscCore/v1/activities/{activityId}/custom-actions/enroute`                                                       |core         |POST  |-     |
|CO022P|`/rest/ofscCore/v1/activities/{activityId}/custom-actions/stopTravel`                                                    |core         |POST  |-     |
|CO023P|`/rest/ofscCore/v1/activities/{activityId}/custom-actions/suspend`                                                       |core         |POST  |-     |
|CO024P|`/rest/ofscCore/v1/activities/{activityId}/custom-actions/move`                                                          |core         |POST  |sync  |
|CO025P|`/rest/ofscCore/v1/activities/{activityId}/custom-actions/complete`                                                      |core         |POST  |-     |
|CO026P|`/rest/ofscCore/v1/activities/{activityId}/custom-actions/notDone`                                                       |core         |POST  |-     |
|CO027G|`/rest/ofscCore/v1/whereIsMyTech`                                                                                        |core         |GET   |-     |
|CO028G|`/rest/ofscCore/v1/folders/dailyExtract/folders`                                                                         |core         |GET   |both  |
|CO029G|`/rest/ofscCore/v1/folders/dailyExtract/folders/{dailyExtractDate}/files`                                                |core         |GET   |both  |
|CO030G|`/rest/ofscCore/v1/folders/dailyExtract/folders/{dailyExtractDate}/files/{dailyExtractFilename}`                         |core         |GET   |both  |
|CO031D|`/rest/ofscCore/v1/events/subscriptions/{subscriptionId}`                                                                |core         |DELETE|both  |
|CO031G|`/rest/ofscCore/v1/events/subscriptions/{subscriptionId}`                                                                |core         |GET   |both  |
|CO032G|`/rest/ofscCore/v1/events/subscriptions`                                                                                 |core         |GET   |both  |
|CO032P|`/rest/ofscCore/v1/events/subscriptions`                                                                                 |core         |POST  |both  |
|CO033G|`/rest/ofscCore/v1/events`                                                                                               |core         |GET   |both  |
|CO034P|`/rest/ofscCore/v1/inventories`                                                                                          |core         |POST  |async |
|CO035A|`/rest/ofscCore/v1/inventories/{inventoryId}`                                                                            |core         |PATCH |async |
|CO035G|`/rest/ofscCore/v1/inventories/{inventoryId}`                                                                            |core         |GET   |async |
|CO035D|`/rest/ofscCore/v1/inventories/{inventoryId}`                                                                            |core         |DELETE|async |
|CO036U|`/rest/ofscCore/v1/inventories/{inventoryId}/{propertyLabel}`                                                            |core         |PUT   |async |
|CO036G|`/rest/ofscCore/v1/inventories/{inventoryId}/{propertyLabel}`                                                            |core         |GET   |async |
|CO036D|`/rest/ofscCore/v1/inventories/{inventoryId}/{propertyLabel}`                                                            |core         |DELETE|async |
|CO037P|`/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/undoInstall`                                                 |core         |POST  |-     |
|CO038P|`/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/undoDeinstall`                                               |core         |POST  |-     |
|CO039P|`/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/install`                                                     |core         |POST  |-     |
|CO040P|`/rest/ofscCore/v1/inventories/{inventoryId}/custom-actions/deinstall`                                                   |core         |POST  |-     |
|CO041G|`/rest/ofscCore/v1/resources`                                                                                            |core         |GET   |both  |
|CO042G|`/rest/ofscCore/v1/resources/{resourceId}/children`                                                                      |core         |GET   |async |
|CO043G|`/rest/ofscCore/v1/resources/{resourceId}/descendants`                                                                   |core         |GET   |both  |
|CO044G|`/rest/ofscCore/v1/resources/{resourceId}/assistants`                                                                    |core         |GET   |async |
|CO045G|`/rest/ofscCore/v1/resources/{resourceId}`                                                                               |core         |GET   |both  |
|CO045U|`/rest/ofscCore/v1/resources/{resourceId}`                                                                               |core         |PUT   |both  |
|CO045A|`/rest/ofscCore/v1/resources/{resourceId}`                                                                               |core         |PATCH |both  |
|CO046G|`/rest/ofscCore/v1/resources/{resourceId}/users`                                                                         |core         |GET   |both  |
|CO046U|`/rest/ofscCore/v1/resources/{resourceId}/users`                                                                         |core         |PUT   |both  |
|CO046D|`/rest/ofscCore/v1/resources/{resourceId}/users`                                                                         |core         |DELETE|both  |
|CO047P|`/rest/ofscCore/v1/resources/{resourceId}/inventories`                                                                   |core         |POST  |async |
|CO047G|`/rest/ofscCore/v1/resources/{resourceId}/inventories`                                                                   |core         |GET   |both  |
|CO048P|`/rest/ofscCore/v1/resources/{resourceId}/inventories/{inventoryId}/custom-actions/install`                              |core         |POST  |async |
|CO049P|`/rest/ofscCore/v1/resources/{resourceId}/workSkills`                                                                    |core         |POST  |async |
|CO049G|`/rest/ofscCore/v1/resources/{resourceId}/workSkills`                                                                    |core         |GET   |both  |
|CO050D|`/rest/ofscCore/v1/resources/{resourceId}/workSkills/{workSkill}`                                                        |core         |DELETE|async |
|CO051P|`/rest/ofscCore/v1/resources/{resourceId}/workZones`                                                                     |core         |POST  |async |
|CO051G|`/rest/ofscCore/v1/resources/{resourceId}/workZones`                                                                     |core         |GET   |both  |
|CO052D|`/rest/ofscCore/v1/resources/{resourceId}/workZones/{workZoneItemId}`                                                    |core         |DELETE|async |
|CO053G|`/rest/ofscCore/v1/resources/{resourceId}/workSchedules`                                                                 |core         |GET   |both  |
|CO053P|`/rest/ofscCore/v1/resources/{resourceId}/workSchedules`                                                                 |core         |POST  |both  |
|CO054D|`/rest/ofscCore/v1/resources/{resourceId}/workSchedules/{scheduleItemId}`                                                |core         |DELETE|async |
|CO055G|`/rest/ofscCore/v1/resources/{resourceId}/workSchedules/calendarView`                                                    |core         |GET   |both  |
|CO056G|`/rest/ofscCore/v1/calendars`                                                                                            |core         |GET   |async |
|CO057U|`/rest/ofscCore/v1/resources/{resourceId}/{propertyLabel}`                                                               |core         |PUT   |async |
|CO057G|`/rest/ofscCore/v1/resources/{resourceId}/{propertyLabel}`                                                               |core         |GET   |async |
|CO057D|`/rest/ofscCore/v1/resources/{resourceId}/{propertyLabel}`                                                               |core         |DELETE|async |
|CO058P|`/rest/ofscCore/v1/resources/{resourceId}/locations`                                                                     |core         |POST  |both  |
|CO058G|`/rest/ofscCore/v1/resources/{resourceId}/locations`                                                                     |core         |GET   |both  |
|CO059G|`/rest/ofscCore/v1/resources/{resourceId}/locations/{locationId}`                                                        |core         |GET   |async |
|CO059A|`/rest/ofscCore/v1/resources/{resourceId}/locations/{locationId}`                                                        |core         |PATCH |async |
|CO059D|`/rest/ofscCore/v1/resources/{resourceId}/locations/{locationId}`                                                        |core         |DELETE|both  |
|CO060G|`/rest/ofscCore/v1/resources/{resourceId}/positionHistory`                                                               |core         |GET   |both  |
|CO061U|`/rest/ofscCore/v1/resources/{resourceId}/assignedLocations`                                                             |core         |PUT   |both  |
|CO061G|`/rest/ofscCore/v1/resources/{resourceId}/assignedLocations`                                                             |core         |GET   |both  |
|CO061A|`/rest/ofscCore/v1/resources/{resourceId}/assignedLocations`                                                             |core         |PATCH |-     |
|CO062D|`/rest/ofscCore/v1/resources/{resourceId}/assignedLocations/{date}`                                                      |core         |DELETE|-     |
|CO063P|`/rest/ofscCore/v1/resources/{resourceId}/plans`                                                                         |core         |POST  |-     |
|CO063G|`/rest/ofscCore/v1/resources/{resourceId}/plans`                                                                         |core         |GET   |async |
|CO063D|`/rest/ofscCore/v1/resources/{resourceId}/plans`                                                                         |core         |DELETE|-     |
|CO064G|`/rest/ofscCore/v1/resources/{resourceId}/routes/{date}`                                                                 |core         |GET   |both  |
|CO065P|`/rest/ofscCore/v1/resources/{resourceId}/routes/{date}/custom-actions/activate`                                         |core         |POST  |-     |
|CO066P|`/rest/ofscCore/v1/resources/{resourceId}/routes/{date}/custom-actions/deactivate`                                       |core         |POST  |-     |
|CO067G|`/rest/ofscCore/v1/resources/{resourceId}/findNearbyActivities`                                                          |core         |GET   |-     |
|CO068P|`/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkSchedules`                                                     |core         |POST  |both  |
|CO069P|`/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkSkills`                                                        |core         |POST  |both  |
|CO070P|`/rest/ofscCore/v1/resources/custom-actions/bulkUpdateWorkZones`                                                         |core         |POST  |both  |
|CO071P|`/rest/ofscCore/v1/resources/custom-actions/bulkUpdateInventories`                                                       |core         |POST  |-     |
|CO072P|`/rest/ofscCore/v1/resources/custom-actions/findMatchingResources`                                                       |core         |POST  |-     |
|CO073P|`/rest/ofscCore/v1/resources/custom-actions/findResourcesForUrgentAssignment`                                            |core         |POST  |-     |
|CO074P|`/rest/ofscCore/v1/resources/custom-actions/setPositions`                                                                |core         |POST  |-     |
|CO075G|`/rest/ofscCore/v1/resources/custom-actions/lastKnownPositions`                                                          |core         |GET   |-     |
|CO076G|`/rest/ofscCore/v1/resources/custom-actions/resourcesInArea`                                                             |core         |GET   |-     |
|CO077G|`/rest/ofscCore/v1/serviceRequests/{requestId}`                                                                          |core         |GET   |-     |
|CO078P|`/rest/ofscCore/v1/serviceRequests`                                                                                      |core         |POST  |-     |
|CO079G|`/rest/ofscCore/v1/serviceRequests/{requestId}/{propertyLabel}`                                                          |core         |GET   |-     |
|CO080G|`/rest/ofscCore/v1/users`                                                                                                |core         |GET   |both  |
|CO081G|`/rest/ofscCore/v1/users/{login}`                                                                                        |core         |GET   |both  |
|CO081U|`/rest/ofscCore/v1/users/{login}`                                                                                        |core         |PUT   |both  |
|CO081A|`/rest/ofscCore/v1/users/{login}`                                                                                        |core         |PATCH |both  |
|CO081D|`/rest/ofscCore/v1/users/{login}`                                                                                        |core         |DELETE|both  |
|CO082U|`/rest/ofscCore/v1/users/{login}/{propertyLabel}`                                                                        |core         |PUT   |async |
|CO082G|`/rest/ofscCore/v1/users/{login}/{propertyLabel}`                                                                        |core         |GET   |async |
|CO082D|`/rest/ofscCore/v1/users/{login}/{propertyLabel}`                                                                        |core         |DELETE|async |
|CO083G|`/rest/ofscCore/v1/users/{login}/collaborationGroups`                                                                    |core         |GET   |async |
|CO083P|`/rest/ofscCore/v1/users/{login}/collaborationGroups`                                                                    |core         |POST  |async |
|CO083D|`/rest/ofscCore/v1/users/{login}/collaborationGroups`                                                                    |core         |DELETE|async |
|AU001P|`/rest/oauthTokenService/v1/token`                                                                                       |auth         |POST  |-     |
|AU002P|`/rest/oauthTokenService/v2/token`                                                                                       |auth         |POST  |async |
|CA001G|`/rest/ofscCapacity/v1/activityBookingOptions`                                                                           |capacity     |GET   |async |
|CA002G|`/rest/ofscCapacity/v1/bookingClosingSchedule`                                                                           |capacity     |GET   |async |
|CA002A|`/rest/ofscCapacity/v1/bookingClosingSchedule`                                                                           |capacity     |PATCH |async |
|CA003G|`/rest/ofscCapacity/v1/bookingStatuses`                                                                                  |capacity     |GET   |async |
|CA003A|`/rest/ofscCapacity/v1/bookingStatuses`                                                                                  |capacity     |PATCH |async |
|CA004G|`/rest/ofscCapacity/v1/capacity`                                                                                         |capacity     |GET   |both  |
|CA005G|`/rest/ofscCapacity/v1/quota`                                                                                            |capacity     |GET   |-     |
|CA005A|`/rest/ofscCapacity/v1/quota`                                                                                            |capacity     |PATCH |-     |
|CA006G|`/rest/ofscCapacity/v2/quota`                                                                                            |capacity     |GET   |both  |
|CA006A|`/rest/ofscCapacity/v2/quota`                                                                                            |capacity     |PATCH |async |
|CA007P|`/rest/ofscCapacity/v1/showBookingGrid`                                                                                  |capacity     |POST  |async |
|CA008G|`/rest/ofscCapacity/v1/bookingFieldsDependencies`                                                                        |capacity     |GET   |async |



## Implementation Summary

- **Sync only**: 4 endpoints
- **Async only**: 109 endpoints
- **Both**: 85 endpoints
- **Not implemented**: 45 endpoints
- **Total sync**: 89 endpoints
- **Total async**: 194 endpoints

## Implementation Statistics by Module and Method

### Synchronous Client

|   Module    |       GET        |Write (POST/PUT/PATCH)|     DELETE     |      Total       |
|-------------|------------------|----------------------|----------------|------------------|
|metadata     |30/51 (58.8%)     |10/30 (33.3%)         |2/5 (40.0%)     |42/86 (48.8%)     |
|core         |25/51 (49.0%)     |15/56 (26.8%)         |5/20 (25.0%)    |45/127 (35.4%)    |
|capacity     |2/7 (28.6%)       |0/5 (0.0%)            |0/0 (0%)        |2/12 (16.7%)      |
|statistics   |0/3 (0.0%)        |0/3 (0.0%)            |0/0 (0%)        |0/6 (0.0%)        |
|partscatalog |0/0 (0%)          |0/2 (0.0%)            |0/1 (0.0%)      |0/3 (0.0%)        |
|collaboration|0/3 (0.0%)        |0/4 (0.0%)            |0/0 (0%)        |0/7 (0.0%)        |
|auth         |0/0 (0%)          |0/2 (0.0%)            |0/0 (0%)        |0/2 (0.0%)        |
|**Total**    |**57/115 (49.6%)**|**25/102 (24.5%)**    |**7/26 (26.9%)**|**89/243 (36.6%)**|

### Asynchronous Client

|   Module    |        GET        |Write (POST/PUT/PATCH)|     DELETE      |       Total       |
|-------------|-------------------|----------------------|-----------------|-------------------|
|metadata     |51/51 (100.0%)     |28/30 (93.3%)         |5/5 (100.0%)     |84/86 (97.7%)      |
|core         |44/51 (86.3%)      |31/56 (55.4%)         |18/20 (90.0%)    |93/127 (73.2%)     |
|capacity     |6/7 (85.7%)        |4/5 (80.0%)           |0/0 (0%)         |10/12 (83.3%)      |
|statistics   |3/3 (100.0%)       |3/3 (100.0%)          |0/0 (0%)         |6/6 (100.0%)       |
|partscatalog |0/0 (0%)           |0/2 (0.0%)            |0/1 (0.0%)       |0/3 (0.0%)         |
|collaboration|0/3 (0.0%)         |0/4 (0.0%)            |0/0 (0%)         |0/7 (0.0%)         |
|auth         |0/0 (0%)           |1/2 (50.0%)           |0/0 (0%)         |1/2 (50.0%)        |
|**Total**    |**104/115 (90.4%)**|**67/102 (65.7%)**    |**23/26 (88.5%)**|**194/243 (79.8%)**|

## Endpoint ID Reference

### ID Format: `XXYYYM`

Endpoint IDs are structured 6-character codes where:

- **XX** = 2-character module code
- **YYY** = 3-digit zero-padded serial number (unique per endpoint path within module)
- **M** = 1-character HTTP method code

### Module Codes

|Code|   Module    |
|----|-------------|
|`CO`|core         |
|`ME`|metadata     |
|`CA`|capacity     |
|`CB`|collaboration|
|`ST`|statistics   |
|`PC`|partscatalog |
|`AU`|auth         |

### Method Codes

|Code|HTTP Method|
|----|-----------|
|`G` |GET        |
|`P` |POST       |
|`U` |PUT        |
|`A` |PATCH      |
|`D` |DELETE     |

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
