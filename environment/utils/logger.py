import logging
import time


def configure_logger(write_on_file: bool = False) -> None:
    fmt = '[%(levelname)s - %(message)s]'
    if write_on_file:
        logging.basicConfig(filename='app.log', filemode='w', format=fmt, level=logging.INFO)
    else:
        logging.basicConfig(format=fmt, level=logging.INFO)


def call_with_measure_time(function, *args, **kwargs) -> float:
    start = time.perf_counter()
    function(*args, **kwargs)
    end = time.perf_counter()
    logging.info(f'time taken {end - start}')
    return end - start
