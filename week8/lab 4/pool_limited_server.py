import argparse
import sys
from pathlib import Path

STARTER = Path(__file__).resolve().parent.parent / "resources"
sys.path.insert(0, str(STARTER))

from app import create_app  

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5001)
    parser.add_argument("--pool-size", type=int, default=5)
    args = parser.parse_args()

    db_file = STARTER / "instance" / "books_pool.db"
    db_file.parent.mkdir(exist_ok=True)
    app = create_app({
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_file}",
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "pool_size": args.pool_size,
            "max_overflow": 0,
            "pool_timeout": 2,
        },
    })
    app.run(host="127.0.0.1", port=args.port, debug=False, threaded=True)
