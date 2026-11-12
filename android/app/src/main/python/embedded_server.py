import os
import threading
import time
import urllib.error
import urllib.request

_server_error = None
_server_thread = None


def _run_server():
    global _server_error
    try:
        import app

        app.app.run(
            host="127.0.0.1",
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True,
        )
    except Exception as error:
        _server_error = error


def start(data_dir, frontend_dir):
    global _server_error, _server_thread
    os.environ["UMBRA_NOX_DATA_DIR"] = data_dir
    os.environ["UMBRA_NOX_FRONTEND_DIR"] = frontend_dir
    if _server_thread is None or not _server_thread.is_alive():
        _server_error = None
        _server_thread = threading.Thread(target=_run_server, daemon=True)
        _server_thread.start()

    for _ in range(100):
        if _server_error is not None:
            raise RuntimeError("Falha ao iniciar o servidor local: %s" % _server_error)
        try:
            with urllib.request.urlopen(
                "http://127.0.0.1:5000/api/enigmas", timeout=1
            ) as response:
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError):
            time.sleep(0.1)

    raise RuntimeError("O servidor local não respondeu. Feche o app e tente novamente.")
