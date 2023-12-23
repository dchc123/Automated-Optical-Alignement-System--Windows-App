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
    public partial class StepperScan : Form
    {
        const string SerialNumber = "70184894";

        public BenchtopStepperMotor _benchtopStepperMotor = null;
        public StepperMotorChannel _stepperMotorChannelX = null;
        public StepperMotorChannel _stepperMotorChannelY = null;
        public StepperMotorChannel _stepperMotorChannelZ = null;

        MainForm mainform = new MainForm();

        public StepperScan()
        {
            InitializeComponent();
        }

        #region run scan and update info
        private void RunScan_Click(object sender, EventArgs e)
        {
            if (ConnectionCheckBox.Checked == true)
            {
                buttonConnect_Click(null, null);

            }

            // Open the named pipe.
            var server = new NamedPipeServerStream("NPtest");

            decimal minimum_step = 0.017m;

            
            decimal midpointx = Globals.Pos_X;
            decimal midpointy = Globals.Pos_Y;

            decimal EdgeLength = 0;
            decimal Scan_Resolution = 0;
            decimal MaxReadingsPerEdge = 0;
            int ReadingsPerEdge = 0;
            decimal Step_Size = 0;

            try
            {

                EdgeLength = Convert.ToDecimal(SideLengthInput.Text);
                if (0m > EdgeLength || 4m < EdgeLength) { throw new Exception(); }

                Scan_Resolution = Convert.ToDecimal(ScanResolutionInput.Text);
                if (0m > Scan_Resolution || 100m < Scan_Resolution) { throw new Exception(); }

                MaxReadingsPerEdge = Decimal.Round((Decimal)EdgeLength / minimum_step);
                ReadingsPerEdge = Convert.ToInt32(Decimal.Round(MaxReadingsPerEdge * (Scan_Resolution / 100)));
                if (ReadingsPerEdge % 2 == 0) { ReadingsPerEdge += 1; }
                Step_Size = (Decimal)EdgeLength / (Decimal)ReadingsPerEdge;

            }
            catch
            {
                MessageBox.Show("Ensure that the scan resolution is an integer/decimal and is between 0 and 100. Also ensure that the Edge Length is an integer/decimal and is between 0 and 20", "Warning", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                goto Finish;
            }


            if (ConnectionCheckBox.Checked)
            {
                if (Globals.Min_Stepper_Pos > (midpointx - (EdgeLength / 2)) || Globals.Max_Stepper_Pos < (midpointx + (EdgeLength / 2)))
                {
                    DialogResult dialog = MessageBox.Show("The scan area chosen it outwith the range of the X Channel Stepper Motor, the scan will automatically terminate once the motor is moved beyond its range. Results up to that point will still be shown.", "Warning", MessageBoxButtons.OKCancel, MessageBoxIcon.Warning);

                    if (dialog == DialogResult.Cancel)
                    {
                        goto Finish;
                    }
                }

                else if (Globals.Min_Stepper_Pos > (midpointy - (EdgeLength / 2)) || Globals.Max_Stepper_Pos < (midpointy + (EdgeLength / 2)))
                {
                    DialogResult dialog = MessageBox.Show("The scan area chosen it outwith the range of the Y Channel Stepper Motor, the scan will automatically terminate once the motor is moved beyond its range. Results up to that point will still be shown.", "Warning", MessageBoxButtons.OKCancel, MessageBoxIcon.Warning);

                    if (dialog == DialogResult.Cancel)
                    {
                        goto Finish;
                    }
                }
            }

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
            
            
            if (DummyCheckBox.Checked == false)
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

            if (ConnectionCheckBox.Checked == true)
            {
                Mode = 1;
            }
            else if (ConnectionCheckBox.Checked == false)
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

                    byte[] position = MainForm.ArrayPosition(MaxValue, MaxValue, array2Dc[i, 0], array2Dc[i, 1]);


                    decimal Xposition = MainForm.MotorPositions(midpointx, Step_Size, array2Dc[i, 0]);
                    decimal Yposition = MainForm.MotorPositions(midpointy, Step_Size, array2Dc[i, 1]);


                    if (ConnectionCheckBox.Checked)
                    {
                        if (Globals.Max_Stepper_Pos>Xposition && Globals.Min_Stepper_Pos<Xposition && Globals.Max_Stepper_Pos>Yposition && Globals.Min_Stepper_Pos<Yposition) 
                        { 
                            _stepperMotorChannelX.MoveTo(Xposition, 20000);
                            _stepperMotorChannelY.MoveTo(Yposition, 20000);

                            Globals.Pos_X = Xposition;
                            Globals.Pos_Y = Yposition;
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
            string ReadingsTotal = Convert.ToString(ReadingsPerEdge * ReadingsPerEdge);
            string StepSize = Convert.ToString(Decimal.Round(Step_Size, 5));

            string file_name = midpointx + "_" + midpointy + "_" + StepSize;
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
        
                
        private void ScanInfoUpdateButton_Click(object sender, EventArgs e)
        {
            try
            {
                decimal minimum_step = 0.017m;

                decimal EdgeLength = Convert.ToDecimal(SideLengthInput.Text);
                if (0m>EdgeLength || 4m < EdgeLength) { throw new Exception(); }

                decimal Scan_Resolution = Convert.ToDecimal(ScanResolutionInput.Text);
                if (0m > Scan_Resolution || 100m < Scan_Resolution) { throw new Exception(); }

                decimal MaxReadingsPerEdge = Decimal.Round((Decimal)EdgeLength / minimum_step);
                int ReadingsPerEdge = Convert.ToInt32(Decimal.Round(MaxReadingsPerEdge * (Scan_Resolution / 100)));
                decimal Step_Size = (Decimal)EdgeLength / (Decimal)ReadingsPerEdge;

                ScanTimeLabel.Text = Convert.ToString((ReadingsPerEdge * ReadingsPerEdge) / 100) + " mins";
                ReadingsTotalLabel.Text = Convert.ToString(ReadingsPerEdge * ReadingsPerEdge);
                StepSizeLabel.Text = Convert.ToString(Decimal.Round(Step_Size, 5));
            }
            catch { MessageBox.Show("Ensure that the scan resolution is an integer/decimal and is between 0 and 100. Also ensure that the Edge Length is an integer/decimal and is between 0 and 4", "Warning", MessageBoxButtons.OK, MessageBoxIcon.Warning); }
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

        public void buttonConnect_Click(object sender, EventArgs e)
        {
            if (Globals.connection_flag)
            {
                MessageBox.Show("Device already connected");
                return;
            }

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

                _benchtopStepperMotor = BenchtopStepperMotor.CreateBenchtopStepperMotor(SerialNumber);

                // Establish a connection with the device.
                _benchtopStepperMotor.Connect(SerialNumber);

                buttonChannelOneConnect_Click(sender, null);
                buttonChannelTwoConnect_Click(null, null);
                ButtonChannelThreeConnect_Click(null, null);

                Globals.connection_flag = true;

            }
            catch (Exception ex)
            {
                
                MessageBox.Show("Unable to connect to device", "warning", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                
            }
        }
        public void buttonChannelOneConnect_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelX != null)
            {
                MessageBox.Show("Device channel 1 already connected");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                _stepperMotorChannelX = _benchtopStepperMotor.GetChannel(1);

                // Wait for the device channel settings to initialize. We ask the
                // device to throw an exception if this takes more than 5000ms (5s)
                // to complete.
                _stepperMotorChannelX.WaitForSettingsInitialized(5000);

                // Initialize the DeviceUnitConverter object required for real world
                // unit parameters.
                MotorConfiguration motorConfigChannelOne = _stepperMotorChannelX.LoadMotorConfiguration(_stepperMotorChannelX.DeviceID);

                // This is how I ususally load device settings
                motorConfigChannelOne.LoadSettingsOption = DeviceSettingsSectionBase.SettingsUseOptionType.UseFileSettings;
                motorConfigChannelOne.DeviceSettingsName = "DRV208";
                motorConfigChannelOne.UpdateCurrentConfiguration();

                // This starts polling the device channel at intervals of 250ms (0.25s).
                _stepperMotorChannelX.StartPolling(250);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to connect to channel 1 on device\n" + ex);
            }
        }
        public void buttonChannelTwoConnect_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelY != null)
            {
                MessageBox.Show("Device channel 2 already connected");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                _stepperMotorChannelY = _benchtopStepperMotor.GetChannel(2);

                // Wait for the device channel settings to initialize. We ask the
                // device to throw an exception if this takes more than 5000ms (5s)
                // to complete.
                _stepperMotorChannelY.WaitForSettingsInitialized(5000);

                MotorConfiguration motorConfigChannelTwo = _stepperMotorChannelY.LoadMotorConfiguration(_stepperMotorChannelY.DeviceID);

                // This is how I ususally load device settings
                motorConfigChannelTwo.LoadSettingsOption = DeviceSettingsSectionBase.SettingsUseOptionType.UseFileSettings;
                motorConfigChannelTwo.DeviceSettingsName = "DRV208";
                motorConfigChannelTwo.UpdateCurrentConfiguration();

                // This starts polling the device channel at intervals of 250ms (0.25s).
                _stepperMotorChannelY.StartPolling(250);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to connect to channel 2 on device\n" + ex);
            }
        }
        public void ButtonChannelThreeConnect_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelZ != null)
            {
                MessageBox.Show("Device channel 3 already connected");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                _stepperMotorChannelZ = _benchtopStepperMotor.GetChannel(3);

                // Wait for the device channel settings to initialize. We ask the
                // device to throw an exception if this takes more than 5000ms (5s)
                // to complete.
                _stepperMotorChannelZ.WaitForSettingsInitialized(5000);

                MotorConfiguration motorConfigChannelThree = _stepperMotorChannelZ.LoadMotorConfiguration(_stepperMotorChannelZ.DeviceID);

                // This is how I ususally load device settings
                motorConfigChannelThree.LoadSettingsOption = DeviceSettingsSectionBase.SettingsUseOptionType.UseFileSettings;
                motorConfigChannelThree.DeviceSettingsName = "DRV208";
                motorConfigChannelThree.UpdateCurrentConfiguration();

                // This starts polling the device channel at intervals of 250ms (0.25s).
                _stepperMotorChannelZ.StartPolling(250);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to connect to channel 3 on device\n" + ex);
            }
        }

        public void buttonChannelOneDisconnect_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelX == null)
            {
                MessageBox.Show("Not connected to channel 1 on device");
                return;
            }

            _stepperMotorChannelX = null;
        }
        public void buttonChannelTwoDisconnect_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelY == null)
            {
                MessageBox.Show("Not connected to channel 2 on device");
                return;
            }

            _stepperMotorChannelY = null;
        }
        public void ButtonChannelThreeDisconnect_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelZ == null)
            {
                MessageBox.Show("Not connected to channel 3 on device");
                return;
            }

            _stepperMotorChannelZ = null;
        }

        private void buttonDisconnect_Click(object sender, EventArgs e)
        {
            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            if (!Globals.connection_flag)
            {
                MessageBox.Show("Device not connected");
                return;
            }

            try
            {
                // Shuts down this device and frees any resources it is using.
                buttonChannelOneDisconnect_Click(null, null);
                buttonChannelTwoDisconnect_Click(null, null);
                ButtonChannelThreeDisconnect_Click(null, null);

                Globals.connection_flag = false; 

                _benchtopStepperMotor.ShutDown();

                _benchtopStepperMotor = null;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to disconnect from device\n" + ex);
            }
        }
        private void StepperScan_FormClosed(object sender, FormClosedEventArgs e)
        {
            try
            {
                if (Globals.connection_flag)
                {
                    buttonDisconnect_Click(null, null);
                }
            }
            catch { }
        }


        #endregion


    }


}
