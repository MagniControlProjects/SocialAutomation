import os
import sys
import csv
import traceback
import json
import datetime
'''
@author: george linsdell
@date: 04/09/2020
'''

BLOCK = "BLOCK"
PERMIT = "PERMIT"
ACCEPT = "ACCEPT"

if os.getenv("FILTER_HOME_DIR") == None:
    currentDirectory = os.getcwd() 
else:
    currentDirectory = os.getenv("FILTER_HOME_DIR")
    
DEFAULT_RULES_FILE = os.path.join(currentDirectory,"Configurations","QuoteParseRules.json")
DEFAULT_DISCOVER_FILE = os.path.join(currentDirectory,"discovered.json")
DEFAULT_BAD_OUTPUT_FILE = os.path.join(currentDirectory,"BadQuotes.json")
DEFAULT_GOOD_OUTPUT_FILE = os.path.join(currentDirectory,"GoodQuotes.json")
DEFAULT_CLEAN_OUTPUT_FILE = os.path.join(currentDirectory,"newQuoteFile.csv")
DEFAULT_INPUT_QUOTE_FILE = os.path.join(currentDirectory,"SampleData","Quotes2.csv")

class QuoteFilter ():
    def __init__(
            self,
            Filename,
            DiscoveredFile = DEFAULT_DISCOVER_FILE,
            RulesFile = DEFAULT_RULES_FILE,
            BadOutputFile = DEFAULT_BAD_OUTPUT_FILE,
            GoodOutputFile = DEFAULT_GOOD_OUTPUT_FILE,
            CleanOutputFile = DEFAULT_CLEAN_OUTPUT_FILE
            ):
        self.Filename = os.path.join(currentDirectory,Filename)
        self.DiscoveredFile = DiscoveredFile
        self.RulesFile = RulesFile #json
        self.BadOutputFile = BadOutputFile #json
        self.GoodOutputFile = BadOutputFile #json
        self.UniqueQuotes = {}
        self.UniqueAuthors = {}
        self.BadAuthors = []
        self.RejectedQuotes = []
        self.AcceptedQuotes = []
        self.CleanedFile = CleanOutputFile
        
    def LoadRules(self):
        try:
            with open(self.RulesFile,"r") as O_file:
                self.Rules = json.loads(O_file.read())
                print("Read In Rules from %s"%self.RulesFile)
                try:
                    self.AuthorRules = self.Rules["AuthorRules"]
                    self.AuthorRules["BadAuthorsLower"] = []
                    for Author in self.AuthorRules["BadAuthors"]:
                        self.AuthorRules["BadAuthorsLower"].append(Author.lower())
                except:
                    self.AuthorRules = {}
                try:
                    self.QuoteRules = self.Rules["QuoteRules"]
                except:
                    self.QuoteRules = {}
        except:
            print("Exception Occured Trying to rule authors. from %s"%self.RulesFile)
            self.AuthorRules = []
            self.QuoteRules = []
            traceback.print_exc()
        return 
    
    def run(self):
        '''
        import the target file into memory
        The submit the memory file for approval processing
        '''
        self.RunStart = datetime.datetime.now()
        with open (self.Filename,"r") as r_file:
            print("Reading csv file '%s'for quote data with authors in column 0."%self.Filename)
            reader = csv.reader(r_file,quotechar='"',delimiter=",")
            for QuoteLine in reader:
                if QuoteLine[0] != "":
                    try:
                        self.UniqueAuthors[QuoteLine[0]].append(QuoteLine[1])
                    except:
                        self.UniqueAuthors[QuoteLine[0]] = []
                        
        with open(self.DiscoveredFile,"w") as w_file:
            w_file.write(json.dumps(self.UniqueAuthors))
            print("Outputted Discovered %s Unique Authors to %s"%(len(self.UniqueAuthors),self.DiscoveredFile))
        
        self.ApproveQuotesBasedOnRules()
        self.ExportQuoteLists()
        self.RunTime = datetime.datetime.now() - self.RunStart
        print("Run Executed in %s"%str(self.RunTime))
        return
    
    def ApproveQuotesBasedOnRules(self):
        '''
        Load the rules into the engine,
        Then run the content discovered against the engine.
        '''
        self.LoadRules()
        for Author,AuthorQuotes in self.UniqueAuthors.items():
            try:
                if Author.lower() in self.AuthorRules["BadAuthorsLower"]:
                    print("Rejecting %s"%Author)
            except:
                print("Unable to parse permitted authors, is there a filter set")
            for Quote in AuthorQuotes:
                self.UniqueQuotes[Quote] = Author
                QuoteAction = []
                quoteValue = "N"
                for rule,action in self.QuoteRules.items():
                    if self.ValidateWordPresence(rule,Quote):
                        QuoteAction.append(action)
                if QuoteAction !=  []:
                    quoteValue = 0
                    for action in QuoteAction:
                        if action == PERMIT:
                            quoteValue += 1
                        elif action == BLOCK:
                            quoteValue -= 1
                        else:
                            pass
                    #print(quoteValue)
                    if quoteValue >= 0:
                        self.AcceptedQuotes.append([Quote,Author])
                    else:
                        self.RejectedQuotes.append([Quote,Author])
                else:
                    #print("Rejecting %s by %s due to null statement ness"%(Quote,Author))
                    self.RejectedQuotes.append([Quote,Author,quoteValue])
        print("Rule Processing Complete")
        
        return 
    
    def ValidateWordPresence(
            self,
            checkWord,
            statement
            ):
        
        checkWord=checkWord.lower()
        checkWord=checkWord.strip(",.?!'")
        checkList = [
            checkWord,
            " %s "%checkWord,
            " %s"%checkWord,
            "%s "%checkWord,
            "%ss"%checkWord,
            "%sed"%checkWord,
            "%sd"%checkWord,
            "%sies"%checkWord,
            "%ses"%checkWord,
            ]
        statement = statement.lower()
        statement = statement.strip(",.?!'")
        statementWords = statement.split(" ")
        Present = False
        for keyword in statementWords:
            for CheckItem in checkList:
                if CheckItem == keyword:
                    Present = True
                    break
        return Present
    
    def ExportQuoteLists(self):
        fileset = [
            [self.GoodOutputFile,self.AcceptedQuotes],
            [self.BadOutputFile,self.RejectedQuotes]
            ]
        for f_set in fileset:
            with open(f_set[0],"w") as w_file:
                w_file.write(json.dumps(f_set[1],indent=4,sort_keys=True))
            print("Outputted json content with %s items to %s"%(len(f_set[1]),f_set[0]))
            
        with open (self.CleanedFile,"w",newline="\n") as w_file:
            print("Exporting cleaned file with %s entries"%len(self.UniqueQuotes))
            writer = csv.writer(w_file,delimiter=",",quotechar='"')
            writer.writerow(["Author","Quote"])
            for QuoteVal,QuoteAuthor in self.UniqueQuotes.items():
                writer.writerow([QuoteAuthor,QuoteVal])
        return
                
if __name__ == '__main__':
    quotefile = DEFAULT_INPUT_QUOTE_FILE
    Filter = QuoteFilter(quotefile)
    Filter.run()
    