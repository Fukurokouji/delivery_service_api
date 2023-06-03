"""initial_data

Revision ID: 487b41c7d1aa
Revises: 5b5b1f983f03
Create Date: 2023-06-03 22:27:52.709485

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "487b41c7d1aa"
down_revision = "5b5b1f983f03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "INSERT INTO courier_type(id, rating_coefficient, salary_coefficient, max_area, max_weight_orders, max_orders_count) "
        "VALUES ('FOOT', 3, 2, 1, 10, 2), ('BIKE', 2, 3, 2, 20, 4), ('AUTO', 1, 4, 3, 40, 7)"
    )


def downgrade() -> None:
    op.execute('DELETE FROM "courier_work_time"')
    op.execute('DELETE FROM "courier_area"')
    op.execute('DELETE FROM "courier"')
    op.execute('DELETE FROM "order_delivery_hour"')
    op.execute('DELETE FROM "order"')
    op.execute('DELETE FROM "courier_type"')
    op.execute('DELETE FROM "area"')
