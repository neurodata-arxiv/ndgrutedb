'''
@author : Disa Mhembere
Module to hold the views of a Django one-click MR-connectome pipeline
'''
import os, sys, re

from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect

from django.core.files import File        # For programmatic file upload

from ocpipeline.models import Document
from ocpipeline.forms import DocumentForm
from ocpipeline.forms import OKForm
from ocpipeline.forms import DataForm
import mrpaths

from django.http import HttpResponse

''' Data Processing imports'''
from mrcap import gengraph as gengraph

#import mrcap.svd as svd
#import mrcap.lcc as lcc

import ocpipeline.filesorter as filesorter
import ocpipeline.zipper as zipper
import ocpipeline.createDirStruct as createDirStruct

from django.core.servers.basehttp import FileWrapper

import subprocess
from shutil import move, rmtree # For moving files

Global Paths
'''
uploadDirPath = '/data/projects/disa/OCPprojects/' # Global path to files that are uploaded by users
processingScriptDirPath = os.path.abspath(os.path.curdir) + "/ocpipeline/mrcap/" # Global path to location of processing code

'''
Global file Names all initialized to an empty string
'''
roi_xml_fn = ''
fiber_fn = ''
roi_raw_fn = ''

smallGraphOutputFileName = '' # fileName of output of gengraph for a small graph
bigGraphOutputFileName = '' # fileName of output of gengraph for a big graph
lccOutputFileName = ''
embedSVDOutputFileName = ''

''' To hold each type of file available for download'''
derivatives = ''    # _fiber.dat, _roi.xml, _roi.raw
rawdata = ''        # none yet
graphs = ''         # biggraph, smallgraph
graphInvariants = ''# LCC.npy (largest connected components), EMBED.ny (Single Value Decomposition)
images = ''	    # To hold images  

userDefProjectDir = '' # To be defined by user
scanId = '' # To be defined by user

progBit = False # This bit will be set if user decides to proceed programmatically
multiProgBit = False # Multiple file option
multiProjTuple = [] # Tuple to hold names of all scan session Dirs

multiFileDir = '' # directory to hold numerous case files 

''' Little welcome message'''
def default(request):
    return render_to_response('welcome.html')

def multiUpload(request, webargs):
    global multiFileDir
    '''TODO: Upload a bunch of files to a single directory & save name of dir in multiFileDir '''
    print '\nProcessing directory for multi scan dataset...'
    multiFileDir =  webargs	# '/data/Multi' dir already exists right now    
    return HttpResponseRedirect('/multiFileProcess')

def multiFileProcess(request):
    global multiFileDir
    global userDefProjectDir
    global scanId
    
    global derivatives
    global rawdata
    global graphs
    global graphInvariants
    global images
    
    global roi_xml_fn
    global fiber_fn
    global roi_raw_fn
    global multiProgBit
    
    multiProgBit = True
    
    fiberPattern = re.compile('.+\.dat$') # regex matching fiber track file name
    fiberList = []
    
    for it in os.listdir(multiFileDir):
        if (re.search(fiberPattern, it)):
            fiberList.append(os.path.join(multiFileDir, it)) #
    
    for it in fiberList:
        fiber_fn = it
        roi_raw_fn = getbaseNameFromFiber(fiber_fn) +'roi.raw'
        roi_xml_fn = getbaseNameFromFiber(fiber_fn) + 'roi.xml'
	
	# Use regex to get as scanId as the baseName of the files
	scanId = re.search(re.compile('.+(?=_)'), fiber_fn).group().split('/')[-1] # regex may have to change
	
	''' Hard coded now, but should be something we can extract from metadata of track file'''
	userDefProjectDir = os.path.join(uploadDirPath, 'Multiprojects', 'site', 'subject', 'session', scanId)
	multiProjTuple.append(userDefProjectDir) # add new scan to project
	
	fiber_fn, roi_raw_fn, roi_xml_fn = createDirStruct.createDirStruct(userDefProjectDir, [fiber_fn, roi_raw_fn, roi_xml_fn])
	derivatives, rawdata,  graphs, graphInvariants, images = defDataDirs(userDefProjectDir)	
	
	processInputData(request) # run files through data analysis & return to here
	
	#zipProcessedData(request) # zipfiles
	#open_new_tab(request.META['HTTP_HOST']+'/zipOutput') # single scan download

    return HttpResponseRedirect('/zipOutput/multiProjTuple')
    #return render_to_response('success.html')


def createProj(request, webargs=None):
    global userDefProjectDir
    global scanId
    
    ''' Programmatic''' 
    if (webargs):
        [userDefProjectName, site, subject, session, scanId] = request.path.split('/')[2:7] # This will always be true
    
        userDefProjectName = os.path.join(uploadDirPath, userDefProjectName) # Fully qualify
        userDefProjectDir =  os.path.join(userDefProjectName, site, subject, session, scanId)
	
        return HttpResponseRedirect('/pipelineUpload') # Redirect after POST
    
    ''' Form '''
    if request.method == 'POST':
        form = DataForm(request.POST)
        if form.is_valid():
            userDefProjectName = form.cleaned_data['UserDefprojectName']
            site = form.cleaned_data['site']
            subject = form.cleaned_data['subject']
            session = form.cleaned_data['session']
            scanId = form.cleaned_data['scanId']
        
	    userDefProjectName = os.path.join(uploadDirPath, userDefProjectName) # Fully qualify
	    userDefProjectDir =  os.path.join(userDefProjectName, site, subject, session, scanId)
	
        return HttpResponseRedirect('/pipelineUpload') # Redirect after POST
    else:
        form = DataForm() # An unbound form
   
    return render(request, 'nameProject.html', {
        'form': form,
    })

def getbaseNameFromFiber(fileName):
    basename = ''
    for i in fileName.split('/')[1:-2]:
        basename = os.path.join(basename,fileName)
    return basename[:-9]

def defDataDirs(projectDir):
    
    derivatives = os.path.join(projectDir, 'derivatives')
    rawdata = os.path.join(projectDir, 'rawdata')
    graphs = os.path.join(projectDir, 'graphs')
    graphInvariants = os.path.join(projectDir, 'graphInvariants')
    images = os.path.join(projectDir, 'images')
    
    return [derivatives, rawdata, graphs, graphInvariants, images]

''' Successful completion of task'''
def success(request):
    return render_to_response('success.html')   

def pipelineUpload(request, webargs=None):
    global userDefProjectDir
    global derivatives
    global rawdata
    global graphs
    global graphInvariants
    global images
    
    print "Uploading files..."
    
    ''' Programmatic Version
        webargs should be fully qualified name of track file e.g /data/files/name_fiber.dat
        Assumption is naming convention is name_fiber.dat, name_roi.dat, name_roi.xml, where
        'name' is the same in all cases
    ''' 
    if(webargs):
	global progBit
	progBit = True # Set the programmatic marker
	
        fiber_fn = request.path[15:] # Directory where
        if fiber_fn[-1] == '/': # in case of trailing backslash
            fiber_fn = fiber_fn[:-1]
            
        '''Assume directory & naming structure matches braingraph1's: "/data/projects/MRN/base" structure'''
	roi_raw_fn = roi_xml_fn = '/'
        for i in fiber_fn.split('/')[1:-2]:
            roi_raw_fn += i + '/'
            roi_xml_fn += i + '/'

        basename = fiber_fn.split('/')[-1][:-9]

        roi_raw_fn += 'roi/' +  basename +'roi.raw'
        roi_xml_fn += 'roi/' +  basename +'roi.xml'
	
	''' Define data directory paths '''
	derivatives, rawdata,  graphs, graphInvariants, images = defDataDirs(userDefProjectDir)

        for files in [fiber_fn, roi_xml_fn, roi_raw_fn] : # Names of files
            doc = Document() # create a new Document for each file
            with open(files, 'rb') as doc_file: # Open file for reading
		doc._meta.get_field('docfile').upload_to = derivatives # route files to correct location
                doc.docfile.save(files, File(doc_file), save=True) # Save upload files
                doc.save()
        
	''' Just the filename with no path info '''
	fiber_fn = fiber_fn.split('/')[-1] 
	roi_raw_fn = roi_raw_fn.split('/')[-1]
	roi_xml_fn = roi_xml_fn.split('/')[-1]
	    
        ''' Make appropriate dirs if they dont already exist'''
        createDirStruct.createDirStruct([derivatives, rawdata, graphs, graphInvariants, images])
	
	#import pdb; pdb.set_trace()
	
	return HttpResponseRedirect('/processInput') # Redirect after POST

    ''' Form '''
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES) # instantiating form
        if form.is_valid():
	    
	    ''' Define data directory paths '''
	    derivatives, rawdata,  graphs, graphInvariants, images = defDataDirs(userDefProjectDir)
	    
            newdoc = Document(docfile = request.FILES['docfile'])
	    newdoc._meta.get_field('docfile').upload_to = derivatives # route files to correct location
	    
	    newdoc2 = Document(docfile = request.FILES['roi_raw_file'])
	    newdoc2._meta.get_field('docfile').upload_to = derivatives
	    
            newdoc3 = Document(docfile = request.FILES['roi_xml_file'])
            newdoc3._meta.get_field('docfile').upload_to = derivatives
	    
            ''' Acquire fileNames '''
            fiber_fn = form.cleaned_data['docfile'].name # get the name of the file input by user
            roi_raw_fn = form.cleaned_data['roi_raw_file'].name
            roi_xml_fn = form.cleaned_data['roi_xml_file'].name
	    
            ''' Save files to temp location '''
            newdoc.save()
            newdoc2.save()
            newdoc3.save()
            print '\nSaving all files complete...'
               
            ''' Make appropriate dirs if they dont already exist '''	    
            createDirStruct.createDirStruct([derivatives, rawdata, graphs, graphInvariants, images])
            
            # Redirect to Processing page
        return HttpResponseRedirect('/processInput')
    else:
        form = DocumentForm() # An empty, unbound form
        
    # Render the form
    return render_to_response(
        'pipelineUpload.html',
        {'form': form},
        context_instance=RequestContext(request) # Some failure to input data & returns a key signaling what is requested
    )

