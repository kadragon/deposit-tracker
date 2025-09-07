from unittest.mock import Mock
from src.models.store import Store
from src.repositories.store_repository import StoreRepository


def test_store_repository_save_adds_and_returns_id():
    mock_firestore = Mock()
    mock_collection = mock_firestore.collection.return_value
    mock_added_ref = Mock()
    mock_added_ref.id = "new-store-id"
    # Firestore add returns (DocumentReference, WriteResult)
    mock_collection.add.return_value = (mock_added_ref, Mock())

    repo = StoreRepository(mock_firestore)
    store = Store(name="편의점A")

    new_id = repo.save(store)

    mock_firestore.collection.assert_called_with("stores")
    mock_collection.add.assert_called_once_with(store.to_dict())
    assert new_id == "new-store-id"


def test_store_repository_find_by_name_returns_none_when_missing():
    mock_firestore = Mock()
    mock_firestore.collection.return_value.where.return_value.limit.return_value.stream.return_value = []

    repo = StoreRepository(mock_firestore)

    result = repo.find_by_name("없는가게")
    assert result is None
