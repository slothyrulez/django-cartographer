#! -*- coding: utf-8 -*-

from .parsers import rediscover
from .registry import get_registry

_INOFITFY = False
try:
    import pyinotify
    _INOTIFY = True
except ImportError as e:
    raise e


def updatable_sources_watcher():
    "Handles assets bundle refreshing on updatable bundles"
    registry = get_registry()

    class EventHandler(pyinotify.ProcessEvent):
        def process_default(self, event):
            """
            Eventually, this method is called for all others types of events.
            This method can be useful when an action fits all events.
            """
            print("EVENT: ", event)
            # RELOAD ASSETS
            rediscover()

    # Watch manager
    wm = pyinotify.WatchManager()
    # mask = pyinotify.ALL_EVENTS
    # TODO: Explore better mask options
    mask = (
        pyinotify.IN_MODIFY
        # pyinotify.IN_DELETE
    )
    notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
    # Start the notifier from a new thread,
    # without doing anything as no directory or file are currently monitored yet.
    notifier.daemon = True
    notifier.start()
    iter_updatables = registry.get_updatable_sources()
    for source in iter_updatables:
        wm.add_watch(source, mask, rec=True)
