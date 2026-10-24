# -*- coding: utf-8 -*-
"""
QSyntaxHighlighter implementáció kódnézethez (Python, C++, C, Java, Pascal, BASIC)
"""
import re
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression


class CodeHighlighter(QSyntaxHighlighter):
    KEYWORDS = [
        # Python
        "def", "class", "if", "else", "elif", "for", "while", "return", "in", "import", "from",
        "as", "None", "True", "False", "yield", "and", "or", "not", "break", "continue", "pass",
        # C / C++ / Java
        "int", "void", "float", "double", "char", "bool", "boolean", "switch", "case",
        "public", "private", "protected", "static", "new", "null", "true", "false",
        # Pascal
        "function", "procedure", "begin", "end", "then", "to", "do", "var", "array", "of", "integer", "exit", "result",
        # BASIC
        "FUNCTION", "SUB", "FOR", "TO", "NEXT", "IF", "THEN", "ELSE", "WHILE", "WEND", "EXIT", "THEN"
    ]

    def __init__(self, parent=None, theme="light", enabled=True):
        super().__init__(parent)
        self.theme = theme
        self.enabled = enabled
        self._rules = []
        self._init_rules()

    def set_theme(self, theme: str):
        self.theme = theme
        self._init_rules()
        self.rehighlight()

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        self.rehighlight()

    def _init_rules(self):
        self._rules = []
        if self.theme == "dark":
            keyword_color = QColor("#569cd6")
            string_color = QColor("#ce9178")
            comment_color = QColor("#6a9955")
            number_color = QColor("#b5cea8")
        else: # light
            keyword_color = QColor("#0000ff")
            string_color = QColor("#a31515")
            comment_color = QColor("#008000")
            number_color = QColor("#098658")

        # Keywords rule
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(keyword_color)
        keyword_format.setFontWeight(QFont.Bold)
        for word in self.KEYWORDS:
            pattern = QRegularExpression(r"\b" + re.escape(word) + r"\b", QRegularExpression.CaseInsensitiveOption)
            self._rules.append((pattern, keyword_format))

        # Numbers rule
        number_format = QTextCharFormat()
        number_format.setForeground(number_color)
        number_pattern = QRegularExpression(r"\b\d+(\.\d+)?\b")
        self._rules.append((number_pattern, number_format))

        # Strings rule ("..." or '...')
        string_format = QTextCharFormat()
        string_format.setForeground(string_color)
        string_pattern = QRegularExpression(r'".*?"|\'.*?\'')
        self._rules.append((string_pattern, string_format))

        # Comments rule (# or //)
        comment_format = QTextCharFormat()
        comment_format.setForeground(comment_color)
        comment_format.setFontItalic(True)
        comment_pattern = QRegularExpression(r"(#|//).*")
        self._rules.append((comment_pattern, comment_format))

    def highlightBlock(self, text: str):
        if not self.enabled:
            return

        for pattern, fmt in self._rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
