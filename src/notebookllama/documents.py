from pydantic import BaseModel, model_validator, Field
from sqlalchemy import Engine, create_engine, Connection, Result, text
from typing_extensions import Self
from typing import Optional, Any, List, cast


def apply_string_correction(string: str) -> str:
    return string.replace("''", "'").replace('""', '"')


class ManagedDocument(BaseModel):
    document_name: str
    content: str
    summary: str
    q_and_a: str
    mindmap: str
    bullet_points: str
    is_exported: bool = Field(default=False, exclude=True)

    @model_validator(mode="after")
    def validate_input_for_sql(self) -> Self:
        if not self.is_exported:
            self.document_name = self.document_name.replace("'", "''")
            self.content = self.content.replace("'", "''")
            self.summary = self.summary.replace("'", "''")
            self.q_and_a = self.q_and_a.replace("'", "''")
            self.mindmap = self.mindmap.replace("'", "''")
            self.bullet_points = self.bullet_points.replace("'", "''")
        return self


class DocumentManager:
    def __init__(
        self,
        engine: Optional[Engine] = None,
        engine_url: Optional[str] = None,
        table_name: Optional[str] = None,
    ):
        self.table_name: str = table_name or "documents"
        self.table_exists: bool = False
        self._connection: Optional[Connection] = None
        if engine:
            self._engine: Engine = engine
        elif engine_url:
            self._engine = create_engine(url=engine_url)
        else:
            raise ValueError("One of engine or engine_setup_kwargs must be set")

    @property
    def connection(self) -> Connection:
        if not self._connection:
            self._connect()
        return cast(Connection, self._connection)

    def _connect(self) -> None:
        self._connection = self._engine.connect()

    def _create_table(self) -> None:
        self.connection.execute(
            text(f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            document_name TEXT NOT NULL,
            content TEXT,
            summary TEXT,
            q_and_a TEXT,
            mindmap TEXT,
            bullet_points TEXT
        );
        """)
        )
        self.connection.commit()
        self.table_exists = True

    def put_documents(self, documents: List[ManagedDocument]) -> None:
        if not self.table_exists:
            self._create_table()
        for document in documents:
            self.connection.execute(
                text(
                    f"""
                    INSERT INTO {self.table_name} (document_name, content, summary, q_and_a, mindmap, bullet_points)
                    VALUES (
                        '{document.document_name}',
                        '{document.content}',
                        '{document.summary}',
                        '{document.q_and_a}',
                        '{document.mindmap}',
                        '{document.bullet_points}'
                    );
                    """
                )
            )
        self.connection.commit()

    def get_documents(self, names: Optional[List[str]] = None) -> List[ManagedDocument]:
        if not self.table_exists:
            self._create_table()
        if not names:
            result = self._execute(
                text(
                    f"""
                    SELECT * FROM {self.table_name} ORDER BY id;
                    """
                )
            )
        else:
            result = self._execute(
                text(
                    f"""
                    SELECT * FROM {self.table_name} WHERE document_name = ANY(ARRAY{names}) ORDER BY id;
                    """
                )
            )
        rows = result.fetchall()
        documents = []
        for row in rows:
            document = ManagedDocument(
                document_name=row.document_name,
                content=row.content,
                summary=row.summary,
                q_and_a=row.q_and_a,
                mindmap=row.mindmap,
                bullet_points=row.bullet_points,
                is_exported=True,
            )
            doc_dict = document.model_dump()
            for field in doc_dict:
                doc_dict[field] = apply_string_correction(doc_dict[field])
                if field == "mindmap":
                    doc_dict[field] = doc_dict[field].replace(
                        "''mynetwork''", "'mynetwork'"
                    )
            documents.append(ManagedDocument.model_validate(doc_dict))
        return documents

    def get_names(self) -> List[str]:
        if not self.table_exists:
            self._create_table()
        result = self._execute(
            text(
                f"""
                SELECT * FROM {self.table_name} ORDER BY id;
                """
            )
        )
        rows = result.fetchall()
        return [row.document_name for row in rows]

    def _execute(
        self,
        statement: Any,
        parameters: Optional[Any] = None,
        execution_options: Optional[Any] = None,
    ) -> Result:
        return self.connection.execute(
            statement=statement,
            parameters=parameters,
            execution_options=execution_options,
        )

    def disconnect(self) -> None:
        if not self._connection:
            raise ValueError("Engine was never connected!")
        self._engine.dispose(close=True)
