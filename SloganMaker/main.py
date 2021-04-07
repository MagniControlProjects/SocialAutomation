'''
Copyright 2021 George Linsdell

Permission is hereby granted, free of charge, to any person obtaining a copy of this 
software and associated documentation files (the "Software"), to deal in the Software 
without restriction, including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to the following 
conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE 
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
'''
import sys
import os
import datetime
import BrandedImageMaker
import csv
import traceback

'''
@author: George Linsdell
@date: 07/04/2021

Entry Level script for generating Frame images.
'''

if os.getenv("SO_AUTO_HOME") != None:
    currentDirectory = os.getenv("SO_AUTO_HOME")
else:
    currentDirectory = os.getcwd()

MODE="SINGLETHREADED"
#MODE="MULTITHREADED"
DEFAULT_CONFIGURATION_FILE = os.path.join(currentDirectory,"SloganMaker","Configurations","imageConfiguration.json")
DEFAULT_QUOTE_FILE = os.path.join(currentDirectory,"SloganMaker","SampleData","GoodQuotes.json")
DEFAULT_FONTS_FOLDER = os.path.join(currentDirectory,"SloganMaker","Fonts")

if __name__ == '__main__':
    TotalStartTimer =  datetime.datetime.now()
    if MODE == "MULTITHREADED":
        runner = BrandedImageMaker.ImageThreadMaker(
            QuoteConfiguration=DEFAULT_CONFIGURATION_FILE,
            QuoteFonts=DEFAULT_FONTS_FOLDER,
            QuoteFile=DEFAULT_QUOTE_FILE)
        runner.run()
        Duration = datetime.datetime.now() - TotalStartTimer
        print("Total Image creation of %s images complete in %s"%(runner.TotalThreads,str(Duration)))
    else:

        TotalStartTimer =  datetime.datetime.now()
        numberOfFiles = 0
        test = BrandedImageMaker.SloganMaker(FileName="Images\\%s.png"%numberOfFiles,
            ConfigurationFile=DEFAULT_CONFIGURATION_FILE,
            FontFolder=DEFAULT_FONTS_FOLDER,
            )#QuoteFile=DEFAULT_QUOTE_FILE)
        inputfile = "SloganMaker\\SampleData\\Quotes1.csv"

        with open (inputfile,"r") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in spamreader:
                StartTimer =  datetime.datetime.now()
                test.SetFileName(FileName="Images_FWA\\%s_%s.png"%(numberOfFiles,row[0].strip('",.-')))
                test.run(row[1],row[0])
                test.WriteFile()
                numberOfFiles += 1
                Duration = datetime.datetime.now() - StartTimer
                print("ImageCreation Completed in %s"%str(Duration))
                print(Duration)
        Duration = datetime.datetime.now() - TotalStartTimer
        print("Total Image creation of %s images complete in "%numberOfFiles)
        print(Duration)
    sys.exit(0)