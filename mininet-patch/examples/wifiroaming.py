#!/usr/bin/python

"""
This example shows how to create an empty Mininet object
(without a topology object) and add nodes to it manually.
"""
import sys

import mininet.net
import mininet.node
import mininet.cli
import mininet.log
import mininet.ns3

from mininet.net import Mininet, MininetWithControlNet
from mininet.node import OVSController
from mininet.cli import CLI
from mininet.log import setLogLevel, info                     
from mininet.ns3 import *        

import ns.core
import ns.network
import ns.wifi
import ns.csma
import ns.wimax
import ns.uan
import ns.netanim

nodes = [ { 'name': 'h1', 'type': 'host', 'position': (0.0, 10.0, 0.0), 'velocity': (2.5, 0, 0) }, 
          { 'name': 'h2', 'type': 'host', 'mobility': setListPositionAllocate(
createMobilityHelper("ns3::RandomWalk2dMobilityModel",n0="Bounds",v0=ns.mobility.RectangleValue(ns.mobility.Rectangle(100,200,-50,50))), createListPositionAllocate(x1=150,y1=30,z1=0)) }, 
          { 'name': 's1', 'type': 'switch', 'position': (0.0, 0.0, 0.0) }, 
          { 'name': 's2', 'type': 'switch', 'position': (120.0, 0.0, 0.0) },
          { 'name': 's3', 'type': 'switch', 'position': (60.0, 60.0*(3**0.5), 0.0) },
          { 'name': 's4', 'type': 'switch', 'position': (60.0, -60.0*(3**0.5), 0.0) },
          { 'name': 's5', 'type': 'switch', 'position': (-120.0, 0.0, 0.0) }, 
          { 'name': 's6', 'type': 'switch', 'position': (-60.0, 60.0*(3**0.5), 0.0) },
          { 'name': 's7', 'type': 'switch', 'position': (-60.0, -60.0*(3**0.5), 0.0) },
        ]

wifiintfs = [ {'nodename': 'h1', 'type': 'sta', 'channel': 1, 'ssid': 'ssid', 'ip': "10.0.0.1"}, 
              {'nodename': 'h2', 'type': 'sta', 'channel': 11, 'ssid': 'ssid', 'ip': "10.0.0.2"},
              {'nodename': 's1', 'type': 'ap', 'channel': 1, 'ssid': 'ssid'}, 
              {'nodename': 's2', 'type': 'ap', 'channel': 6, 'ssid': 'ssid'},
              {'nodename': 's3', 'type': 'ap', 'channel': 11, 'ssid': 'ssid'},
              {'nodename': 's4', 'type': 'ap', 'channel': 11, 'ssid': 'ssid'},
              {'nodename': 's5', 'type': 'ap', 'channel': 6, 'ssid': 'ssid'},
              {'nodename': 's6', 'type': 'ap', 'channel': 11, 'ssid': 'ssid'}, 
              {'nodename': 's7', 'type': 'ap', 'channel': 11, 'ssid': 'ssid'},
            ]

csmalinks = [ {'nodename1': 's1', 'nodename2': 's2'},
              {'nodename1': 's1', 'nodename2': 's3'},
              {'nodename1': 's1', 'nodename2': 's4'},
              {'nodename1': 's1', 'nodename2': 's5'},
              {'nodename1': 's1', 'nodename2': 's6'},
              {'nodename1': 's1', 'nodename2': 's7'}, 
            ]

def getWifiNode( wifinode, name ):
    for n in wifinode:    
        if n.name == name:
            return n
    return None

def WifiNet():

    "Create an Wifi network and add nodes to it."

    net = Mininet()

    info( '*** Adding controller\n' )
    net.addController( 'c0' )

    wifi = WifiSegment(standard = ns.wifi.WIFI_PHY_STANDARD_80211g)
    wifinodes = []

    for n in nodes:
        nodename = n.get('name', None)
        nodetype = n.get('type', None)
        nodemob = n.get('mobility', None)
        nodepos = n.get('position', None)
        nodevel = n.get('velocity', None)
        if nodetype is 'host':
            addfunc = net.addHost
            color = (255, 0, 0)
        elif nodetype is 'switch':
            addfunc = net.addSwitch
            color = (0, 0, 255)
        else:
            addfunc = None
        if nodename is None or addfunc is None: 
            continue
        node = addfunc (nodename)
        mininet.ns3.setMobilityModel (node, nodemob)
        if nodepos is not None:
            mininet.ns3.setPosition (node, nodepos[0], nodepos[1], nodepos[2])
        if nodevel is not None:
            mininet.ns3.setVelocity (node, nodevel[0], nodevel[1], nodevel[2])
        wifinodes.append (node)
        ns.netanim.AnimationInterface.SetNodeDescription (node.nsNode, nodename+'-'+str(node.nsNode.GetId()))
        ns.netanim.AnimationInterface.SetNodeColor (node.nsNode, color[0], color[1], color[2])

    for wi in wifiintfs:
        winodename = wi.get('nodename', None)
        witype = wi.get('type', None)
        wichannel = wi.get('channel', None)
        wissid = wi.get('ssid', None)
        wiip = wi.get('ip', None)
        if witype is 'sta':
            addfunc = wifi.addSta
        elif witype is 'ap':
            addfunc = wifi.addAp
        else:
            addfunc = None
        if winodename is None or addfunc is None or wichannel is None:
            continue
        node = getWifiNode (wifinodes, winodename)
        tb = addfunc (node, wichannel, wissid)
        if wiip is not None:
            tb.setIP (wiip)
    
    for cl in csmalinks:
        clnodename1 = cl.get('nodename1', None)  
        clnodename2 = cl.get('nodename2', None)
        if clnodename1 is None or clnodename2 is None:
            continue
        clnode1 = getWifiNode (wifinodes, clnodename1)
        clnode2 = getWifiNode (wifinodes, clnodename2)
        if clnode1 is None or clnode2 is None:
            continue
        CSMALink( clnode1, clnode2, DataRate="100Mbps")


    ns.wifi.YansWifiPhyHelper().Default().EnablePcapAll("/tmp/pcap/wifi")
    ns.csma.CsmaHelper().EnablePcapAll("/tmp/pcap/csma")

    anim = ns.netanim.AnimationInterface("/tmp/xml/wifi-wired-bridged4.xml")
    anim.EnablePacketMetadata (True)

    info( '*** Starting network\n')
    net.start()
    mininet.ns3.start()                    
    
    info( 'Testing network connectivity\n' )
    wifinodes[0].cmdPrint('ping 10.0.0.2 -c 100')

    info( '*** Stopping network' )
    mininet.ns3.clear()                    
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    WifiNet()
