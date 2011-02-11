using System;
using System.Collections.Generic;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Xml;

namespace CraftInfo
{
    class ServerInfo
    {
        private bool m_IsOnline = false;
        List<string> m_Players = new List<string>();
        List<string> m_Updates = new List<string>();
        private bool m_IsLoaded = false;

        public void Load(string Host, int Port)
        {
            m_Players.Clear();
            m_Updates.Clear();

            IPEndPoint ip = new IPEndPoint(Dns.GetHostAddresses(Host)[0], Port);

            Socket server = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.IP);
            server.Connect(ip);

            byte[] data = new byte[1024];
            
            string xmlstring = "";
            int length = 0;
            while (! xmlstring.Contains("</info>"))
            {
                length = server.Receive(data);
                
                if (length == 0)
                    break;
                
                xmlstring += Encoding.ASCII.GetString(data, 0, length);
            }

            server.Shutdown(SocketShutdown.Both);
            server.Close();

            var Xml = new XmlDocument();
            Xml.InnerXml = xmlstring;

            XmlNode online = Xml.GetElementsByTagName("online").Item(0);
            if (online.InnerText.ToLower() == "true")
                m_IsOnline = true;
            else
                m_IsOnline = false;

            if (m_IsOnline)
            {
                XmlNode players = Xml.GetElementsByTagName("players").Item(0);
                foreach (XmlNode player in players)
                {
                    m_Players.Add(player.InnerText);
                }

                XmlNode updates = Xml.GetElementsByTagName("updates").Item(0);
                foreach (XmlNode update in updates)
                {
                    m_Updates.Add(update.InnerText);
                }
            }

            m_IsLoaded = true;
        }

        public bool IsOnline()
        {
            return m_IsOnline;
        }

        public List<string> GetPlayers()
        {
            return m_Players;
        }

        public List<string> GetUpdates()
        {
            return m_Updates;
        }

        public bool IsLoaded()
        {
            return m_IsLoaded;
        }
    }
}
