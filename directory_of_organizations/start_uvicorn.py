from uvicorn import Config, Server
from uvicorn.supervisors import ChangeReload


def main(host="127.0.0.1", port=8000, log_level="info", reload=True):
    config = Config(
        "app.main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=reload,
    )
    server = Server(config)

    if reload:
        sock = config.bind_socket()
        ChangeReload(config, target=server.run, sockets=[sock]).run()
    else:
        server.run()


if __name__ == "__main__":
    main()