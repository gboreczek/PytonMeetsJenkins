import jenkins, sys
from datetime import datetime

class JenkinsConnection:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.connFlag = False

    def startConnection(self):
        try:
            self.__server = jenkins.Jenkins('http://' + self.host, username=self.user, password=self.password, timeout=5)
            self.__user = self.__server.get_whoami()
            self.version = self.__server.get_version()
        except jenkins.TimeoutException:
            print('Jenkins connection timeout')
        else:
            self.connFlag = True

    def getServer(self):
        return self.__server

    def getUser(self):
        return self.__user

    def printDetails(self):
        if self.connFlag:
            return ('User %s logged to Jenkins v.%s' % (self.__user['fullName'], self.version))
        else:
            return 'No connection'

class JenkinsJobs:
    def __init__(self, connection):
        self.connection = connection

    def getJobsInfo(self):
        self.output = []
        self.jobs = self.connection.getServer().get_jobs()
        for eachJob in self.jobs:
            self.builds = self.connection.getServer().get_job_info(eachJob['name'])
            for eachBuild in self.builds['builds']:
                self.build = self.connection.getServer().get_build_info(eachJob['name'],int(eachBuild['number']))
                self.output.append((eachJob['name'],eachBuild['number'],str(datetime.utcfromtimestamp(int(str(self.build['timestamp'])[:10]))),self.build['actions'][0]['causes'][0].get('userName'),self.build['result']))
        return self.output


host = sys.argv[1]
user = sys.argv[2]
password = sys.argv[3]
'''host = '54.246.249.61:8080'
user = 'gb'
password = 'jennyohjenny'''

c = JenkinsConnection(host, user, password)
c.startConnection()
print(c.printDetails())

j = JenkinsJobs(c)
jobs = j.getJobsInfo()

for each in jobs:
    print(each)

