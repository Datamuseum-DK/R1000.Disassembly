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
    ''' An item on the stack '''
    def __init__(self, width, what):
        self.width = width
        self.what = what
        self.stack = None

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

    def resolve(self):
        idx = self.stack.items.index(self) - 1
        sitem = self.stack.items[idx]
        walk = self.backref
        while walk > 0 and idx >= 0:
            walk -= sitem.width
            idx -= 1
            sitem = self.stack.items[idx]
        if not walk:
            return sitem
        print("BACKREF residual", walk, self.stack.render(), self)
        return None

class StackItemString(StackItem):
    ''' A String on the stack '''
    def __init__(self, text=None):
        super().__init__(4, "$…")
        self.text = text

    def __str__(self):
        if self.text:
            return "[$$%s]" % self.text
        return "[$$…]"

class StackItemBlob(StackItem):
    ''' A pushed object '''

    def __init__(self, blob=None, width=None, src=None):
        if blob:
            width = len(blob)
        super().__init__(width, "**(%d)**" % width)
        self.blob = blob
        self.src = src

    def __str__(self):
        if not self.blob:
            return '[«' + str(self.width) + '»]'
        txt = ''
        for i in self.blob:
            if 32 <= i <= 126 and i != 92:
                txt += "%c" % i
            else:
                txt += "\\x%02x" % i
        return '[«%d"' % self.width + txt + '"»]'

    def __getitem__(self, idx):
        if self.blob:
            return self.blob[idx]
        return None

class StackItemStringLiteral(StackItem):
    ''' A pushed String Literal '''

    def __str__(self):
        return "[" + str(self.width) + ', "' + self.what + '"]'

class Stack():
    ''' A model of the stack '''
    def __init__(self):
        self.items = []
        self.mangled = False

    def push(self, item):
        ''' Push an item onto the stack '''
        if self.mangled:
            return
        assert isinstance(item.width, int)
        item.stack = self
        if item.what is None and self.items and self.items[-1].what == item.what:
            self.items[-1].width += item.width
        else:
            self.items.append(item)

    def pop(self, width):
        ''' Push width worth of items off the stack '''
        if self.mangled:
            return
        while self.items and self.items[-1].width <= width:
            width -= self.items[-1].width
            self.items.pop(-1)
        while width > 0 and self.items:
            last = self.items[-1]
            if last.what is not None:
                last = StackItem(last.width, None)
                last.stack = self
                self.items[-1] = last
            take = min(last.width, width)
            self.items[-1].width -= take
            if self.items[-1].width == 0:
                self.items.pop(-1)
            width -= take
        if width:
            print("EMPTY POP", width)
            self.mangled = True

    def find(self, offset, width):
        ''' Find item on stack, rearrange if necessary '''
        if self.mangled:
            return 0, None
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
        if ptr < 0:
            return 0, None
        sitem = self.items[ptr]
        if offset and sitem.width > offset:
            nitem = StackItem(offset, None)
            nitem.stack = self
            self.items.insert(ptr + 1, nitem)
            sitem.width -= offset
            offset = 0
        #print("C", offset, width, ptr, self.render())
        if sitem.width == width:
            return ptr, sitem
        while sitem.width < width:
            pitem = self.items[ptr - 1]
            sitem = StackItem(sitem.width + pitem.width, None)
            sitem.stack = self
            ptr -= 1
            self.items[ptr] = sitem
            self.items.pop(ptr + 1)
            #print("D", offset, width, ptr, self.render())
        if sitem.width == width:
            return ptr, sitem
        nitem = StackItem(width, None)
        nitem.stack = self
        sitem.width -= width
        self.items.insert(ptr + 1, nitem)
        #print("E", offset, width, ptr, self.render())
        return ptr + 1, nitem

    def get(self, offset, width):
        ''' Get width item at offset '''
        _ptr, item = self.find(offset, width)
        return item

    def put(self, offset, item):
        ''' Put item at offset '''
        ptr, sitem = self.find(offset, item.width)
        if sitem is not None:
            self.items[ptr] = item
        elif not self.mangled:
            print("BAD PUT", offset, item, self.render())
            self.mangled = True

    def render(self):
        ''' Render stack image '''
        if self.mangled:
            return "{MANGLED}"
        return "{" + "|".join(str(x) for x in self.items) + "}"