def processInputData(request):
    '''
    Extract File Name
    Determine what file corresponds to what for gengraph
    '''
    global roi_xml_fn
    global fiber_fn
    global roi_raw_fn
    global derivatives
    global progBit
    
    filesInUploadDir = os.listdir(derivatives)
    
    roi_xml_fn, fiber_fn, roi_raw_fn = filesorter.checkFileExtGengraph(filesInUploadDir) # Check & sort files
    
    for fileName in [roi_xml_fn, fiber_fn, roi_raw_fn]:
	if fileName == "": # Means a file is missing from i/p
	    return render_to_response('pipelineUpload.html', {'form': form}, context_instance=RequestContext(request)) # Missing file for processing Gengraph    
    
    baseName = fiber_fn[:-9] #MAY HAVE TO CHANGE
    
    ''' Fully qualify file names''' 
    fiber_fn = os.path.join(derivatives, fiber_fn)
    roi_raw_fn = os.path.join(derivatives, roi_raw_fn)
    roi_xml_fn = os.path.join(derivatives, roi_xml_fn)
    
    
    global graphs  # let function see path for final graph residence
    global smallGraphOutputFileName # Change global name for small graph o/p file name so all methods can see it
    global processingScriptDirPath
    
    '''Run gengraph SMALL & save output'''
    print("Running Small gengraph....")
    smallGraphOutputFileName = os.path.join(graphs, (fiber_fn[:-9] +'fiberSmGr.mat'))
    ''' spawn subprocess to create small since its result is not necessary for processing '''
    #arguments = 'python ' + '/home/disa/MR-connectome/mrcap/gengraph.py /home/disa' + fiber_fn + ' /home/disa' + smallGraphOutputFileName +' /home/disa' + roi_xml_fn + ' /home/disa' + roi_raw_fn
    #arguments = 'python ' + '/Users/dmhembere44/MR-connectome/mrcap/gengraph.py /Users/dmhembere44' + fiber_fn + ' /Users/dmhembere44' + smallGraphOutputFileName + ' roixmlname=/Users/dmhembere44' + roi_xml_fn + ' roirawname=/Users/dmhembere44' + roi_raw_fn
    #subprocess.Popen(arguments,shell=True) 
    #**gengraph.genGraph(fiber_fn, smallGraphOutputFileName, roi_xml_fn ,roi_raw_fn)
    
    ''' Run gengrah BIG & save output '''
    global bigGraphOutputFileName  # Change global name for small graph o/p file name
    print("\nRunning Big gengraph....")
    bigGraphOutputFileName = os.path.join(graphs, (fiber_fn[:-9] +'fiberBgGr.mat')) 
    #**gengraph.genGraph(fiber_fn, bigGraphOutputFileName, roi_xml_fn ,roi_raw_fn, True)
    
    ''' Run LCC '''
    global graphInvariants
    lccOutputFileName = os.path.join(graphInvariants, (baseName + 'lcc.npy'))
    
    '''Should be big but we'll do small for now'''
    #**lcc.process_single_brain(roi_xml_fn, roi_raw_fn, bigGraphOutputFileName, lccOutputFileName)
    #**lcc.process_single_brain(roi_xml_fn, roi_raw_fn, smallGraphOutputFileName, lccOutputFileName)
    
    ''' Run Embed - SVD '''
    global embedSVDOutputFileName
    embedSVDOutputFileName = os.path.join(graphInvariants, (baseName + 'embed.npy'))
    
    print("Running SVD....")
    roiBaseName = str(roi_xml_fn[:-4])
    #**svd.embed_graph(lccOutputFileName, roiBaseName, bigGraphOutputFileName, embedSVDOutputFileName)
    #**svd.embed_graph(lccOutputFileName, roiBaseName, smallGraphOutputFileName, embedSVDOutputFileName)
    
    if (multiProgBit):
	return request # response

    if (progBit):
	return HttpResponseRedirect('/zipOutput')

    return HttpResponseRedirect('/confirmDownload')

