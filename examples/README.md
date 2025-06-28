# Running the Examples (v3.0 Async):

⚠️ **Important**: All examples in v3.0 are async and must be run with `asyncio.run()` or in an async context.

## Connecting to your instance

1. Ask your OFS administrator for an application ID *(Configuration > Users, Security, Integration > Applications)* with access to the Core and Metadata APIs and authentication via client_id / client_secret
2. The parameter `instance` is the name of your OFS instance. For example, if your instance is on http://mycompany.etadirect.com then your instance is *mycompany*
3. Some scripts need an extra instance parameter (`ROOT`), that is the external ID of the root resource in the resource tree, or the root of the resources you can access
4. Set the instance parameters either via environment vars (OFSC_INSTANCE, OFSC_CLIENT_ID, OFSC_CLIENT_SECRET) or directly in the async functions

## Examples provided ##

`get_users_simple.py`: extract from the OFS instance a list of users and print their login, names and full_names (async version)

`get_capacity_areas.py`: extracts the list of capacity areas (buckets) defined in the system (async version)

## Running examples

All examples are now async and should be run like this:

```python
import asyncio
from ofsc import OFSC

async def main():
    async with OFSC(
        instance="your_instance",
        client_id="your_client_id", 
        client_secret="your_client_secret"
    ) as client:
        # Your async code here
        users = await client.core.get_users()
        print(f"Found {users.totalResults} users")

if __name__ == "__main__":
    asyncio.run(main())
```