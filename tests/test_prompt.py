import sys
import os
import json

# --- Add project root to sys.path so 'app' can be imported ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) # Assumes script is in /tests
if project_root not in sys.path:
    sys.path.append(project_root)

from app.pipeline.extractors.llm_extractor import LLMExtractor
from app.core.schemas import DocumentChunk, DocumentMetadata
from app.pipeline.extractors import get_extractor

# Load a sample of raw OCR text that caused issues
sample_text2 = """
Tuesday, August 12, 2025\nPage 2\n 2. Case Number: VAR2025-00024\nApplicant: Genuine Mapping & Design, LLC\nOwner: Asfaw Ambaye\nContact: Benjamin Drerup\nPhone Number: 678.557.0384\nZoning: C-2\nLocation: 4934 Stone Mountain Highway\nMap Number: R6057 010\nVariance Requested: Buffer reduction\nCommission District: (2) Ku\n{Action: Approved with Conditions; Motion: Edinger Second: Walthour; Vote: 5-0: Timler-Yes; Edinger-Yes;\nWalthour-Yes; Rumbaugh-Yes; Nash-Yes}\n\n 3. Case Number: VAR2025-00025\nApplicant: Genevieve Adjahoto\nOwner: Patrice Houessou\nContact: Genevieve Adjahoto\nPhone Number: 678.382.5050\nZoning: R-100\nLocation: 4108 Anthony Creek Drive\nMap Number: R5033 129\nVariance Requested: Reduce minimum lot size for a personal care home\nCommission District: (3) Watkins\n{Action: Approved with Conditions; Motion: Timler Second: Edinger; Vote: 5-0: Timler-Yes; Edinger-Yes;\nWalthour-Yes; Rumbaugh-Yes; Nash-Yes}\n G. OTHER BUSINESS\n H. ANNOUNCEMENTS\n\n I. ADJOURNMENT\n{Action: Approved; Motion: Edinger Second: Timler; Vote: 5-0: Timler-Yes; Edinger-Yes; Walthour-Yes;\nRumbaugh-Yes; Nash-Yes}
"""

sample_text1 = """
Zoning Board of Appeals\nTuesday, August 12, 2025, at 6:30pm\nGwinnett Justice and Administration Center\n75 Langley Drive, Lawrenceville, GA 30046\nPresent: Jeff Timler, Bess Walthour, Jim Nash, Denise Rumbaugh, Rich Edinger\nA. Call To Order, Pledge to Flag\nB. Opening Remarks by Chairwoman and Rules of Order\nC. Approval of Agenda\n{Action: Approved; Motion: Timler Second: Edinger; Vote: 5-0: Timler-Yes; Edinger-Yes; Walthour-Yes;\nRumbaugh-Yes; Nash-Yes}\nD. Approval of Minutes: July 8, 2025\n{Action: Approved; Motion: Timler Second: Walthour; Vote: 5-0: Timler-Yes; Edinger-Yes; Walthour-Yes;\nRumbaugh-Yes; Nash-Yes}\nE. Announcements\nF. New Business\n1. Case Number: VAR2025-00023\nApplicant: Genuine Mapping & Design, LLC\nOwner: Asfaw Ambaye\nContact: Benjamin Drerup\nPhone Number: 678.557.0384\nZoning: C-2\nLocation: 4934 Stone Mountain Highway\nMap Number: R6057 010\nVariance Requested: To not provide interparcel access\nCommission District: (2) Ku\n{Action: Approved with Conditions; Motion: Edinger Second: Walthour; Vote: 5-0: Timler-Yes; Edinger-Yes;\nWalthour-Yes; Rumbaugh-Yes; Nash-Yes}
"""

