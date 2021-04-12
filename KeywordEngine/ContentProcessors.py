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

import os
import sys
import json
import copy
import traceback
import operator

def printAndFlush (
        textToPrint,
        error=False
        ):
    '''
    Print content to the screen, When run under jenkins, flush 
    is called to force the text onto console log screen.
    '''
    if not error :
        sys.stdout.write(f"LOG: {textToPrint}")
        sys.stdout.flush()
    else:
        sys.stderr.write(f"ERR: {textToPrint}")
        sys.stderr.flush()
    return

#States
AVAILABLE = "AVAILABLE"
PROCESSING = "PROCESSING"
FILE_LOADED = "FILE_LOADED"
COMPLETE = "COMPLETE"
ERROR = "ERROR"

try:
    if os.getenv("KEYWORD_ENGINE_HOME") == None:
        os.environ["KEYWORD_ENGINE_HOME"] = os.getcwd()
        print()
    KEYWORD_HOME = os.environ["KEYWORD_ENGINE_HOME"]
except:
    self.Log("Something where wrong identifying %KEYWORD_ENGINE_HOME%", True)
#DEFAULT_CONFIG = os.path.join(KEYWORD_HOME,"SampleData","DEFAULT_ModeratorRules.config")
DEFAULT_CONFIG = os.path.join(KEYWORD_HOME,"SampleData","FTLOS_ModeratorRules.config")
DEFAULT_FILE = os.path.join(KEYWORD_HOME,"SampleData","testData.json")

