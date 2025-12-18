import os
import logging

LOGS_DIR = os.path.join(os.getcwd(), 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

from src.logger import log_admin_action, log_user_action

def test_log_admin_action_content(caplog):
    """Проверяем содержимое лога админа"""
    user_id = 99
    action = "delete_user"
    extra_data = {"target_id": 105}

    with caplog.at_level(logging.INFO, logger='admin'):
        log_admin_action(user_id, action, extra_data)

    assert f"user_id={user_id}" in caplog.text
    assert f"action={action}" in caplog.text
    assert "target_id=105" in caplog.text

def test_log_user_action_no_data(caplog):
    """Проверяем лог пользователя без data"""
    user_id = 1
    action = "login"

    with caplog.at_level(logging.INFO, logger='user'):
        log_user_action(user_id, action)

    expected_msg = f"user_id={user_id}\taction={action}"
    assert expected_msg in caplog.text

def test_loggers_are_distinct(caplog):
    """Проверяем, что логи не перемешиваются"""
    with caplog.at_level(logging.INFO, logger='user'):
        log_admin_action(7, "admin_only")
        # В логгере user не должно быть админских записей
        assert "admin_only" not in caplog.text