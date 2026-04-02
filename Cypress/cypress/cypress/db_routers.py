"""
Database routers for Athena.
- LottoRouter: Routes lotto-specific models to the 'lotto' database
- PrimaryReplicaRouter: Routes reads to replica, writes to default
"""

class PrimaryReplicaRouter:
    """
    Routes:
      - Writes → default (leader)
      - Reads → replica, unless explicitly pinned to default
    """

    def db_for_write(self, model, **hints):
        return "default"

    def db_for_read(self, model, **hints):
        # Respect explicit DB pinning
        return hints.get("using", "replica")

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == "default"

