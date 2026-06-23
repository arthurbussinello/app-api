"""Registry de queries SQL pré-definidas e seguras."""


class SQLRegistry:
    """Contém queries validadas e aprovadas para execução no banco de dados."""

    # Exemplo de query aprovada — retorna lista de tabelas do sistema.
    GET_TABLES = (
        "SELECT TABLE_NAME, TABLE_TYPE FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME"
    )

    # Retorna colunas de uma tabela específica.
    GET_COLUMNS_BY_TABLE = (
        "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE "
        "FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_NAME = ? ORDER BY ORDINAL_POSITION"
    )

    @classmethod
    def get_query(cls, key: str) -> str | None:
        """Retorna uma query pelo nome da chave."""
        value = getattr(cls, key, None)
        if value is None:
            return None
        return str(value)

    @classmethod
    def list_queries(cls) -> list[str]:
        """Retorna lista de chaves disponíveis."""
        keys = [
            "GET_TABLES",
            "GET_COLUMNS_BY_TABLE",
        ]
        return keys