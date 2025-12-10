import logging

_formatter = logging.Formatter('%(asctime)s\t%(message)s')

_admin_logger = logging.getLogger('admin')
_admin_logger_handler = logging.FileHandler('./logs/admin.log')
_admin_logger_handler.setFormatter(_formatter)
_admin_logger.addHandler(_admin_logger_handler)

_user_logger = logging.getLogger('user')
_user_logger_handler = logging.FileHandler('./logs/user.log')
_user_logger_handler.setFormatter(_formatter)
_user_logger.addHandler(_user_logger_handler)


def log_admin_action(user_id: int, action: str, data: dict = None):
    s = f'user_id={user_id}\taction={action}'
    if data is not None:
        for k, v in data.items():
            s += f'\t{k}={v}'
    _admin_logger.info(s)


def log_user_action(user_id: int, action: str, data: dict = None):
    s = f'user_id={user_id}\taction={action}'
    if data is not None:
        for k, v in data.items():
            s += f'\t{k}={v}'
    _user_logger.info(s)
