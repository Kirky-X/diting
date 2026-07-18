#!/usr/bin/env python3
"""
Code Analyzer Module

Provides static analysis capabilities for code review.
"""

import ast
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# Curated nullable-source patterns for null-safety detection.
#
# Design note: a previous version used r'\b\w+\.\w+\s*\(' which matches EVERY method
# call (`obj.method(`) — a near-100% false-positive rate when framed as "potential
# NoneType access". The patterns below narrow detection to chained attribute/method
# access (`.X(...).Y`) on sources that commonly evaluate to None / undefined / null,
# so normal method calls are no longer flagged.
#
# The previous per-line skip `if 'if ' in line or '?' in line or '?.' in line: continue`
# is also gone: it skipped ANY line containing a ternary `?` or an unrelated `if`
# keyword, silently hiding real null-derefs on those lines (false negatives). We now
# only skip a JS/TS line when the dev already used optional chaining (`?.`) on it.
_ARG = r"(?:[^()]|\([^()]*\))*"  # one level of nested parentheses inside argument lists


def _build_null_chain_patterns() -> Dict[str, List[Tuple["re.Pattern", str, str]]]:
    """Build per-language curated nullable-source chained-access patterns."""
    return {
        "python": [
            (
                re.compile(
                    rf"\bre\.(?:match|search|fullmatch)\s*\({_ARG}\)\s*\.\s*\w+"
                ),
                "match",
                "Potential NoneType access — re.match/search/fullmatch() returns None on no match; guard before chaining (.group())",
            ),
            (
                re.compile(rf"\.get\s*\({_ARG}\)\s*\.\s*\w+"),
                "get",
                "Potential NoneType access — dict.get() returns None for missing keys; guard before chaining",
            ),
            (
                re.compile(rf"\.find\s*\({_ARG}\)\s*\.\s*\w+"),
                "find",
                "Potential NoneType access — .find() may return None; guard before chaining",
            ),
        ],
        "java": [
            (
                re.compile(r"\b\w+\.get\s*\([^()]*\)\s*\.\s*\w+"),
                "get",
                "Potential NullPointerException — Map.get() returns null for missing keys",
            ),
        ],
        "javascript": [
            (
                re.compile(rf"\.match\s*\({_ARG}\)\s*\.\s*\w+"),
                "match",
                "Potential null access — String.match() returns null on no match; use optional chaining (?.)",
            ),
            (
                re.compile(rf"\.find\s*\({_ARG}\)\s*\.\s*\w+"),
                "find",
                "Potential undefined access — Array.find() returns undefined if no match; use optional chaining (?.)",
            ),
            (
                re.compile(r"\.getElementById\s*\([^()]*\)\s*\.\s*\w+"),
                "getElementById",
                "Potential null access — getElementById() returns null if element missing; use optional chaining (?.)",
            ),
        ],
        "typescript": [
            (
                re.compile(rf"\.match\s*\({_ARG}\)\s*\.\s*\w+"),
                "match",
                "Potential null access — String.match() returns null on no match; use optional chaining (?.)",
            ),
            (
                re.compile(rf"\.find\s*\({_ARG}\)\s*\.\s*\w+"),
                "find",
                "Potential undefined access — Array.find() returns undefined if no match; use optional chaining (?.)",
            ),
            (
                re.compile(r"\.getElementById\s*\([^()]*\)\s*\.\s*\w+"),
                "getElementById",
                "Potential null access — getElementById() returns null if element missing; use optional chaining (?.)",
            ),
        ],
    }


_NULL_CHAIN_PATTERNS: Dict[str, List[Tuple["re.Pattern", str, str]]] = (
    _build_null_chain_patterns()
)


@dataclass
class AnalysisResult:
    file_path: str
    language: str
    metrics: Dict[str, Any]
    issues: List[Dict[str, Any]]
    structure: Dict[str, Any]


