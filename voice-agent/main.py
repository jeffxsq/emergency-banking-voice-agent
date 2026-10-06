import os
import time
import uvicorn
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel

# Initialize single FastAPI instance
app = FastAPI(title="Emergency Banking Voice Agent API")

# Simulated Banking Database
MOCK_ACCOUNTS = {
    "acc_9921": {"name": "Alex Chen", "phone": "+15550192834", "card_status": "ACTIVE", "balance": 14250.00},
    "acc_4012": {"name": "Jordan Smith", "phone": "+15550123456", "card_status": "ACTIVE", "balance": 3100.50}
}

class FreezeCardRequest(BaseModel):
    account_id: str
    reason: str | None = None

    
# --- 1. Banking Freeze Card Tool Endpoint ---  
@app.post("/api/v1/banking/freeze-card")
async def freeze_card(payload: FreezeCardRequest):
    clean_account_id = payload.account_id.strip().lower()
    account = MOCK_ACCOUNTS.get(clean_account_id)
    
    if not account:
        return {
            "success": False,
            "account_id": payload.account_id,
            "message": f"Account {payload.account_id} was not found."
        }
    
    account["card_status"] = "FROZEN"
    
    return {
        "success": True,
        "action_taken": "CARD_FROZEN",
        "account_id": clean_account_id,
        "account_holder": account["name"],
        "message": f"SUCCESS: The debit card for account {clean_account_id} belonging to {account['name']} has been frozen immediately.",
        "instructions_for_agent": "Tell the user that their debit card has been successfully frozen and ask if they need further emergency assistance."
    }


# --- 2. POST-CALL TELEMETRY AUDIT ENDPOINT (Unverified) ---
@app.post("/api/v1/telemetry/post-call-audit")
async def post_call_audit(request: Request):
    """Receives post-call transcripts & analysis without signature checks"""
    body = await request.json()
    conversation_id = body.get("conversation_id")
    analysis = body.get("analysis", {})

    print(f"[AUDIT LOG] Received Call {conversation_id} telemetry.")
    print(f"Summary: {analysis.get('transcript_summary')}")
    print(f"User Sentiment: {analysis.get('user_sentiment')}")

    return {"status": "LOGGED"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)