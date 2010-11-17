#!/usr/bin/env python
import xmlrpclib
import git
import getpass
import sys
import re
import tempfile
import subprocess
import shutil

#### configuration ####
commit_start = "48e477f4c1d9" # hash of version used on last release notes
commit_end = "HEAD" # current hash
branch = "master" # git branch to be used
release_name = "1.6" 
clonepath = None # set this to the complete path of a vistrails clone to be used
                 # if None, the remote repository will be cloned to a temporary
                 # folder and removed at the end of the script
cloneremote = 'git://vistrails.sci.utah.edu/vistrails.git'
#### end configuration #####

## The script will ask for your Trac user and password
## so no need to change this now
username = None
password = None
need_cleanup = False

################################################################################
def userpass(realm, u, may_save):
    global username
    global password
    if not username:
        print "Username:",
        sys.stdout.flush()
        username = raw_input()
        password = getpass.getpass()
    return True, username, password, False

################################################################################

def clone_vistrails_git_repository(path_to):
    global cloneremote
    cmdlist = ['git', 'clone', cloneremote,
               path_to]
    cmdline = subprocess.list2cmdline(cmdlist)
    print "Cloning vistrails from:"
    print "  %s to"%cloneremote
    print "  %s"%path_to
    print "Be patient. This may take a while."
    process = subprocess.Popen(cmdline, shell=True,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               close_fds=True)
    result = None
    while result == None:
        result = process.poll()
    print "repository is cloned."
    return result

################################################################################

def init_repo():
    global clonepath, need_cleanup, branch
    ok = True
    if clonepath is None:
        clonepath = tempfile.mkdtemp(prefix="vtrel")
        try:
            if clone_vistrails_git_repository(clonepath) == 0:
                ok = True
            need_cleanup = True
        except Exception, e:
            print "ERROR: Could not clone vistrails repository!"
            print str(e)
            shutil.rmtree(clonepath)
            sys.exit(1)
    if ok:
        repo = git.Repo(clonepath)
        return repo
    else:
        print "ERROR: git clone failed."
        sys.exit(1)
################################################################################

def cleanup_repo():
    global clonepath, need_cleanup
    if need_cleanup:
        shutil.rmtree(clonepath)
        
################################################################################

def checkout_branch(repo, branch):
    repobranch = getattr(repo.heads, branch)
    repobranch.checkout()

##############################################################################
def build_release_notes(repo, branch):
    global username
    global password
    global commit_start, commit_end
    
    def check_inside_skip(skip_list, message):
        found = False
        for s in skip_list:
            if s.find(message) != -1:
                found = True
                break
        return found
    
    re_ticket = re.compile(r'<ticket>(.*?)</ticket>', re.M | re.S)
    re_bugfix = re.compile(r'<bugfix>(.*?)</bugfix>', re.M | re.S)
    re_feature = re.compile(r'<feature>(.*?)</feature>', re.M | re.S)
    re_skip = re.compile(r'<skip>(.*?)</skip>', re.M | re.S)

    #build list and dictionary with commits
    logs = []
    log_map_time = {}
    checkout_branch(repo,branch)
    for c in repo.iter_commits("%s..%s"%(commit_start,commit_end)):
        logs.append(c)
        log_map_time[c.hexsha] = c.committed_date
        
    #populate dictionaries
    bugfixes = {}
    tickets = {}
    features = {}
    changes = {}
    ticket_info = {}
    
    for log in logs:
        ls = re_skip.findall(log.message)
        lf = re_feature.findall(log.message)
        lt = re_ticket.findall(log.message)
        lb = re_bugfix.findall(log.message)
        if len(ls) > 0:
            changes[log.hexsha] = []
            for s in ls:
                changes[log.hexsha].append(s)
        if len(lf) > 0:
            features[log.hexsha] = []
            for f in lf:
                if not check_inside_skip(ls,f):
                    features[log.hexsha].append(f)
        if len(lt) > 0:
            tickets[log.hexsha] = []
            for t in lt:
                if not check_inside_skip(ls,t):
                    tickets[log.hexsha].append(t)
        if len(lb) > 0:
            bugfixes[log.hexsha] = []
            for b in lb:
                if not check_inside_skip(ls,b):
                    bugfixes[log.hexsha].append(b)
        if len(ls) == 0 and len(lf) == 0 and len(lt) == 0 and len(lb) == 0:
            if not changes.has_key(log.hexsha):
                changes[log.hexsha] = []
            changes[log.hexsha].append(log.message)
                

    #get ticket summaries from xmlrpc plugin installed on vistrails trac
    print "Will connect to VisTrails Trac with authentication..."
    if not username:
        print "Username:",
        sys.stdout.flush()
        username = raw_input()
        password = getpass.getpass()

    url = "https://%s:%s@vistrails.sci.utah.edu/login/xmlrpc"%(username,
                                                               password)
    server = xmlrpclib.ServerProxy(url)
    print "downloading tickets.",
    for (r,tl) in tickets.iteritems():
        print ".",
        sys.stdout.flush()
        for t in tl:
            if not ticket_info.has_key(t):
                try:
                    tid = int(t[1:])
                    ticket_info[t] = server.ticket.get(tid)
                except Exception, e:
                    tickets[r].remove(t)
                    print "commit %s: Could not get info for ticket %s"%(r,t)
    print "done."

    #place tickets on bugfixes or enhancements
    for (r,tlist) in tickets.iteritems():
        for t in tlist:
            txt = "Ticket %s: %s"%(t,ticket_info[t][3]['summary'])
            if ticket_info[t][3]['type'] == 'enhancement':
                if features.has_key(r):
                    features[r].insert(0,txt)
                else:
                    features[r] = [txt]
            elif ticket_info[t][3]['type'] == 'defect':
                if bugfixes.has_key(r):
                    bugfixes[r].insert(0,txt)
                else:
                    bugfixes[r] = [txt]
            else:
                #put the rest as changes
                if changes.has_key(r):
                    changes[r].insert(0,txt)
                else:
                    changes[r] = [txt]
    if commit_end == "HEAD" and len(logs) > 0:
        commit_end = logs[0].hexsha

    print
    print
    print "Release Name: v%s build %s from %s branch" % (release_name,
                                                         commit_end[0:12],
                                                         branch)
    print 
    print "Enhancements: "
    times = []
    for k in features.keys():
        times.append((log_map_time[k], k))
    revisions = sorted(times)
    revisions.reverse()
    for (t,r) in revisions:
        rfeats = features[r]
        for f in rfeats:
            print " - %s (%s)" %(f,r[0:12])
    
    print
    print "Bug fixes: "
    times = []
    for k in bugfixes.keys():
        times.append((log_map_time[k], k))
    revisions = sorted(times)
    revisions.reverse()
    for (t,r) in revisions:
        rbugs = bugfixes[r]
        for b in rbugs:
            print " - %s (%s)" %(b,r[0:12])
    print
    print "Other changes: "
    times = []
    for k in changes.keys():
        times.append((log_map_time[k], k))
    revisions = sorted(times)
    revisions.reverse()
    for (t,r) in revisions:
        print "(%s): "%r[0:12]
        for c in changes[r]:
            print "  - %s... "%c[0:100]

repo = init_repo()
build_release_notes(repo, branch)
cleanup_repo()


