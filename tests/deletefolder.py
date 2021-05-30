from staticker.folder import DBDirectory

def delete():
    dir = DBDirectory()
    dir.del_db()
    dir.del_folder()    
    
if __name__ == '__main__':
    delete()
