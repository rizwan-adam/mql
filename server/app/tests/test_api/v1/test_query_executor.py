from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.crud.crud_user_database import crud_user_database
from app.schemas.user_database import UserDatabase as UserDatabaseSchema
from app.utilities.fernet_manager import FernetManager
import logging

logger = logging.getLogger("mql")

def test_query_executor(
    client: TestClient, db: Session, valid_jwt: str, valid_user_model: UserModel
) -> None:
    headers = {"Authorization": f"Bearer {valid_jwt}"}
    fernet_manager = FernetManager(valid_user_model.hashed_key)
    connection_string = fernet_manager.encrypt("postgresql://shuru:password@localhost:5432/mql_test")
    database = crud_user_database.create(
        db=db,
        user_database_obj=UserDatabaseSchema(
            name="Test",
            user_id=valid_user_model.id,
            connection_string=connection_string
        ),
    )
    db.commit()

    response = client.get(
        f"api/v1/sql-data?db_id={database.id}&sql_query=SELECT name, email FROM users limit 1;",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Query executed successfully",
        "data": {
            "query_result": {
                "column_names": ["name", "email"],
                "rows": [
                    ["test", "test@test.com"],
                ]
            },
            "sql_query": "SELECT name, email FROM users limit 1;"
        }
    }

