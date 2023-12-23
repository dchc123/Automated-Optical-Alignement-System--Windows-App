using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Text;
using System.Windows.Forms;
using System.Threading.Tasks;
using System.Diagnostics;
using Thorlabs.MotionControl.Benchtop.StepperMotorCLI;
using Thorlabs.MotionControl.KCube.PiezoCLI;
using Thorlabs.MotionControl.DeviceManagerCLI;
using Thorlabs.MotionControl.GenericMotorCLI.Settings;
using System.Threading;
using System.Runtime.InteropServices;
using System.IO.Pipes;
using Microsoft.Win32.SafeHandles;
using System.Linq;
using System.Globalization;
using Microsoft.VisualBasic.FileIO;
using System.Reflection;

namespace Automated_Optical_Alignment
{
    public partial class PiezoScan : Form
    {
        const string SerialNumber = "70184894";  

        public KCubePiezo _kCubePiezoX = null;
        public KCubePiezo _kCubePiezoY = null;
        public KCubePiezo _kCubePiezoZ = null;

        MainForm mainform = new MainForm();

        public PiezoScan()
        {
            InitializeComponent();
        }

        #region piezo scan and update info 
        private void RunScan2_Click(object sender, EventArgs e)
        {
            if (ConnectionCheckBox2.Checked == true)
            {
                buttonConnect_Click(null, null);

            }

            // Open the named pipe.
            var server = new NamedPipeServerStream("NPtest");

            decimal minimum_step = 0.001m;

            decimal midpointX;
            decimal midpointY;

            if (Globals.connection_flag)
            {
                midpointX = MainForm.Volt2Pos(_kCubePiezoX.GetOutputVoltage());
                midpointY = MainForm.Volt2Pos(_kCubePiezoY.GetOutputVoltage());
            }
            else
            {
                midpointX = 0.01m;
                midpointY = 0.01m;
            }

            decimal EdgeLength=0;
            decimal Scan_Resolution=0;
            decimal MaxReadingsPerEdge=0;
            int ReadingsPerEdge=0;
            decimal Step_Size=0;

            try
            {

                EdgeLength = Convert.ToDecimal(SideLengthInput2.Text) / 1000;
                if (0m > EdgeLength || 0.02m < EdgeLength) { throw new Exception(); }

                Scan_Resolution = Convert.ToDecimal(ScanResolutionInput2.Text);
                if (0m > Scan_Resolution || 100m < Scan_Resolution) { throw new Exception(); }

                MaxReadingsPerEdge = Decimal.Round((Decimal)EdgeLength / minimum_step);
                ReadingsPerEdge = Convert.ToInt32(Decimal.Round(MaxReadingsPerEdge * (Scan_Resolution / 100)));
                Step_Size = (Decimal)EdgeLength / (Decimal)ReadingsPerEdge;

            }
            catch 
            { 
                MessageBox.Show("Ensure that the scan resolution is an integer/decimal and is between 0 and 100. Also ensure that the Edge Length is an integer/decimal and is between 0 and 20", "Warning", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                goto Finish;
            }
        

            if (ConnectionCheckBox2.Checked)
            {
                if (Globals.Min_Piezo_Pos > (midpointX - (EdgeLength / 2)) || Globals.Max_Piezo_Pos < (midpointX + (EdgeLength / 2)))
                {
                    DialogResult dialog = MessageBox.Show("The scan area chosen it outwith the range of the X Channel Piezo Motor, the scan will automatically terminate once the motor is moved beyond its range. Results up to that point will still be shown.", "Warning", MessageBoxButtons.OKCancel, MessageBoxIcon.Warning);
                    
                    if (dialog == DialogResult.Cancel)
                    {
                        goto Finish;
                    }
                }

                else if (Globals.Min_Piezo_Pos > (midpointY - (EdgeLength / 2)) || Globals.Max_Piezo_Pos < (midpointY + (EdgeLength / 2)))
                {
                    DialogResult dialog = MessageBox.Show("The scan area chosen it outwith the range of the Y Channel Stepper Motor, the scan will automatically terminate once the motor is moved beyond its range. Results up to that point will still be shown.", "Warning", MessageBoxButtons.OKCancel, MessageBoxIcon.Warning);
                   
                    if (dialog == DialogResult.Cancel)
                    {
                        goto Finish;
                    }
                }
            }

            if (ReadingsPerEdge % 2 == 0) { ReadingsPerEdge += 1; }

            Globals.Serpent2(ReadingsPerEdge);

            Console.WriteLine("Waiting for connection...");
            string fileName = @"Python_Alignment_Script.py";

            var entries = Environment.GetEnvironmentVariable("path").Split(';');
            string python_location = null;

            foreach (string entry in entries)
            {
                if (entry.ToLower().Contains("python"))
                {
                    var breadcrumbs = entry.Split('\\');
                    foreach (string breadcrumb in breadcrumbs)
                    {
                        if (breadcrumb.ToLower().Contains("python"))
                        {
                            python_location += breadcrumb + '\\';
                            break;
                        }
                        python_location += breadcrumb + '\\';
                    }
                    break;
                }
            }

            python_location = python_location + @"Python38-32\python.exe";

            if (DummyCheckBox2.Checked == false)
            {
                Process p = new Process();
                p.StartInfo = new ProcessStartInfo(python_location, fileName)
                {
                    UseShellExecute = false,
                    RedirectStandardError = true,
                    RedirectStandardInput = true,
                    //RedirectStandardOutput = false,
                    CreateNoWindow = true,
                    ErrorDialog = false
                };
                p.Start();
            }

            server.WaitForConnection();
            Console.WriteLine("Connected.");

            Stopwatch sw = new Stopwatch();
            sw.Start();

            var br = new BinaryReader(server);
            var bw = new BinaryWriter(server);

            int[,] array2Dc = Globals.Serpentine();
            int array_length = (array2Dc.Length / 2);
            int MaxValue = array2Dc.Cast<int>().Max();
            byte ByteMaxValue = Convert.ToByte(MaxValue);

            int Mode = 0;

            if (ConnectionCheckBox2.Checked == true)
            {
                Mode = 1;
            }
            else if (ConnectionCheckBox2.Checked == false)
            {
                Mode = 0;
            }

            byte ModeByte = Convert.ToByte(Mode);

            bw.Write(ModeByte);

            bw.Write(ByteMaxValue);

            int Maximum = array2Dc.Cast<int>().Max();
            int scale = 155 / Maximum;
            
            Canvas_Clear();


            for (int i = 0; i < array_length; i++)
            {
                try
                {
                    //Console.WriteLine("Trying");

                    int x1 = (array2Dc[i, 0]) + (MaxValue);
                    int y1 = (array2Dc[i, 1]) + (MaxValue);

                    byte X1 = Convert.ToByte(x1);
                    byte Y1 = Convert.ToByte(y1);

                    byte[] position = new byte[2];
                    position[0] = X1;
                    position[1] = Y1;



                    if (ConnectionCheckBox2.Checked == true)
                    {

                        decimal Xposition = MainForm.MotorPositions(midpointX, Step_Size, array2Dc[i, 0]);
                        decimal Yposition = MainForm.MotorPositions(midpointY, Step_Size, array2Dc[i, 1]);

                        decimal XVoltage = MainForm.Pos2Volt(Xposition);
                        decimal YVoltage = MainForm.Pos2Volt(Yposition);

                        if(Globals.Max_Piezo_Pos > Xposition && Globals.Min_Piezo_Pos < Xposition && Globals.Max_Piezo_Pos > Yposition && Globals.Min_Piezo_Pos < Yposition)
                        {
                            _kCubePiezoX.SetOutputVoltage(XVoltage);
                            _kCubePiezoY.SetOutputVoltage(YVoltage);

                        }
                        else
                        {
                            MessageBox.Show("Attempt was made to move the motor outwith its' range and therefore, the scan was terminated.", "Warning", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                            break;
                        }
                        

                    }

                    bw.Write(position);

                    if (i > 0)
                    {
                        Canvas_JoinPoints(array2Dc[i - 1, 0], array2Dc[i - 1, 1], array2Dc[i, 0], array2Dc[i, 1], scale);
                    }

                    byte[] current_reading = br.ReadBytes(4);
                    int current_reading2 = current_reading[3];


                }
                catch (EndOfStreamException)
                {
                    Console.WriteLine("Failed.");

                    break;                    // When client disconnects
                }
            }

            string kill = "kill";
            byte[] kill_command = Encoding.ASCII.GetBytes(kill);
            bw.Write(kill_command);

            string ScanTime = Convert.ToString((ReadingsPerEdge * ReadingsPerEdge) / 100) + " mins";
            string ReadingsTotalLabel = Convert.ToString(ReadingsPerEdge * ReadingsPerEdge);
            string StepSizeLabel = Convert.ToString(Decimal.Round(Step_Size, 5));

            string file_name = midpointX + "_" + midpointY + "_" + StepSizeLabel;
            byte[] file_name_bytes = Encoding.ASCII.GetBytes(file_name);
            byte file_name_size = Convert.ToByte(file_name_bytes.Length);

            bw.Write(file_name_size);
            bw.Write(file_name_bytes);

            byte[] file_number = br.ReadBytes(4);

            string filenum = "_" + Convert.ToString(8 * Convert.ToUInt64(file_number[0]) + 4 * Convert.ToUInt64(file_number[1]) + 2 * Convert.ToUInt64(file_number[2]) + Convert.ToUInt64(file_number[3]));

            if (filenum == "_0") { filenum = ""; }

            file_name = file_name + filenum;

            Globals.Results_File_Name = file_name;

            Console.Read();
            sw.Stop();
            Console.WriteLine("Elapsed={0}", sw.Elapsed);
            sw.Reset();

        Finish:
            Console.WriteLine("Client disconnected.");
            server.Close();
            server.Dispose();

            this.Close();

            //mainform.Run(file_name);
            
        }
       
        
        private void ScanInfoUpdateButton2_Click(object sender, EventArgs e)
        {

            try
            {
                decimal minimum_step = 0.001m;

                decimal EdgeLength = Convert.ToDecimal(SideLengthInput2.Text) / 1000;
                if (0m > EdgeLength || 0.02m < EdgeLength) { throw new Exception(); }

                decimal Scan_Resolution = Convert.ToDecimal(ScanResolutionInput2.Text);
                if (0m > Scan_Resolution || 100m < Scan_Resolution) { throw new Exception(); }

                decimal MaxReadingsPerEdge = Decimal.Round((Decimal)EdgeLength / minimum_step);
                int ReadingsPerEdge = Convert.ToInt32(Decimal.Round(MaxReadingsPerEdge * (Scan_Resolution / 100)));
                decimal Step_Size = (Decimal)EdgeLength / (Decimal)ReadingsPerEdge;

                ScanTimeLabel2.Text = Convert.ToString((ReadingsPerEdge * ReadingsPerEdge) / 100) + " mins";
                ReadingsTotalLabel2.Text = Convert.ToString(ReadingsPerEdge * ReadingsPerEdge);
                StepSizeLabel2.Text = Convert.ToString(Decimal.Round(Step_Size, 5));
            }
            catch { MessageBox.Show("Ensure that the scan resolution is an integer/decimal and is between 0 and 100. Also ensure that the Edge Length is an integer/decimal and is between 0 and 20", "Warning", MessageBoxButtons.OK, MessageBoxIcon.Warning); }
        }
        #endregion

        #region 2D drawing functions

        #region clear canvas

        public void Canvas_Clear()
        {
            Graphics DrawingArea = scan_panel.CreateGraphics();
            DrawingArea.Clear(Color.White);

        }

        #endregion

        #region Serpentine Scan Join Points
        public void Canvas_JoinPoints(int x1, int y1, int x2, int y2, int scale)
        {

            Graphics DrawingArea = scan_panel.CreateGraphics();

            Brush red = new SolidBrush(Color.Red);
            Pen redPen = new Pen(red, 2);

            int centreX = Convert.ToInt32(Decimal.Round(Convert.ToDecimal(scan_panel.Size.Width / 2.1)));
            int centreY = scan_panel.Size.Height / 2;

            int X1 = centreX + (scale * x1);
            int Y1 = centreY - (scale * y1);
            int X2 = centreX + (scale * x2);
            int Y2 = centreY - (scale * y2);


            DrawingArea.DrawLine(redPen, X1, Y1, X2, Y2);



        }
        #endregion



        #endregion

        #region Connection Events

        private void buttonConnect_Click(object sender, EventArgs e)
        {

            // All of this operation has been placed inside a single "catch-all"
            // exception handler. This is to reduce the size of the example code.
            // Normally you would have a try...catch per API call and catch the
            // specific exceptions that could be thrown (details of which can be
            // found in the Kinesis .NET API document).
            if (Globals.connection_flag)
            {
                MessageBox.Show("Device already connected");
                return;
            }

            try
            {
                // Instructs the DeviceManager to build and maintain the list of
                // devices connected.
                DeviceManagerCLI.BuildDeviceList();

               
                PiezoChannelOneConnect_Click(null, null);
                PiezoChannelTwoConnect_Click(null, null);
                PiezoChannelThreeConnect_Click(null, null);

                Globals.connection_flag = true;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to connect to device", "warning", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }
        public void PiezoChannelOneConnect_Click(object sender, EventArgs e)
        {
            if (_kCubePiezoX != null)
            {
                MessageBox.Show("Device already connected");
                return;
            }

            const string serialNumber = "29503069";

            // All of this operation has been placed inside a single "catch-all"
            // exception handler. This is to reduce the size of the example code.
            // Normally you would have a try...catch per API call and catch the
            // specific exceptions that could be thrown (details of which can be
            // found in the Kinesis .NET API document).
            try
            {
                // Instructs the DeviceManager to build and maintain the list of
                // devices connected.
                DeviceManagerCLI.BuildDeviceList();

                _kCubePiezoX = KCubePiezo.CreateKCubePiezo(serialNumber);

                // Establish a connection with the device.
                _kCubePiezoX.Connect(serialNumber);

                // Wait for the device settings to initialize. We ask the device to
                // throw an exception if this takes more than 5000ms (5s) to complete.
                _kCubePiezoX.WaitForSettingsInitialized(5000);

                // Initialize the DeviceUnitConverter object required for real world
                // unit parameters.
                _kCubePiezoX.GetPiezoConfiguration(serialNumber);

                // This starts polling the device at intervals of 250ms (0.25s).
                _kCubePiezoX.StartPolling(250);

                // We are now able to enable the device for commands.
                _kCubePiezoX.EnableDevice();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to connect to device\n" + ex);
            }
        }
        public void PiezoChannelTwoConnect_Click(object sender, EventArgs e)
        {

            if (_kCubePiezoY != null)
            {
                MessageBox.Show("Device already connected");
                return;
            }

            const string serialNumber = "29502895";

            // All of this operation has been placed inside a single "catch-all"
            // exception handler. This is to reduce the size of the example code.
            // Normally you would have a try...catch per API call and catch the
            // specific exceptions that could be thrown (details of which can be
            // found in the Kinesis .NET API document).
            try
            {
                // Instructs the DeviceManager to build and maintain the list of
                // devices connected.
                DeviceManagerCLI.BuildDeviceList();

                _kCubePiezoY = KCubePiezo.CreateKCubePiezo(serialNumber);

                // Establish a connection with the device.
                _kCubePiezoY.Connect(serialNumber);

                // Wait for the device settings to initialize. We ask the device to
                // throw an exception if this takes more than 5000ms (5s) to complete.
                _kCubePiezoY.WaitForSettingsInitialized(5000);

                // Initialize the DeviceUnitConverter object required for real world
                // unit parameters.
                _kCubePiezoY.GetPiezoConfiguration(serialNumber);

                // This starts polling the device at intervals of 250ms (0.25s).
                _kCubePiezoY.StartPolling(250);

                // We are now able to enable the device for commands.
                _kCubePiezoY.EnableDevice();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to connect to device\n" + ex);
            }
        }
        public void PiezoChannelThreeConnect_Click(object sender, EventArgs e)
        {
            if (_kCubePiezoZ != null)
            {
                MessageBox.Show("Device already connected");
                return;
            }

            const string serialNumber = "29000034";

            // All of this operation has been placed inside a single "catch-all"
            // exception handler. This is to reduce the size of the example code.
            // Normally you would have a try...catch per API call and catch the
            // specific exceptions that could be thrown (details of which can be
            // found in the Kinesis .NET API document).
            try
            {
                // Instructs the DeviceManager to build and maintain the list of
                // devices connected.
                DeviceManagerCLI.BuildDeviceList();

                _kCubePiezoZ = KCubePiezo.CreateKCubePiezo(serialNumber);

                // Establish a connection with the device.
                _kCubePiezoZ.Connect(serialNumber);

                // Wait for the device settings to initialize. We ask the device to
                // throw an exception if this takes more than 5000ms (5s) to complete.
                _kCubePiezoZ.WaitForSettingsInitialized(5000);

                // Initialize the DeviceUnitConverter object required for real world
                // unit parameters.
                _kCubePiezoZ.GetPiezoConfiguration(serialNumber);

                // This starts polling the device at intervals of 250ms (0.25s).
                _kCubePiezoZ.StartPolling(250);

                // We are now able to enable the device for commands.
                _kCubePiezoZ.EnableDevice();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to connect to device\n" + ex);
            }
        }

        public void PiezoChannelOneDisconnect_Click(object sender, EventArgs e)
        {
            if (_kCubePiezoX == null)
            {
                MessageBox.Show("Not connected to device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // Shuts down this device and frees any resources it is using.
                _kCubePiezoX.ShutDown();

                _kCubePiezoX = null;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to disconnect from device\n" + ex);
            }
        }
        public void PiezoChannelTwoDisconnect_Click(object sender, EventArgs e)
        {
            if (_kCubePiezoY == null)
            {
                MessageBox.Show("Not connected to device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // Shuts down this device and frees any resources it is using.
                _kCubePiezoY.ShutDown();

                _kCubePiezoY = null;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to disconnect from device\n" + ex);
            }
        }
        public void PiezoChannelThreeDisconnect_Click(object sender, EventArgs e)
        {
            if (_kCubePiezoZ == null)
            {
                MessageBox.Show("Not connected to device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // Shuts down this device and frees any resources it is using.
                _kCubePiezoZ.ShutDown();

                _kCubePiezoZ = null;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to disconnect from device\n" + ex);
            }
        }

        private void PiezoScan_FormClosed(object sender, FormClosedEventArgs e)
        {
            try
            {
                if (Globals.connection_flag)
                {
                    buttonDisonnect_Click(null, null);
                }
            }
            catch { }
        }
        private void buttonDisonnect_Click(object sender, EventArgs e)
        {

            // All of this operation has been placed inside a single "catch-all"
            // exception handler. This is to reduce the size of the example code.
            // Normally you would have a try...catch per API call and catch the
            // specific exceptions that could be thrown (details of which can be
            // found in the Kinesis .NET API document).
            if (!Globals.connection_flag)
            {
                MessageBox.Show("Device not connected");
                return;
            }

            try
            {

                PiezoChannelOneDisconnect_Click(null, null);
                PiezoChannelTwoDisconnect_Click(null, null);
                PiezoChannelThreeDisconnect_Click(null, null);

                Globals.connection_flag = false;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to connect to device", "warning", MessageBoxButtons.OK, MessageBoxIcon.Warning);

            }
        }

        #endregion



    }
}
