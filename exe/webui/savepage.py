# ===========================================================================
# eXe
# Copyright 2004-2005, University of Auckland
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# ===========================================================================

"""
The SavePage is responsible for saving the current project
"""

import os
import os.path
import logging
import gettext
from twisted.web.resource import Resource
from exe.webui import common


log = logging.getLogger(__name__)
_   = gettext.gettext


class SavePage(Resource):
    """
    The SavePage is responsible for saving the current project
    """
    
    def __init__(self, webserver):
        """
        Initialize
        """
        Resource.__init__(self)
        self.package      = None
        self.packageStore = webserver.application.packageStore
        self.url          = ""
        self.message      = ""
        self.isSaved      = False
        self.dataDir      = webserver.application.config.dataDir

        
    def process(self, request):
        """
        Save the current package 
        """
        log.debug("process " + repr(request.args))
        
        self.isSaved = False
        self.url     = request.path
        packageName  = request.prepath[0]
        self.package = self.packageStore.getPackage(packageName)
        
        if "save" in request.args or \
           ("action" in request.args and 
            request.args["action"][0]=="saveChange"):
            filePathName = request.args["fileName"][0]
            log.debug("filePathName: " + filePathName)
            fileDir  = os.path.dirname(filePathName)
            fileName = os.path.basename(filePathName)
            log.debug("fileName: " + fileName)
            if fileDir == "":
                fileDir = self.dataDir
                
            if os.path.isdir(fileDir):
                self.dataDir = fileDir
                oldDir = os.path.abspath('.')
                os.chdir(fileDir)
                try:
                    self.package.name = \
                            os.path.splitext(os.path.basename(fileName))[0]
                    if not fileName.endswith(".elp"):
                        fileName = fileName + ".elp"
                  
                    log.info("saving " + fileName)
                    self.package.save(fileDir)                
                    self.message = _("The course package has been "\
                                     +"saved successfully.")
                finally:
                    os.chdir(oldDir)
            else:
                self.message = _("Invalid path, please enter an another one.")
                
            
            

    def render_GET(self, request):
        """Called for all requests to this object"""
        
        # Processing 
        log.debug("render_GET")
        self.process(request)
        path = os.path.join(self.dataDir, self.package.name+".elp")
                        
        # Rendering
        html  = common.header() 
        html += common.banner(request)
        html += "<div id=\"main\"> \n"
        html += "<h3>Save Project</h3>\n"        
        html += "<form method=\"post\" action=\"%s\" " % self.url
        html += "name=\"contentForm\" >"  
        html += common.hiddenField("action")
        html += common.hiddenField("isChanged", self.package.isChanged)
        html += "<br/><b>" + self.message+ "</b>"           
        html += "<br/>%s<br/>" % _("Enter a filename for your project")        
        html += common.textInput("fileName", path, 70)
        html += "<br/><br/>"
        html += common.submitButton("save", _("Save"))
        html += "<br/></form>"
        html += "</div> \n"
        html += common.footer()
        self.message = ""
        
        return html
    
    render_POST = render_GET
