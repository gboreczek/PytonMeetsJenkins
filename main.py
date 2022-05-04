from datetime import datetime

import jenkins
import sys
import json


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

    def sortBuild(joblist):
        return joblist[1]

    def sortDate(joblist):
        return datetime.strptime(joblist[2], '%Y-%m-%d %H:%M:%S')

    def getJobsInfo(self, sort = 'b'):
        if sort == 'b' or sort == 'd':
            self.output = []
            self.temp = []
            self.jobs = self.connection.getServer().get_jobs()
            for eachJob in self.jobs:
                self.builds = self.connection.getServer().get_job_info(eachJob['name'])
                for eachBuild in self.builds['builds']:
                    self.build = self.connection.getServer().get_build_info(eachJob['name'],int(eachBuild['number']))
                    self.temp.append({'JobName':eachJob['name'],'BuildNumber':eachBuild['number'],'StartDate':str(datetime.utcfromtimestamp(int(str(self.build['timestamp'])[:10]))),'StartedBy':self.build['actions'][0]['causes'][0].get('userName'),'BuildResult':self.build['result']})
                if sort == 'b':
                    #self.temp.sort(reverse=True, key=JenkinsJobs.sortBuild)
                    self.output += sorted(self.temp, reverse=True, key = lambda d: d['BuildNumber'])
                    self.temp.clear()
                if sort == 'd':
                    #self.temp.sort(reverse=True, key=JenkinsJobs.sortDate)
                    self.output += sorted(self.temp, reverse=True, key = lambda d: d['StartDate'])
                    self.temp.clear()
        else:
            return 'Wrong parameter'
        self.output = json.dumps(self.output, indent=4)
        return self.output


host = sys.argv[1]
user = sys.argv[2]
password = sys.argv[3]
'''host = '34.241.236.151:8080'
user = 'gb'
password = 'jennyohjenny'''''

c = JenkinsConnection(host, user, password)
c.startConnection()
print(c.printDetails())

j = JenkinsJobs(c)
jobs = j.getJobsInfo(sort='d')

#print(jobs[0][1])

'''
def sortBuild(joblist):
    return joblist[1]

def sortDate(joblist):
    return datetime.strptime(joblist[2], '%Y-%m-%d %H:%M:%S')
'''
#jobs.sort(reverse=True, key=sortBuild)

#jobs.sort(reverse=True, key=sortDate)

'''for each in jobs:
    print(each)'''
print(jobs)

