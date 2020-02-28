#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 14:13:14 2020

@author: Carl
"""

import os
import sys

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine


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

        # Process each page contained in the document.
        for page in doc.get_pages():
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    lines += lt_obj.get_text().splitlines()
        first_data_items = 0
        last_data_items = 0
        for i,thing in enumerate(lines):
            if thing.lower().startswith('(u) index of data items'):
                first_data_items = i+1
                break
        for i,thing in enumerate(lines):
            if thing.lower().startswith('1.0 (u) introduction') and i > first_data_items:
                last_data_items = i
                break
                
        RELEVANT_TEXT = lines[first_data_items:last_data_items]
        
        DID_Lines = []
        for item in RELEVANT_TEXT:
            DID_Lines+=item.splitlines()
        DIDs = list(map(lambda x:x.split(' ')[0],DID_Lines))
        if get_all:
            DIDs = [d for d in DIDs if '-' in d and 'gti' not in d.lower()]
        else:
            DIDs = [d for d in DIDs if '-' in d and 'gti' not in d.lower() and
                    not '-pre-' in d.lower() and not d.lower().startswith('ee')]
        
    return DIDs


if __name__ == '__main__':
    fpath = ''
    uu = read_IDMP(fpath,get_all=True)
    
