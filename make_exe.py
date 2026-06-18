# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 11:09:48 2022

@author: Admin
"""

import PyInstaller.__main__

# noinspection PyPackageRequirements
'''
pip install pyinstaller
'''

__author__ = 'Alexey A.Tsukanov'


def main():

    print('Старт сборки...')

    # собрать
    PyInstaller.__main__.run([
        'main.py',
        '--onefile',
        '--windowed',
        '--console',
        '--icon=tsukanov_lab.ico'
    ])

    print('Завершено: dist/main.exe')


if __name__ == '__main__':
    main()
