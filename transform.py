import sys
import os

# Set Path for files in support/
rootdiroftools = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(rootdiroftools,'support'))

#from subprocess import Popen, PIPE, call
import subprocess
import getopt

import readerise
import mediawikiPrinter

import asciiRenderer
import csvRenderer
import mdRenderer
import contextRenderer
import singlehtmlRenderer
import loutRenderer
import htmlRenderer

def runscriptold(c, prefix=''):
    print prefix + ':: ' + c
    pp = Popen(c, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    for ln in pp.stdout:
        print prefix + ln[:-1]

def runscript(c, prefix='', repeatFilter = ''):
    print prefix + ':: ' + c
    pp = subprocess.Popen([c], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    (result, stderrdata) = pp.communicate()
    print result
    print stderrdata
    if not repeatFilter == '' and not stderrdata.find(repeatFilter) == -1:
        runscript(c, prefix, repeatFilter)

def buildLout(usfmDir, builtDir, buildName):
 
    print '#### Building Lout...'

    # Prepare
    print '     Clean working dir'
    runscript('rm "' + builtDir + '/working/lout/*"', '       ')

    # Convert to Lout
    print '     Converting to Lout'
    ensureOutputDir(builtDir + '/working/lout')
    c = loutRenderer.LoutRenderer(usfmDir, builtDir + '/working/lout/' + buildName + '.lout')
    c.render()
    
    # Run Lout
    print '     Copying support files'
    runscript('cp support/lout/oebbook working/lout', '       ')
    print '     Running Lout'
    runscript('cd "' + builtDir + '/working/lout"; lout "./' + buildName + '.lout" > "' + buildName + '.ps"', '       ', repeatFilter='unresolved cross reference')
    print '     Running ps2pdf'
    runscript('cd "' + builtDir + '/working/lout"; ps2pdf -dDEVICEWIDTHPOINTS=432 -dDEVICEHEIGHTPOINTS=648 "' + buildName + '.ps" "' + buildName + '.pdf" ', '       ')
    print '     Copying into builtDir'
    runscript('cp "' + builtDir + '/working/lout/' + buildName + '.pdf" "' + builtDir + '/' + buildName + '.pdf" ', '       ')

def buildConTeXt(usfmDir, builtDir, buildName, order):

    print '#### Building PDF via ConTeXt...'

    # Convert to ConTeXt
    print '     Converting to ConTeXt...'
    #c = texise.TransformToContext()
    #c.setupAndRun(usfmDir, 'working/tex', buildName)
    ensureOutputDir(builtDir + '/working/tex')
    ensureOutputDir(builtDir + '/working/tex-working')
    c = contextRenderer.ConTeXtRenderer(usfmDir, builtDir + '/working/tex/bible.tex')
    c.render(order)

    # Build PDF
    print '     Building PDF..'
    c = '. ./support/thirdparty/context/tex/setuptex ; cd "' + builtDir + '/working/tex-working"; rm * ; context ../tex/bible.tex; cp bible.pdf "../../' + buildName + '.pdf"'
    runscript(c, '     ')

def buildWeb(usfmDir, builtDir, buildName, oebFlag=False):
    # Convert to HTML
    print '#### Building HTML...'
    ensureOutputDir(builtDir + '/' + buildName + '_html')
    c = htmlRenderer.HTMLRenderer(usfmDir, builtDir + '/' + buildName + '_html', oebFlag)
    c.render()

def buildSingleHtml(usfmDir, builtDir, buildName, order="normal"):
    # Convert to HTML
    print '#### Building HTML...'
    ensureOutputDir(builtDir)
    c = singlehtmlRenderer.SingleHTMLRenderer(usfmDir, builtDir + '/' + buildName + '.html')
    c.render(order)

def buildCSV(usfmDir, builtDir, buildName):
    # Convert to CSV
    print '#### Building CSV...'
    ensureOutputDir(builtDir)
    c = csvRenderer.CSVRenderer(usfmDir, builtDir + '/' + buildName + '.csv.txt')
    c.render()

def buildReader(usfmDir, builtDir, buildName, order="normal"):
    # Convert to js for online reader
    print '#### Building for Reader...'
    ensureOutputDir(builtDir + 'en_oeb')
    c = readerise.ReaderRenderer(usfmDir, builtDir + '/' + buildName + '.js')
    c.render(order)

def buildMarkdown(usfmDir, builtDir, buildName, order="normal"):
    # Convert to Markdown for Pandoc
    print '#### Building for Markdown...'
    ensureOutputDir(builtDir)
    c = mdRenderer.MarkdownRenderer(usfmDir, builtDir + '/' + buildName + '.md')
    c.render(order)

def buildASCII(usfmDir, builtDir, buildName):
    # Convert to ASCII
    print '#### Building for ASCII...'
    ensureOutputDir(builtDir)
    c = asciiRenderer.ASCIIRenderer(usfmDir, builtDir + '/' + buildName + '.txt')
    c.render()

def buildMediawiki(usfmDir, builtDir, buildName):
    # Convert to MediaWiki format for Door43
    print '#### Building for Mediawiki...'
    # Check output directory
    ensureOutputDir(builtDir + '/mediawiki')
    mediawikiPrinter.Transform().setupAndRun(usfmDir, builtDir + '/mediawiki')

def ensureOutputDir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

savedCWD = ''
def saveCWD():    global savedCWD ; savedCWD = os.getcwd() ; os.chdir(rootdiroftools)
def restoreCWD(): os.chdir(savedCWD)
    
def main(argv):
    saveCWD() 
    oebFlag = False  
    order="normal" 
    print '#### Starting Build.'
    try:
        opts, args = getopt.getopt(argv, "ht:u:b:n:or:", ["help", "target=", "usfmDir=", "builtDir=", "name=","oeb","order="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            return usage()
        elif opt in ("-t", "--target"):
            targets =  arg
        elif opt in ("-u", "--usfmDir"):
            usfmDir = arg
        elif opt in ("-b", "--builtDir"):
            buildDir = arg
        elif opt in ("-n", "--name"):
            buildName = arg
        elif opt in ("-r", "--order"):
            order = arg
        elif opt in ("-o", "--oeb"):
            oebFlag = True
        else:
            usage()

    if targets == 'context':
        buildConTeXt(usfmDir, buildDir, buildName, order)
    elif targets == 'html':
        buildWeb(usfmDir, buildDir, buildName, oebFlag)
    elif targets == 'singlehtml':
        buildSingleHtml(usfmDir, buildDir, buildName, order)
    elif targets == 'md':
        buildMarkdown(usfmDir, buildDir, buildName, order)
    elif targets == 'reader':
        buildReader(usfmDir, buildDir, buildName)
    elif targets == 'mediawiki':
        buildMediawiki(usfmDir, buildDir, buildName)
    elif targets == 'lout':
        buildLout(usfmDir, buildDir, buildName)
    elif targets == 'csv':
        buildCSV(usfmDir, buildDir, buildName)
    elif targets == 'ascii':
        buildASCII(usfmDir, buildDir, buildName)
    elif targets == 'csv':
        buildCSV(usfmDir, buildDir, buildName)
    else:
        usage()

    print '#### Finished.'
    restoreCWD()

def usage():
    print """
        USFM-Tools
        ----------

        Build script.  See source for details.
        
        Setup:
        transform.py --setup 
        
    """

if __name__ == "__main__":
    main(sys.argv[1:])