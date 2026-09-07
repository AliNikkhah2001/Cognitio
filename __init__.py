"""Submodule import surface used by IMPERIUM.

Installed consumers should import :mod:`cognitio`. IMPERIUM checks this
repository out at ``modules/cognitio`` and imports ``modules.cognitio``.
"""

from .cognitio import KnowledgeService, __version__

__all__ = ["KnowledgeService", "__version__"]
