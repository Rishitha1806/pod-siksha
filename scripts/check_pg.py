for pkg in ["psycopg2", "psycopg", "asyncpg", "sqlalchemy"]:
    try:
        __import__(pkg)
        print(f"{pkg}: available")
    except ImportError:
        print(f"{pkg}: not installed")
