"""
Monkey-patch for Django 5.1.x + Python 3.14 compatibility.

Python 3.14 changed the behavior of super().__copy__() which breaks
Django's Context classes. This patch replaces __copy__ methods with
versions that work on both Python 3.13 and 3.14 by manually constructing
copies avoiding the broken super() chain.
"""
import django.template.context as ctx


def _patched_basecontext_copy(self):
    """
    Manual copy implementation to avoid super().__copy__() on Py3.14.
    Replicates behavior of BaseContext.__copy__.
    """
    duplicate = self.__class__.__new__(self.__class__)
    duplicate.__dict__ = self.__dict__.copy()
    duplicate.dicts = self.dicts[:]
    return duplicate


def _patched_context_copy(self):
    """
    Manual copy for Context.
    Replicates behavior of Context.__copy__.
    """
    duplicate = _patched_basecontext_copy(self)
    return duplicate


def _patched_rendercontext_copy(self):
    """
    Manual copy for RenderContext.
    Replicates behavior of RenderContext.__copy__.
    """
    duplicate = _patched_basecontext_copy(self)
    return duplicate


# Apply patches
ctx.BaseContext.__copy__ = _patched_basecontext_copy
ctx.Context.__copy__ = _patched_context_copy
ctx.RenderContext.__copy__ = _patched_rendercontext_copy
