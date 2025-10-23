"""add_test_data.py

Revision ID: c09a34aa13e6
Revises: 87b8e34c378b
Create Date: 2025-10-22 13:16:27.096309

"""
from alembic import op
import sqlalchemy as sa
import datetime
import uuid

# revision identifiers, used by Alembic.
revision = "add_test_data"
down_revision = "c09a34aa13e6"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    now = datetime.datetime.now()

    # Helper to insert activity and return its id
    def insert_activity(name, parent_id=None):
        id_ = uuid.uuid4()
        connection.execute(
            sa.text(
                "INSERT INTO activities (id, name, parent_id, created_at, modified_at) VALUES (:id, :name, :parent_id, :created_at, :modified_at)"
            ),
            {
                "id": id_,
                "name": name,
                "parent_id": parent_id,
                "created_at": now,
                "modified_at": now,
            },
        )
        return id_

    # Insert activities hierarchy
    id_eda = insert_activity("Еда")
    id_myasnaya = insert_activity("Мясная продукция", id_eda)
    id_ptitsa = insert_activity("Птица", id_myasnaya)
    id_polufabrikaty = insert_activity("Полуфабрикаты", id_myasnaya)
    id_molochnaya = insert_activity("Молочная продукция", id_eda)

    id_avtomobili = insert_activity("Автомобили")
    id_gruzovye = insert_activity("Грузовые", id_avtomobili)

    id_legkovye = insert_activity("Легковые")
    id_zapchasti = insert_activity("Запчасти", id_legkovye)
    id_aksessuary = insert_activity("Аксессуары", id_legkovye)

    # Insert buildings (несколько примеров)
    buildings = [
        {
            "id": uuid.uuid4(),
            "address": "ул. Пушкина, д.1",
            "latitude": 55.751244,
            "longitude": 37.618423,
        },
        {
            "id": uuid.uuid4(),
            "address": "пр. Ленина, д.10",
            "latitude": 59.934280,
            "longitude": 30.335099,
        },
        {
            "id": uuid.uuid4(),
            "address": "ул. Чехова, д.5",
            "latitude": 56.838011,
            "longitude": 60.597465,
        },
    ]
    for b in buildings:
        connection.execute(
            sa.text(
                "INSERT INTO buildings (id, address, latitude, longitude, created_at, modified_at) VALUES (:id, :address, :latitude, :longitude, :created_at, :modified_at)"
            ),
            {
                "id": b["id"],
                "address": b["address"],
                "latitude": b["latitude"],
                "longitude": b["longitude"],
                "created_at": now,
                "modified_at": now,
            },
        )

    # Insert organizations with their activities and phones
    # По каждой категории 1-2 организации

    # Для простоты сопоставим здания с организациями:
    # Еда и подкатегории - здание 1
    # Автомобили грузовые - здание 2
    # Легковые и подкатегории - здание 3

    organizations = [
        # Еда
        {
            "name": "Магазин Еда",
            "building_id": buildings[0]["id"],
            "activities": [id_eda],
            "phones": ["8-900-999-00-11"],
        },
        {
            "name": "Мясной магазин Птица",
            "building_id": buildings[0]["id"],
            "activities": [id_ptitsa],
            "phones": ["8-900-111-22-33", "8-900-111-22-34"],
        },
        {
            "name": "Полуфабрикаты и Молочка",
            "building_id": buildings[0]["id"],
            "activities": [id_polufabrikaty, id_molochnaya],
            "phones": ["8-900-222-33-44"],
        },
        # Автомобили грузовые
        {
            "name": "Грузовые Автозапчасти",
            "building_id": buildings[1]["id"],
            "activities": [id_gruzovye],
            "phones": ["8-910-555-66-77"],
        },
        # Легковые
        {
            "name": "Легковые Запчасти",
            "building_id": buildings[2]["id"],
            "activities": [id_zapchasti],
            "phones": ["8-920-333-44-55"],
        },
        {
            "name": "Автомобильные Аксессуары",
            "building_id": buildings[2]["id"],
            "activities": [id_aksessuary],
            "phones": ["8-921-444-55-66", "8-921-444-55-67"],
        },
        {
            "name": "Авторынок",
            "building_id": buildings[1]["id"],
            "activities": [id_avtomobili],
            "phones": ["8-910-999-00-22", "8-910-999-00-23"],
        },
        {
            "name": "Автосалон Лада",
            "building_id": buildings[2]["id"],
            "activities": [id_legkovye],
            "phones": ["8-920-999-00-33"],
        },
    ]

    for org in organizations:
        org_id = uuid.uuid4()
        connection.execute(
            sa.text(
                "INSERT INTO organizations (id, name, building_id, created_at, modified_at) VALUES (:id, :name, :building_id, :created_at, :modified_at)"
            ),
            {
                "id": org_id,
                "name": org["name"],
                "building_id": org["building_id"],
                "created_at": now,
                "modified_at": now,
            },
        )
        # Связи с activities
        for act_id in org["activities"]:
            connection.execute(
                sa.text(
                    "INSERT INTO organization_activities (organization_id, activity_id) VALUES (:organization_id, :activity_id)"
                ),
                {"organization_id": org_id, "activity_id": act_id},
            )
        # Телефоны
        for phone in org["phones"]:
            phone_id = uuid.uuid4()
            connection.execute(
                sa.text(
                    "INSERT INTO organization_phones (id, phone, organization_id, created_at, modified_at) VALUES (:id, :phone, :organization_id, :created_at, :modified_at)"
                ),
                {
                    "id": phone_id,
                    "phone": phone,
                    "organization_id": org_id,
                    "created_at": now,
                    "modified_at": now,
                },
            )


def downgrade():
    connection = op.get_bind()

    # Удаляем телефоны, организации, связи, активности по именам

    # Для удаления по именам нужно сначала получить id активностей и организаций

    # Для упрощения можно удалить все добавленные организации по именам
    org_names = [
        "Мясной магазин Птица",
        "Полуфабрикаты и Молочка",
        "Грузовые Автозапчасти",
        "Легковые Запчасти",
        "Автомобильные Аксессуары",
        "Магазин Еда",
        "Авторынок",
        "Автосалон Лада",
    ]
    for name in org_names:
        # Удаляем телефоны организации
        res = connection.execute(
            sa.text("SELECT id FROM organizations WHERE name = :name"), {"name": name}
        )
        org_ids = [row[0] for row in res]
        for org_id in org_ids:
            connection.execute(
                sa.text(
                    "DELETE FROM organization_phones WHERE organization_id = :org_id"
                ),
                {"org_id": org_id},
            )
            connection.execute(
                sa.text(
                    "DELETE FROM organization_activities WHERE organization_id = :org_id"
                ),
                {"org_id": org_id},
            )
        # Удаляем организации
        connection.execute(
            sa.text("DELETE FROM organizations WHERE name = :name"), {"name": name}
        )

    # Удаляем активности (иерархия) по именам
    activity_names = [
        "Птица",
        "Полуфабрикаты",
        "Молочная продукция",
        "Мясная продукция",
        "Еда",
        "Грузовые",
        "Автомобили",
        "Запчасти",
        "Аксессуары",
        "Легковые",
    ]
    for act_name in activity_names:
        connection.execute(
            sa.text("DELETE FROM activities WHERE name = :name"), {"name": act_name}
        )

    # Удаляем здания по адресам (те, что вставляли)
    addresses = ["ул. Пушкина, д.1", "пр. Ленина, д.10", "ул. Чехова, д.5"]
    for addr in addresses:
        connection.execute(
            sa.text("DELETE FROM buildings WHERE address = :addr"), {"addr": addr}
        )
