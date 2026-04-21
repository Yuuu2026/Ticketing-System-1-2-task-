from __future__ import annotations

import re


def normalize_phone(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def normalize_id_card(s: str) -> str:
    return (s or "").strip().upper().replace(" ", "")


def is_valid_phone(phone: str) -> bool:
    return bool(re.fullmatch(r"1\d{10}", phone))


def is_valid_id_card(c: str) -> bool:
    return bool(re.fullmatch(r"\d{17}[\dX]", c)) or bool(re.fullmatch(r"\d{15}", c))


def mask_phone(phone: str) -> str:
    if len(phone) == 11:
        return phone[:3] + "****" + phone[-4:]
    if len(phone) > 4:
        return phone[:3] + "****" + phone[-2:]
    return "****"


def mask_name(name: str) -> str:
    name = (name or "").strip()
    if not name:
        return ""
    if len(name) == 1:
        return "*"
    return name[0] + "*" * (len(name) - 1)


def id_card_last4(c: str) -> str:
    if len(c) >= 4:
        return c[-4:]
    return "****"


def user_public(user) -> dict:
    return {
        "id": user.id,
        "phone": mask_phone(user.phone),
        "full_name": mask_name(user.full_name),
        "id_card_last4": id_card_last4(user.id_card),
    }
