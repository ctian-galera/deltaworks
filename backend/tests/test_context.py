from uuid import uuid4

from app.models.context_edge import ContextRelationshipType
from app.models.context_node import ContextNodeType


def test_context_node_types():
    assert ContextNodeType.ASSET.value == "ASSET"
    assert ContextNodeType.COMPONENT.value == "COMPONENT"


def test_context_relationship_types():
    assert ContextRelationshipType.PART_OF.value == "PART_OF"
    assert ContextRelationshipType.CONTROLS.value == "CONTROLS"
    assert ContextRelationshipType.SENSES.value == "SENSES"


def test_uuid_generation():
    first = uuid4()
    second = uuid4()

    assert first != second