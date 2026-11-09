import ast

with open(r"C:\Users\jvris\Downloads\pod-siksha\server.py", "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())

public_routes = {
    "/",
    "/prototype",
    "/redesign",
    "/privacy",
    "/api/privacy",
    "/terms",
    "/api/terms",
    "/api/health",
    "/api/auth/register",
    "/api/auth/verify-email",
    "/api/auth/resend-verification",
    "/api/auth/login",
    "/api/auth/logout",
    "/api/auth/forgot-password",
    "/api/auth/reset-password",
}

print(f"{'METHOD':<7} {'PATH':<42} {'HANDLER':<30} {'STATUS'}")
print("-" * 95)

total = 0
exposed = 0

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr in ("get", "post", "delete", "patch", "put"):
                method = dec.func.attr.upper()
                if dec.args and isinstance(dec.args[0], ast.Constant):
                    path = dec.args[0].value
                    total += 1
                    params = [arg.arg for arg in node.args.args]
                    is_public = path in public_routes
                    
                    # Check if get_current_user or require_teacher_user is in defaults
                    has_auth = False
                    for default in node.args.defaults:
                        default_str = ast.unparse(default)
                        if "get_current_user" in default_str or "require_teacher_user" in default_str:
                            has_auth = True
                            break
                    
                    if is_public:
                        status = "PUBLIC [OK]"
                    elif has_auth:
                        status = "PROTECTED [OK]"
                    else:
                        status = "EXPOSED [CRITICAL FAIL]"
                        exposed += 1
                    
                    print(f"{method:<7} {path:<42} {node.name:<30} {status}")

print("-" * 95)
print(f"Total Routes Audited: {total} | Exposed Unprotected Routes: {exposed}")
