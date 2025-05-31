import asyncio.events as aioevents
import ctypes
import sys
from contextvars import Context, ContextVar, copy_context

import fastapi

libc = ctypes.CDLL(None)
syscall = libc.syscall
null_file = open("/dev/null", "wb", buffering=0)


class ConnId:
    total = 0
    last = 0
    current: ContextVar[int] = ContextVar("unit_id", default=None)

    @classmethod
    def new(cls) -> int:
        cls.total += 1
        return cls.total


class RecordMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        req_id = ConnId.new()
        ConnId.current.set(req_id)
        try:
            null_file.write(
                f"python request_start {req_id}".encode("utf-8"),
            )
            await self.app(scope, receive, send)
        except:
            raise
        finally:
            try:
                null_file.write(f"python request_end {req_id}".encode("utf-8"))
            except:
                raise


class HookedFastAPI(fastapi.FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_middleware(RecordMiddleware)


fastapi.FastAPI = HookedFastAPI


class HookedHandle(aioevents.Handle):
    def _run(self):
        conn_id = self._context.get(ConnId.current)

        if conn_id is None:
            conn_id = 0

        null_file.write(f"python conn_start {conn_id}".encode("utf-8"))

        super()._run()

        # syscall(667, conn_id)
        null_file.write(f"python conn_end {conn_id}".encode("utf-8"))


class HookedTimerHandle(aioevents.TimerHandle, HookedHandle):
    pass


# monkey patch
aioevents.Handle = HookedHandle
aioevents.TimerHandle = HookedTimerHandle

# monkey patch 之后才能继续导入，否则无法覆盖
import errno
from asyncio import constants, trsock
from asyncio.events import get_event_loop_policy, set_event_loop_policy
from asyncio.log import logger

BasePolicy = get_event_loop_policy().__class__
BaseLoop = getattr(get_event_loop_policy(), "_loop_factory")


class HookedLoop(BaseLoop):
    def _accept_connection(
        self,
        protocol_factory,
        sock,
        sslcontext=None,
        server=None,
        backlog=100,
        ssl_handshake_timeout=constants.SSL_HANDSHAKE_TIMEOUT,
        ssl_shutdown_timeout=constants.SSL_SHUTDOWN_TIMEOUT,
    ):
        # This method is only called once for each event loop tick where the
        # listening socket has triggered an EVENT_READ. There may be multiple
        # connections waiting for an .accept() so it is called in a loop.
        # See https://bugs.python.org/issue27906 for more details.
        for _ in range(backlog):
            try:
                conn, addr = sock.accept()

                # * hooks

                conn_id = ConnId.new()
                null_file.write(f"python conn_init {conn_id}".encode("utf-8"))

                # ************

                if self._debug:
                    logger.debug(
                        "%r got a new connection from %r: %r", server, addr, conn
                    )
                conn.setblocking(False)
            except (BlockingIOError, InterruptedError, ConnectionAbortedError):
                # Early exit because the socket accept buffer is empty.
                return None
            except OSError as exc:
                # There's nowhere to send the error, so just log it.
                if exc.errno in (
                    errno.EMFILE,
                    errno.ENFILE,
                    errno.ENOBUFS,
                    errno.ENOMEM,
                ):
                    # Some platforms (e.g. Linux keep reporting the FD as
                    # ready, so we remove the read handler temporarily.
                    # We'll try again in a while.
                    self.call_exception_handler(
                        {
                            "message": "socket.accept() out of system resource",
                            "exception": exc,
                            "socket": trsock.TransportSocket(sock),
                        }
                    )
                    self._remove_reader(sock.fileno())
                    self.call_later(
                        constants.ACCEPT_RETRY_DELAY,
                        self._start_serving,
                        protocol_factory,
                        sock,
                        sslcontext,
                        server,
                        backlog,
                        ssl_handshake_timeout,
                        ssl_shutdown_timeout,
                    )
                else:
                    raise  # The event loop will catch, log and ignore it.
            else:
                extra = {"peername": addr}
                accept = self._accept_connection2(
                    protocol_factory,
                    conn,
                    extra,
                    sslcontext,
                    server,
                    ssl_handshake_timeout,
                    ssl_shutdown_timeout,
                )

                # * hooks
                context = copy_context()
                context.run(lambda: ConnId.current.set(conn_id))
                self.create_task(accept, context=context)
                # ************


class HookedPolicy(BasePolicy):
    _loop_factory = HookedLoop


set_event_loop_policy(HookedPolicy())
