# vvijayk1999
# E-Mail : vvijayk1999@gmail.com

# Python program to extract MCQS

import sys
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
import io
import pandas as pd
import re
import json

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

def rmUTF(str):

    # replace UTF-8 chars with its ASCII 
    str = re.sub('\n+|\uf020','',str)
    str = re.sub('\u2013+|\u2014+','-',str)
    str = re.sub('\u2019+|\u2018+|\u201c|\u201d',"'",str)
    str = re.sub('\uf0ae+',"->",str)
    str = re.sub('\u00d7+',"x",str)

    return str


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
                question = rmUTF(group.split('Sol. Answer (')[0])
                ans = group.split('Sol. Answer (')[1].split(')')[0]
                mcq_list.append(
                    {
                        'Question':question,
                        'Answer':ans
                    }
                )
            else:
                # non Assertion type questions
                question = rmUTF(group.split('\n\n(1)')[0])
                options_lst = re.split('[(][0-9][)]',group)[1:5]
                for option in options_lst:
                    lst =  re.split('\n+',option)
                    lst = [i for i in lst if i]
                    try:
                        options.append(rmUTF(lst[0]))
                    except(IndexError): 
                        print('Could not parse - question no : ',q_no)

                ans = group.split('Sol. Answer (')[1].split(')')[0]

                # append all the list of questions, options and solutions respectively    
                try:
                    mcq_list.append(
                        {
                            'Question':question,
                            'Option_A':options[0],
                            'Option_B':options[1],
                            'Option_C':options[2],
                            'Option_D':options[3],
                            'Answer':ans
                        }
                    )
                except(IndexError):
                    print('Index out of range for question:',q_no)
            # Creating a JSON Object

            q_no += 1

    # Creating a JSON string from the list 'mcq_list'
    json_str = json.dumps(mcq_list, indent=4).encode('ascii',errors='ignore').decode('ascii')

    # Saving the JSON string to output file
    with open("output.json", "w") as write_file:
        write_file.write(json_str)
        
