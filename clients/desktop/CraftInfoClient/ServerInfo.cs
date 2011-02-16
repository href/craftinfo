using System;
using System.Collections.Generic;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Xml;

namespace CraftInfo
{
    /// <summary>
    /// Class representing the server-information
    /// 
    /// This class can connect to a Craftinfo-server, get the XML and parse
    /// it. The results are stored within the members of this very class.
    /// </summary>
    class ServerInfo
    {
        private bool m_IsOnline = false;
        List<string> m_Players = new List<string>();
        List<string> m_Updates = new List<string>();
        private bool m_IsLoaded = false;

        /// <summary>
        /// Connects to the server, gets the XML and parses it.
        /// Can be called multiple times within lifetime.
        /// </summary>
        /// <param name="Host">Hostadress</param>
        /// <param name="Port">Port</param>
        public void Load(string Host, int Port)
        {
            //clear info from any previous runs
            m_Players.Clear();
            m_Updates.Clear();

            //connect to the server and get the xml string via socket
            string xmlstring = "";
            Socket server = null;
            try
            {
                IPEndPoint ip = new IPEndPoint(Dns.GetHostAddresses(Host)[0], Port);

                server = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.IP);
                server.Connect(ip);

                //read from the socket until the end of the stream
                byte[] data = new byte[1024];
                int length = 0;
                while (!xmlstring.Contains("</info>"))
                {
                    length = server.Receive(data);

                    if (length == 0)
                        break;

                    xmlstring += Encoding.ASCII.GetString(data, 0, length);
                }
            }
            finally
            {
                server.Shutdown(SocketShutdown.Both);
                server.Close();
            }
            
            //Parse the xml
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

        /// <summary>
        /// True if the server is online
        /// </summary>
        public bool IsOnline()
        {
            return m_IsOnline;
        }

        /// <summary>
        /// Returns a string list with the online players
        /// </summary>
        public List<string> GetPlayers()
        {
            return m_Players;
        }

        /// <summary>
        /// Returns a string list with the server updates
        /// </summary>
        public List<string> GetUpdates()
        {
            return m_Updates;
        }

        /// <summary>
        /// Returns true if Load() was successfully executed
        /// </summary>
        public bool IsLoaded()
        {
            return m_IsLoaded;
        }
    }
}
