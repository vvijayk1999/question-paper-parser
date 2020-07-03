# vvijayk1999
# E-Mail : vvijayk199@gmail.com

# Python program to extract MCQS

import sys
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
import io
import pandas as pd
import re

def pdfparser(filename):

    fp = open(filename, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.

    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        data =  retstr.getvalue()

    return data

def sectionExtraction(data):
    
    sections = []

    sections = data.split('SECTION')

    return sections[1:]


if __name__ == '__main__':

    mcq_list = []
    q_no = 0

    # file name is passed as an arguement 
    # function pdfparser parses the PDF document and returns the string data

    data = pdfparser(sys.argv[1]) 

    # splitting the data into multiple sections
    sections = sectionExtraction(data)

    # itterate through all the sections.
    for section in sections:

        # from each section we are splitting the data into groups
        # each group contains questions, options and the solution
        groups = re.split('[0-9]+[.][ ]*\n*',section)[1:]
        for group in groups:
            options = []

            # The document may contain Asserion type questions where the options are not available
            if re.search('Assertion',section):
                question = group.split('Sol. Answer (')[0]
                ans = group.split('Sol. Answer (')[1].split(')')[0]
            else:
                # non Assertion type questions
                question = group.split('\n\n(1)')[0]
                options_lst = re.split('[(][0-9][)]',group)[1:5]
                for option in options_lst:
                    lst =  re.split('\n+',option)
                    lst = [i for i in lst if i]
                    try:
                        options.append(lst[0])
                    except(IndexError): 
                        print('Could not parse - question no : ',q_no)

            ans = group.split('Sol. Answer (')[1].split(')')[0]

            # append all the list of questions, options and solutions respectively    
            mcq_list.append([question,options,ans])
            q_no += 1

    # create a Pandas Dataframe
    df = pd.DataFrame(mcq_list)

    # store the data into a CSV file
    df.to_csv('output.csv', encoding='utf-8-sig')
        
