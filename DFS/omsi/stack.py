#!/usr/bin/env python3
#
# Copyright (c) 2023 Poul-Henning Kamp <phk@phk.freebsd.dk>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

'''
   OMSI PASCAL stack modelling
   ===========================
'''

class StackItem():

    def __init__(self, width, what):
        self.width = width
        self.what = what

    def __str__(self):
        if self.what is None:
            return "[-%d-]" % self.width
        return str([self.width, self.what])

class StackItemInt(StackItem):
    ''' A 16 bit integer '''
    def __init__(self, val):
        super().__init__(2, "#" + str(val))
        self.val = val

    def __str__(self):
        return "[#%d]" % self.val

class StackItemLong(StackItem):
    ''' A 32 bit integer '''
    def __init__(self, val):
        super().__init__(4, "##" + str(val))
        self.val = val

    def __str__(self):
        return "[##%d]" % self.val

class StackItemBackReference(StackItem):
    ''' A Pointer to something further up the stack '''
    def __init__(self, offset):
        super().__init__(4, "^^" + str(offset))
        self.backref = offset

    def __str__(self):
        return "[^^%d]" % self.backref

class StackItemString(StackItem):
    ''' A String on the stack '''
    def __init__(self, text=None):
        super().__init__(4, "$…")
        self.text = text

    def __str__(self):
        if self.text:
            return "[$$%s]" % self.text
        else:
            return "[$$…]"

class StackItemStringLiteral(StackItem):
    ''' A pushed String Literal '''

    def __str__(self):
        return "[" + str(self.width) + ', "' + self.what + '"]'

class Stack():
    def __init__(self):
        self.items = []

    def push(self, item):
        if item.what is None and self.items and self.items[-1].what == item.what:
            self.items[-1].width += item.width
        else:
            self.items.append(item)

    def pop(self, width):
        while self.items and self.items[-1].width <= width:
            width -= self.items[-1].width
            self.items.pop(-1)
        while width > 0 and self.items:
            last = self.items[-1]
            if last.what is not None:
                last = StackItem(last.width, None)
                self.items[-1] = last
            take = min(last.width, width)
            self.items[-1].width -= take
            if self.items[-1].width == 0:
                self.items.pop(-1)
            width -= take
        if width:
            print("EMPTY POP", width)

    def find(self, offset, width):
        ptr = len(self.items) - 1
        #print("A", offset, width, ptr, self.render())
        while offset > 0 and ptr >= 0:
            sitem = self.items[ptr]
            if sitem.width <= offset:
                ptr -= 1
                offset -= sitem.width
                continue
            break
        #print("B", offset, width, ptr, self.render())
        sitem = self.items[ptr]
        if offset and sitem.width > offset:
            nitem = StackItem(offset, None)
            self.items.insert(ptr + 1, nitem)
            sitem.width -= offset
            offset = 0
        #print("C", offset, width, ptr, self.render())
        if sitem.width == width:
            return ptr, sitem
        while sitem.width < width:
            pitem = self.items[ptr - 1]
            sitem = StackItem(sitem.width + pitem.width, None)
            ptr -= 1
            self.items[ptr] = sitem
            self.items.pop(ptr + 1)
            #print("D", offset, width, ptr, self.render())
        if sitem.width == width:
            return ptr, sitem
        nitem = StackItem(width, None)
        sitem.width -= width
        self.items.insert(ptr + 1, nitem)
        #print("E", offset, width, ptr, self.render())
        return ptr + 1, nitem

    def get(self, offset, width):
        ptr, item = self.find(offset, width)
        #print("I", ptr, item)
        return item

    def put(self, offset, item):
        ptr, _sitem = self.find(offset, item.width)
        self.items[ptr] = item

    def render(self):
        return "{" + "|".join(str(x) for x in self.items) + "}"
