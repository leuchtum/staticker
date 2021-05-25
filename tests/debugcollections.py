from staticker.collections import PlayerCollection

pc = PlayerCollection()
pc.load_all(sort_by="name")
names = pc.get_names()

print("finished")