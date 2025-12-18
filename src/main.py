import logging

import uvicorn

import src.config as config

logging.basicConfig(level=config.log_level())

if __name__ == '__main__':
    uvicorn.run('app:app', host='0.0.0.0', port=8080)
