from kivymd.app import MDApp
from kivymd.toast import toast
from kivy.core.window import Window
from kivymd.uix.filemanager import MDFileManager
from kivy.utils import platform
from kivy.properties import StringProperty
import os, marshal ,base64, py_compile

if platform == 'android':
    from android.permissions import (
        Permission,
        request_permission,
        check_permission
    )

class hashing:
    A = '#!/usr/bin/python3 -B\n'
    def __init__(self,path,app):
        self.path = path
        self.app = app
        self.check = self.check_type()

    def check_type(self):
        if os.path.isdir(self.path):
            return 'dir'
        elif os.path.isfile(self.path):
            return 'file'
        return None

    def get_files(self):
        for d,r,f in os.walk(self.path):
            for i in f:
                if os.path.join(d,i).endswith('.py'):
                    yield os.path.join(d,i)

    def md5(self):
        def encode(path):
            with open(path,'rb') as f:
                rb_file = base64.b16encode(f.read())
            with open(path,'w') as f:
                f.write(f"{self.A}import base64 as b\ndata = lambda x: x({rb_file})\nexec (compile(data(b.b16decode),'<string>','exec'))")
        if self.check == 'file':
            encode(self.path)
        elif self.check == 'dir':
            for i in self.get_files():
                encode(i)
        toast('Done')
        self.app.path = ''

    def marshal(self):
        def encode(path):
            with open(path,'r') as f:
                r_file = compile(f.read(),'string','exec')
                r_file = marshal.dumps(r_file)
            with open(path,'w') as f:
                f.write(f"{self.A}import marshal as m\ndata = m.loads({r_file})\nexec (data)")
        if self.check == 'file':
            encode(self.path)
        else:
            for i in self.get_files():
                encode(i)
        toast('Done')
        self.app.path = ''

    def pyc(self):
        def encode(source_path):
            basename = source_path[:-3]
            bytecode_path = "%s.pyc" % (basename)
            py_compile.compile(source_path, bytecode_path, "exec")
            os.remove(source_path)
            return bytecode_path
        if self.check == 'file':
            encode(self.path)
        elif self.check == 'dir':
            for i in self.get_files():
                encode(i)
        toast('Done')
        self.app.path = ''

class MDFileManager(MDFileManager):
    def get_content(self, path):
        """Returns a list of the type [[Folder List], [file list]]."""
        try:
            files = []
            dirs = []

            if self.history_flag:
                self.history.append(path)
            if not self.history_flag:
                self.history_flag = True

            for _path,_dirs,_files in os.walk(path):
                dirs += _dirs
                files += [f for f in _files if f.endswith('.py')]
                break
            return sorted(dirs), sorted(files)

        except OSError:
            self.history.pop()
            return None, None

class HashApp(MDApp):
    path = StringProperty('')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,

        )

    def get_permission(self):
        if platform == 'android':
            PE = Permission.WRITE_EXTERNAL_STORAGE
            if (status := check_permission(PE)):
                return status
            else:
                request_permission(PE)
                return None
            return check_permission(PE)
        else : return True

    def file_manager_open(self):
        state = self.get_permission()
        path = '/sdcard' if platform == 'android' else '/home/mohamed'
        path = self.path if self.path != '' or self.path == path else path
        if state == True:
            self.file_manager.show(path)  # output manager to the screen
            self.manager_open = True
        elif state == None:
            pass
        else:
            toast('No Permission')

    def select_path(self, path):
        '''It will be called when you click on the file name
        or the catalog selection button.

        :type path: str;
        :param path: path to the selected directory or file;
        '''

        self.exit_manager()
        self.path = path

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

if __name__ == '__main__':
    HashApp().run()