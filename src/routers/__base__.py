from fastapi import HTTPException


def assert_exists(db, cls, uid):
    try:
        o = db.get(cls, uid)
    except Exception:
        raise HTTPException(404)

    if o is None:
        raise HTTPException(404)

    return o