def confirmDownload(request):
    if request.method == 'POST': # If form is submitted
        form = OKForm(request.POST)
        if form.is_valid():
            pass # Maybe log response in database
        return HttpResponseRedirect('/zipOutput') # Redirect after POST
    else:
        form = OKForm() # An unbound form
    return render(request, 'confirmDownload.html', {
        'form': form,
    })

def zipProcessedData(request, multiarg = None):
    '''
    Compress data products to single zip for upload
    '''
    print '\nBeginning file compression...'
    # Take dir with multiple scans, compress it & send it off 
    if (multiarg):
	global multiProjTuple
	
	''' Zip it '''
	temp = zipper.zipFilesFromFolders(multiTuple = multiProjTuple)
	''' Wrap it '''
	wrapper = FileWrapper(temp)
	response = HttpResponse(wrapper, content_type='application/zip')
	response['Content-Disposition'] = ('attachment; filename=MultiScan.zip')
	response['Content-Length'] = temp.tell()
	temp.seek(0)
	''' Send it '''
	return response
    
    global scanId
    global userDefProjectDir
    
    ''' Zip it '''
    temp = zipper.zipFilesFromFolders(dirName = userDefProjectDir)
    ''' Wrap it '''
    wrapper = FileWrapper(temp) 
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = ('attachment; filename='+ scanId +'.zip')
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    ''' Send it '''
    return response
