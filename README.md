# Fetch Dynatrace KeyRequests with respective service ID, Name and ManagementZone

# Initial steps:
 1. Enter valid token with scope
 2. Replace Dynatrace URI{your-environment-domain-id} to you environemt domain and id
 3. RUN the python file in a machine where python installed and connectivity available to dynatrace cluster.
 4. Key Request Data Exported as Excel file.

## Detailed steps and algorithm explained below
### 1. GET/settings/objectsLists persisted settings objects
Setting-KeyReq-API: Parameter (schema id, field [obj, value, scope]

  url ="https://{your-environment-domain-id}/api/v2/settings/objects?schemaIds=builtin%3Asettings.subscriptions.service&fields=objectId%2Cvalue%2Cscope&pageSize=500" 

Setting-KeyReq-API_response = requests.get(url, headers=headers, verify=False)


### 2. Setting-KeyReq-NPK-API : Parameter (nextpagekey)

 url = "https://{your-environment-domain-id}/api/v2/settings/objects?nextPageKey=DynamicValue-****" 

Setting-KeyReq-NPK-API_response = requests.get(url, headers=headers, verify=False)


### 3. GET/entities  Gets the information about monitored entities
Entities-Service-API: Praameter(time=now-365d,field =type(SERVICE)

url = https://{your-environment-domain-id}/api/v2/entities?entitySelector=type%28SERVICE%29&from=now-365

Entities-Service-API_response = requests.get(url, headers=headers, verify=False)


### 4. GET/entities/{entityId} Gets the properties of the specified monitored entity
EntityID-Service-API: Parameters( fileds –properties,mgmtzone, serviceId- It is a dynamic filter)

 url =  "https://{your-environment-domain-id}/api/v2/entities/DynamicValueSERVICE-*****?fields=properties%2CmanagementZones" 

EntityID-Service-API_response = requests.get(url, headers=headers, verify=False)


## Algorithm / Steps:

    1. First  Setting-KeyReq-API
    2. Check whether the O/P contains nextPagekey or not.
    3. If does not contain, move to step 7.
    4. If contains run Setting-KeyReq-NPK-API using nextpagekey which available in previous O/P,
    5. Repeat step 4, untill, nextpagekey is not available in O/P.
    6. After all RUN completed, MERGE all the output using logics and move to 7th step.
    7. Covert the o/p  to dataframe/table with column Objid, service Id, Keyreq names → KeyReqDF
    8. Export service ID alone in separate list(List1)
    9. RUN Entity-Service-API(3rd api)  to get All service name,id and mgmtzone details. Large env contains nextpagekey. So repeat step 4 and 5 based on o/p
    10. Find unique service ID in List1(8th step) using – List1(KeyReqAPI) & List2( Entity-Service-API)
    11. RUN EntityID-Service-API which is used to get entity details(mgmtzone,servicename) using ServiceID for UniqueServicID(o/p of step 10)
    12. CONCAT EntityID-Service-API(4th) o/p and Entities-Service-API o/p → ServiceDF
    13. MERGE ServiceDF and KeyReqDF O/Ps Dataframe contains ObjId, Sid, KeyReq. Mgmt, sname. Convert to Excel.
