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
using System.Windows.Forms.Integration;

namespace Automated_Optical_Alignment
{
    public partial class MainForm : Form
    {
        const string SerialNumber = "70184894";

        public BenchtopStepperMotor _benchtopStepperMotor = null;
        public StepperMotorChannel _stepperMotorChannelX = null;
        public StepperMotorChannel _stepperMotorChannelY = null;
        public StepperMotorChannel _stepperMotorChannelZ = null;

        public KCubePiezo _kCubePiezoX = null;
        public KCubePiezo _kCubePiezoY = null;
        public KCubePiezo _kCubePiezoZ = null;

        PictureBox pb = new PictureBox();
        PictureBox pb_2 = new PictureBox();

        public MainForm()
        {
            InitializeComponent();

            Console.WriteLine("started");
                        
        }

     

        #region Events Handlers


        #region connect and disconnect

        private void buttonConnect_Click(object sender, EventArgs e)
        {
            if (Globals.connection_flag)
            {
                MessageBox.Show("Device already initialised");
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

                buttonChannelOneConnect_Click(null, null);
                buttonChannelTwoConnect_Click(null, null);
                ButtonChannelThreeConnect_Click(null, null);

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

        private void buttonDisconnect_Click(object sender, EventArgs e)
        {
            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                if (!Globals.connection_flag)
                {
                    throw new Exception();
                }

                // Shuts down this device and frees any resources it is using.
                buttonChannelOneDisconnect_Click(null, null);
                buttonChannelTwoDisconnect_Click(null, null);
                ButtonChannelThreeDisconnect_Click(null, null);

                PiezoChannelOneDisconnect_Click(null, null);
                PiezoChannelTwoDisconnect_Click(null, null);
                PiezoChannelThreeDisconnect_Click(null, null);

                Globals.connection_flag = false;

                _benchtopStepperMotor.ShutDown();

                _benchtopStepperMotor = null;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to disconnect from device", "warning", MessageBoxButtons.OK,MessageBoxIcon.Warning);
            }
        }

        #endregion

        #region Connect and Centre Motors

        private void Centre_Click(object sender, EventArgs e)
        {
            try
            {
                Console.WriteLine("Homing and Centering All Motors");

                _stepperMotorChannelX.SetVelocityParams(10m, 100);
                _stepperMotorChannelY.SetVelocityParams(10m, 100);
                _stepperMotorChannelZ.SetVelocityParams(10m, 100);

                _stepperMotorChannelX.Home(20000);
                _stepperMotorChannelY.Home(20000);
                _stepperMotorChannelZ.Home(20000);
                _stepperMotorChannelX.MoveTo(Globals.StepperXCentre, 20000);
                _stepperMotorChannelY.MoveTo(Globals.StepperYCentre, 20000);
                _stepperMotorChannelZ.MoveTo(Globals.StepperZCentre, 20000);

                _kCubePiezoX.SetOutputVoltage(35);
                _kCubePiezoY.SetOutputVoltage(35);
                _kCubePiezoZ.SetOutputVoltage(35);

            }
            catch(NullReferenceException ex)
            {
                MessageBox.Show("Make sure that all motor channels are connected and enabled before attempting to Home and Centre","warning",MessageBoxButtons.OK,MessageBoxIcon.Warning);

            }


        }

        #endregion

        private void Motor_Control_Panel_Click(object sender, EventArgs e)
        {
            if (Globals.connection_flag)
            {
                buttonDisconnect_Click(null, null);
            }
           
            var motor_control_panel = new MotorControlPanel();


            motor_control_panel.ShowDialog();
        }

        private void Stepper_Scan_Click(object sender, EventArgs e)
        {
            if (Globals.connection_flag)
            {
                buttonDisconnect_Click(null, null);
            }

            var steppper_scan_panel = new StepperScan();

            
            steppper_scan_panel.FormClosed += Single_Scan_Panel_FormClosed;

            steppper_scan_panel.ShowDialog();
        }

        private void Piezo_Scan_Click(object sender, EventArgs e)
        {
            if (Globals.connection_flag)
            {
                buttonDisconnect_Click(null, null);
            }

            var piezo_scan_panel = new PiezoScan();

            piezo_scan_panel.FormClosed += Single_Scan_Panel_FormClosed;

            piezo_scan_panel.ShowDialog();
        }

        private void Automatic_Scan_Click(object sender, EventArgs e)
        {
            var auto_scan_panel = new AutomaticScan();

            auto_scan_panel.Show();
        }

        private void Single_Scan_Panel_FormClosed(object sender, FormClosedEventArgs e)
        {
            string file_path = Directory.GetCurrentDirectory();
            string file_name = Globals.Results_File_Name;
            string full_path = file_path + @"\Results\CSV_Data\" + file_name;

            if (Results_Directory.Text != full_path)
            {
                Results_Directory.Text = full_path;

                if (full_path.Substring(full_path.Length - 9) != @"CSV_Data\")
                {
                    string ImageA_Path = file_path + @"\Results\JPG_data\" + file_name + ".jpg";
                    string ImageB_Path = file_path + @"\Results\JPG_data\" + file_name + @"_ViewB.jpg";

                    while (true)
                    {
                        try
                        {
                            pb.Load(ImageA_Path);
                            pb_2.Load(ImageB_Path);
                            break;
                        }
                        catch
                        {

                        }
                    }
                }

            }

        }

        public void MainForm_Load(object sender, EventArgs e)
        {
            string OpeningFile = @"0.0100009155552842666666666667_0.0099996948149052266666666667_0.001";
            Globals.Results_File_Name = OpeningFile;


            pb.Location = new Point(300, 75);
            pb.Size = new Size(425, 350);
            pb.ImageLocation = @"Results/JPG_Data/"+OpeningFile+".jpg";
            pb.SizeMode = PictureBoxSizeMode.StretchImage;
            pb.BorderStyle = BorderStyle.Fixed3D;
            pb.Visible = true;
            this.Controls.Add(pb);


            pb_2.Location = new Point(730, 75);
            pb_2.Size = new Size(425, 350);
            pb_2.ImageLocation = @"Results/JPG_Data/" + OpeningFile + "_ViewB.jpg";
            pb_2.SizeMode = PictureBoxSizeMode.StretchImage;
            pb_2.BorderStyle = BorderStyle.Fixed3D;
            pb_2.Visible = true;
            this.Controls.Add(pb_2);

            Globals.Serpent();

            string file_path = Directory.GetCurrentDirectory();
            
            string full_path = file_path + @"\Results\JPG_Data\"+OpeningFile;
            Results_Directory.Text = full_path;

            GPIBAddress.Text = File.ReadAllText(@"GPIBAddress.txt");
        }

        private void ExpandIsometric_Click(object sender, EventArgs e)
        {
            var server = new NamedPipeServerStream("NPtest");

            Console.WriteLine("Waiting for connection...");
            string fileName = @"ShowIsometric.py";

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

            server.WaitForConnection();
            Console.WriteLine("Connected.");

            var br = new BinaryReader(server);
            var bw = new BinaryWriter(server);

            byte[] file_name_bytes = Encoding.ASCII.GetBytes(Globals.Results_File_Name);
            byte file_name_size = Convert.ToByte(file_name_bytes.Length);

            bw.Write(file_name_size);
            bw.Write(file_name_bytes);

            Console.WriteLine("Client disconnected.");
            server.Close();
            server.Dispose();

            
        }

        private void Expand_Button_Click(object sender, EventArgs e)
        {
            var server = new NamedPipeServerStream("NPtest");

            Console.WriteLine("Waiting for connection...");
            string fileName = @"ShowArial.py";

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

            server.WaitForConnection();
            Console.WriteLine("Connected.");

            var br = new BinaryReader(server);
            var bw = new BinaryWriter(server);

            byte[] file_name_bytes = Encoding.ASCII.GetBytes(Globals.Results_File_Name);
            byte file_name_size = Convert.ToByte(file_name_bytes.Length);

            bw.Write(file_name_size);
            bw.Write(file_name_bytes);

            Console.WriteLine("Client disconnected.");
            server.Close();
            server.Dispose();
        }

        private void UpdateGPIB_Click(object sender, EventArgs e)
        {
            File.WriteAllText(@"GPIBAddress.txt", GPIBAddress.Text);
        }

        #endregion


        #region Extra functions

        #region unit conversion

        public static decimal Pos2Volt(decimal position)
        {
            decimal max_position = 0.02m;
            decimal max_voltage = 75;
            decimal scaling_factor = max_voltage / max_position;

            decimal voltage = (position) * scaling_factor;
            return voltage;
        }
        public static decimal Volt2Pos(decimal voltage)
        {
            decimal max_position = 0.02m;
            decimal max_voltage = 75;
            decimal scaling_factor = max_voltage / max_position;

            decimal position = (voltage) / scaling_factor;
            return position;
        }

        #endregion

        #region Motor position function

        public static decimal MotorPositions(decimal midpoint, decimal Step_Size, int array_position)
        {
            decimal position = midpoint + Step_Size * array_position;

            return position;
        }
        #endregion

        #region Array position funcion
        public static byte[] ArrayPosition(int MaxValueX, int MaxValueY, int array_position_X, int array_position_Y)
        {

            int x1 = (array_position_X + (MaxValueX));
            int y1 = (array_position_Y + (MaxValueY));

            byte X1 = Convert.ToByte(x1);
            byte Y1 = Convert.ToByte(y1);

            byte[] position = new byte[2];
            position[0] = X1;
            position[1] = Y1;
            

            return position;
        }

        #endregion

        #region move on check
        public static bool move_on_check(byte[] current_reading)
        {
            if (current_reading[0] == 107 & current_reading[1] == 105 & current_reading[2] == 108 & current_reading[3] == 108) //if move on command received
            {
                return true;
            }
            return false;
        }

        #endregion

        #region Connection Events

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





        #endregion

        #endregion

        
    }

    static class Globals
    {
        public static decimal Pos_X = 5.435m;
        public static decimal Pos_Y = 5.165m;
        public static decimal Pos_Z = 5.355m;
        public static decimal Min_Stepper_Pos = 2.5m;
        public static decimal Max_Stepper_Pos = 7.5m;
        public static decimal Min_Piezo_Pos = 0m;
        public static decimal Max_Piezo_Pos = 0.02m;
        public static bool connection_flag = false;
        public static decimal StepperXCentre = 5.435m;
        public static decimal StepperYCentre = 5.165m;
        public static decimal StepperZCentre = 5.33m;
        public static string Results_File_Name = "";
        public static int shape = 300;
        public static int length = 500;
        public static int length2 = 100000;
        public static int iterator1 = 1;
        public static int iterator2 = 2;
        public static int iterator3 = 1;
        public static int iterator4 = 2;
        public static int[,] array2D = new int[length, 2];
        public static int[,] array2Db = new int[length2, 2];
        public static int[,] array2Dc = new int[shape * shape, 2];
        public static int extra_element_counter = 0;
        public static int offset = 0;

        public static void Serpent()
        {

            for (int j = 0; j < length; j++)
            {
                if ((j % 2) == 0)
                {
                    if ((j % 4) == 0)
                    {

                        int next_val = array2D[j, 0] + iterator1;

                        for (int i = j; i < (array2D.Length / 2) - 1; i++)
                        {
                            array2D[i + 1, 0] = next_val;
                        }

                        iterator1 += 2;
                    }
                    else
                    {

                        int next_val = array2D[j, 0] - iterator2;

                        for (int i = j; i < (array2D.Length / 2) - 1; i++)
                        {
                            array2D[i + 1, 0] = next_val;
                        }

                        iterator2 += 2;
                    }
                }

                if ((j % 2) != 0)
                {
                    if ((j % 4) == 1)
                    {

                        int next_val = array2D[j, 1] + iterator3;

                        for (int i = j; i < (array2D.Length / 2) - 1; i++)
                        {
                            array2D[i + 1, 1] = next_val;
                        }

                        iterator3 += 2;
                    }
                    else
                    {

                        int next_val = array2D[j, 1] - iterator4;

                        for (int i = j; i < (array2D.Length / 2) - 1; i++)
                        {
                            array2D[i + 1, 1] = next_val;
                        }

                        iterator4 += 2;
                    }
                }

            }

            array2Db = new int[length2, 2];

            for (int i = 0; i < length - 1; i++)
            {
                int differenceX = Math.Abs(array2D[i, 0] - array2D[i + 1, 0]);
                int differenceY = Math.Abs(array2D[i, 1] - array2D[i + 1, 1]);

                if (differenceX > 1)
                {
                    array2Db[i + extra_element_counter, 0] = array2D[i, 0];
                    array2Db[i + extra_element_counter, 1] = array2D[i, 1];
                    offset = extra_element_counter;

                    for (int j = 1; j < differenceX; j++)
                    {
                        if (array2D[i, 0] < array2D[i + 1, 0])
                        {

                            array2Db[i + j + offset, 0] = array2D[i, 0] + j;
                            array2Db[i + j + offset, 1] = array2D[i, 1];
                        }

                        if (array2D[i, 0] > array2D[i + 1, 0])
                        {

                            array2Db[i + j + offset, 0] = array2D[i, 0] - j;
                            array2Db[i + j + offset, 1] = array2D[i, 1];
                        }
                    }
                    extra_element_counter += differenceX - 1;
                }
                else if (differenceY > 1)
                {

                    array2Db[i + extra_element_counter, 0] = array2D[i, 0];
                    array2Db[i + extra_element_counter, 1] = array2D[i, 1];
                    offset = extra_element_counter;

                    for (int j = 1; j < differenceY; j++)
                    {
                        if (array2D[i, 1] < array2D[i + 1, 1])
                        {
                            array2Db[i + j + offset, 1] = array2D[i, 1] + j;
                            array2Db[i + j + offset, 0] = array2D[i, 0];
                        }

                        if (array2D[i, 1] > array2D[i + 1, 1])
                        {
                            array2Db[i + j + offset, 1] = array2D[i, 1] - j;
                            array2Db[i + j + offset, 0] = array2D[i, 0];
                        }
                    }
                    extra_element_counter += differenceY - 1;
                }
                else
                {
                    array2Db[i, 0] = array2D[i, 0];
                    array2Db[i, 1] = array2D[i, 1];
                }

            }

            return;
        }

        public static void Serpent2(int shape)
        {
            array2Dc = new int[shape * shape, 2];

            for (int k = 0; k < shape * shape; k++)
            {
                for (int j = 0; j < 2; j++)
                {
                    array2Dc[k, j] = array2Db[k, j];
                }
            }

            return;
        }

        // global function
        public static int[,] Serpentine()
        {

            return array2Dc;
        }
    }

}