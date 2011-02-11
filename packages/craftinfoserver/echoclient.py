from gevent import socket
import xml.etree.ElementTree as ET

def get_serverxml(server, port):
    c = socket.socket()
    ip = socket.gethostbyname(server)
    
    try:
        c.connect((ip, port))
        
        xml = ""
        while "</info>" not in xml:
            xml = c.recv(1024)    
            if xml is None:
                break
         
        return xml
    finally:
        c.close()

def get_servervalue(server, port):
    c = socket.socket()
    ip = socket.gethostbyname(server)
    try:
        c.connect((ip, port))
        return c.recv(1024)
    finally:
        c.close()

def get_serverinfo(server, port):    
    root = ET.fromstring(get_serverxml(server, port))

    info = dict()

    if root.find("online").text == "True":
        info["online"] = True
    else:
        info["online"] = False
    
    info["players"] = []
    for player in root.find("players").getchildren():
        info["players"].append(player.text)
    
    info["updates"] = []
    for update in root.find("updates").getchildren():
        info["updates"].append(update.text)

    return info

def generate_xml(is_running, log, session, messages):
    """Puts the info from the minecraft module together into an XML"""

    log.update()

    root = ET.Element('info')

    online = ET.SubElement(root, 'online')
    online.text = str(is_running())

    players = ET.SubElement(root, 'players')
    for nick in log.get_playerlist():
        player = ET.SubElement(players, 'player')
        player.text = nick

    updates = ET.SubElement(root, 'updates')
    for msg in messages:
        update = ET.SubElement(updates, 'update')
        datetxt = msg.date.strftime("%d.%m.%Y - %H:%M")
        update.text = "%s, %s" % (datetxt, msg.text)
    
    return ET.tostring(root)