class CodeAnalyzer:
    """Multi-language code analyzer."""

    LANGUAGE_EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
    }

    def __init__(self):
        self.complexity_threshold = 10
        self.method_length_threshold = 50
        self.class_length_threshold = 300
        self.parameter_count_threshold = 4
        self.nesting_threshold = 4

    def analyze(self, file_path: str) -> AnalysisResult:
        """Analyze a single file."""
        language = self._detect_language(file_path)

        # FIX #4: always use errors='replace' so non-UTF-8 bytes
        # don't silently drop content or raise on binary files.
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        lines = content.split("\n")

        metrics = self._calculate_metrics(content, lines, language)
        issues = self._detect_issues(file_path, content, lines, language)
        structure = self._analyze_structure(content, language)

        return AnalysisResult(
            file_path=file_path,
            language=language,
            metrics=metrics,
            issues=issues,
            structure=structure,
        )

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        _, ext = os.path.splitext(file_path)
        return self.LANGUAGE_EXTENSIONS.get(ext.lower(), "unknown")

    def _calculate_metrics(
        self, content: str, lines: List[str], language: str
    ) -> Dict[str, Any]:
        """Calculate code metrics."""
        metrics = {
            "lines_of_code": len([l for l in lines if l.strip()]),
            "total_lines": len(lines),
            "blank_lines": len([l for l in lines if not l.strip()]),
            "comment_lines": self._count_comments(lines, language),
            "cyclomatic_complexity": 0,
            "cognitive_complexity": 0,
            "maintainability_index": 0,
            "halstead_volume": 0,
        }

        if language == "python":
            try:
                tree = ast.parse(content)
                metrics["cyclomatic_complexity"] = (
                    self._calculate_cyclomatic_complexity(tree)
                )
                metrics["function_count"] = sum(
                    1 for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                )
                metrics["class_count"] = sum(
                    1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef)
                )
            except SyntaxError:
                pass

        return metrics

    def _count_comments(self, lines: List[str], language: str) -> int:
        """Count comment lines."""
        count = 0
        in_block_comment = False

        for line in lines:
            stripped = line.strip()

            if language in ["python", "ruby"]:
                if stripped.startswith("#"):
                    count += 1
            elif language in [
                "javascript",
                "typescript",
                "java",
                "c",
                "cpp",
                "csharp",
                "go",
                "rust",
            ]:
                if in_block_comment:
                    count += 1
                    if "*/" in stripped:
                        in_block_comment = False
                elif stripped.startswith("/*"):
                    count += 1
                    if "*/" not in stripped[2:]:
                        in_block_comment = True
                elif stripped.startswith("//"):
                    count += 1
            elif language == "php":
                if stripped.startswith("#") or stripped.startswith("//"):
                    count += 1

        return count

    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity for Python code.

        Decision points counted:
          - if / elif
          - while / for
          - except handler
          - boolean operators in BoolOp (and/or add N-1 branches each)
        """
        complexity = 1  # base path

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                # FIX #1: BoolOp.values has N operands → N-1 extra branches.
                # ast.And and ast.Or are operator *types*, not nodes visited
                # by ast.walk(), so we count here inside the BoolOp node.
                complexity += len(node.values) - 1

        return complexity

    def _detect_issues(
        self,
        file_path: str,
        content: str,
        lines: List[str],
        language: str,
    ) -> List[Dict[str, Any]]:
        """Detect code issues."""
        issues = []
        issues.extend(self._check_long_methods(file_path, lines))
        issues.extend(self._check_deep_nesting(file_path, lines))
        issues.extend(self._check_long_lines(file_path, lines))
        issues.extend(self._check_todo_comments(file_path, lines))
        issues.extend(self._check_magic_numbers(file_path, lines, language))
        issues.extend(self._check_accessibility(file_path, content, lines, language))
        issues.extend(self._check_correctness(file_path, content, lines, language))
        return issues

    def _check_long_methods(
        self, file_path: str, lines: List[str]
    ) -> List[Dict[str, Any]]:
        """Check for long methods / functions."""
        issues = []

        METHOD_RE = re.compile(
            r"^\s*(def |function |public |private |protected |static )"
        )

        # Bug 4 fix: track nested methods with method_stack
        # Each stack element: (start_line, indent, name)
        method_stack: List[tuple] = []

        def _report(start: int, end: int, name: str, outer: Optional[str]) -> None:
            length = end - start
            if length > self.method_length_threshold:
                issues.append(
                    {
                        "file": file_path,
                        "line": start,
                        "end_line": end,
                        "severity": "medium",
                        "category": "quality",
                        "description": f"Long method '{name}' ({length} lines, threshold {self.method_length_threshold})",
                        "recommendation": "Extract smaller methods with single responsibility",
                        "method": name,
                        "outer_method": outer,
                    }
                )

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                continue

            current_indent = len(line) - len(line.lstrip())

            if METHOD_RE.match(line):
                # Bug 4 fix: close all methods with indent >= current_indent (outer method ends)
                while method_stack and current_indent <= method_stack[-1][1]:
                    start, indent, name = method_stack.pop()
                    outer = method_stack[0][2] if method_stack else None
                    _report(start, i - 1, name, outer)

                # Enter new method
                try:
                    method_name = stripped.split("(")[0].split()[-1]
                except IndexError:
                    method_name = stripped[:20]

                method_stack.append((i, current_indent, method_name))

            elif method_stack:
                # Check if exiting current method (indent returns to or below method definition level)
                if (
                    current_indent <= method_stack[-1][1]
                    and stripped
                    and not stripped.startswith("#")
                ):
                    start, indent, name = method_stack.pop()
                    outer = method_stack[0][2] if method_stack else None
                    _report(start, i - 1, name, outer)

        # FIX #2: flush any method still open at end of file
        while method_stack:
            start, indent, name = method_stack.pop()
            outer = method_stack[0][2] if method_stack else None
            _report(start, len(lines), name, outer)

        return issues

    def _check_deep_nesting(
        self, file_path: str, lines: List[str]
    ) -> List[Dict[str, Any]]:
        """Check for deeply nested code."""
        issues = []

        for i, line in enumerate(lines, 1):
            if not line.strip():
                continue

            indent = len(line) - len(line.lstrip())
            nesting_level = indent // 4

            if nesting_level > self.nesting_threshold:
                issues.append(
                    {
                        "file": file_path,
                        "line": i,
                        "end_line": i,
                        "severity": "medium",
                        "category": "quality",
                        "description": f"Deep nesting detected (level {nesting_level}, threshold {self.nesting_threshold})",
                        "recommendation": "Use guard clauses or extract methods to reduce nesting",
                    }
                )

        return issues

    def _check_long_lines(
        self, file_path: str, lines: List[str]
    ) -> List[Dict[str, Any]]:
        """Check for overly long lines."""
        issues = []
        max_line_length = 120

        for i, line in enumerate(lines, 1):
            # Strip trailing newline for accurate length measurement
            length = len(line.rstrip("\n"))
            if length > max_line_length:
                issues.append(
                    {
                        "file": file_path,
                        "line": i,
                        "end_line": i,
                        "severity": "low",
                        "category": "style",
                        "description": f"Line exceeds {max_line_length} characters ({length} chars)",
                        "recommendation": "Break long lines for better readability",
                    }
                )

        return issues

    def _check_todo_comments(
        self, file_path: str, lines: List[str]
    ) -> List[Dict[str, Any]]:
        """Check for TODO/FIXME/HACK comments."""
        issues = []
        todo_pattern = re.compile(r"(#|//)\s*(TODO|FIXME|XXX|HACK)", re.IGNORECASE)

        for i, line in enumerate(lines, 1):
            match = todo_pattern.search(line)
            if match:
                issues.append(
                    {
                        "file": file_path,
                        "line": i,
                        "end_line": i,
                        "severity": "info",
                        "category": "maintenance",
                        "description": f"{match.group(2).upper()} comment found",
                        "recommendation": "Address or create a tracking issue with reference number",
                    }
                )

        return issues

    def _check_magic_numbers(
        self, file_path: str, lines: List[str], language: str
    ) -> List[Dict[str, Any]]:
        """Check for magic numbers (unexplained numeric literals)."""
        issues = []

        # FIX #3: regex already requires \d{2,} (2+ digits), so single-digit
        # exclusions in the set were dead code. Align exclusions to what the
        # regex can actually produce. Common well-understood constants:
        SAFE_NUMBERS = {
            "10",
            "16",
            "24",
            "32",
            "64",
            "100",
            "128",
            "200",
            "255",
            "256",
            "400",
            "404",
            "500",
            "1000",
            "1024",
            "3600",
            "8080",
            "86400",
            "65535",
        }

        magic_pattern = re.compile(r"\b(\d{2,})\b")
        comment_prefix = re.compile(r"^\s*(#|//|/\*|\*)")

        for i, line in enumerate(lines, 1):
            if comment_prefix.match(line):
                continue

            for match in magic_pattern.finditer(line):
                number = match.group(1)
                if number not in SAFE_NUMBERS:
                    issues.append(
                        {
                            "file": file_path,
                            "line": i,
                            "end_line": i,
                            "severity": "info",
                            "category": "quality",
                            "description": f"Magic number {number} — consider a named constant",
                            "recommendation": f"Replace {number} with a descriptive constant",
                        }
                    )

        return issues

    def _check_accessibility(
        self, file_path: str, content: str, lines: List[str], language: str
    ) -> List[Dict[str, Any]]:
        """Check for accessibility issues (frontend code only)."""
        issues = []

        # Only check frontend file types
        frontend_extensions = {".html", ".jsx", ".tsx", ".vue", ".svelte"}
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in frontend_extensions:
            return issues

        # Check for missing alt attributes on images
        img_pattern = re.compile(r"<img(?![^>]*alt=)[^>]*>", re.IGNORECASE)
        for i, line in enumerate(lines, 1):
            for match in img_pattern.finditer(line):
                issues.append(
                    {
                        "file": file_path,
                        "line": i,
                        "end_line": i,
                        "severity": "high",
                        "category": "accessibility",
                        "description": "Image missing alt attribute",
                        "recommendation": "Add descriptive alt text for screen readers",
                    }
                )

        # Check for outline:none without alternative focus style
        # Bug 6 fix: extract CSS {...} block and match on the block as a whole, supporting multi-line outline:none
        # \boutline\s*: word boundary excludes outline-offset and similar prefix properties
        css_block_pattern = re.compile(r"\{([^{}]*)\}", re.DOTALL)
        outline_none_pattern = re.compile(r"\boutline\s*:\s*none")
        for block_match in css_block_pattern.finditer(content):
            block = block_match.group(1)
            outline_match = outline_none_pattern.search(block)
            if outline_match:
                # Calculate line number using absolute position in content (start(1) is block content start)
                absolute_pos = block_match.start(1) + outline_match.start()
                line_number = content.count("\n", 0, absolute_pos) + 1
                issues.append(
                    {
                        "file": file_path,
                        "line": line_number,
                        "end_line": line_number,
                        "severity": "high",
                        "category": "accessibility",
                        "description": "outline:none without visible focus alternative",
                        "recommendation": "Provide alternative focus indicator (box-shadow, border)",
                    }
                )

        # Check for input without label
        input_pattern = re.compile(
            r'<input[^>]*type=["\']?(text|email|password|tel|number|search)["\']?[^>]*>',
            re.IGNORECASE,
        )
        for i, line in enumerate(lines, 1):
            if input_pattern.search(line):
                # Check if line contains aria-label, aria-labelledby, or id for label association
                if not re.search(
                    r"(aria-label|aria-labelledby|id\s*=)", line, re.IGNORECASE
                ):
                    issues.append(
                        {
                            "file": file_path,
                            "line": i,
                            "end_line": i,
                            "severity": "high",
                            "category": "accessibility",
                            "description": "Input may lack accessible label",
                            "recommendation": "Associate label with input (for/id, aria-label, or aria-labelledby)",
                        }
                    )

        return issues

    def _is_in_string_literal(self, code: str, pos: int) -> bool:
        """Check if position pos in code is inside a string literal.

        Bug 7 fix: state machine tracking single/double quoted strings,
        handling escaped quotes (backslash escapes the next char).
        """
        in_string = False
        quote_char: Optional[str] = None
        i = 0
        while i < pos:
            ch = code[i]
            if in_string:
                if ch == "\\":
                    i += 2  # skip escaped char
                    continue
                if ch == quote_char:
                    in_string = False
                    quote_char = None
            else:
                if ch in ('"', "'"):
                    in_string = True
                    quote_char = ch
            i += 1
        return in_string

    def _check_correctness(
        self, file_path: str, content: str, lines: List[str], language: str
    ) -> List[Dict[str, Any]]:
        """Check for correctness issues (null safety, race conditions, edge cases)."""
        issues = []

        # Null-safety: chained access on nullable sources.
        # See _NULL_CHAIN_PATTERNS (module level) for the rationale — the previous
        # r'\b\w+\.\w+\s*\(' matched every method call (~100% false-positive rate),
        # and the `'?' in line` skip hid real issues on ternary lines.
        for rx, method_label, description in _NULL_CHAIN_PATTERNS.get(language, []):
            for i, line in enumerate(lines, 1):
                if line.strip().startswith(("#", "//", "/*", "*")):
                    continue
                if rx.search(line) is None:
                    continue
                # JS/TS: skip only when the dev already guarded this line with
                # optional chaining. Removed the old `'?' in line` / `'if ' in line`
                # whole-line skip, which silently dropped real null-derefs.
                if language in ("javascript", "typescript") and "?." in line:
                    continue
                issues.append(
                    {
                        "file": file_path,
                        "line": i,
                        "end_line": i,
                        "severity": "medium",
                        "category": "correctness",
                        "description": description,
                        "recommendation": (
                            f"Add an explicit None/undefined check or use optional"
                            f" chaining before using the .{method_label}() result"
                        ),
                    }
                )

        # Check for potential race conditions (check-then-act pattern)
        # Bug 2 fix: use re.search's match.start() to calculate true match start line,
        # instead of line-by-line scanning for 'exists()' / '== null' keywords (which could misattribute to comment lines)
        race_patterns = [
            (
                r"if\s+.*\.exists\(\).*:\s*\n\s*.*write",
                "Check-then-act pattern — potential race condition",
            ),
            (
                r"if\s+.*==\s*null.*:\s*\n\s*.*create",
                "Check-then-create pattern — potential race condition",
            ),
        ]

        for pattern, description in race_patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                # Use match.start() to calculate true match start line number
                line_number = content.count("\n", 0, match.start()) + 1
                issues.append(
                    {
                        "file": file_path,
                        "line": line_number,
                        "end_line": line_number,
                        "severity": "high",
                        "category": "correctness",
                        "description": description,
                        "recommendation": "Use atomic operations or locks to prevent race conditions",
                    }
                )

        # Check for division without zero check
        # D-P1-2: narrowed pattern to identifier/identifier form to reduce false positives
        # Bug 7 fix: use _is_in_string_literal state machine to precisely locate if / is inside a string
        # replacing old `if '"' in line or "'" in line: continue` whole-line skip
        div_pattern = re.compile(r"\b[a-zA-Z_]\w*\s*/\s*[a-zA-Z_]\w*\b")
        # Precompute line start offsets for absolute position in content
        line_starts = [0]
        for ln in lines[:-1]:
            line_starts.append(line_starts[-1] + len(ln) + 1)  # +1 for \n
        for i, line in enumerate(lines, 1):
            if line.strip().startswith(("#", "//", "/*", "*")):
                continue
            for match in div_pattern.finditer(line):
                # Find position of / in match, then absolute position in content
                slash_offset_in_match = match.group().index("/")
                slash_pos_in_content = (
                    line_starts[i - 1] + match.start() + slash_offset_in_match
                )
                # Bug 7 fix: only skip matches where / is inside a string, don't skip entire line
                if self._is_in_string_literal(content, slash_pos_in_content):
                    continue
                # Check if there's a zero check nearby (current line or ±2 lines context)
                context = " ".join(lines[max(0, i - 3) : min(len(lines), i + 1)])
                if (
                    "if " not in context
                    and "== 0" not in context
                    and "!= 0" not in context
                ):
                    issues.append(
                        {
                            "file": file_path,
                            "line": i,
                            "end_line": i,
                            "severity": "medium",
                            "category": "correctness",
                            "description": "Division without zero check",
                            "recommendation": "Verify divisor is not zero before division",
                        }
                    )

        return issues

    def _analyze_structure(self, content: str, language: str) -> Dict[str, Any]:
        """Analyze code structure."""
        structure: Dict[str, Any] = {
            "imports": [],
            "classes": [],
            "functions": [],
            "variables": [],
        }

        if language == "python":
            try:
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            structure["imports"].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            structure["imports"].append(f"{module}.{alias.name}")
                    elif isinstance(node, ast.ClassDef):
                        structure["classes"].append(node.name)
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        structure["functions"].append(node.name)
            except SyntaxError:
                pass

        return structure


def analyze_file(file_path: str) -> AnalysisResult:
    """Convenience function to analyze a single file."""
    return CodeAnalyzer().analyze(file_path)


def analyze_directory(directory: str) -> List[AnalysisResult]:
    """Analyze all code files in a directory."""
    analyzer = CodeAnalyzer()
    results = []

    for root, _, files in os.walk(directory):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in CodeAnalyzer.LANGUAGE_EXTENSIONS:
                file_path = os.path.join(root, file)
                results.append(analyzer.analyze(file_path))

    return results


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <file_or_directory>")
        sys.exit(1)

    path = sys.argv[1]

    if os.path.isfile(path):
        result = analyze_file(path)
        print(
            json.dumps(
                {
                    "file_path": result.file_path,
                    "language": result.language,
                    "metrics": result.metrics,
                    "issues": result.issues,
                    "structure": result.structure,
                },
                indent=2,
            )
        )
    elif os.path.isdir(path):
        results = analyze_directory(path)
        print(
            json.dumps(
                [
                    {
                        "file_path": r.file_path,
                        "language": r.language,
                        "metrics": r.metrics,
                        "issues": r.issues,
                        "structure": r.structure,
                    }
                    for r in results
                ],
                indent=2,
            )
        )
    else:
        print(f"Path not found: {path}")
        sys.exit(1)

    # P1: CodeNexus bridge — emit a blast-radius worklist to stderr when an index
    # is present. The agent layer runs the listed `codenexus` CLI commands (the CLI
    # is not invoked from this subprocess). See SKILL.md Step 1.5.
    try:
        import codenexus_helpers

        all_issues = (
            result.issues
            if os.path.isfile(path)
            else [i for r in results for i in r.issues]
        )
        section = codenexus_helpers.section_for_findings(all_issues, start=path)
        if section:
            print("\n" + section, file=sys.stderr)
    except ImportError:
        pass
