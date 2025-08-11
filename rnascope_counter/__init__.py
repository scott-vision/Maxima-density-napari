"""RNAScope spot counting Napari plugin."""

__all__ = ["counter_widget"]


def counter_widget(*args, **kwargs):
    from .widget import counter_widget as _counter_widget
    return _counter_widget(*args, **kwargs)
