'''

A class exploring the database images with a dialog for adding tag strings

@author: Agusti Pellicer (Aalto University)

'''

import wx
import gadoDB
import sqlite3
import wx.grid
import subprocess
from PIL import Image



class TagDialog(wx.Dialog):
    """ wxDialog to modify the tags """
    def __init__(self,*args, **kw):
        self.tags = kw.pop('tags', None)
        self.artifact = kw.pop('artifact',None)
        super(TagDialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((250,100))
        self.SetTitle("Modify tags")
        print self.tags

    def InitUI(self):
        """ Set up the UI stuff """

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)


        tagsLabel = wx.StaticText(self, label="Tags:")
        self.tagsText = wx.TextCtrl(self)
        self.tagsText.SetValue(self.tags)

        hbox1.Add(self.tagsText, flag=wx.EXPAND, border=10, proportion=1)

        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Cancel')

        okButton.Bind(wx.EVT_BUTTON, self.saveTags)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)


        hbox2.Add(okButton,flag=wx.CENTER,border=10)
        hbox2.Add((-1,10))
        hbox2.Add(closeButton,flag=wx.CENTER,border=10)

        vbox.Add(tagsLabel,border=10)
        vbox.Add((-1,10))
        vbox.Add(hbox1, flag=wx.EXPAND, border=10)
        vbox.Add((-1,10))
        vbox.Add(hbox2,flag=wx.CENTER, border=10)
        vbox.Add((-1,10))

        self.SetSizer(vbox)

    def OnClose(self, event):
        self.Destroy()
    def saveTags(self,event):
        db = gadoDB.GadoDB('gado.db')
        tags = self.tagsText.GetValue().strip()
        if tags[-1] == ',':
            tags = tags[:-1].split(',')
        else:
            tags = tags.split(',')
        #just removing whitespaces
        tags = [x.strip() for x in tags]
        db.setTagsOfArtifact(self.artifact,tags)
        self.Destroy()

class MyImageRenderer(wx.grid.PyGridCellRenderer):
    """ Class to print images in the grid, extracted from http://commentsarelies.blogspot.fi/2008/01/simple-wxgridgrid-example.html"""
    def __init__(self, img):
        wx.grid.PyGridCellRenderer.__init__(self)
        self.img = img
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        image = wx.MemoryDC()
        image.SelectObject(self.img)
        dc.SetBackgroundMode(wx.SOLID)
        if isSelected:
            dc.SetBrush(wx.Brush(wx.BLUE, wx.SOLID))
            dc.SetPen(wx.Pen(wx.BLUE, 1, wx.SOLID))
        else:
            dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
            dc.SetPen(wx.Pen(wx.WHITE, 1, wx.SOLID))
        dc.DrawRectangleRect(rect)
        width, height = self.img.GetWidth(), self.img.GetHeight()
        if width > rect.width-2:
            width = rect.width-2
        if height > rect.height-2:
            height = rect.height-2
        dc.Blit(rect.x+1, rect.y+1, width, height, image, 0, 0, wx.COPY, True)

class DBExplorer(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "DBExplorer", size=(840,640))

        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        db = gadoDB.GadoDB('gado.db')
        runs = db.getRuns()
        db.closeDB()
        labelRuns = wx.StaticText(self,label="Runs:")
        self.listRuns = wx.Choice(self,choices=[x[0] for x in runs])

        #To store the IDs of the artifacts in the grid
        self.artifactsIds = []
        #Event for the list
        self.listRuns.Bind(wx.EVT_CHOICE,self.runChange)
        
        self.gridArtifacts = wx.grid.Grid(self,size=(820,630))
        self.gridArtifacts.CreateGrid(1,2)
        self.gridArtifacts.SetColLabelValue(0,'Thumbnail')
        self.gridArtifacts.SetColLabelValue(1,'Tags')
        self.gridArtifacts.DisableCellEditControl()
        self.gridArtifacts.DisableDragColMove()
        self.gridArtifacts.DisableDragColSize()
        self.gridArtifacts.DisableDragRowSize()
        

        self.gridArtifacts.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.editCell)


        hsizer1.Add(labelRuns,flag=wx.CENTER)
        hsizer1.Add(self.listRuns)
        hsizer2.Add(self.gridArtifacts, flag=wx.EXPAND, proportion=1)

        #Vertical sizer
        vsizer.Add(hsizer1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vsizer.Add((-1,10))
        vsizer.Add(hsizer2,flag=wx.EXPAND, border=10)
        self.SetSizer(vsizer)

        self.populateList(0)
        self.Show()


    def editCell(self,event):
        print "editCell: (%d,%d)\n" % (event.GetRow(),event.GetCol())
        if event.GetCol() == 1:
            tagsCell = self.gridArtifacts.GetCellValue(event.GetRow(),event.GetCol())
            #print self.artifactsIds[event.GetRow()]
            tagDialog = TagDialog(None,tags=tagsCell,artifact=self.artifactsIds[event.GetRow()])
            tagDialog.ShowModal()
            self.populateList(self.listRuns.GetCurrentSelection())
        if event.GetCol() == 0:
            #Open picture
            db = gadoDB.GadoDB('gado.db')
            artifact = db.getArtifactById(self.artifactsIds[event.GetRow()])
            subprocess.Popen(['xdg-open', artifact[0][1]])
            pass

    def adjustGrid(self,size):
        rows = self.gridArtifacts.GetNumberRows()
        #No need to adjust the grid
        #print str(rows) + ' ' + str(size) 
        if size == rows:
            return
        if rows > size:
            self.gridArtifacts.DeleteRows(size,rows-size)
        else:
            self.gridArtifacts.InsertRows(rows,size-rows)
    def populateList(self,run):
        """ Populates the ListCtrl with the specified run """
        self.gridArtifacts.ClearGrid()
        db = gadoDB.GadoDB('gado.db')
        runs = db.getRuns()
        artifacts = db.getArtifactsByRun(runs[run][0])
        index = 0
        #We reset it every time
        self.artifactsIds = []
        self.adjustGrid(len(artifacts))
        for artifact_id, path, thumb in artifacts:
            tags = db.getTagsByArtifact(artifact_id)
            if not tags:
                tags = ['pictures','other tag']
            img = wx.Bitmap(thumb,wx.BITMAP_TYPE_PNG)
            imageRenderer = MyImageRenderer(img)
            self.gridArtifacts.SetCellRenderer(index,0,imageRenderer)
            self.gridArtifacts.SetReadOnly(index,0,True)
            self.gridArtifacts.SetColSize(index,img.GetWidth()+2)
            self.gridArtifacts.SetRowSize(index,img.GetHeight()+2)

            self.gridArtifacts.SetCellValue(index,1,','.join(tags))
            self.gridArtifacts.SetReadOnly(index,1,True)
            index = index + 1
            #Saving the artifactIds
            self.artifactsIds.append(artifact_id)

        self.gridArtifacts.ForceRefresh()
        self.gridArtifacts.AutoSizeColumn(1)
        self.gridArtifacts.SetRowLabelSize(wx.grid.GRID_AUTOSIZE)

        db.closeDB()

    def runChange(self,event):
        """ We update the ListCtrl every time the user selects a new run """
        self.populateList(event.GetEventObject().GetCurrentSelection())


if __name__ == '__main__':
    app = wx.App()
    frame = DBExplorer()
    app.MainLoop()