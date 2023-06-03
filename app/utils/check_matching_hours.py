def check_hours_have_matches(courier_hours: dict, order_hours: dict) -> bool:
    if (  # noqa:SIM103
        (order_hours["start_at"] < courier_hours["end_at"] and order_hours["end_at"] > courier_hours["start_at"])
        or (  # noqa:W503
            order_hours["end_at"] > courier_hours["start_at"] and order_hours["start_at"] < courier_hours["end_at"]
        )
        or (  # noqa:W503
            order_hours["start_at"] > courier_hours["start_at"] and order_hours["end_at"] > courier_hours["end_at"]
        )
        or (  # noqa:W503
            order_hours["start_at"] < courier_hours["start_at"] and order_hours["end_at"] < courier_hours["end_at"]
        )
    ):
        return True
    else:
        return False


def match_hours(courier_hours: dict, order_hours: dict) -> bool:
    """Проверяю, что есть пересечение между часами приема заказа и часами работы курьера"""
    if (order_hours["start_at"] < order_hours["end_at"]) and (courier_hours["start_at"] < courier_hours["end_at"]):
        return check_hours_have_matches(courier_hours, order_hours)
    else:
        """Кейс когда мы переходим 24 часа непонятен, из саппорта точно не получил ответ, валидно ли это,
        может ли курьер рабоать с 23 часов по 2 часа, поэтому решил сразу такой случай не пытаться матчить"""
        return False
