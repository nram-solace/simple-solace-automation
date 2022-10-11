# create-dmr-cluster
# Configure and enable Solace DMR cluster with compression and TLS
# - Added support for multiple remote links (for HA/DR setup)
# Ramesh Natarajan (nram), Solace PSG

import argparse
import getpass
import requests
import json
import sys
import re
import pprint
pp = pprint.PrettyPrinter(indent=4)

# some globals
Cfg = {} # cfg dict
Verbose = 0 

def main(argv):
    global Cfg, Verbose
    p = argparse.ArgumentParser()
    p.add_argument('--cfgfile', dest="cfgfile", required=True, help='config json file') 
    p.add_argument( '--verbose', '-v', action="count",  required=False, default=0,
                help='Turn Verbose. Use -vvv to be very verbose')
    r = p.parse_args()
    Verbose = r.verbose

    Cfg = read_json_file(r.cfgfile)
    
    # Make sure required tags are in the config
    assert "internal" in Cfg
    assert "dmrCluster" in Cfg
    cfg_dmr = Cfg["dmrCluster"]
    assert "local" in cfg_dmr
    assert "remote" in cfg_dmr
    cfg_dmr_local = cfg_dmr["local"]
    cfg_dmr_remote = cfg_dmr["remote"]
    assert "cluster" in cfg_dmr_local
    assert "links" in cfg_dmr_local
    assert "cluster" in cfg_dmr_remote
    assert "links" in cfg_dmr_remote

    if Verbose > 1:
        print ('CONFIG'); pp.pprint(Cfg)

    # create dmr clusters - not required on Cloud
    cfg_local  = cfg_dmr_local["cluster"]
    print (f"=== Processing local cluster {cfg_local['dmrClusterName']}")
    post_target ('dmrCluster', cfg_local)

    # Process links
    n = len(cfg_dmr_local['links'])
    print (f"=== Processing {n} local links")
    i = 0
    for lcfg in cfg_dmr_local['links']:
        i = i+1
        print (f"--- Processing local link {i}/{n}")
        for target in (['externalLink', 'remoteAddress', 'vpnDmrBridge', 'trustedCommonName']):
            post_target (target, cfg_local, lcfg)
     
    # Create on the remote nodes
    rcfg = cfg_dmr_remote['cluster']
    print (f"=== Processing {n} remote links")
    i = 0
    for cfg_remote in cfg_dmr_remote['links']:
        i = i+1
        print (f"--- Processing remote link {i}/{n}")
        post_target ('dmrCluster', cfg_remote)
        for target in (['externalLink', 'vpnDmrBridge']):    
            post_target (target, cfg_remote, rcfg)

    # Enable links & cluster
    for lcfg in cfg_dmr_local['links']:
        patch_target ("enableLink", cfg_local, lcfg)
    for cfg_remote in cfg_dmr_remote['links']:
        patch_target ("enableLink", cfg_remote, rcfg)

    # Enable clusters - no need to run for cloud instances
    patch_target ("enableCluster", cfg_local)
    for cfg_remote in cfg_dmr_remote['links']:
        patch_target ("enableCluster", cfg_remote, rcfg)

def post_target(target, ccfg, lcfg={}):
    cfg = {**ccfg, **lcfg}
    if Verbose > 1:
        print ("post_target: Config: "); pp.pprint(cfg)
    return processs_target(target, cfg, "post")

def patch_target(target, ccfg, lcfg={}):
    cfg = {**ccfg, **lcfg}
    if Verbose > 1:
        print ("patch_target: Config: "); pp.pprint(cfg)
    return processs_target(target, cfg, "patch")

def processs_target (target, cfg, action="post"):
    end = cfg['initiator']
    print (f"\n*** Working on {end} {target} ({action})")
    cfg_int = Cfg["internal"]
    semp_dir = cfg_int['sempDir']
    semp_file = f'{semp_dir}/{target}.json'
    semp_data = read_json_file(semp_file)
    data = expand_vars(semp_data, cfg)
    if Verbose > 1:
        #print ('processs_target: Template: '); pp.pprint(semp_data)
        print ('processs_target: Processed: '); pp.pprint(data)

    curl = f"{cfg['sempUrl']}/{cfg_int['configUrl']}"
    urls = expand_vars(expand_vars(cfg_int, cfg, False), cfg, False) # lazy hack to get at most two vars expanded
    assert target in urls, 'Misssing tag {} in url section'.format(target)
    url = f"{curl}/{urls[target]}"
    if Verbose:
        print ('processs_target: ConfigURL:', url)
    return post_semp(url, cfg['sempUser'], cfg['sempPassword'], data, action)

def post_semp(url, user, passwd, json_data, action="post"):
    print (f'    {action} url: {url}')
    if Verbose > 1 :
        print ('request json:\n---\n', json.dumps(json_data, indent=4))
    stats = getattr(requests, action)(url, 
        headers={"content-type": "application/json"},
        auth=(user, passwd),
        data=(json.dumps(json_data)))
    if Verbose > 1 :
        print('response :\n---\n', stats.text)
    okStatus = Cfg['internal']['okStatus']
    assert stats.status_code in okStatus , stats.text
    print (f'    Status: {stats.status_code}')
    return stats

def read_json_file(file):
    if Verbose > 0 :
        print (f'--- read_json_file: file = {file}')
    with open(file, "r") as fp:
        data = json.load(fp)
    return data

def expand_vars (data, cfg, assertive=True):
    rc = re.compile('(.*)({{)(.*)(}})(.*)')
    out = data.copy() # prevent caching by not inline updating
    for k,v in out.items():
        if type(v) is not str:
            continue
        m = rc.match(v)
        if m :
            t = m.group(3)
            if t in cfg:
                t1 = cfg[m.group(3)]
                out[k] = f'{m.group(1)}{t1}{m.group(5)}'
            else:
                if assertive:
                    assert t in cfg, 'Missing tag {} in config'.format(t)
    #if Verbose > 1:
    #    print('expand_vars: in:'); pp.pprint(data)
    #    print('expand_vars: out: ({t1}):'); pp.pprint(out)
    return out

if __name__ == "__main__":
    main(sys.argv[1:])