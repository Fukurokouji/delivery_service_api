import asyncio
from collections import namedtuple

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import decl_base, Session

from app.utils.split_list import split_list


async def bulk_insert_by_parts(
    session: Session, model: decl_base, partitision_size: int, batch: list[dict], returning: Column | None = None
) -> None:
    """Функция, которая делает балкинсерт данных в базу, с делением данных на несколько вставок,во избежания ошибки,
    что инсертим больше int16 элементов, также можно задать значения, которые надо вернуть после инсерта"""
    if returning:
        query = insert(model).returning(returning)
    else:
        query = insert(model)
    if len(batch) > partitision_size:
        courutine_add_list = []
        for order_sub_list in split_list(batch, partitision_size):
            added_query = query.values(order_sub_list)
            cursor_courutine = session.execute(added_query)
            courutine_add_list.append(cursor_courutine)
        all_res = await asyncio.gather(*courutine_add_list)
        await session.commit()
        if returning:  # noqa:R503
            all_returned_values = [x.all() for x in all_res]
            return [item for sublist in all_returned_values for item in sublist]

    else:
        added_query = query.values(batch)
        query_cursor = await session.execute(added_query)
        await session.commit()
        if returning:  # noqa:R503
            return query_cursor.all()


CourierStats = namedtuple("Stats", ["id", "rating", "salary"])  # Именнованный кортеж, для удобного
# перехода из рекордов с raw sql в нормальный маппинг
