import sys
from sqlalchemy import create_engine, text

def run_query(query_str, force_local=False):
    # Determine which database to connect to
    engine = None
    if force_local:
        engine = create_engine("sqlite:///shakthidb_local.db")
        print("Forced connection to SQLite (Local DB)")
    else:
        try:
            engine = create_engine("postgresql://postgres:ShakthiDB%402026@localhost:15234/postgres", connect_args={"connect_timeout": 2})
            with engine.connect():
                print("Connected to PostgreSQL (Docker)")
        except Exception:
            engine = create_engine("sqlite:///shakthidb_local.db")
            print("Connected to SQLite (Local Fallback)")

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query_str))
            
            # If it's a SELECT query, print the results
            if result.returns_rows:
                rows = result.fetchall()
                if not rows:
                    print("Query returned 0 rows.")
                for row in rows:
                    print(row)
            else:
                conn.commit()
                print("Query executed successfully.")
    except Exception as e:
        print(f"Error executing query: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Check if they want to force local DB
        if sys.argv[1] == "--local":
            query = " ".join(sys.argv[2:])
            if query.strip():
                run_query(query, force_local=True)
            else:
                print("Usage: python run_query.py --local \"YOUR SQL QUERY\"")
        else:
            query = " ".join(sys.argv[1:])
            run_query(query, force_local=False)
    else:
        print("Usage: python run_query.py [\"--local\"] \"YOUR SQL QUERY\"")
        print("Example: python run_query.py \"SELECT * FROM audit_finding\"")
        print("Example (Force Local DB): python run_query.py --local \"SELECT * FROM audit_finding\"")
