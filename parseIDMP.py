#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 14:13:14 2020

@author: Carl
"""

import os
import sys
import glob

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

import time


def read_IDMP(fpath,**kwargs):
    '''
    This function will read an IDMP and return the DIDs that are expected to be
    obtained for the event.  There is no known way to obtain which TC these belong
    to, however, that will be addressed manually be some user.

    Input:
        fpath - The absolute file path to the IDMP pdf

    Kwargs:
        get_all - True: Returns all the DIDs
                  False:  Returns the DIDs that follow our criteria - no "pre" no "ee"
                  TODO-UPDATE THESE BECAUSE I CANNOT RECALL ALL OF THEM
    Returns:
        Returns a list of DIDs expected for the event
    '''

    get_all = kwargs.get('get_all',True)
    lines = []
    DIDs = []
    ladd = lines.append
    if os.path.isfile(fpath) and os.path.splitext(fpath)[-1] == '.pdf' and 'IDMP' in fpath:
        file_content = open(fpath,'rb')

        parser = PDFParser(file_content)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)
        doc.initialize('')
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        #I changed the following 2 parameters to get rid of white spaces inside words:
        laparams.char_margin = 1.0
        laparams.word_margin = 1.0
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        first_data_items = 0
        last_data_items = 0
        # Process each page contained in the document.
        for page in doc.get_pages():
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    newlines = lt_obj.get_text().splitlines()
                    for i,l in enumerate(newlines):
                        if l.lower().startswith('(u) index of data items') and first_data_items == 0:
                            first_data_items = i + len(lines) -1
                        if l.lower().startswith('1.0 (u) introduction') and first_data_items\
                            and len(lines) - 1 + i > first_data_items:
                            last_data_items = i + len(lines) - 1
                        ladd(l)
            if first_data_items and last_data_items:
                break
        if first_data_items and last_data_items:
            RELEVANT_TEXT = lines[first_data_items:last_data_items]

            DIDs = list(map(lambda x:x.split(' ')[0],RELEVANT_TEXT))
            if get_all:
                DIDs = [d for d in DIDs if '-' in d and 'gti' not in d.lower()]
            else:
                DIDs = [d for d in DIDs if '-' in d and 'gti' not in d.lower() and
                        not '-pre-' in d.lower() and not d.lower().startswith('ee')]
        else:
            print('Could not find the relevant information needed to parse..  Returning []')
        file_content.close()
    else:
        print(''''The IDMP path given failed one or more of the following:\n
              1: not a valid file\n
              2: not a pdf\n
              3: the file does not contain the string 'IDMP'. ''')

    return DIDs


if __name__ == '__main__':
    # fpath = '/home/klinetry/Desktop/GTI-07b_EC_Draft_2_IDMP.pdf'
    start = time.time()
    z = {}
    for path in map(os.path.realpath,sys.argv[1:]):
        if os.path.isdir(path):
            for infile in glob.glob(os.path.join(path,'*.pdf')):
                print(infile)
                z[os.path.basename(infile)] = read_IDMP(infile,get_all=True)
    # jj = read_IDMP(fpath,get_all=True)
    print(time.time() - start)
    jj = []
    for key in z:
        jj.extend(z[key])
    jj = sorted(map(str.lower,set(jj)))