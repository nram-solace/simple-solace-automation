# About

Sample Python script for DMR provisioning. Supports multiple external links.

## Config file

``` json
{
    "dmrCluster" : {
        "local" : {
            "cluster" : {
                "initiator": "local",
                "sempUrl" : "http://localhost:8080",
                "sempUser" : "admin",
                "sempPassword" : "*****",
                "dmrClusterName": "nram-test-local",
                "nodeName" : "solace-100141-test",
                "msgVpnName" : "TestVPN",
                "authenticationBasicPassword": "******"            },

            "links" : [
                {
                    "remoteAddress": "nram-latitude:55333",
                    "remoteNodeName": "solace-100141-nram",
                    "remoteAuthenticationBasicPassword": "*****",
                    "remoteMsgVpnName" : "ProdVPN"
                }
            ]
        },

        "remote" : {
            "cluster" : {
                "initiator": "remote",
                "remoteAddress": "localhost",
                "remoteNodeName": "solace-100141-test",
                "remoteAuthenticationBasicPassword": "*****",
                "remoteMsgVpnName" : "TestVPN"
            },

            "links" : [
                    {
                        "initiator": "remote",
                        "dmrClusterName": "nram-test-remote",
                        "nodeName": "solace-100141-nram",
                        "authenticationBasicPassword": "*****",
                        "sempUrl" : "http://nram-latitude:8080",
                        "sempUser" : "admin",
                        "sempPassword" : "*****" ,
                        "msgVpnName" : "ProdVPN",

                        "remoteAddress": "localhost:55555",
                        "remoteNodeName": "solace-100141-test",
                        "remoteAuthenticationBasicPassword": "*****",
                        "remoteMsgVpnName" : "TestVPN"
                    }
            ]
        }
    },

    "internal" : {
        "META": "*** DONOT CHANGE THESE VALUES ***",
        "sempDir" : "semp",
        "configUrl" : "SEMP/v2/config",
        "dmrCluster": "dmrClusters",
        "externalLink": "dmrClusters/{{dmrClusterName}}/links",
        "remoteAddress": "dmrClusters/{{dmrClusterName}}/links/{{remoteNodeName}}/remoteAddresses",
        "trustedCommonName": "dmrClusters/{{dmrClusterName}}/links/{{remoteNodeName}}/tlsTrustedCommonNames",
        "vpnDmrBridge": "msgVpns/{{msgVpnName}}/dmrBridges",
        "enableLink": "dmrClusters/{{dmrClusterName}}/links/{{remoteNodeName}}",
        "enableCluster": "dmrClusters/{{dmrClusterName}}",
        "okStatus" : [200, 400]
    } 
}

```

## Usage

``` bash
▶ python create-dmr-cluster.py --cfgfile nram-local-dmr-cluster.json

===  Create local cluster nram-test-local
*** Working on local dmrCluster (post)
    post url: http://localhost:8080/SEMP/v2/config/dmrClusters
    Status: 400

=== Processing 1 local links

--- Processing local link 1/1
*** Working on local externalLink (post)
    post url: http://localhost:8080/SEMP/v2/config/dmrClusters/nram-test-local/links
    Status: 400
*** Working on local remoteAddress (post)
    post url: http://localhost:8080/SEMP/v2/config/dmrClusters/nram-test-local/links/solace-100141-nram/remoteAddresses
    Status: 200
*** Working on local vpnDmrBridge (post)
    post url: http://localhost:8080/SEMP/v2/config/msgVpns/TestVPN/dmrBridges
    Status: 400

===  Processing 1 remote links

---  Processing remote link 1/1
*** Working on remote dmrCluster (post)
    post url: http://nram-latitude:8080/SEMP/v2/config/dmrClusters
    Status: 200
*** Working on remote externalLink (post)
    post url: http://nram-latitude:8080/SEMP/v2/config/dmrClusters/nram-test-remote/links
    Status: 200
*** Working on remote vpnDmrBridge (post)
    post url: http://nram-latitude:8080/SEMP/v2/config/msgVpns/ProdVPN/dmrBridges
    Status: 200
*** Working on local enableLink (patch)
    patch url: http://localhost:8080/SEMP/v2/config/dmrClusters/nram-test-local/links/solace-100141-nram
    Status: 200
*** Working on remote enableLink (patch)
    patch url: http://nram-latitude:8080/SEMP/v2/config/dmrClusters/nram-test-remote/links/solace-100141-test
    Status: 200
*** Working on local enableCluster (patch)
    patch url: http://localhost:8080/SEMP/v2/config/dmrClusters/nram-test-local
    Status: 200
*** Working on remote enableCluster (patch)
    patch url: http://nram-latitude:8080/SEMP/v2/config/dmrClusters/nram-test-remote
    Status: 200```

