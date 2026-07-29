import re


def format_phone(phone: str) -> str:
    if not phone:
        return ""

    # 숫자만 추출
    phone = re.sub(r"\D", "", phone)

    # 서울(02)
    if phone.startswith("02"):
        if len(phone) == 9:
            return f"{phone[:2]}-{phone[2:5]}-{phone[5:]}"
        elif len(phone) == 10:
            return f"{phone[:2]}-{phone[2:6]}-{phone[6:]}"

    # 휴대폰
    if phone.startswith("010") and len(phone) == 11:
        return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"

    # 지역번호(031, 042, 051 ...)
    if len(phone) == 10:
        return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
    elif len(phone) == 11:
        return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"

    return phone
