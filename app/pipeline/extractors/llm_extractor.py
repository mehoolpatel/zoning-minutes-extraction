import os
import json
import logging
import openai
from typing import List, Dict, Any
from app.core.schemas import DocumentChunk, ExtractionResult, VoteStatus, MemberVote, MeetingItem, ItemType
from app.core.prompts import SYSTEM_PROMPT, EXTRACTION_SCHEMA
from .base import BaseExtractor

logger = logging.getLogger(__name__)

class LLMExtractor(BaseExtractor):
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)

    def _call_llm(self, content: str) -> Dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content}
                ]
            )
            raw_json_str = response.choices[0].message.content

            # --- DEBUG PRINT ---
            #print(f"DEBUG: LLM Raw Output: {raw_json_str}")
            #logger.info(f"LLM Raw Output: {raw_json_str}")
            # ----------------------------
                        
            return json.loads(raw_json_str)
        except Exception as e:
            logger.error(f"LLM API Error: {e}")
            return {}

    def extract(self, chunks: List[DocumentChunk]) -> List[ExtractionResult]:
            results = []
            for chunk in chunks:
                # 1. Call LLM to get raw JSON structure
                llm_json = self._call_llm(chunk.content)
                
                # --- NEW: Parse top-level meeting date ---
                meeting_date = llm_json.get("meeting_date")
                logger.info(
                    f"EXTRACTOR: doc={chunk.metadata.source_id}, page={chunk.metadata.page_number}, "
                    f"meeting_date={meeting_date} (type={type(meeting_date)})"
                ) 
                
                items_for_this_chunk = []
                
                # 2. Iterate through items found in the text (cases + agenda + adjournment)
                for item in llm_json.get("items", []):
                    raw_votes = item.get("votes", [])
                    normalized_votes = []
                    
                    # 3. Normalize Votes
                    if isinstance(raw_votes, list):
                        for vote_item in raw_votes:
                            name = vote_item.get("member_name")
                            vote_str = vote_item.get("status") 
                            
                            try:
                                # Matches string to VoteStatus Enum
                                enum_status = VoteStatus(vote_str)
                            except ValueError:
                                enum_status = VoteStatus.UNKNOWN
                            
                            normalized_votes.append(
                                MemberVote(
                                    member_name=name,
                                    status=enum_status,
                                    raw_status=vote_str
                                )
                            )
                    
                    # 4. Create MeetingItem Pydantic object
                    # Normalize item_type into the ItemType Enum
                    try:
                        item_type_norm = ItemType(item.get("item_type", "").upper())  # will raise ValueError if unknown
                    except ValueError:
                        logger.info(f"[NORMALIZE] Unknown item_type '{item.get('item_type')}' → 'OTHER'")
                        item_type_norm = ItemType.OTHER  # fallback Enum value

                    meeting_item = MeetingItem(
                        item_type=item_type_norm,
                        item_name=item.get("item_name"), # This is case_number for cases
                        applicant=item.get("applicant"),
                        owner=item.get("owner"),
                        contact=item.get("contact"),
                        phone_number=item.get("phone_number"),
                        zoning=item.get("zoning"),
                        location=item.get("location"),
                        map_number=item.get("map_number"),
                        variance_requested=item.get("variance_requested"),
                        commission_district=item.get("commission_district"),
                        action=item.get("action"),
                        motion_by=item.get("motion_by"),
                        seconded_by=item.get("seconded_by"),
                        votes=normalized_votes
                    )
                    items_for_this_chunk.append(meeting_item)
                
                # 5. Append final result object
                results.append(
                    ExtractionResult(
                        document_id=chunk.metadata.source_id,
                        page_number=chunk.metadata.page_number,
                        meeting_date=meeting_date,
                        items=items_for_this_chunk # List of MeetingItem objects
                    )
                )
            return results