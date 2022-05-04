from datetime import datetime

import jenkins
import sys
import json
import os
import logging


class JenkinsConnection:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.connFlag = False

    def startConnection(self):
        try:
            logging.info(str(datetime.now()) + ' connecting to Jenkins server')
            self.__server = jenkins.Jenkins('http://' + self.host, username=self.user, password=self.password, timeout=5)
            self.__user = self.__server.get_whoami()
            self.version = self.__server.get_version()
        except jenkins.TimeoutException:
            print('Jenkins connection timeout')
        else:
            self.connFlag = True
            logging.info(str(datetime.now()) + ' connected to Jenkins server')

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
                logging.info(str(datetime.now()) + ' opening file for saving data')
                f.write(self.output)
                f.close()
                logging.info(str(datetime.now()) + ' file closed')
                return 'File ' + str(fpath) + ' created'
            else:
                return 'File already exits'
        except FileNotFoundError:
            return str(fpath) + ' - Wrong file name'


    def getJobsInfo(self, sort = 'b', fpath = None):
        if sort == 'b' or sort == 'd':
            self.output = []
            self.temp = []
            logging.info(str(datetime.now()) + ' fetching jobs data')
            print('Fetching jobs data')
            self.jobs = self.connection.getServer().get_jobs()
            logging.info(str(datetime.now()) + ' creating output data')
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
        logging.info(str(datetime.now()) + ' counting failed/passed jobs')
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
        logging.info(str(datetime.now()) + ' creating output data')
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
            try:
                self.__jobInfoSaver(fpath)
            except TypeError:
                return 'Fetched job data needed. Call info or provide a file.'
        try:
            if os.path.isfile(fpath) != False:
                logging.info(str(datetime.now()) + ' opening file for counting failed/passed jobs')
                f = open(fpath, 'r')
                JSON = json.load(f)
                f.close()
                return self.__jobsResultCounter(JSON)
        except FileNotFoundError:
            return str(fpath) + ' - Wrong file name'

logging.basicConfig(filename='log.log', level=logging.INFO)
logging.basicConfig(filename='debug.log', level=logging.DEBUG)

host = sys.argv[1]
user = sys.argv[2]
password = sys.argv[3]
'''host = '54.154.29.204:8080'
user = 'gb'
password = 'jennyohjenny'''

print('-----------------Jenkins Job Info Fetcher v1.0')

c = JenkinsConnection(host, user, password)
c.startConnection()
j = JenkinsJobs(c)
print(c.printDetails())
state = True
while state:
    option = None
    sort = None
    fpath = None
    print('''\nWhich path of destiny will you choose young devops apprentice?
Type:
info for fetching Jenkins jobs information
count for counting failed/passed jobs (it needs fetched jobs info - it can be fetched from local file)
exit for exit ;)''')
    option = input('\n')
    match option:
        case 'info':
            print('type b/d for sorting the data by build number or start date - b is default')
            sort = input('\n')
            if len(sort)<1: sort = 'b'
            print('''if you want to save the data to local file, type it\'s path,
otherwise the data will be shown on the screen''')
            fpath = input('\n')
            if len(fpath)<1: fpath = None
            print(j.getJobsInfo(sort = sort, fpath = fpath))
            input('\nHit enter to continue')
        case 'count':
            print('if you want to use data from a file, type it\'s path')
            fpath = input('\n')
            if len(fpath) < 1: fpath = None
            print(j.jobResultPresenter(fpath = fpath))
            input('\nHit enter to continue')
        case 'exit':
            print('''
★─▄█▀▀║░▄█▀▄║▄█▀▄║██▀▄║─★
★─██║▀█║██║█║██║█║██║█║─★
★─▀███▀║▀██▀║▀██▀║███▀║─★
★───────────────────────★
★───▐█▀▄─ ▀▄─▄▀ █▀▀──█───★
★───▐█▀▀▄ ──█── █▀▀──▀───★
★───▐█▄▄▀ ──▀── ▀▀▀──▄───★ ''')
            state = False
        case _:
            print('Przed wyruszeniem w drogę, należy zebrać drużynę')
            input('\nHit enter to continue')
#jobs = j.getJobsInfo(sort='d', fpath='plik.txt')
#print(jobs)

#print(j.jobsResultCounter('plik.txt'))

#print(j.jobResultPresenter())
