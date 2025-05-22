def generate_nickname(member_info, existing_members):
    first = member_info.get("first_name", "").strip()
    last = member_info.get("last_name", "").strip()
    base = (first[:1] + last).lower()
    count = sum(1 for m in existing_members if m.nick and m.nick.startswith(base))
    return f"{base}{count + 1}" if count else base
