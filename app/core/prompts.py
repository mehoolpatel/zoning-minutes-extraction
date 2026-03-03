# /app/cor/
import json

# The "Contract" for the JSON output
EXTRACTION_SCHEMA = {
    "meeting_date": "YYYY-MM-DD",
    "items": [
        {
            "item_type": "string", # e.g., "CASE", "AGENDA", "MINUTES", "ADJOURNMENT"
            "item_name": "string", # Case number (e.g., VAR2025-00004) or Item name
            "applicant": "string",
            "owner": "string",
            "contact": "string",
            "phone_number": "string",
            "zoning": "string",
            "location": "string",
            "map_number": "string",
            "variance_requested": "string",
            "commission_district": "string",
            "action": "string",
            "motion_by": "string",
            "seconded_by": "string",
            "votes": [
                {
                    "member_name": "string",
                    "status": "string", # Yes, No, Abstain, etc.
                    "raw_status": "string"
                }
            ]
        }
    ]
}

SYSTEM_PROMPT = f"""
You are an expert data extraction assistant. 
Extract zoning board meeting information into the following JSON format exactly:

{json.dumps(EXTRACTION_SCHEMA, indent=2)}

- Extract the meeting_date from the document header and format it as YYYY-MM-DD. Apply it to every item in the items list.
- Look for lists labeled "Present", "Teleconference", "Absent", or something similar at the beginning of the document to identify full names of members.
- If a full name cannot be mapped from these lists, use the name as it appears in the 'votes' section.
- Ensure the 'status' field exactly matches one of: Yes, No, Abstain, Absent, Out of Room, Recused, Unknown.
- Identify the item_type as 'CASE' if it is a variance request, 'AGENDA' for agenda approvals, 'MINUTES' for minutes approvals, and 'ADJOURNMENT' for adjournments.
- If a field like applicant or variance_requested does not exist in the text (e.g., for an Adjournment item), populate it with null or an empty string "".
- For location and map_number, if multiple values exist, capture all of them as a single, combined string.                
- Output ONLY valid JSON.
"""