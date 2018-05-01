import tokenize
import inspect
import token
import sys
import re
import io
import os

_NAME_MATCHING_REGEX = re.compile(r'\bdprint\b')


def dprint(value):
    """A simple printing debugging helper.

    Designed to be used on any expression, to print the value of an expression,
    without modifying the result of the same.

    In most cases, the only visible effect of this function is a call to
    __str__ of the passed value and a call to the builtin print function.
    """

    frame_info = inspect.stack()[1]
    message = _construct_message(value, frame_info)

    # The parts that matter.
    print(message)
    return value


def _construct_message(value, frame_info):
    """Construct a human readable message for context.
    """

    # Parts
    filename_str = _format_filename(frame_info.filename)
    line_str = _format_lineno(frame_info.lineno)
    function_str = _format_function(frame_info.function)
    expression_str = _format_expression(frame_info.code_context)
    val_str = _format_value(value)

    # Put an arrow on it.
    context = filename_str + line_str + function_str
    if context:
        context += "\n"

    # Show the expression with the output.
    if expression_str:
        main_text = "  {} -> {}".format(expression_str, val_str)
    else:
        main_text = "  -> {}" + val_str

    return context + main_text


def _format_filename(filename):
    """Format the filename in a nicer manner than given.

    Try to make the filename shorter when it makes sense to, without losing the
    clarity of what it means.
    """
    if filename is None:
        return "<unknown-file>"

    # A tiny helper
    def in_dir(dirpath, abspath):
        return dirpath == os.path.commonpath([dirpath, abspath])

    abspath = os.path.abspath(filename)
    cwd = os.getcwd()

    # If it's in the current directory, return the path, with current directory
    # removed.
    if in_dir(cwd, abspath):
        return abspath[len(cwd) + 1:]

    # If it's importable, we show the path to it.
    for location in sys.path:
        if in_dir(location, abspath):
            fpath = abspath[len(location) + 1:]
            if fpath.endswith(".py"):
                fpath = fpath[:-3]
            return "<installed> " + fpath.replace(os.path.sep, ".")

    return abspath


def _format_lineno(lineno):
    """Just convert the line number into a better form.
    """
    if lineno is None:
        return ""
    return ":" + str(lineno)


def _format_function(func_name):
    """Provide better context for a "function" of the caller.
    """
    if func_name is None:
        return ""
    elif func_name == "<module>":
        return " (top level stmt)"
    else:
        return " in " + func_name


def _format_expression(code_context):
    """Provide the expression used to call dprint.

    Constraints:
    - Function must be called dprint
    - A call should span no more than 1 line
    - No more than 1 call on 1 line

    If these constraints are violated, the current implementation doesn't
    manage to extract the expression.
    """
    if not code_context:
        return ""

    line = code_context[0]

    # Tokenize the line
    token_list = tokenize.tokenize(io.BytesIO(line.encode('utf-8')).readline)

    # Determine the start and end of expression
    start = None
    end = None
    level = 0  # because nesting
    for tok in token_list:
        # Looking for the start of string.
        if start is None:
            if tok.type == token.NAME and tok.string == "dprint":
                start = tok.start[1]  # we get the proper value later.
            continue
        if end is None:
            if tok.type != token.OP:
                continue

            if tok.string == "(":
                if level == 0:  # opening parens
                    start = tok.end[1]
                level += 1
            elif tok.string == ")":
                level -= 1
                if level == 0:  # closing parens
                    end = tok.start[1]
                    # This is fine since we don't need more information
                    break

    return line[start:end]


def _format_value(value):
    """Convert to a string or be very visibly wrong.
    """
    try:
        val_str = repr(value)
    except Exception:
        val_str = "<could not convert to string>"

    return val_str
