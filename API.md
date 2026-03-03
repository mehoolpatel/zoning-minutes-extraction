### 1. Member Directory

**GET** `/api/v1/analytics/members`  

Returns a list of members in the database.

**Query Parameters:**
- `member_name` (optional, string) — filter by member name
- `limit` (optional, integer, default=50, max=500) — max number of members to return

**Response Example:**
```json
[
  {
    "id": 2,
    "name": "John Edinger",
    "first_seen": "2025-01-12",
    "last_seen": "2025-08-12"
  },
  {
    "id": 5,
    "name": "Jane Nash",
    "first_seen": "2025-03-15",
    "last_seen": "2025-08-12"
  }
]
```

### 2. Member Statistics

**GET** `/api/v1/analytics/members/{member_id}`  

Returns aggregated vote statistics and first/last seen dates for a specific member.

**Path Parameters:**
- `member_id` (int, required) — ID of the member

**Response Example:**
```json
{
  "member_id": 2,
  "member_name": "John Edinger",
  "first_seen": "2025-01-12",
  "last_seen": "2025-08-12",
  "vote_summary": {
    "Yes": 15,
    "No": 3,
    "Abstain": 1,
    "Absent": 2
  }
}
```

### 3. Votes Timeline

**GET** `/api/v1/analytics/votes`  

Returns a timeline of votes, optionally filtered by member, item type, and date range.

**Query Parameters:**
- `member_id` (optional, int) — filter by specific member
- `item_type` (optional, string) — e.g., "CASE", "AGENDA"
- `start_date` (optional, string, YYYY-MM-DD) — filter votes from this date
- `end_date` (optional, string, YYYY-MM-DD) — filter votes up to this date
- `limit` (optional, int, default=100, max=500) — maximum number of votes to return

**Response Example:**
```json
[
  {
    "member_name": "John Edinger",
    "member_id": 2,
    "item_type": "CASE",
    "item_id": 3,
    "description": "VAR2025-00023",
    "vote_cast": "Yes",
    "meeting_date": "2025-08-12"
  },
  {
    "member_name": "Jane Nash",
    "member_id": 5,
    "item_type": "CASE",
    "item_id": 3,
    "description": "VAR2025-00023",
    "vote_cast": "Yes",
    "meeting_date": "2025-08-12"
  }
]
```

### 4. Meeting Items List

**GET** `/api/v1/analytics/meeting-items`  

Returns a list of meeting items with vote summaries.

**Query Parameters:**
- `item_type` (optional, string) — e.g., "CASE", "AGENDA"
- `start_date` (optional, string, YYYY-MM-DD) — filter items from this date
- `end_date` (optional, string, YYYY-MM-DD) — filter items up to this date
- `limit` (optional, int, default=100, max=500) — maximum number of items to return

**Response Example:**
```json
[
  {
    "item_id": 3,
    "item_type": "CASE",
    "item_name": "VAR2025-00023",
    "meeting_date": "2025-08-12",
    "vote_count": 5,
    "yes_votes": 5,
    "no_votes": 0,
    "abstain_votes": 0,
    "absent_count": 0,
    "action": "Approved with Conditions"
  },
  {
    "item_id": 4,
    "item_type": "AGENDA",
    "item_name": "Approval of Minutes",
    "meeting_date": "2025-08-12",
    "vote_count": 5,
    "yes_votes": 5,
    "no_votes": 0,
    "abstain_votes": 0,
    "absent_count": 0,
    "action": "Approved"
  }
]
```
### 5. Meeting Item Details

**GET** `/api/v1/analytics/meeting-items/{item_id}`  

Returns full details of a single meeting item including votes and optional CASE-specific fields.

**Path Parameters:**
- `item_id` (int, required) — ID of the meeting item

**Response Example:**
```json
{
  "item_id": 3,
  "item_type": "CASE",
  "item_name": "VAR2025-00023",
  "meeting_date": "2025-08-12",
  "vote_count": 5,
  "yes_votes": 5,
  "no_votes": 0,
  "abstain_votes": 0,
  "absent_count": 0,
  "action": "Approved with Conditions",
  "applicant": "Genuine Mapping & Design, LLC",
  "owner": "Asfaw Ambaye",
  "contact": "Benjamin Drerup",
  "phone_number": "678.557.0384",
  "zoning": "C-2",
  "location": "4934 Stone Mountain Highway",
  "map_number": "R6057 010",
  "variance_requested": "To not provide interparcel access",
  "commission_district": "(2) Ku",
  "motion_by": "Edinger",
  "seconded_by": "Walthour",
  "votes": [
    {
      "member_name": "Edinger",
      "member_id": 2,
      "item_type": "CASE",
      "item_id": 3,
      "description": "VAR2025-00023",
      "vote_cast": "Yes",
      "meeting_date": "2025-08-12"
    },
    {
      "member_name": "Nash",
      "member_id": 5,
      "item_type": "CASE",
      "item_id": 3,
      "description": "VAR2025-00023",
      "vote_cast": "Yes",
      "meeting_date": "2025-08-12"
    }
  ]
}
```
### 6. Trigger Ingestion

**POST** `/api/v1/analytics/ingest`  

Triggers the document ingestion pipeline using the currently configured vector store.

**Query Parameters:**
- `use_mock` (optional, boolean, default=True) — whether to use mocked data

**Response Example:**
```json
{
  "status": "success",
  "processed_chunks": 25,
  "extractions_found": 80
}
```