#The purpose of the operation to fetch keyrequest data in dynatrace
# in setting API service subsription used to get key req
# But It has obj ID, scope/service Id and and key request
# We use entity api to get service name and managementzone name details. and merging both api result 

import requests
import pandas as pd
import requests
import logging
import warnings
warnings.simplefilter("ignore")
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("pandas").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

#Need to give value and replace DynatraceURI-> Authorization ,https://{your-domain}/e/{your-environment-id} for managed or https://{your-environment-id}.live.dynatrace.com for SaaS

result_df = pd.DataFrame()
headers = {
    'accept': 'application/json; charset=utf-8',
    'Authorization': 'Api-Token *************************************'
}

def Get_KeyReq(result_df):
    url = "https://{your-enviroment-domain-or-id}/api/v2/settings/objects?schemaIds=builtin%3Asettings.subscriptions.service&fields=objectId%2Cvalue%2Cscope&pageSize=500"
    url2 = "https://{your-enviroment-domain-or-id}/api/v2/settings/objects?nextPageKey="
    print("----Function to repeat next page key is called -----")
    result_df = nextpagekey_loop_data(url,url2,result_df)
    print("----Result Data / Ouput after Combining all data ----")
    print(result_df)
    # result_df.to_excel("result_df_nextpageKey.xlsx",index=False)

    df_items = result_df["items"]
    df_extracted = df_items.apply(pd.Series) # It Splits data from dictionary and makes keys as colunn
    print("----Extracted separate col for new df from Items(obj id,scope,value) column -----")
    print(df_extracted)
    # df_extracted.to_excel("df_extracted_keyReq.xlsx",index=False)

    new_col =[]
    for row in df_extracted["value"]:
        value = row # Convert 'str' into 'python dict'
        value = list(value.values())[0] # Converts to the values of dict into List
        new_col.append(value) # New column contains list of request
    df_extracted["List_value"] = new_col # New column added
    return df_extracted
    
def nextpagekey_loop_data(url,url2,result_df):
    response = requests.get(url, headers=headers, verify=False)
    dfm = pd.DataFrame(response.json())
    # print(dfm.columns)
    if "nextPageKey" in dfm.columns:
        nextpagekey = dfm["nextPageKey"][0]
        url = url2+nextpagekey
        # print(url)
        result_df = pd.concat([result_df,dfm], ignore_index=True)
        return nextpagekey_loop_data(url,url2,result_df)
    else:
        result_df = pd.concat([result_df,dfm], ignore_index=True)
        print("------ nextpagekey OUT ------")
        return result_df

# ===========================================================================================================================

def servicebulk(result_df,df_extracted):
    result_df = Get_Service_Bulk(result_df) # called Get_Service_Bulk function to get service data for certain period and stores result
    # result_df.to_excel("nextpage_df_servicedetail.xlsx",index=False)
    service_df = result_df["entities"].apply(pd.Series) # It Splits data from dictionary and makes keys as colunn

    print("---- list operation (KeyReqservice to Entities Service----")
    keyreq_service = list(df_extracted["scope"])
    entities_service = list(service_df["entityId"])
    print("keyreq service :", len(keyreq_service))
    print("entities service :", len(entities_service))

    unique_service = [item for item in keyreq_service if item not in entities_service]
    common_service = [item for item in keyreq_service if item in entities_service]
    print("unique ",len(unique_service))
    print("common ",len(common_service))

    print("---- Service appending...")
    service_df = servicesingle(service_df,unique_service) # It calles other API to get details for single servcice
    print("*******All Service details********")
    print(service_df)
    return service_df

def Get_Service_Bulk(result_df):
    url = "https://{your-enviroment-domain-or-id}/api/v2/entities?pageSize=4000&entitySelector=type%28%22SERVICE%22%29&from=now-500d&fields=%2BmanagementZones"
    url2 = "https://{your-enviroment-domain-or-id}/api/v2/entities?nextPageKey="
    service_df = nextpagekey_loop_data(url,url2,result_df) # It calls nextpagekey fun to get all result
    print(service_df)
    return service_df

def servicesingle(service_df,unique_service):
    url1 = "https://{your-enviroment-domain-or-id}/api/v2/entities/"
    url2 = "?fields=properties%2CmanagementZones" 

    responses=[]
    for SID in unique_service:
        response = requests.get(url1+SID+url2, headers=headers, verify=False)
        # print(response.json())
        responses.append(response.json())  
    service_respdf = pd.DataFrame(responses)
    service_respdf = service_respdf[["entityId","type","displayName","managementZones"]] # Restructure the servcie dataframe and drpping unwanted column
    print(service_respdf)
    service_df = pd.concat([service_df,service_respdf], ignore_index=True)
    return service_df

# ==================================================================================================================

def merge(df_extracted,service_df):
    merged_df = pd.merge(df_extracted,service_df, left_on="scope", right_on="entityId", how ="left")
    mgmtzone = []
    for mgmtz in merged_df["managementZones"]:
        mgmtzone.append(str([d[list(d.keys())[1]] for d in mgmtz])) # each mgmt row contains dict , so creating list to store all values of dict. and looping
    merged_df ["MgmtZone"] = mgmtzone # Adding column into dataframe
    print(merged_df.columns)
    merged_df = merged_df[['objectId', 'scope', 'displayName','List_value', 'MgmtZone']] # Restructure dataframe/ Rename column
    # print(merged_df)
    print("---- Column containing lists splits into separate rows for each element in list ----")

    # Splits(explodes)column containing lists into separate rows for each element in list
    merged_df = merged_df.explode("List_value").reset_index(drop=True) # Splits(explodes)column containing lists into separate rows for each element in list
    merged_df.to_excel("KeyReqData.xlsx")
    print("==== >>> Excel Exported ...!...")
    print("********..D..O..N..E..*********")
    
keyreq_data = Get_KeyReq(result_df)  # It gets key req data and stores
service_data = servicebulk(result_df,keyreq_data) # It gets servicename and managementzone
merge(keyreq_data,service_data) #It merges both the result (keyreq+service) 
