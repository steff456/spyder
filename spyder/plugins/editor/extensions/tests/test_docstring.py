# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#
"""Tests for close quotes."""
# Third party imports
import pytest
from qtpy.QtCore import Qt
from qtpy.QtGui import QTextCursor

# Local imports
from spyder.config.main import CONF
from spyder.utils.qthelpers import qapplication
from spyder.plugins.editor.widgets.codeeditor import CodeEditor
from spyder.plugins.editor.extensions.docstring import (FunctionInfo,
                                                        DocstringExtension)


# =============================================================================
# ---- Fixtures
# =============================================================================
@pytest.fixture
def editor_auto_docstring():
    """Set up Editor with auto docstring activated."""
    app = qapplication()
    editor = CodeEditor(parent=None)
    kwargs = {}
    kwargs['language'] = 'Python'
    kwargs['auto_docstring'] = True
    editor.setup_editor(**kwargs)
    return editor


# =============================================================================
# ---- Tests
# =============================================================================
@pytest.mark.parametrize(
    "text, n_indent, name_list, type_list, value_list, rtype",
    [
        ('def foo():', 0, [], [], [], None),
        (""" def foo(arg0, arg1=':', arg2: str='-> (float, str):') -> \
             (float, int): """,
         1, ['arg0', 'arg1', 'arg2'], [None, None, 'str'],
         [None, "':'", "'-> (float, str):'"],
         '(float, int)')
    ])
def test_information_of_function(text, n_indent, name_list, type_list,
                                 value_list, rtype):
    """Test FunctionInfo."""
    func_info = FunctionInfo()
    func_info.parse(text)

    assert func_info.n_indent == n_indent
    assert func_info.arg_name_list == name_list
    assert func_info.arg_type_list == type_list
    assert func_info.arg_value_list == value_list
    assert func_info.return_type == rtype


@pytest.mark.parametrize(
    "doc_type, text, expected",
    [
        ('one-line',
         '''def foo():
    print(''',
         '''def foo():
    print("""
          '''
         ),
        ('one-line',
         '''async def foo():
    ''',
         '''async def foo():
    """"""'''
         ),
        ('numpy',
         '''  def foo():
      ''',
         '''  def foo():
      """

      Returns
      -------
      None

      """''',
         ),

        ('numpy',
         '''def foo(arg1: int, arg2: List[Tuple[str, float]],
arg3='-> (float, int):', arg4=':float, int[', arg5: str='""') -> \
  (List[Tuple[str, float]], str, float):
    ''',
         '''def foo(arg1: int, arg2: List[Tuple[str, float]],
arg3='-> (float, int):', arg4=':float, int[', arg5: str='""') -> \
  (List[Tuple[str, float]], str, float):
    """

    Parameters
    ----------
    arg1 : int
        [description]
    arg2 : List[Tuple[str, float]]
        [description]
    arg3 : [type], optional
        [description] (the default is '-> (float, int):')
    arg4 : [type], optional
        [description] (the default is ':float, int[')
    arg5 : str, optional
        [description] (the default is '""')

    Returns
    -------
    (List[Tuple[str, float]], str, float)
        [description]

    """'''),
    ])
def test_editor_docstring(qtbot, editor_auto_docstring, doc_type, text,
                          expected):
    """Test auto docstring."""
    CONF.set('editor', 'docstring_type', doc_type)
    editor = editor_auto_docstring
    editor.set_text(text)

    cursor = editor.textCursor()
    cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(text))
    cursor.clearSelection()
    editor.setTextCursor(cursor)

    qtbot.keyClicks(editor, '"""')
    qtbot.keyClick(editor, Qt.Key_Enter)

    assert editor.toPlainText() == expected


@pytest.mark.parametrize(
    "enable, text, expected",
    [
        (True,
         '''def foo():
    ''',
         '''def foo():
    """"""'''
         ),
        (False,
         '''def foo():
    ''',
         '''def foo():
    """
    '''
         )
    ])
def test_activate_deactivate(qtbot, editor_auto_docstring, enable, text,
                             expected):
    """Test activating/deactivating docstring editor extension."""
    CONF.set('editor', 'docstring_type', 'one-line')
    editor = editor_auto_docstring
    editor.set_text(text)

    cursor = editor.textCursor()
    cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(text))
    cursor.clearSelection()
    editor.setTextCursor(cursor)

    docstring_extension = editor.editor_extensions.get(DocstringExtension)
    docstring_extension.enabled = enable

    qtbot.keyClicks(editor, '"""')
    qtbot.keyClick(editor, Qt.Key_Return)
    assert editor.toPlainText() == expected

# =============================================================================
# ---- Example for manual Testing of numpy docstring
# =============================================================================
# def foo():
#     """
#
#     Returns
#     -------
#     None
#
#     """
#     pass
#
#
# def foo1(arg1):
#     """
#
#     Parameters
#     ----------
#     arg1 : [type]
#         [description]
#
#     Returns
#     -------
#     None
#
#     """
#     pass
#
#
# def foo2(arg1, arg2) -> (float, str):
#     """
#
#     Parameters
#     ----------
#     arg1 : [type]
#         [description]
#      arg2 : [type]
#         [description]
#
#     Returns
#     -------
#     (float, str)
#         [description]
#
#     """
#     pass
#
# def foo3(arg1: int, arg2: List[Tuple[str, float]], arg3='-> (float, int):',
#           arg4=':float, int[',  arg5: str='"\'"', arg6: str="""string1
#           string2""") -> \
#           (List[Tuple[str, float]], str, float):
#     """
#
#     Parameters
#     ----------
#     arg1 : int
#         [description]
#     arg2 : List[Tuple[str, float]]
#         [description]
#     arg3 : [type], optional
#         [description] (the default is '-> (float, int):')
#     arg4 : [type], optional
#         [description] (the default is ':float, int[')
#     arg5 : str, optional
#         [description] (the default is '"\'"')
#     arg6 : str, optional
#         [description] (the default is '''string1          string2''')
#
#     Returns
#     -------
#     (List[Tuple[str, float]], str, float)
#         [description]
#
#     """
#     pass
