from itertools import combinations

import pytest

from game.systems.entity.entities import Entity, CurrencyMixin, InventoryMixin, ResourceMixin, EquipmentMixin, \
    EntityFactory

all_mixins = [CurrencyMixin, InventoryMixin, ResourceMixin, EquipmentMixin]  # All existing mixin classes


def test_factory_trivial():
    """
    Test that EntityFactory can create a bare Entity object.
    """

    entity_json = {
        "class": "Entity",
        "name": "TestEntity",
        "id": 0,
        "features": [],
        "attributes": {}
    }

    e = EntityFactory.get(entity_json)
    assert isinstance(e, Entity)
    assert e.name == "TestEntity"
    assert e.id == 0


test_factory_mixin_cases = [
]

for n in range(len(all_mixins) + 1):
    test_factory_mixin_cases += list(combinations(all_mixins, n))


@pytest.mark.parametrize("mixins", test_factory_mixin_cases)
def test_factory_mixins(mixins: list[type]):
    """
    Test that the EntityFactory can create an arbitrarily complex Entity subclass.
    """

    entity_json = {
        "class": "Entity",
        "name": "TestEntity",
        "id": 0,
        "features": [cls.__name__.__str__() for cls in mixins],
        "attributes": {}
    }

    e = EntityFactory.get(entity_json)
    assert isinstance(e, Entity)
    assert e.name == "TestEntity"
    assert e.id == 0

    for cls in mixins:
        assert isinstance(e, cls)


factory_init_cascade_cases = [
    [['InventoryMixin'], ['inventory'], {}],
    [['InventoryMixin', 'EquipmentMixin'], ['inventory', 'equipment_controller'], {}],
    [['CurrencyMixin', 'EquipmentMixin'], ['coin_purse', 'equipment_controller'], {}]
]


@pytest.mark.parametrize("mixins, checked_attributes, external_attributes", factory_init_cascade_cases)
def test_factory_init_cascade(mixins:list[str], checked_attributes: list[str], external_attributes):
    """
    Create a multi-mixin Entity subclass, then verify that it contains the instance attributes that are defined in that
    subclass's __init__.
    """

    entity_json = {
        "class": "Entity",
        "name": "TestEntity",
        "id": 0,
        "features": mixins,
        "attributes": external_attributes
    }

    e = EntityFactory.get(entity_json)

    for attr in checked_attributes + ['name', 'id']:
        assert hasattr(e, attr)
