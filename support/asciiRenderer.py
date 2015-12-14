# -*- coding: utf-8 -*-
#

import abstractRenderer
import codecs
import os

#
#   Simplest renderer. Ignores everything except ascii text.
#

class Renderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputDir, outputName):
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName)
        # Unset
        self.f = None  # output file stream
        # IO
        self.outputFilename = os.path.join(outputDir, outputName + '.txt')
        self.inputDir = inputDir
        # Flags
        self.d = False
        self.narrower = False
        self.inFootnote = False
        self.inX = False
        
    def render(self):
        self.f = codecs.open(self.outputFilename, 'w', 'ascii')
        self.loadUSFM(self.inputDir)
        self.run()
        self.f.close()
        
    # Support
    
    def startNarrower(self, n):
        s = u'\n'
        if not self.narrower: s = s + u'\n'
        self.narrower = True
        return s + u'    ' * n

    def stopNarrower(self):
        self.narrower = False
        return u''

    def startD(self):
        self.d = True
        return u''

    def stopD(self):
        self.d = False
        return u''
        
    def escape(self, text):
        if self.inX or self.inFootnote:
            return u''
        t = text.replace(u'‘', u"'")
        t = t.replace(u'’', u"'")
        t = t.replace(u'“', u'"')
        t = t.replace(u'”', u'"')
        t = t.encode('ascii', 'ignore')
        return t
        
    # Tokens
                    
    def render_h(self, token):       self.f.write(u'\n\n\n### ' + token.value + u' ###\n\n\n')
    def renderMS2(self, token):     self.f.write(u'\n\n[' + token.value + u']\n\n')
    def render_p(self, token):       self.f.write(self.stopD() + self.stopNarrower() + u'\n\n    ')
    def render_b(self, token):       self.f.write(self.stopD() + self.stopNarrower() + u'\n\n    ')
    def render_s1(self, token):       self.f.write(self.stopD() + self.stopNarrower() + u'\n\n    ')
    def render_s2(self, token):      self.f.write(self.stopD() + self.stopNarrower() + u'\n\n    ')
    def render_c(self, token):       self.f.write(u' ' )
    def render_v(self, token):       self.f.write(u' ' )
    def render_text(self, token):    self.f.write(self.escape(token.value))
    def render_q(self, token):       self.f.write(self.stopD() + self.startNarrower(1))
    def render_q1(self, token):      self.f.write(self.stopD() + self.startNarrower(1))
    def render_q2(self, token):      self.f.write(self.stopD() + self.startNarrower(2))
    def render_q3(self, token):      self.f.write(self.stopD() + self.startNarrower(3))
    def render_nb(self, token):      self.f.write(self.stopD() + self.stopNarrower() + u"\n\n")
    def render_li(self, token):      self.f.write(u' ')
    def render_d(self, token):       self.f.write(self.startD())
    def render_sp(self, token):      self.f.write(self.startD())
    def render_nd_e(self, token):     self.f.write(u' ')
    def render_pbr(self, token):     self.f.write(u'\n')
    
    # Ignore...
    def render_x_s(self,token):       self.inX = True
    def render_x_e(self,token):       self.inX = False
    def render_f_s(self,token):       self.inFootnote = True
    def render_f_e(self,token):       self.inFootnote = False
            