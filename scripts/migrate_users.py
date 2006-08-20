#!/usr/bin/python

from conary.repository.netrepos.netserver import ServerConfig
from conary import dbstore

cnrPath ='/srv/conary/repository.cnr'
cfg = ServerConfig()
cfg.read(cnrPath)

db = dbstore.connect(cfg.repositoryDB[1], cfg.repositoryDB[0])
cu = db.cursor()
cu.execute("""UPDATE Permissions SET canRemove=1 WHERE userGroupId IN 
              (SELECT userGroupId FROM userGroups WHERE canMirror=1)""")
db.commit()
db.close()
