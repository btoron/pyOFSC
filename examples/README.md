# Running the Examples:

## Connecting to your instance

1. Ask your OFS administrator for an application ID *(Configuration > Users, Security, Integration > Applications)* with access to the Core and Metadata APIs and authentication via client_id / client_secret
2. The parameter `COMPANY` is the name of your OFS instance. For example, if your instance is on https://mycompany.fs.ocs.oraclecloud.com then your COMPANY is *mycompany*
   - **Note:** Older instances may use etadirect.com domain. The base URL will be automatically set to the Oracle Cloud domain unless you explicitly set `OFSC_BASE_URL`
3. Some scripts need an extra instance parameter (`ROOT`), that is the external ID of the root resource in the resource tree, or the root of the resources you can access
4. Set the instance parameters either via environment vars (OFSC_CLIENT_ID, OFSC_CLIENT_SECRET, OFSC_COMPANY) or directly in the config.py file

## Examples provided ##

### Synchronous Client Examples

`get_users_simple.py`: extract from the OFS instance a list of users and print their login, names and full_names

`get_capacity_areas.py`: extracts the list of capacity areas (buckets) defined in the system

`export_routing_plans.py`: exports all routing plans from all profiles to separate JSON files (profileName_planName.json)

`get_workzones.py`: extracts workzones and exports them to an Excel file

### Asynchronous Client Examples

`async_basic_usage.py`: demonstrates basic AsyncOFSC usage with async context manager and simple API calls

`async_parallel_requests.py`: shows the SAFE way to parallelize API calls using `asyncio.gather()`, with performance comparison between sequential and parallel execution

`async_antipatterns.py`: educational example showing UNSAFE patterns (threading, shared event loops) to avoid when using AsyncOFSC

`async_parallel_pagination.py`: demonstrates how to parallelize paginated API requests using `asyncio.gather()`, with three approaches (sequential, parallel, controlled concurrency) and performance comparisons

**Note:** Async examples require the async client. Use `asyncio.gather()` for concurrent requests, NOT threading.