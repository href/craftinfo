using System;
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
        private const string m_Server = "href.ch";
        private const int m_Port = 5001;

        public Main()
        {
            InitializeComponent();
            this.Visible = false;
        }

        private void Main_Load(object sender, EventArgs e)
        {
            notifyIcon.Icon = CraftInfo.Properties.Resources.err;
            notifyIcon.ContextMenu = new ContextMenu();
            UpdateStatus();
            this.timerUpdate.Start();
        }

        private void On_Close(object sender, EventArgs e)
        {
            Close();
        }

        private void UpdateStatus()
        {
            bool LoadedBefore = m_Info.IsLoaded();
            bool OnlineBefore = m_Info.IsOnline();

            List<string> OldPlayers = new List<string>(m_Info.GetPlayers());
            
            try
            {
                m_Info.Load(m_Server, m_Port);
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
            else
            {
                notifyIcon.Text = String.Format("{0} Offline", m_Server);
                notifyIcon.Icon = Resources.off;
            }

            if (LoadedBefore && OnlineBefore != m_Info.IsOnline())
            {
                if (m_Info.IsOnline())
                    ShowTip("Server went online");
                else
                    ShowTip("Server went offline");

            }

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

        private void timerUpdate_Tick(object sender, EventArgs e)
        {
            UpdateStatus();
        }

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
