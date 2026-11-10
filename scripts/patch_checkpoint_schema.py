"""
Patches CheckpointAnswerRequest in animated_router.py to accept both
selected_option_index and selected_idx.
"""

ROUTER_PATH = r"C:\Users\jvris\Downloads\pod-siksha\animated_router.py"

with open(ROUTER_PATH, "r", encoding="utf-8") as f:
    text = f.read()

OLD_MODEL = """class CheckpointAnswerRequest(BaseModel):
    scene_id: str
    selected_option_index: int"""

NEW_MODEL = """class CheckpointAnswerRequest(BaseModel):
    scene_id: str
    selected_option_index: Optional[int] = None
    selected_idx: Optional[int] = None
    question: Optional[str] = None
    is_correct: Optional[bool] = None"""

text = text.replace(OLD_MODEL, NEW_MODEL)

OLD_CHECK = """        correct_idx = chk.get("correct_index", 0)
        is_correct = (payload.selected_option_index == correct_idx)"""

NEW_CHECK = """        sel_idx = payload.selected_option_index if payload.selected_option_index is not None else (payload.selected_idx or 0)
        correct_idx = chk.get("correct_index", 0)
        is_correct = (sel_idx == correct_idx)"""

text = text.replace(OLD_CHECK, NEW_CHECK)

with open(ROUTER_PATH, "w", encoding="utf-8") as f:
    f.write(text)

print("animated_router.py CheckpointAnswerRequest updated successfully!")
