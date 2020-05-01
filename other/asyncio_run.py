import sys
import asyncio

def run_sync(main, debug=False):  # pragma: no cover
    """Run a coroutine.
    For compatibility with python3.6
    """

    if sys.version_info >= (3, 7):
        return asyncio.run(main, debug=debug)

    # Emulate asyncio.run() on older versions
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(main)
    finally:
        loop.close()
        asyncio.set_event_loop(None)
