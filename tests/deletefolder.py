from staticker.folder import DBDirectory

def delete_folder():
    dir = DBDirectory()
    dir.del_folder()    
    
if __name__ == '__main__':
    delete_folder()
