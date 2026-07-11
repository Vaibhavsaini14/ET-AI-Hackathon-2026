from fastapi import APIRouter

router = APIRouter()

@router.get("/standards")
async def get_standards():
    return {
        "standards": [
            "Factory Act - Safety",
            "OISD Safety Standards"
        ]
    }

@router.post("/audit")
async def run_audit(request: dict):
    return {
        "message": "Compliance agent coming Day 5",
        "standard_name": request.get("standard_name", "")
    }