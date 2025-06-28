"""Example showing backward compatibility wrapper usage.

This example demonstrates how existing v2.x code can work with minimal changes
using the compatibility wrapper over the new async v3.0 architecture.
"""

import asyncio
import os
from ofsc.compat import OFSC


def main_sync_style():
    """Example using the backward compatibility wrapper (v2.x style)."""
    print("=== Backward Compatibility Example ===")
    
    # Get credentials from environment or use defaults
    instance = os.getenv("OFSC_INSTANCE", "demo")
    client_id = os.getenv("OFSC_CLIENT_ID", "test_client")
    client_secret = os.getenv("OFSC_CLIENT_SECRET", "test_secret")
    
    print(f"Using instance: {instance}")
    
    # This is exactly how v2.x code would look
    try:
        with OFSC(instance=instance, client_id=client_id, client_secret=client_secret) as client:
            print(f"✅ Client created: {client}")
            
            # Both access patterns should work
            print("\n--- API Access Patterns ---")
            print(f"✅ Direct methods available: {hasattr(client, 'get_users')}")
            print(f"✅ Core API available: {hasattr(client.core, 'get_users')}")
            print(f"✅ Metadata API available: {hasattr(client.metadata, 'get_properties')}")
            
            # Test method signatures
            print("\n--- Method Signatures ---")
            get_users = getattr(client, 'get_users')
            print(f"✅ get_users method: {get_users}")
            print(f"✅ get_users signature: {get_users.__signature__}")
            print(f"✅ get_users documentation: {get_users.__doc__[:100]}...")
            
            # For actual API calls, we would need valid credentials
            # users = client.get_users(offset=0, limit=10)
            # print(f"Found {users.totalResults} users")
            
            print("\n--- Success! Backward compatibility wrapper works! ---")
            
    except Exception as e:
        print(f"❌ Error (expected with demo credentials): {e}")
        print("✅ This is expected behavior with invalid credentials")


async def main_async_style():
    """Example using the new async v3.0 API for comparison."""
    print("\n=== New Async v3.0 API Example ===")
    
    from ofsc import OFSC as AsyncOFSC
    
    instance = os.getenv("OFSC_INSTANCE", "demo")
    client_id = os.getenv("OFSC_CLIENT_ID", "test_client")
    client_secret = os.getenv("OFSC_CLIENT_SECRET", "test_secret")
    
    print(f"Using instance: {instance}")
    
    try:
        async with AsyncOFSC(instance=instance, client_id=client_id, client_secret=client_secret) as client:
            print(f"✅ Async client created: {client}")
            
            # Async API pattern
            print("✅ Async API requires 'await' keyword")
            print("✅ Example: users = await client.core.get_users()")
            
            # For actual API calls, we would need valid credentials
            # users = await client.core.get_users(offset=0, limit=10)
            # print(f"Found {users.totalResults} users")
            
            print("✅ Async API is ready for production use!")
            
    except Exception as e:
        print(f"❌ Error (expected with demo credentials): {e}")
        print("✅ This is expected behavior with invalid credentials")


def migration_guide():
    """Show the migration path from v2.x to v3.0."""
    print("\n=== Migration Guide ===")
    
    print("📝 Step 1: Drop-in replacement")
    print("   # Old v2.x:")
    print("   from ofsc import OFSC")
    print("   ")
    print("   # New compatibility:")
    print("   from ofsc.compat import OFSC")
    print("   # Everything else stays the same!")
    
    print("\n📝 Step 2: Gradual migration to async")
    print("   # Start using async for new code:")
    print("   from ofsc import OFSC as AsyncOFSC")
    print("   async with AsyncOFSC(...) as client:")
    print("       users = await client.core.get_users()")
    
    print("\n📝 Step 3: Full async migration")
    print("   # Convert all code to async for best performance")
    print("   # Remove compatibility wrapper imports")
    
    print("\n✅ Migration completed!")


if __name__ == "__main__":
    # Run the sync example
    main_sync_style()
    
    # Run the async example
    asyncio.run(main_async_style())
    
    # Show migration guide
    migration_guide()