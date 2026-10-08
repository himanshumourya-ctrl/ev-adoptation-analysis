import os

import streamlit.components.v1 as components

_RELEASE = True

if not _RELEASE:
    _component = components.declare_component(
        "geo_locator",
        url="http://localhost:3001",
    )
else:
    component_dir = os.path.dirname(os.path.abspath(__file__))
    _component = components.declare_component("geo_locator", path=component_dir)


def geo_locator(label: str = "Use my current location", key: str | None = None):
    return _component(label=label, key=key)
