# coding=utf8

import copy, os
import wx._core as wx
import blogtrans
from wx.html import HtmlWindow

from BlogTreeCtrl import BlogTreeCtrl
from BlogHtmlCtrl import BlogHtmlWindow
from ProgressDialog import *

from blogtrans.data import *
from blogtrans.wretch.WretchImporter import WretchImporter
from blogtrans.mt import *

from blogtrans.blogger.BloggerExporter import *
from blogtrans.blogger.BloggerImporter import *

from blogtrans.ui.BlogHtmlCtrl import CommentToHTML


ID_IMPORT_WRETCH = wx.NewId()
ID_IMPORT_BLOGGER = wx.NewId()
ID_IMPORT_MT = wx.NewId()

ID_EXPORT_BLOGGER = wx.NewId()
ID_EXPORT_MT = wx.NewId()

ID_TOOL_COMBINE_COMMENT = wx.NewId()


class MainWindow(wx.Frame):

    def __init_menubar(self) :

        #Todo: use a smarter way to manage menu...
        import_menu = wx.Menu()

        import_menu.Append(ID_IMPORT_WRETCH, u"無名XML檔案(&W)...",u"匯入無名XML檔案")
        wx.EVT_MENU(self, ID_IMPORT_WRETCH, self.OnImportWretch)

        # import_menu.Append(ID_IMPORT_BLOGGER, u"Blogger Atom XML(&B)...",u"匯入Blogger Atom XML")
        # wx.EVT_MENU(self, ID_IMPORT_BLOGGER, self.OnImportBlogger)

        import_menu.Append(ID_IMPORT_MT, u"&MT檔案...",u"匯入MT Import檔案")
        wx.EVT_MENU(self, ID_IMPORT_MT, self.OnImportMT)

        export_menu = wx.Menu()
        export_menu.Append(ID_EXPORT_BLOGGER, u"Blogger Atom XML(&B)...",u"匯出至Blogger Atom XML")
        wx.EVT_MENU(self, ID_EXPORT_BLOGGER, self.OnExportBlogger)

        export_menu.Append(ID_EXPORT_MT, u"&MT檔案...",u"匯出至MT檔案")
        wx.EVT_MENU(self, ID_EXPORT_MT, self.OnExportMT)

        tool_menu = wx.Menu()
        tool_menu.Append(ID_TOOL_COMBINE_COMMENT, u"結合留言至文章", u"結合留言至文章")
        wx.EVT_MENU(self, ID_TOOL_COMBINE_COMMENT, self.OnCombineComment)

        menuBar = wx.MenuBar()
        menuBar.Append(import_menu,u"匯入(&I)")
        menuBar.Append(export_menu,u"匯出(&E)")
        menuBar.Append(tool_menu,u"工具(&T)")

        self.SetMenuBar(menuBar)

    def __init__(self) :
        wx.Frame.__init__(self, None, wx.ID_ANY, u'BlogTrans 部落格搬家工具 ' + blogtrans.VERSION, size=(800,600))

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.treectrl = BlogTreeCtrl(self)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.treectrl)

        self.html = BlogHtmlWindow(self)

        self.sizer.Add(self.treectrl,1,wx.EXPAND)
        self.sizer.Add(self.html,2,wx.EXPAND)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)

        self.__init_menubar()
        self.CreateStatusBar()

        self.Show(True)
        #self.setBlogData( self.genTestData() )

    # TODO: Bad design here, takes O(n^2) time complexity....
    def GetCheckedBlogData(self) :
        checked = self.treectrl.GetAllCheckedData()

        data = BlogData()
        comment_count = 0

        for article in self.blogdata.articles :
            if article in checked :
                a = copy.deepcopy(article)
                data.articles.append(a)
                a.comments = []

            for comment in article.comments :
                if comment in checked :
                    a.comments.append(comment)
                    comment_count += 1

        return data

    def setBlogData(self, blogdata) :
        self.blogdata = blogdata
        self.treectrl.setBlogData(blogdata)

    def genTestData(self) :
        blogdata = BlogData()

        a = Article()
        a.author = "TestAuthor"
        a.title = "TestArticle"
        a.date = datetime.today()
        a.category = ["TestCategory"]
        a.status = Article.PUBLISH
        a.allow_comments = True
        a.allow_pings = True
        a.body = "TestArticleBody\n"
        a.extended_body = "TestArticleExtendedBody"
        a.excerpt = ""
        a.comments = []
        a.pings = []

        for i in range(0,2) :
            c = Comment()
            c.author = "Comment user %i " % i
            c.email = "user%i@gggggmail.com" % i
            c.url = "http://www.url%d.com" % i
            c.ip = "127.0.0.1"
            c.date = datetime.today()
            c.body = "Comment body %i" % i
            a.comments.append(c)

        blogdata.articles.append(a)

        return blogdata

    #Todo: lots of dumb code in callbacks, need refactoring
    def OnImportWretch(self, e) :
        dialog = wx.FileDialog(self)
        result = dialog.ShowModal()
        dialog.Destroy()
        if result != wx.ID_OK :
            return

        file = dialog.GetFilename()
        dir = dialog.GetDirectory()
        filename = os.path.join(dir, file)

        wi = WretchImporter(filename)
        blogdata = wi.parse()
        self.setBlogData(blogdata)

    def OnImportMT(self, e) :
        dialog = wx.FileDialog(self)
        result = dialog.ShowModal()
        dialog.Destroy()
        if result != wx.ID_OK :
            return
        file = dialog.GetFilename()
        dir = dialog.GetDirectory()
        filename = os.path.join(dir, file)

        mi = MTImporter(filename)
        blogdata = mi.parse()
        self.setBlogData(blogdata)

    def OnExportMT(self, e) :
        checked_data = self.GetCheckedBlogData()
        dialog = wx.FileDialog(self, style=wx.SAVE|wx.OVERWRITE_PROMPT)
        result = dialog.ShowModal()
        dialog.Destroy()
        if result != wx.ID_OK :
            return

        file = dialog.GetFilename()
        dir = dialog.GetDirectory()
        filename = os.path.join(dir, file)

        me = MTExporter(filename, checked_data)
        me.Export()

    def OnExportBlogger(self, e) :
        checked_data = self.GetCheckedBlogData()

        dialog = wx.TextEntryDialog(self, "http://BloggerID.blogspot.tw", "Blogger ID", "changyy")
        result = dialog.ShowModal()
        dialog.Destroy()
        if result != wx.ID_OK :
            return
        target_blogger_id = dialog.GetValue()

        dialog = wx.TextEntryDialog(self, "Author", "Author", "Yuan-Yi Chang")
        result = dialog.ShowModal()
        dialog.Destroy()
        if result != wx.ID_OK :
            return
        target_author = dialog.GetValue()

        dialog = wx.NumberEntryDialog(self, "Article Begin Number", "Begin Number:", "Article Begin Number", 1, 1, 99999999)
        result = dialog.ShowModal()
        dialog.Destroy()
        if result != wx.ID_OK :
            return
        target_aid_begin = dialog.GetValue()

        dialog = wx.NumberEntryDialog(self, "Article End Number", "End Number:", "Article End Number", 99999, 1, 99999999)
        result = dialog.ShowModal()
        dialog.Destroy()
        if result != wx.ID_OK :
            return
        target_aid_end = dialog.GetValue()

        dialog = wx.MessageDialog(self, "Skip all Comments ?", "remove all comment:", wx.YES_NO | wx.NO_DEFAULT)
        result = dialog.ShowModal()
        dialog.Destroy()
        if result == wx.ID_NO:
             target_skip_comment = False
        else:
             target_skip_comment = True

        dialog = wx.FileDialog(self, style=wx.SAVE|wx.OVERWRITE_PROMPT)
        result = dialog.ShowModal()
        dialog.Destroy()
        if result != wx.ID_OK :
            return

        file = dialog.GetFilename()
        dir = dialog.GetDirectory()
        filename = os.path.join(dir, file)

        me = BloggerExporter(filename, checked_data, target_blogger_id, target_author, target_aid_begin, target_aid_end, target_skip_comment)
        me.Export()

    def OnImportBlogger(self, e) :
        dialog = wx.FileDialog(self)
        result = dialog.ShowModal()
        dialog.Destroy()
        if result != wx.ID_OK :
            return
        file = dialog.GetFilename()
        dir = dialog.GetDirectory()
        filename = os.path.join(dir, file)

        mi = BloggerImporter(filename)
        blogdata = mi.parse()
        self.setBlogData(blogdata)


    def OnCombineComment(self, e) :
        for a in self.blogdata.articles :
            if len(a.comments) :
                comment_htmls = map(CommentToHTML, a.comments)
                a.extended_body += "<hr/>" + "<br><br><br><br><hr/>".join(comment_htmls)
            a.comments = []
        self.setBlogData(self.blogdata)

    def OnSelChanged(self, e) :
        # Tofix:  seems a sync problem here
        data = e.GetItem().GetData()
        # print data.__class__
        if data.__class__ == Article :
            self.html.ShowArticle(data)
        elif data.__class__ == Comment :
            self.html.ShowComment(data)
        else :
            self.html.SetPage("")

