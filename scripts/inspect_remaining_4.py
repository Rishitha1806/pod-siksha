import ast

with open(r"C:\Users\jvris\Downloads\pod-siksha\server.py", "r", encoding="utf-8") as f:
    text = f.read()

tree = ast.parse(text)
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name in ("start_oral_quiz", "generate_quiz_legacy", "evaluate_quiz_legacy", "get_teacher_recommendations"):
            print(f"Function {node.name} on line {node.lineno}:")
            lines = text.splitlines()[node.lineno-2:node.lineno+5]
            for l in lines:
                print("  ", l)
