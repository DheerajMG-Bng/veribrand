from fastapi import Header, HTTPException

def get_role(x_role: str = Header(default='creator')):
    if x_role not in {'creator', 'manager', 'reviewer', 'admin'}:
        raise HTTPException(403, 'Choose a valid demo role: creator, manager, reviewer or admin.')
    return x_role

def require(role, *allowed):
    if role not in allowed:
        raise HTTPException(403, f"This action requires the {' or '.join(allowed)} role. Your current demo role is {role}.")
