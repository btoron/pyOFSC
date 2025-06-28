# Backward Compatibility Guide for OFSC v3.0

## Overview

OFSC v3.0 introduces a major architectural change from dual sync/async support to async-only. To help with migration, we provide a backward compatibility wrapper that allows existing v2.x code to work with minimal changes.

## Quick Start

### Drop-in Replacement

Change only the import statement:

```python
# Old v2.x code:
# from ofsc import OFSC

# New compatibility wrapper:
from ofsc.compat import OFSC

# Everything else stays exactly the same!
client = OFSC(instance="demo", client_id="your_id", client_secret="your_secret")
users = client.get_users()
print(f"Found {users.totalResults} users")
```

## API Compatibility

### All v2.x Methods Supported

The compatibility wrapper supports ALL methods from v2.x:

#### Core API Methods
- `get_users(offset=0, limit=100)`
- `get_user(login)`
- `create_user(login, data)`
- `update_user(login, data)`
- `delete_user(login)`
- `get_activities(params)`
- `get_activity(activity_id)`
- `update_activity(activity_id, data)`
- `move_activity(activity_id, data)`
- `search_activities(params)`
- `bulk_update(data)`
- `get_subscriptions(allSubscriptions=False)`
- And many more...

#### Metadata API Methods
- `get_properties(offset=0, limit=100)`
- `get_property(label)`
- `get_workskills(offset=0, limit=100)`
- `get_workskill(label)`
- `get_activity_types(offset=0, limit=100)`
- `get_activity_type(label)`
- And many more...

### API Access Patterns

Both v2.x access patterns are supported:

```python
from ofsc.compat import OFSC

client = OFSC(instance="demo", client_id="id", client_secret="secret")

# Pattern 1: Direct method access (v2.x style)
users = client.get_users()
properties = client.get_properties()

# Pattern 2: API namespace access (also supported)
users = client.core.get_users()
properties = client.metadata.get_properties()
```

### Response Types

The compatibility wrapper returns the **same Pydantic models** as the new async API:

```python
users = client.get_users()
# Returns: UserListResponse (Pydantic model)
print(f"Total: {users.totalResults}")
print(f"Users: {users.items}")

properties = client.get_properties()
# Returns: Property (Pydantic model)
print(f"Property: {properties.label}")
```

## Migration Path

### Phase 1: Drop-in Replacement

```python
# Change ONLY the import
from ofsc.compat import OFSC  # was: from ofsc import OFSC

# All existing code works unchanged
with OFSC(instance="demo", client_id="id", client_secret="secret") as client:
    users = client.get_users()
    activities = client.get_activities({'date': '2025-06-28'})
    properties = client.get_properties()
```

### Phase 2: Gradual Async Migration

Start using async for new code:

```python
# Keep using compatibility wrapper for existing code
from ofsc.compat import OFSC

# Use async for new code
from ofsc import OFSC as AsyncOFSC

def existing_function():
    """Existing code keeps working"""
    client = OFSC(instance="demo", client_id="id", client_secret="secret")
    return client.get_users()

async def new_function():
    """New code uses async for better performance"""
    async with AsyncOFSC(instance="demo", client_id="id", client_secret="secret") as client:
        return await client.core.get_users()
```

### Phase 3: Full Async Migration

Convert all code to async:

```python
# Remove compatibility imports
# from ofsc.compat import OFSC

# Use only async API
from ofsc import OFSC

async def main():
    async with OFSC(instance="demo", client_id="id", client_secret="secret") as client:
        users = await client.core.get_users()
        properties = await client.metadata.get_properties()
        return users, properties

# Run with asyncio
import asyncio
asyncio.run(main())
```

## Performance Considerations

### Compatibility Wrapper Performance

The compatibility wrapper:
- ✅ **Works**: Provides 100% API compatibility
- ⚠️ **Performance**: Slightly slower than direct async due to event loop management
- ⚠️ **Resources**: Creates event loop per client instance
- ✅ **Thread-safe**: Safe to use in multi-threaded applications

### Async API Performance

The new async API:
- ✅ **Fast**: Native async performance
- ✅ **Efficient**: Connection pooling and resource management
- ✅ **Scalable**: Built for high-throughput applications
- ✅ **Modern**: Uses httpx.AsyncClient internally

## Context Manager Support

Both patterns are supported:

```python
# Automatic cleanup
with OFSC(instance="demo", client_id="id", client_secret="secret") as client:
    users = client.get_users()
    # Resources automatically cleaned up

# Manual cleanup
client = OFSC(instance="demo", client_id="id", client_secret="secret")
try:
    users = client.get_users()
finally:
    client.close()  # Manual cleanup
```

## Error Handling

Errors are handled the same way as v2.x:

```python
from ofsc.compat import OFSC
from ofsc.exceptions import OFSException

try:
    client = OFSC(instance="demo", client_id="invalid", client_secret="invalid")
    users = client.get_users()
except OFSException as e:
    print(f"OFSC API error: {e}")
except Exception as e:
    print(f"Other error: {e}")
```

## Deprecation Warning

The compatibility wrapper issues a light deprecation warning:

```
DeprecationWarning: Sync OFSC is deprecated. Consider migrating to async for better performance.
```

To suppress warnings during migration:

```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="ofsc.compat")
```

## Examples

### Basic Usage

```python
from ofsc.compat import OFSC

# Same as v2.x
client = OFSC(instance="demo", client_id="id", client_secret="secret")

# Get users with pagination
users = client.get_users(offset=0, limit=50)
print(f"Found {users.totalResults} users")

# Get single user
user = client.get_user("john.doe")
print(f"User: {user.name}")

# Get activities
activities = client.get_activities({
    'date': '2025-06-28',
    'status': 'pending'
})

# Get properties
properties = client.get_properties()
print(f"Properties: {len(properties.items)}")
```

### Advanced Usage

```python
from ofsc.compat import OFSC
from ofsc.models import BulkUpdateRequest, BulkUpdateActivityItem

with OFSC(instance="demo", client_id="id", client_secret="secret") as client:
    # Bulk operations
    bulk_request = BulkUpdateRequest(
        items=[
            BulkUpdateActivityItem(
                activityId="12345",
                status="completed"
            )
        ]
    )
    result = client.bulk_update(bulk_request)
    
    # Metadata operations
    workskills = client.get_workskills(limit=100)
    skill = client.get_workskill("PLUMBING")
    
    # Event subscriptions
    subscriptions = client.get_subscriptions()
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure to import from `ofsc.compat`
   ```python
   # Correct
   from ofsc.compat import OFSC
   
   # Incorrect
   from ofsc import OFSC  # This is the async-only version
   ```

2. **Event Loop Errors**: If running in Jupyter/async environment:
   ```python
   # The wrapper handles this automatically, but if you get errors:
   import nest_asyncio
   nest_asyncio.apply()
   ```

3. **Performance Issues**: For high-throughput applications, migrate to async:
   ```python
   # Replace with async for better performance
   from ofsc import OFSC
   async with OFSC(...) as client:
       users = await client.core.get_users()
   ```

### Getting Help

- **Documentation**: Check the main README for v3.0 features
- **Examples**: See `examples/compat_example.py` for working code
- **Issues**: Report problems at https://github.com/btoron/pyOFSC/issues

## Conclusion

The backward compatibility wrapper allows you to:

1. ✅ **Keep existing code working** with minimal changes
2. ✅ **Migrate gradually** to the new async API  
3. ✅ **Maintain the same API** you're familiar with
4. ✅ **Get the same response types** as v3.0 async API

Start with the compatibility wrapper and migrate to async when you're ready for the performance benefits!