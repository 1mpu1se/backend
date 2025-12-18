def test_import_routers():
    from src.routers import admin_router, user_router

    assert admin_router is not None
    assert user_router is not None
