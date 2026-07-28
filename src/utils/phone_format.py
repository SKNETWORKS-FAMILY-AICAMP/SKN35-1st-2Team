# crawling 해온 전화번호의 데이터 형태가 다름으로 통일화 함수

import re


def format_phone(phone: str) -> str:
    if not phone:
        return ""

    phone = phone.strip()

    if phone.startswith("+82"):
        phone = phone[3:]

    elif phone.startswith("82"):
        phone = phone[2:]

    phone = re.sub(r"\D", "", phone)

    if not phone.startswith("0"):
        phone = "0" + phone

    if phone.startswith("02"):
        if len(phone) == 9:
            return f"{phone[:2]}-{phone[2:5]}-{phone[5:]}"
        elif len(phone) == 10:
            return f"{phone[:2]}-{phone[2:6]}-{phone[6:]}"

    if phone.startswith("010") and len(phone) == 11:
        return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"

    if len(phone) == 10:
        return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
    elif len(phone) == 11:
        return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"

    return phone
