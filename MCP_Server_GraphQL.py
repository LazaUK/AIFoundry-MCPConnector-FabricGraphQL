import os
from dotenv import load_dotenv
import requests
import json
from azure.identity import InteractiveBrowserCredential
from mcp.server.fastmcp import FastMCP

# Extracting environment variables
load_dotenv()
AZURE_FABRIC_GRAPHQL_ENDPOINT = os.getenv("AZURE_FABRIC_GRAPHQL_ENDPOINT")

# Initialising MCP server
mcp = FastMCP("Microsoft Fabric GraphQL MCP Server")

# Getting Entra ID access token
app = InteractiveBrowserCredential()
scp = "https://analysis.windows.net/powerbi/api/user_impersonation"
result = app.get_token(scp)
if not result.token:
    raise Exception("Could not get access token")
token = result.token

# Function to execute GraphQL query
def execute_graphql_query(endpoint, query, variables):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(endpoint, json={'query': query, 'variables': variables}, headers=headers)
        response.raise_for_status()
        data = response.json()
        return json.dumps(data, indent=4)
    except Exception as error:
        return f"Query failed with error: {error}"

@mcp.tool()
def get_trips_and_total_amount(medallion_id: int) -> str:
    """Retrieve the number of trips and total amount paid by a specific Medallion ID."""
    query = """
        query GetTripsAndTotalAmount($medallionId: Int!) {
            trips(filter: { MedallionID: { eq: $medallionId } }) {
                groupBy(fields: [MedallionID]) {
                    aggregations {
                        count(field: MedallionID)
                        sum(field: TotalAmount)
                    }
                }
            }
        }
    """
    variables = {"medallionId": medallion_id} # Try with 8137
    result = execute_graphql_query(AZURE_FABRIC_GRAPHQL_ENDPOINT, query, variables)
    return result

@mcp.tool()
def charge_new_trip(medallion_id: int, total_amount: float) -> str:
    """Charge a Medallion ID for a new trip."""
    fare_amount = total_amount / 1.10
    tip_amount = fare_amount * 0.10

    # Hard-coded values by Laziz for the sake of example
    # In a real-world scenario, these values would be dynamically generated or retrieved
    trip_data = {
        "DateID": 20150317,
        "MedallionID": medallion_id,
        "HackneyLicenseID": 18384,
        "PickupTimeID": 25381,
        "DropoffTimeID": 25387,
        "PickupGeographyID": 11584,
        "DropoffGeographyID": 224403,
        "PickupLatitude": 40.7128,
        "PickupLongitude": -74.0060,
        "PickupLatLong": "40.7128,-74.0060",
        "DropoffLatitude": 40.7128,
        "DropoffLongitude": -74.0060,
        "DropoffLatLong": "40.7128,-74.0060",
        "PassengerCount": 1,
        "TripDurationSeconds": 600,
        "TripDistanceMiles": 5.0,
        "PaymentType": "CRD",
        "FareAmount": fare_amount,
        "SurchargeAmount": 0,
        "TaxAmount": 0,
        "TipAmount": tip_amount,
        "TollsAmount": 0.0,
        "TotalAmount": total_amount
    }

    query = f"""
        mutation {{
            createTrip(item: {{
                DateID: {trip_data['DateID']},
                MedallionID: {medallion_id},
                HackneyLicenseID: {trip_data['HackneyLicenseID']},
                PickupTimeID: {trip_data['PickupTimeID']},
                DropoffTimeID: {trip_data['DropoffTimeID']},
                PickupGeographyID: {trip_data['PickupGeographyID']},
                DropoffGeographyID: {trip_data['DropoffGeographyID']},
                PickupLatitude: {trip_data['PickupLatitude']},
                PickupLongitude: {trip_data['PickupLongitude']},
                PickupLatLong: "{trip_data['PickupLatLong']}",
                DropoffLatitude: {trip_data['DropoffLatitude']},
                DropoffLongitude: {trip_data['DropoffLongitude']},
                DropoffLatLong: "{trip_data['DropoffLatLong']}",
                PassengerCount: {trip_data['PassengerCount']},
                TripDurationSeconds: {trip_data['TripDurationSeconds']},
                TripDistanceMiles: {trip_data['TripDistanceMiles']},
                PaymentType: "{trip_data['PaymentType']}",
                FareAmount: {fare_amount},
                SurchargeAmount: {trip_data['SurchargeAmount']},
                TaxAmount: {trip_data['TaxAmount']},
                TipAmount: {tip_amount},
                TollsAmount: {trip_data['TollsAmount']},
                TotalAmount: {total_amount}
            }}) {{
                result
            }}
        }}
    """
    variables = {} 
    result = execute_graphql_query(AZURE_FABRIC_GRAPHQL_ENDPOINT, query, variables)
    return result

# Start the server for custom implementations
if __name__ == "__main__":
    mcp.run()