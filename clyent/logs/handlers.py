from __future__ import absolute_import, print_function, unicode_literals

from functools import partial
import json
from inspect import getargspec
import logging
import sys
import traceback

from clyent import colors, errors


COLOR_MAP = {logging.ERROR: 'red',
             logging.WARN: 'yello',
             logging.DEBUG: 'blue'}

class ColorStreamHandler(logging.Handler):

    def __init__(self, level=logging.INFO, show_tb='tty', exceptions=(errors.ClyentError,)):
        self.show_tb = show_tb
        self.exceptions = exceptions

        logging.Handler.__init__(self, level=level)


    def emit(self, record):

        if not self.filter(record):
            return

        msg = self.format(record)

        if record.levelno <= logging.INFO:
            stream = sys.stdout
        else:
            stream = sys.stderr

        color = colors.Color(COLOR_MAP.get(record.levelno), file=stream)

        is_hidable = record.exc_info and isinstance(record.exc_info[1], self.exceptions)
        should_hide = True if self.show_tb == 'never' else False if self.show_tb == 'always' else stream.isatty()

        if is_hidable and should_hide:
            err = record.exc_info[1]
            msg = str(err)
            with color:
                print('[%s] ' % type(err).__name__, file=stream, end='')

            print(msg, file=stream)


        else:
            header = record.levelname if record.levelname != 'INFO' else ''
            if header.strip():
                with color:
                    print('[%s] ' % header, file=stream, end='')

            print(msg, file=stream)


class JsonStreamHandler(logging.Handler):

    exceptions = (errors.ClyentError,)
    def emit(self, record):
        message = record.msg.format(*record.args)
        message_dict = { 'message': message,
                         'args': list(record.args),
                        }
        message_dict['metadata'] =  getattr(record, 'metadata', {})
        if record.exc_info and isinstance(record.exc_info[1], self.exceptions):
            message_dict['traceback'] = traceback.format_exc()
        json_message = json.dumps(message_dict)
        sys.stdout.write(json_message + '\n')


class JsonFormatter(logging.Formatter):
    def format(self, record):
        if getattr(record, 'exc_info', False):
            return self.formatException(record.exc_info)
        return json.dumps({
                            'message': record.msg.format(*record.args),
                            'metadata': getattr(record, 'metadata', {}),
                            'args': list(record.args),
                         #   'record': repr(record.__dict__),
                        })
    def formatException(self, exc_info):
        """
        Format an exception so that it prints on a single line.
        """
        result = super(JsonFormatter, self).formatException(exc_info)
        return json.dumps({'error': repr(result),})



def main():

    colors.initialize_colors()
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    h = ColorStreamHandler(logging.DEBUG, show_tb=False)
    logger.addHandler(h)

    logger.debug("DEBUG")
    logger.info("INFO")
    logger.warn("WARN")
    logger.error("ERROR")

#     FormatterWrapper.wrap(h, prefix=color('prefix |', [color.WHITE, color.BACKGROUND_COLORS[0]]))
    try:
        asdf
    except:
        logger.exception("Show this tb")

    try:
        raise errors.ClyentError("This will be a short message")
    except:
        logger.exception("This wil not be displayed")



if __name__ == '__main__':
    main()
