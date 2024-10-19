# This file is used to configure the uvicorn server
# https://www.uvicorn.org/settings/
# from uvicorn import Config


host = "{{HOST}}"
port = {{PORT}}

# Using Unix Domain Socket, will disable host and port config.
# uds = "lexin.sock"

reload = False
log_level = "info"
workers = 1
log_config = "{{LOG_CONFIG}}"
