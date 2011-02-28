using System;
using System.IO;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Net;
using System.Net.Sockets;
using CraftInfo.Properties;

namespace CraftInfo
{
    public partial class Main : Form
    {
        private ServerInfo m_Info = new ServerInfo();

        //set these values before compiling to create a config-free app
        private string m_Server = "";
        private int m_Port = 0;

        public Main()
        {
            InitializeComponent();
            this.Visible = false;
        }

        /// <summary>
        /// Starts up the application and loads the config.ini, if the server
        /// is not hard-coded. The config.ini must reside in the same directory
        /// as the executable and must contain the following lines:
        /// server = example.com
        /// port = 1234
        /// </summary>
        private void Main_Load(object sender, EventArgs e)
        {
            //Load the config.ini
            if (m_Server.Length == 0 || m_Port == 0)
            {
                StreamReader reader = null;
                try
                {
                    reader = new StreamReader("./config.ini");

                    string line, value;
                    while ((line = reader.ReadLine()) != null)
                    {
                        if ((value = GetIniLine(ref line, "server")) != null)
                            m_Server = value;

                        if ((value = GetIniLine(ref line, "port")) != null)
                            m_Port = System.Convert.ToInt32(value);
                    }
                }
                catch (FileNotFoundException)
                {
                    MessageBox.Show("Server undefined and config.ini not found");
                    System.Environment.Exit(1);
                }
                finally
                {
                    if (reader != null)
                        reader.Close();
                }
            }

            //Start up with an error-icon to be replaced on connect
            notifyIcon.Icon = CraftInfo.Properties.Resources.err;
            notifyIcon.ContextMenu = new ContextMenu();
            
            //Start showing information
            UpdateStatus();

            //.. and schedule further lookups
            this.timerUpdate.Start();
        }

        /// <summary>
        /// Gets the value of an ini-style config file
        /// </summary>
        /// <param name="Line">The complete line of the ini</param>
        /// <param name="ItemName">The value to be read i.e. the value name
        /// in front of the equal sign ("ItemName = Value")</param>
        /// <returns>The trimmed value after the equal sign or null</returns>
        private string GetIniLine(ref string Line, string ItemName)
        {
            if (Line.StartsWith(ItemName,StringComparison.OrdinalIgnoreCase))
            {
                int pos = Line.IndexOf("=");
                string Value = Line.Substring(pos + 1);
                return Value.Trim(new char[] { ' ', '\t', '\n' });
            }
            return null;
        }

        private void On_Close(object sender, EventArgs e)
        {
            Close();
        }

        /// <summary>
        /// Gets the current server status and shows balloons for items that
        /// changed since the last update.
        /// </summary>
        private void UpdateStatus()
        {
            bool LoadedBefore = m_Info.IsLoaded();
            bool OnlineBefore = m_Info.IsOnline();

            List<string> OldPlayers = new List<string>(m_Info.GetPlayers());
            
            //connect to the server
            try
            {
                m_Info.Init(m_Server, m_Port);
            }
            catch (System.Exception)
            {
                notifyIcon.Icon = CraftInfo.Properties.Resources.err;
                notifyIcon.ContextMenu.MenuItems.Clear();
                notifyIcon.ContextMenu.MenuItems.Add("Unable to connect to server " + m_Server);
                notifyIcon.ContextMenu.MenuItems.Add(new MenuItem("Close", On_Close));
                return;
            }
            
            List<string> NewPlayers = m_Info.GetPlayers();
            int PlayerCount = NewPlayers.Count;

            if (m_Info.IsOnline())
            {
                //show icon with the number of players (1-9 or more)

                //TODO: dynamically draw icons to allow for more than 1-9 as 
                //number-of-players icons
                notifyIcon.Text = String.Format("Server Online ({0} Player)", PlayerCount);
                switch (PlayerCount)
                {
                    case 0:
                        notifyIcon.Icon = Resources.p0;
                        break;
                    case 1:
                        notifyIcon.Icon = Resources.p1;
                        break;
                    case 2:
                        notifyIcon.Icon = Resources.p2;
                        break;
                    case 3:
                        notifyIcon.Icon = Resources.p3;
                        break;
                    case 4:
                        notifyIcon.Icon = Resources.p4;
                        break;
                    case 5:
                        notifyIcon.Icon = Resources.p5;
                        break;
                    case 6:
                        notifyIcon.Icon = Resources.p6;
                        break;
                    case 7:
                        notifyIcon.Icon = Resources.p7;
                        break;
                    case 8:
                        notifyIcon.Icon = Resources.p8;
                        break;
                    case 9:
                        notifyIcon.Icon = Resources.p9;
                        break;
                    default: //more
                        notifyIcon.Icon = Resources.pmore;
                        break;
                }
            }
            else //server offline
            {
                notifyIcon.Text = String.Format("{0} Offline", m_Server);
                notifyIcon.Icon = Resources.off;
            }

            // show ballon upon server boot/shutdown
            if (LoadedBefore && OnlineBefore != m_Info.IsOnline())
            {
                if (m_Info.IsOnline())
                    ShowTip("Server went online");
                else
                    ShowTip("Server went offline");

            }

            // show players that joined or left since the last update
            if (LoadedBefore && OnlineBefore == m_Info.IsOnline())
            {
                StringBuilder Balloon = new StringBuilder();

                List<string> Changes = GetChanges(OldPlayers, NewPlayers);
                foreach (string Change in Changes)
                {
                    Balloon.Append(Change);
                    Balloon.Append("\n");
                }

                ShowTip(Balloon.ToString());
            }

            //redraw the context menu
            notifyIcon.ContextMenu.MenuItems.Clear();

            notifyIcon.ContextMenu.MenuItems.Add(PlayerCount + " Players Online");
            notifyIcon.ContextMenu.MenuItems.Add("-");

            foreach (string Player in NewPlayers)
            {
                notifyIcon.ContextMenu.MenuItems.Add(Player);
            }

            if (NewPlayers.Count > 0)
                notifyIcon.ContextMenu.MenuItems.Add("-");

            notifyIcon.ContextMenu.MenuItems.Add(new MenuItem("Close", On_Close));
        }

        /// <summary>
        /// Creates a human readable list of players that joined or left the server
        /// </summary>
        /// <param name="OldPlayers">List of players from the previous update</param>
        /// <param name="NewPlayers">List of players from the current update</param>
        /// <returns>The changes in human readable format</returns>
        private List<string> GetChanges(List<string> OldPlayers, List<string> NewPlayers)
        {
            List<string> Changes = new List<string>();

            foreach (string op in OldPlayers)
            {
                if (!NewPlayers.Contains(op))
                {
                    Changes.Add(op + " left the server");
                }
            }

            foreach (string np in NewPlayers)
            {
                if (!OldPlayers.Contains(np))
                {
                    Changes.Add(np + " joined the server");
                }
            }

            return Changes;
        }

        /// <summary>
        /// Update status on every timer event
        /// </summary>
        private void timerUpdate_Tick(object sender, EventArgs e)
        {
            UpdateStatus();
        }

        /// <summary>
        /// Show a balloon text
        /// </summary>
        /// <param name="Tip">Any value to be shown</param>
        private void ShowTip(string Tip)
        {
            if (Tip.Length > 0)
            {
                notifyIcon.BalloonTipTitle = "Minecraft";
                notifyIcon.BalloonTipIcon = ToolTipIcon.Info;
                notifyIcon.BalloonTipText = Tip;
                notifyIcon.ShowBalloonTip(5000);
            }
        }
    }
}
