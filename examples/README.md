# Running the Examples:

## Connecting to your instance

1. Ask your OFS administrator for an application ID *(Configuration > Users, Security, Integration > Applications)* with access to the Core and Metadata APIs and authentication via client_id / client_secret
2. The parameter `COMPANY` is the name of your OFS instance. For example, if your instance is on http://mycompany.etadirect.com then your COMPANY is *mycompany*
3. Some scripts need an extra instance parameter (`ROOT`), that is the external ID of the root resource in the resource tree, or the root of the resources tou can access
4. Set the instance parameters either via environment vars (OFSC_CLIENT_ID, OFS_CLIENT_SECRET, OFS_COMPANY) or directly in the config.py file

## Examples provided ##

`get_users_simple.py`: extract from the OFS instance a list of users and print their login, names and full_names

`get_capacity_areas.py`: extracts the list of capacity areas (buckets) defined in the system