sample_text_2_1 = """
Zoning Board of Appeals\nTuesday, January 14, 2025, at 6:30pm\nGwinnett Justice and Administration Center\n75 Langley Drive, Lawrenceville, GA 30046\nPresent: Jeff Timler, Denise Rumbaugh, Jim Nash, Bess Walthour\nAbsent: Rich Edinger\nA. Call To Order, Pledge to Flag\nB. Opening Remarks by Chairman and Rules of Order\nC. Approval of Agenda\n{Action: Approved; Motion: Nash Second: Rumbaugh; Vote: 3-0: Timler-Yes; Edinger-Absent;\nWalthour-Out of Room; Rumbaugh-Yes; Nash-Yes}\nD. Approval of Minutes: December 11, 2024\n{Action: Approved; Motion: Nash Second: Rumbaugh; Vote: 3-0: Timler-Yes; Edinger-Absent;\nWalthour-Out of Room; Rumbaugh-Yes; Nash-Yes}\nE. Announcements\nF. New Business\n1. Case Number: ZVR2024-00105\nApplicant: Pet Supplies Plus\nOwner: Thomas Prandato\nContact: Felicia Johnson\nPhone Number: 678.539.0443\nZoning: C-2\nLocation: 3280 Hamilton Mill Road\nMap Number: R7182 002\nVariance Requested: Exceed maximum wall sign area per facade\nCommission District: (4) Holtkamp\n{Action: Approved with Conditions; Motion: Rumbaugh Second: Nash; Vote: 4-0: Timler-Yes;\nEdinger-Absent; Walthour-Yes; Rumbaugh-Yes; Nash-Yes} 
"""

sample_text_2_2 = """
Tuesday, January 14, 2025\nPage 2\n2. Case Number: ZVR2024-00106\nApplicant: Pet Supplies Plus\nOwner: Thomas Prandato\nContact: Felicia Johnson\nPhone Number: 678.539.0443\nZoning: C-2\nLocation: 3280 Hamilton Mill Road\nMap Number: R7182 002\nVariance Requested: Exceed maximum wall sign area\nCommission District: (4) Holtkamp\n{Action: Approved with Conditions; Motion: Rumbaugh Second: Nash; Vote: 4-0: Timler-Yes;\nEdinger-Absent; Walthour-Yes; Rumbaugh-Yes; Nash-Yes}\n\n3. Case Number: ZVR2025-00001 (Public Hearing Held on 1/14/2025)\nApplicant/Owner/Contact: Vanessa Canty\nPhone Number: 470.222.6480\nZoning: R-100\nLocation: 2331 Laura Court\nMap Number: R6054 218\nVariance Requested: Reduce minimum lot size for personal care home\nCommission District: (2) Ku\n{Action: Tabled to February 11, 2025; Motion: Nash Second: Rumbaugh; Vote: 4-0: Timler-Yes; EdingerAbsent; Walthour-Yes; Rumbaugh-Yes; Nash-Yes}\n4. Case Number: ZVR2025-00002–Administratively Withdrawn\n5. Case Number: ZVR2025-00003\nApplicant: Boersma Bros., LLC\nOwner: Fuqua BCDC Ballpark Project Owner, LLC\nContact: Harry Raft\nPhone Number: 541.955.4700\nZoning: C-2\nLocation: 2505 Buford Drive\nMap Number: R7132 071\nVariance Requested: Exceed maximum parking\nCommission District: (4) Holtkamp\n{Action: Approved with Conditions; Motion: Rumbaugh Second: Nash; Vote: 4-0: Timler-Yes;\nEdinger-Absent; Walthour-Yes; Rumbaugh-Yes; Nash-Yes}\n6. Case Number: ZVR2025-00004-Administratively Withdrawn\n7. Case Number: ZVR2025-00005 – Administratively Held\n G. OTHER BUSINESS\n H. ANNOUNCEMENTS\n\n I. ADJOURNMENT\n{Action: Approved; Motion: Nash Second: Walthour; Vote: 4-0: Timler-Yes; Edinger-Absent; Walthour-Yes;\nRumbaugh-Yes; Nash-Yes}
"""

sample_text = sample_text1 + "\n" + sample_text2

# Setup metadata (as needed by the extractor)
meta = DocumentMetadata(source_id="test-doc", page_number=1)
chunk = DocumentChunk(content=sample_text, metadata=meta)

# The factory handles the env vars and returns a configured extractor
extractor = get_extractor(provider="openai")

print("--- Running LLM Extraction ---")
results = extractor.extract([chunk])

# Inspect results
for result in results:
    # 1. NEW: The result now contains a list of items, not a single case_number
    # Assuming your updated Extractor model has an 'items' field
    print(f"Extraction for source: {result.document_id}")                
    
    # 2. Print the whole raw JSON output for debugging
    print("Full ExtractionResult Object:")
    print(result.model_dump_json(indent=2))                

    # 3. NEW: Add assertions to verify the nested structure
    # You'll need to parse the raw json output or access the attributes if 
    # you updated your Pydantic models in app/core/schemas.py
    
    # Example assertion (if result.items is a list of Pydantic models):
    # assert len(result.items) > 0
    # assert result.items[0].item_type == "CASE"
    # assert result.items[0].meeting_date == "2025-01-14"
