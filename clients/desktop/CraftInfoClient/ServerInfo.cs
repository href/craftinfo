using System;
using System.Collections.Generic;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Xml;
using System.Threading;

namespace CraftInfo
{

    /// <summary>
    /// Class representing the server-information
    /// 
    /// This class can connect to a CraftInfo Server, get the XML and parse
    /// it. The results are stored within the members of this very class.
    /// </summary>
    class ServerInfo
    {
        List<string> m_Players = new List<string>();
        List<string> m_Updates = new List<string>();
        private bool m_IsOnline = false;
        private bool m_IsInit = false;

        /// <summary>
        /// Connects to the server, gets the XML and parses it.
        /// Can be called multiple times within lifetime.
        /// </summary>
        /// <param name="Host">Hostadress</param>
        /// <param name="Port">Port</param>
        public void Init(string Host, int Port)
        {
            //clear info from any previous runs
            m_Players.Clear();
            m_Updates.Clear();

            //connect to the server and get the XML string via socket
            string xmlstring = ServerInfo.GetServerValue(Host, Port);
            
            //Parse the XML
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

            m_IsInit = true;
        }

        /// <summary>
        /// Gets the value of a CraftInfo Server
        /// TODO: Threads to avoid hanging
        /// </summary>
        public static string GetServerValue(string Host, int Port)
        {
            string Value = "";
            Socket Server = null;

            try
            {
                IPEndPoint ip = new IPEndPoint(Dns.GetHostAddresses(Host)[0], Port);

                Server = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.IP);
                Server.Connect(ip);

                //read from the socket until the end of the stream
                byte[] data = new byte[1024];
                int length = 0;
                while (!Value.Contains("</info>"))
                {
                    length = Server.Receive(data);

                    if (length == 0)
                        break;

                    Value += Encoding.ASCII.GetString(data, 0, length);
                }
            }
            finally
            {
                Server.Shutdown(SocketShutdown.Both);
                Server.Close();
            }

            return Value;
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
            return m_IsInit;
        }
    }
}
