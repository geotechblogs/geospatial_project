"""Root test conftest — prevents database.py from connecting to a real DB at import time.

database.py calls Base.metadata.create_all(bind=engine) at module scope (line 15),
which tries to open a real PostgreSQL connection.  We monkey-patch create_all to a
no-op BEFORE pytest collects the sub-conftest files that trigger the import chain.
"""

import sqlalchemy.sql.schema

# Replace MetaData.create_all with a no-op so that importing database.py
# does not attempt a live database connection.
sqlalchemy.sql.schema.MetaData.create_all = lambda *args, **kwargs: None  # type: ignore[assignment]
