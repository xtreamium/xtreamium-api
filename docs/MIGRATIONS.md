# Database Migrations

This project uses Alembic for database migrations to manage database schema changes in a controlled and versioned manner.

## Migration Commands

### Using the Migration Script

The project includes a convenient CLI script for managing migrations:

```bash
# Show current migration status
python scripts/migrate.py current

# Show migration history
python scripts/migrate.py history

# Create a new migration (auto-generates based on model changes)
python scripts/migrate.py create "Description of changes"

# Create a manual migration (empty template)
python scripts/migrate.py create "Manual migration" --no-autogenerate

# Upgrade database to latest version
python scripts/migrate.py upgrade

# Upgrade to specific revision
python scripts/migrate.py upgrade --revision abc123

# Downgrade to specific revision
python scripts/migrate.py downgrade abc123
```

### Using Alembic Directly

You can also use Alembic commands directly:

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Create new migration
alembic revision --autogenerate -m "Migration message"

# Upgrade to head
alembic upgrade head

# Downgrade to previous revision
alembic downgrade -1
```

## Automatic Migrations on Startup

The application automatically runs pending migrations when it starts up. This ensures that the database schema is always up-to-date when the application launches.

## Creating New Migrations

When you make changes to your SQLAlchemy models:

1. Create a new migration:
   ```bash
   python scripts/migrate.py create "Add new column to users table"
   ```

2. Review the generated migration file in `migrations/versions/`

3. Test the migration:
   ```bash
   python scripts/migrate.py upgrade
   ```

4. Commit both your model changes and the migration file to version control

## Migration Best Practices

- Always review auto-generated migrations before applying them
- Test migrations on a copy of production data before deploying
- Create meaningful migration messages that describe the changes
- Never edit applied migrations - create new ones for corrections
- Back up your database before running migrations in production
