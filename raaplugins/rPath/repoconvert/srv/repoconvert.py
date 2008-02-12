#
# Copyright (C) 2006 rPath, Inc.
# All rights reserved
#

import raa.lib.command
from raa import rpath_error
from raa.constants import *
from raa.modules.raasrvplugin import rAASrvPlugin
from conary import dbstore
from conary.lib import util
from conary.repository.netrepos.netserver import ServerConfig
import pgsql
import os, subprocess, select

import time
import logging
log = logging.getLogger('raa.service')

class ConversionError(rpath_error.ConfigurationError):
    def __str__(self):
        return self.msg

class PreparationError(rpath_error.ConfigurationError):
    def __str__(self):
        return self.msg

def _startPostgresql():
    while True:
        count = 0
        started = False
        try:
            dbm = dbstore.connect('postgres@localhost.localdomain/template1', 'postgresql')
        except pgsql.ProgrammingError, e:
            log.warning("PostgreSQL was not running, attempting to start it")
            try:
                raa.lib.command.runCommand(['/sbin/service', 'postgresql', 'start'], close_fds=True)
            except PreparationError, e:
                log.error("An error occured when attempting to start the PostgreSQL service")
                raise
            else:
                started = True
            # Bail if we've tried more than 8 times already
            if started and count > 8:
                raise PreparationError("Unable to connect to PostgreSQL service after approximately 30 seconds" % count)
            time.sleep(4) #Don't spin loop here
            count = count + 1
        else:
            break
    return True

class reportList(list):
    MAX = 5
    def append(self, item):
        if len(self) == self.MAX:
            self.pop(0)
        list.append(self, item)

class reportCallback:
    _msgs = None
    _lastreport = 0

    def __init__(self, serverplg, execId):
        self._sp = serverplg
        self._execId = execId
        self._msgs = reportList()

    def _report(self):
        self._lastreport = time.time()
        self._sp.reportMessage(self._execId, '\n'.join(self._msgs))
        self._msgs = reportList()

    def addMessage(self, msg):
        self._msgs.append(msg)
        elapsedTime = time.time() - self._lastreport
        if len(self._msgs) >= 5 and elapsedTime > 3:
            self._report()

    def flush(self):
        if len(self._msgs) > 0:
            self._report()


class SqliteToPgsql(rAASrvPlugin):
    #convertScript = '/usr/share/conary/migration/db2db.py'
    convertScript = '/home/jtate/hg/conary-2.0/scripts/migration/db2db.py'
    cfgPath       = '/srv/conary/repository.cnr'
    newCfgPath    = '/srv/conary/config/50_repositorydb.cnr'

    def _runScriptAndReportOutput(self, execId, cmd, messagePrefix = '', reportClass = reportCallback):
        env = os.environ
        env.update(dict(LANG="C"))
        poller = select.poll()

        po = subprocess.Popen(cmd, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        poller.register(po.stdout.fileno(), select.POLLIN)
        poller.register(po.stderr.fileno(), select.POLLIN)
        stdoutReader = util.LineReader(po.stdout.fileno())
        stderrReader = util.LineReader(po.stderr.fileno())

        count = 2
        reporter = reportClass(self, execId)
        while count:
            fds = [ x[0] for x in poller.poll() ]
            for (fd, reader, isError) in (
                        (po.stdout.fileno(), stdoutReader, False),
                        (po.stderr.fileno(), stderrReader, True) ):
                if fd not in fds: continue
                lines = reader.readlines()

                if lines == None:
                    poller.unregister(fd)
                    count -= 1
                else:
                    for l in lines:
                        #Report the last five lines to the frontend
                        line = l.strip()
                        reporter.addMessage(line)
                        if isError:
                            log.error('%s%s' % (messagePrefix, line))
                        else:
                            log.info('%s%s' % (messagePrefix, line))
        rc = po.wait()
        reporter.flush()
        return rc

    def _runConversion(self, execId):
        cmd = [self.convertScript, '--sqlite=/srv/conary/sqldb', '--postgresql=updateservice@localhost.localdomain/updateservice']
        # Capture the output
        rc = self._runScriptAndReportOutput(execId, cmd,
                messagePrefix='Conary PostgreSQL Conversion: ',
                reportClass=reportCallback)
        if rc:
            raise ConversionError("Error running conversion script, returned %d" % rc)
        else:
            self.reportMessage(execId, 'Conversion completed successfully')

    def _saveRepositoryDbPath(self):
        cfg = ServerConfig()
        cfg.read(self.cfgPath)

        f = open(self.newCfgPath, 'w')
        cfg.repositoryDB = ('postgresql', 'updateservice@localhost.localdomain/updateservice')

        cfg.displayKey('repositoryDB', out=f)
        f.close()

    def doTask(self, schedId, execId):
        '''
        '''
        #shut down httpd
        self.reportMessage(execId, "Shutting down httpd")
        raa.lib.command.runCommand(['/sbin/service', 'httpd', 'stop'])

        # Check to see if we can talk to the server, and start it if necessary
        self.reportMessage(execId, "Checking that PostgreSQL is running, and if not, starting it")
        _startPostgresql()

        #ASSUMPTION: there is a database created already with a user named updateservice
        db = dbstore.connect('updateservice@localhost.localdomain/updateservice', 'postgresql')
        cu = db.cursor()
        cu.execute("select count(lanname) from pg_catalog.pg_language where lanname='plpgsql'")
        if not cu.fetchone()[0]:
            raise PreparationError('plpgsql not available in the updateservice database')

        #Run the conversion script
        self.reportMessage(execId, "Running database conversion script")
        #self._runConversion(execId)

        #restart httpd
        self.reportMessage(execId, "Starting httpd")
        raa.lib.command.runCommand(['/sbin/service', 'httpd', 'start'])

        #Save the new repository setting
        self._saveRepositoryDbPath()

