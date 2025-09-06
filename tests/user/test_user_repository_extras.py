from unittest.mock import Mock
from src.models.user import User
from src.repositories.user_repository import UserRepository


def test_user_repository_save_adds_and_returns_id():
    mock_firestore = Mock()
    mock_collection = mock_firestore.collection.return_value
    mock_added_ref = Mock()
    mock_added_ref.id = "new-user-id"
    mock_collection.add.return_value = mock_added_ref

    repo = UserRepository(mock_firestore)
    user = User(name="홍길동", deposit=123)

    new_id = repo.save(user)

    mock_firestore.collection.assert_called_with("users")
    mock_collection.add.assert_called_once_with(user.to_dict())
    assert new_id == "new-user-id"


def test_user_repository_get_by_id_returns_none_when_missing():
    mock_firestore = Mock()
    mock_doc_ref = Mock()
    mock_doc = Mock()
    mock_doc.exists = False
    mock_doc_ref.get.return_value = mock_doc
    mock_firestore.collection.return_value.document.return_value = mock_doc_ref

    repo = UserRepository(mock_firestore)

    assert repo.get_by_id("missing") is None