class ContentBot():
    def __init__(
            self,
            FilePath=None,
            Log = printAndFlush
            ):
        '''
        Give Relative of abs path to a valid json file
        '''
        self.Log = Log
        self.File = FilePath
        OutBase,OutExt = os.path.splitext(self.File)
        self.OutFile = "%s_Proc%s"%(OutBase,OutExt)
        self.State = AVAILABLE
        self.PostIntent = {}
        self.PostContent = ""
        
        self.BinList = {}
        self.KeepList = {}
        self.AcceptList = {}
        
    def ImportConfig(
            self,
            Configurationfile=DEFAULT_CONFIG
            ):
        '''
        Import Configuration File with Key Uris and access details.
        '''
        try:
            with open (Configurationfile,"r") as r_file:
                self.Configuration = json.loads(r_file.read())
        except:
            self.Log(traceback.format_exc())
            self.Log("Failed to unpack confiuration file at %s"%Configurationfile)
            return
        try:
            self.Filters = self.Configuration["Filters"]
            self.ScoreBands = self.Configuration["ScoreBands"]
            self.GenerateExtendedFilters()
        except KeyError:
            self.Log("Failed to find Acces credentials or Urls.")
        except:
            traceback.print_exc()
        return
        
    def GenerateExtendedFilters (self):
        '''
        Take the keywords and extend them with other common typing bad habits.
        '''
        NewFilters = 0
        ExtendedFiltering = []
        for FilterName,FilterContent in self.Filters.items():
            for FilterText in FilterContent["Include"]:
                ExtendedFiltering = [
                    f"{FilterText}",
                    f" {FilterText} ",
                    f"{FilterText} ",
                    f" {FilterText}",
                    f"{FilterText}.",#Statement
                    f"{FilterText}?",#Question
                    f"{FilterText}s",
                    f"{FilterText}es",
                    f"{FilterText}sed",
                    f"{FilterText}sies",
                    f"{FilterText}ses",
                    f"{FilterText.replace(' ','. ')}",#poor grammar
                    f"{FilterText.replace('.',',')}",#Commas not full stop.
                    f"{FilterText.replace('.',':')}",#Colon not full stop.
                    f"{FilterText.replace('.','!')}"#Explaimation not full stop.
                    ]
            try:
                for ExtendedFilter in ExtendedFiltering:
                    self.Filters[FilterName]["Include"].append(ExtendedFilter)
                    NewFilters +=1
            except:
                traceback.print_exc()
        self.Log(f"Added an extra {NewFilters} Filter Options")
        return 
        
    def run(self):
        self.LoadFileContent()
        self.ImportConfig()
        if type(self.Content) == type([]):
            self.backContent = copy.deepcopy(self.Content)
            self.Content = {}
            for RecordID in range(len(self.backContent)):
                self.Content[RecordID] = self.backContent[RecordID]
                    
        if type(self.Content) == type({}):
            for PostID,PostContent in self.Content.items():
                self.PostIntent[PostID] = {
                    "Content":PostContent,
                    "Intent": copy.deepcopy(self.DecideOnContentIntent(PostContent))
                    }
                
                Action,comments = self.GetAction(PostContent)
                if Action == "Decline" or Action == "BanUser":
                    self.BinList[PostID] = self.PostIntent[PostID]
                elif Action == "DoNothing":
                    self.KeepList[PostID] = self.PostIntent[PostID]
                elif Action == "Accept":
                    self.AcceptList[PostID] = self.PostIntent[PostID]
        self.OutputProcessedFile()
        
        print("Bin %s"%len(self.BinList))
        print("Keep %s"%len(self.KeepList))
        print("Accept %s"%len(self.AcceptList))
        return 
    
    def OutputProcessedFile(self):
        '''
        Output the processed file under a new file name.
        '''
        with open(self.OutFile,"w") as o_file:
            o_file.write(
                json.dumps(
                    {
                    "Bin":self.BinList,
                    "Accept":self.AcceptList,
                    "Keep":self.KeepList
                    },
                    indent=4
                )
            )
        print ("Written to %s"%os.path.join(os.getcwd(),self.OutFile))
        return
    
    def LoadFileContent(self):
        '''
        Load JSON content for filtering from file.
        '''
        self.State = PROCESSING
        try:
            if os.path.exists(self.File):
                with open (self.File,"r") as o_file:
                    self.Content = json.loads(o_file.read())
            else:
                self.Log(f"File {self.File} Does not exist")
                return False
        except:
            traceback.print_exc()
            self.State = ERROR
            return False
        self.State = FILE_LOADED
        return True
    
    def LoadContent(
            self,
            Content
            ):
        '''
        Load JSON content for filtering from a third party caller.
        '''
        self.Content = Content
        self.State = FILE_LOADED
        return
    
    def DecideOnContentIntent(
            self,
            PostWording
            ):
        '''
        Separate the block data into sentences, remove newlines.
        Generate Filters for string intent from configuration file.
        
        '''
        Intent = {}
        for p_key,p_value in self.Filters.items():
            Intent[p_key] = False
            
        SplitSentences = PostWording.split(". ")
        CleanSentences = []
        for DirtySentence in SplitSentences:
            if "\n" in DirtySentence:
                CleanSentences.append(DirtySentence.strip("\n"))
            else:
                CleanSentences.append(DirtySentence)
                
        for Sentence in CleanSentences:
            for FilterName in self.Filters.keys():
                Result,Comment = self.PerformCheck(Sentence,FilterName)
                Intent[FilterName] = Result or Intent[FilterName]
                if Comment != "":
                    Intent["Comments"] = Intent["Comments"] + "\n" + Comment
        return Intent
            
    def PerformCheck(
            self,
            Sentences,
            FilterID
            ):
        '''
        Pass a sentence for parsing and the ID of the filter so
        appropriate keywords are used.
        '''
        Comment= ""
        FilterFlagged = False
        
        if type(Sentences) == type(""):
            Sentences = [Sentences]
        if self.Filters[FilterID]["Exclude"] == []:
            self.Filters[FilterID]["Exclude"] = ["~"]#unlikely character to be present.
        for Sentence in Sentences:
            for Keyword in self.Filters[FilterID]["Include"]:
                for antiKeyword in self.Filters[FilterID]["Exclude"]:
                    if  (Keyword.lower() in Sentence.lower()) and not (antiKeyword.lower() in Sentence.lower()):
                        FilterFlagged = True
                        break
        if FilterFlagged:
            try:
                Comment = self.Filters[FilterID]["TriggerMesage"]
            except:
                #No Trigger Message is set but default empty string returned.
                pass
        return FilterFlagged,Comment
            
    def GetAction (
            self,
            PostData
            ):
        '''
        Pass either a single string or array of strings, and get a the determined intent of
         
        '''
        returnVal = "" 
        Score = 0
        FilterMisConfigureError = False
        testList = []
        testKeys = []
        Intent = self.DecideOnContentIntent(PostData)
        for IntentOption,IntentOutput in Intent.items():
            try:
                Score = Score + (IntentOutput * self.Filters[IntentOption]["Score"])
            except:
                traceback.print_exc()
                FilterMisConfigureError = True
        ScoreBands = dict(sorted(self.ScoreBands.items(),key=operator.itemgetter(1),reverse=True))
        TotalBands = len(self.ScoreBands)
        for BandKey in self.ScoreBands.keys():
            testList.append(BandKey)
        try:
            if Score < self.ScoreBands[testList[0]]:
                returnVal = testList[0]
            elif Score > self.ScoreBands[testList[len(testList)-1]]:
                returnVal = testList[len(testList)-1]
            else:
                for i in range(len(testList)):
                    if self.ScoreBands[testList[i]] < Score <= self.ScoreBands[testList[i+1]]:
                        returnVal = testList[[i+1]]
        except:
            traceback.print_exc()
        if FilterMisConfigureError: 
            print ("A Filter Is misconfigured, check configuration")
        try:
            returnComments = Intent["Comments"]
        except:
            returnComments = ""
        return returnVal,returnComments
        
if __name__ == '__main__':
    ModerBot = ContentBot(DEFAULT_FILE)
    ModerBot.run()
