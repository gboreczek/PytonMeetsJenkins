from datetime import datetime

import jenkins
import sys
import json
import os


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
        self.output = []

    def sortBuild(joblist):
        return joblist[1]

    def sortDate(joblist):
        return datetime.strptime(joblist[2], '%Y-%m-%d %H:%M:%S')

    def __jobInfoSaver(self, fpath):
        try:
            if os.path.isfile(fpath) == False:
                f = open(fpath, 'w')
                f.write(self.output)
                f.close()
                return 'File ' + str(fpath) + ' created'
            else:
                return 'File already exits'
        except FileNotFoundError:
            return str(fpath) + ' - Wrong file name'


    def getJobsInfo(self, sort = 'b', fpath = None):
        if sort == 'b' or sort == 'd':
            self.output = []
            self.temp = []
            self.jobs = self.connection.getServer().get_jobs()
            for eachJob in self.jobs:
                self.builds = self.connection.getServer().get_job_info(eachJob['name'])
                for eachBuild in self.builds['builds']:
                    self.build = self.connection.getServer().get_build_info(eachJob['name'],int(eachBuild['number']))
                    self.temp.append({'JobName':eachJob['name'],'BuildNumber':eachBuild['number'],
                                      'StartDate':str(datetime.utcfromtimestamp(int(str(self.build['timestamp'])[:10]))),
                                      'StartedBy':self.build['actions'][0]['causes'][0].get('userName'),
                                      'BuildResult':self.build['result']})
                if sort == 'b':
                    #self.temp.sort(reverse=True, key=JenkinsJobs.sortBuild)
                    self.output += sorted(self.temp, reverse=True, key = lambda d: d['BuildNumber'])
                    self.temp.clear()
                if sort == 'd':
                    #self.temp.sort(reverse=True, key=JenkinsJobs.sortDate)
                    self.output += sorted(self.temp, reverse=True, key = lambda d: d['StartDate'])
                    self.temp.clear()
        else:
            return 'Wrong parameter - sort = b for order by build no, sort = d for order by start date, fpath = /path/ ' \
                   'for writing results into a file'
        self.output = json.dumps(self.output, indent=4)
        if fpath == None:
            return self.output
        else:
            return self.__jobInfoSaver(fpath)


    def __jobsResultCounter(self, source):
        jobList = []
        first = True
        jobCounter = 0
        successCounter = 0
        failureCounter = 0
        abortedCounter = 0
        for eachRecord in source:
            try:
                if eachRecord['JobName'] not in jobList[jobCounter - 1]:
                    first = True
            except IndexError:
                placeholder = None
            if first:
                jobList.append({eachRecord['JobName']: eachRecord['BuildNumber'], 'result': eachRecord['BuildResult']})
                jobCounter += 1
                first = False
            if not first and int(jobList[jobCounter - 1][eachRecord['JobName']]) < int(eachRecord['BuildNumber']):
                jobList[jobCounter - 1].update({eachRecord['JobName']: eachRecord['BuildNumber']})
        for eachJob in jobList:
            match eachJob['result']:
                case 'SUCCESS':
                    successCounter += 1
                case 'FAILURE':
                    failureCounter += 1
                case 'ABORTED':
                    abortedCounter += 1
        return str(len(jobList)) + ' jobs total, ' + str(successCounter) + ' was succesful, ' + str(
            failureCounter) + ' was failed, ' + str(abortedCounter) + ' was aborted.'

    def jobResultPresenter(self, fpath = None):
        if fpath == None:
            fpath = str(datetime.timestamp(datetime.now())) + '.txt'
            self.__jobInfoSaver(fpath)
        try:
            if os.path.isfile(fpath) != False:
                f = open(fpath, 'r')
                JSON = json.load(f)
                f.close()
                return self.__jobsResultCounter(JSON)
        except FileNotFoundError:
            return str(fpath) + ' - Wrong file name'


'''host = sys.argv[1]
user = sys.argv[2]
password = sys.argv[3]'''
host = '54.154.29.204:8080'
user = 'gb'
password = 'jennyohjenny'

c = JenkinsConnection(host, user, password)
c.startConnection()
print(c.printDetails())

j = JenkinsJobs(c)
j.getJobsInfo()
#jobs = j.getJobsInfo(sort='d', fpath='plik.txt')
#print(jobs)

#print(j.jobsResultCounter('plik.txt'))

print(j.jobResultPresenter())
