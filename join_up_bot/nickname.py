def generate_nickname(member_info, existing_members):
    first = member_info.get("first_name", "").strip().capitalize()
    last = member_info.get("last_name", "").strip()[:1].capitalize()
    base = f"{first}{last}"
    count = sum(1 for member in existing_members if member.nick and member.nick.startswith(base))
    return f"{base}{count + 1}" if count else base
