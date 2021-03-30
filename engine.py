# coding=utf8

import datetime
import locale
import logging
import os
import platform
import shutil
import time
from pathlib import Path
import argparse

start_time = time.time()


def create_logger(filename, log_name='engine'):
    """
    create logger for app
    """

    logger = logging.getLogger(log_name)
    file_handler = logging.FileHandler(filename, 'w')
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger


def init_logger(res_folder):
    logger = create_logger("{0}Converter.log".format(res_folder), log_name='engine')
    logger.info("Information Sfotex Group converter.")
    logger.info('Timestamp: {0}'.format(datetime.datetime.now()))
    logger.info('OS: {0} {1}'.format(platform.system(), platform.release()))
    logger.info('OS Locale: Format {0}'.format(locale.getdefaultlocale()[0]))


def get_list_convert_files(args_dir, ext_files, folder):
    list_convert_files = []
    if os.path.isfile(args_dir):
        list_convert_files = [str(args_dir)]
    else:
        for address, dirs, files in folder:
            for file in files:
                if os.path.isfile(file):
                    ch_path_str = os.path.normpath('/' + address[len(args_dir):] + '/' + file)
                    list_convert_files.append(ch_path_str)
    return list_convert_files


def translator(args_dir=""):
    """
    Method for convert files
    :param args_dir: path to files
    :return: result convertation files to Results folder
    """
    # list_input_fmts = ['.sql']

    ext_files = '.sql'
    res_path = os.path.dirname(args_dir)
    res_folder = res_path + "/Results/"
    if not os.path.exists(res_folder):
        try:
            os.makedirs(res_folder)
        except:
            print('Error for create dir res_folder')

    init_logger(res_folder)
    logger = logging.getLogger('engine')

    # создаем список директорий по папкам
    folder = []
    for i in os.walk(args_dir):
        folder.append(i)

    list_convert_files = []
    list_convert_files = get_list_convert_files(args_dir, ext_files, folder)

    logger.info('list converting files: {0}\n'.format(str(list_convert_files)))
    for n_file, fileConvert in enumerate(list_convert_files):
        print(Path(fileConvert).name)
        shutil.copy(fileConvert, res_folder + Path(fileConvert).name)
    time.sleep(3)


def arg_cmd_lst():
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", "--dir", default="", type=str, help="Path to Directory or file")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    print('start: ')
    cmd_parse_args = arg_cmd_lst()

    if cmd_parse_args.dir != '':
        translator(args_dir=cmd_parse_args.dir)
    else:
        translator(args_dir=r".\test.csv")
    logger = logging.getLogger('engine')
    out_tmstmp = datetime.datetime.now()
    logger.info('Timestamp: {0}'.format(out_tmstmp))
    print(out_tmstmp)
    logger.info('Time convert: {}'.format(round(time.time()-start_time, 4)))

    print(round(time.time()-start_time, 4))

# python engine.py -dir=E:\Work\Python\CheckAny\test.csv
