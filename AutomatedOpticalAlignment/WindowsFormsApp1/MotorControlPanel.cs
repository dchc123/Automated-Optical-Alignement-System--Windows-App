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
using System;
using System.Collections.Generic;
using System.Drawing.Drawing2D;
using System.Windows.Forms;
using System.Linq;
using System.Text;

namespace Automated_Optical_Alignment
{
    public partial class MotorControlPanel : Form
    {
        const string SerialNumber = "70184894";

        private BenchtopStepperMotor _benchtopStepperMotor = null;
        private StepperMotorChannel _stepperMotorChannelX = null;
        private StepperMotorChannel _stepperMotorChannelY = null;
        private StepperMotorChannel _stepperMotorChannelZ = null;

        private KCubePiezo _kCubePiezoX = null;
        private KCubePiezo _kCubePiezoY = null;
        private KCubePiezo _kCubePiezoZ = null;

        

        public MotorControlPanel()
        {
            InitializeComponent();

            Round_Buttons();
            
            try
            {
                buttonConnect_Click(null, null);
            }
            catch { MessageBox.Show("Make sure all hardware is connected before attempting to operate", "Warning", MessageBoxButtons.OK, MessageBoxIcon.Warning); }
        }


        #region other functions
        private void buttonConnect_Click(object sender, EventArgs e)
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

        private void buttonDisonnect_Click(object sender, EventArgs e)
        {
            if (!Globals.connection_flag)
            {
                MessageBox.Show("Not connected to device");
                return;
            }
            // All of this operation has been placed inside a single "catch-all"
            // exception handler. This is to reduce the size of the example code.
            // Normally you would have a try...catch per API call and catch the
            // specific exceptions that could be thrown (details of which can be
            // found in the Kinesis .NET API document).
            try
            {
                

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
                
                 MessageBox.Show("Unable to disconnect from device", "warning", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                
            }
        }

        public void Round_Buttons()
        {
            GraphicsPath p = new GraphicsPath();
            p.AddEllipse(1, 1, StepperHomeZ.Width - 4, StepperHomeZ.Height - 4);

            StepperHomeZ.Region = new Region(p);
            StepperHomeXY.Region = new Region(p);
            PiezoHomeZ.Region = new Region(p);
            PiezoHomeXY.Region = new Region(p);

        }

        private void StepperHomeXY_Click(object sender, EventArgs e)
        {
            try
            {

                _stepperMotorChannelX.MoveTo(Globals.StepperXCentre, 20000);
                _stepperMotorChannelY.MoveTo(Globals.StepperYCentre, 20000);

                Globals.Pos_X = Globals.StepperXCentre;
                Globals.Pos_Y = Globals.StepperYCentre;

            }
            catch { MessageBox.Show("Make sure that the channel is connected,enabled and the position provided is within the motor range", "warning", MessageBoxButtons.OK, MessageBoxIcon.Warning); }
        }

        private void PiezoHomeXY_Click(object sender, EventArgs e)
        {
            try
            {

                decimal voltage = 37.5m;

                _kCubePiezoX.SetOutputVoltage(voltage);
                _kCubePiezoY.SetOutputVoltage(voltage);

            }
            catch { MessageBox.Show("Make sure that the channel is connected,enabled and the position provided is within the motor range", "warning", MessageBoxButtons.OK, MessageBoxIcon.Warning); }
        }

        private void MotorControlPanel_FormClosed(object sender, FormClosedEventArgs e)
        {
            try
            {
                if (Globals.connection_flag) { buttonDisonnect_Click(null, null); }

            }
            catch { }
        }

        private void MotorControlPanel_Load(object sender, EventArgs e)
        {
            StepperPosLabelX.Text = Globals.Pos_X.ToString();
            StepperPosLabelY.Text = Globals.Pos_Y.ToString();
            StepperPosLabelZ.Text = Globals.Pos_Z.ToString();

        }

        private void UpdateStepperX_Click(object sender, EventArgs e)
        {
            StepperPosLabelX.Text = Globals.Pos_X.ToString();

        }

        private void UpdateStepperY_Click(object sender, EventArgs e)
        {
            StepperPosLabelY.Text = Globals.Pos_Y.ToString();

        }

        private void UpdateStepperZ_Click(object sender, EventArgs e)
        {
            StepperPosLabelZ.Text = Globals.Pos_Z.ToString();
        }

        #endregion  


        #region Channel 1 - Piezo

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

        public void GetHVOutChannelOne_Click(object sender, EventArgs e)
        {
            try
            {
                decimal reading = _kCubePiezoX.GetOutputVoltage();
                labelGetHVOUTResultChannelOne.Text = reading.ToString(CultureInfo.CurrentUICulture);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to get a reading\n" + ex);
            }
        }

        public void HVOutIncrementDownChannelOne_Click(object sender, EventArgs e)
        {
            try
            {
                decimal small_Step = Convert.ToDecimal(PiezoSmallStep.Text);

                decimal reading = _kCubePiezoX.GetOutputVoltage() - small_Step;

                _kCubePiezoX.SetOutputVoltage(reading);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to set HV OUT\n" + ex);
            }
        }

        public void HVOutIncrementUpChannelOne_Click(object sender, EventArgs e)
        {
            try
            {
                decimal small_Step = Convert.ToDecimal(PiezoSmallStep.Text);

                decimal reading = _kCubePiezoX.GetOutputVoltage() + small_Step;

                _kCubePiezoX.SetOutputVoltage(reading);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to set HV OUT\n" + ex);
            }
        }

        private void PiezoChannelXJumpForwards_Click(object sender, EventArgs e)
        {
            try
            {
                decimal big_Step = Convert.ToDecimal(PiezoBigStep.Text);

                decimal reading = _kCubePiezoX.GetOutputVoltage() + big_Step;

                _kCubePiezoX.SetOutputVoltage(reading);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to set HV OUT\n" + ex);
            }
        }

        private void PiezoChannelXJumpBackwards_Click(object sender, EventArgs e)
        {
            try
            {
                decimal big_Step = Convert.ToDecimal(PiezoBigStep.Text);

                decimal reading = _kCubePiezoX.GetOutputVoltage() - big_Step;

                _kCubePiezoX.SetOutputVoltage(reading);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to set HV OUT\n" + ex);
            }
        }

        private void PiezoChannelXMoveTo_Click(object sender, EventArgs e)
        {
            try
            {
                decimal position = Convert.ToDecimal(PiezoMoveToX.Text);

                if (position>Globals.Max_Piezo_Pos || position < Globals.Min_Piezo_Pos)
                {
                    throw new Exception();
                }

                decimal voltage = MainForm.Pos2Volt(position);

                _kCubePiezoX.SetOutputVoltage(voltage);

            }
            catch 
            { MessageBox.Show("Make sure that the channel is connected,enabled and the position provided is within the motor range", "warning", MessageBoxButtons.OK, MessageBoxIcon.Warning); }
        }

        #endregion

        #region Channel 2 - Piezo

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

        public void GetHVOutChannelTwo_Click(object sender, EventArgs e)
        {
            try
            {
                decimal reading = _kCubePiezoY.GetOutputVoltage();
                labelGetHVOUTResultChannelTwo.Text = reading.ToString(CultureInfo.CurrentUICulture);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to get a reading\n" + ex);
            }
        }

        public void HVOutIncrementDownChannelTwo_Click(object sender, EventArgs e)
        {
            try
            {
                decimal small_Step = Convert.ToDecimal(PiezoSmallStep.Text);

                decimal reading = _kCubePiezoY.GetOutputVoltage() - small_Step;

                _kCubePiezoY.SetOutputVoltage(reading);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to set HV OUT\n" + ex);
            }
        }

        public void HVOutIncrementUpChannelTwo_Click(object sender, EventArgs e)
        {
            try
            {
                decimal small_Step = Convert.ToDecimal(PiezoSmallStep.Text);

                decimal reading = _kCubePiezoY.GetOutputVoltage() + small_Step;

                _kCubePiezoY.SetOutputVoltage(reading);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to set HV OUT\n" + ex);
            }
        }

        private void PiezoChannelYJumpForwards_Click(object sender, EventArgs e)
        {
            try
            {
                decimal big_Step = Convert.ToDecimal(PiezoBigStep.Text);

                decimal reading = _kCubePiezoY.GetOutputVoltage() + big_Step;

                _kCubePiezoY.SetOutputVoltage(reading);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to set HV OUT\n" + ex);
            }
        }

        private void PiezoChannelYJumpBackwards_Click(object sender, EventArgs e)
        {
            try
            {
                decimal big_Step = Convert.ToDecimal(PiezoBigStep.Text);

                decimal reading = _kCubePiezoY.GetOutputVoltage() - big_Step;

                _kCubePiezoY.SetOutputVoltage(reading);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to set HV OUT\n" + ex);
            }
        }

        private void PiezoChannelYMoveTo_Click(object sender, EventArgs e)
        {

            try
            {
                decimal position = Convert.ToDecimal(PiezoMoveToY.Text);

                if (position > Globals.Max_Piezo_Pos || position < Globals.Min_Piezo_Pos)
                {
                    throw new Exception();
                }

                decimal voltage = MainForm.Pos2Volt(position);

                _kCubePiezoY.SetOutputVoltage(voltage);

            }
            catch { MessageBox.Show("Make sure that the channel is connected,enabled and the position provided is within the motor range", "warning", MessageBoxButtons.OK, MessageBoxIcon.Warning); }
        }

        #endregion

        #region Channel 3 - Piezo

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

        public void GetHVOutChannelThree_Click(object sender, EventArgs e)
        {
            try
            {
                decimal reading = _kCubePiezoZ.GetOutputVoltage();
                labelGetHVOUTResultChannelThree.Text = reading.ToString(CultureInfo.CurrentUICulture);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to get a reading\n" + ex);
            }
        }

        public void HVOutIncrementDownChannelThree_Click(object sender, EventArgs e)
        {
            try
            {
                decimal small_Step = Convert.ToDecimal(PiezoSmallStep.Text);

                decimal reading = _kCubePiezoZ.GetOutputVoltage() - small_Step;

                _kCubePiezoZ.SetOutputVoltage(reading);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to set HV OUT\n" + ex);
            }
        }

        public void HVOutIncrementUpChannelThree_Click(object sender, EventArgs e)
        {
            try
            {
                decimal small_Step = Convert.ToDecimal(PiezoSmallStep.Text);

                decimal reading = _kCubePiezoZ.GetOutputVoltage() + small_Step;

                _kCubePiezoZ.SetOutputVoltage(reading);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to set HV OUT\n" + ex);
            }
        }

        private void PiezoChannelZJumpForwards_Click(object sender, EventArgs e)
        {
            try
            {
                decimal big_Step = Convert.ToDecimal(PiezoBigStep.Text);

                decimal reading = _kCubePiezoZ.GetOutputVoltage() + big_Step;

                _kCubePiezoZ.SetOutputVoltage(reading);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to set HV OUT\n" + ex);
            }
        }

        private void PiezoChannelZJumpBackwards_Click(object sender, EventArgs e)
        {
            try
            {
                decimal big_Step = Convert.ToDecimal(PiezoBigStep.Text);

                decimal reading = _kCubePiezoZ.GetOutputVoltage() - big_Step;

                _kCubePiezoZ.SetOutputVoltage(reading);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to set HV OUT\n" + ex);
            }
        }

        private void PiezoChannelZMoveTo_Click(object sender, EventArgs e)
        {

            try
            {
                decimal position = Convert.ToDecimal(PiezoMoveToZ.Text);

                if (position > Globals.Max_Piezo_Pos || position < Globals.Min_Piezo_Pos)
                {
                    throw new Exception();
                }

                decimal voltage = MainForm.Pos2Volt(position);

                _kCubePiezoZ.SetOutputVoltage(voltage);

            }
            catch { MessageBox.Show("Make sure that the channel is connected,enabled and the position provided is within the motor range", "warning", MessageBoxButtons.OK, MessageBoxIcon.Warning); }
        }

        private void PiezoHomeZ_Click(object sender, EventArgs e)
        {
            try
            {

                decimal voltage = 37.5m;

                _kCubePiezoZ.SetOutputVoltage(voltage);

            }
            catch { MessageBox.Show("Make sure that the channel is connected,enabled and the position provided is within the motor range", "warning", MessageBoxButtons.OK, MessageBoxIcon.Warning); }
        }
        #endregion



        #region Channel 1 - stepper

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

        public void buttonChannelOneDisconnect_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelX == null)
            {
                MessageBox.Show("Not connected to channel 1 on device");
                return;
            }

            _stepperMotorChannelX = null;
        }

        public void buttonChannelOneEnable_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelX == null)
            {
                MessageBox.Show("Not connected to channel 1 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                _stepperMotorChannelX.EnableDevice();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to enable channel 1 on device\n" + ex);
            }
        }

        public void buttonChannelOneDisable_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelX == null)
            {
                MessageBox.Show("Not connected to channel 1 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                _stepperMotorChannelX.DisableDevice();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to disable channel 1 on device\n" + ex);
            }
        }

        public void buttonChannelOneHome_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelX == null)
            {
                MessageBox.Show("Not connected to channel 1 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // We ask the device to throw an exception if the operation takes
                // longer than 20,000ms (20s).


                _stepperMotorChannelX.MoveTo(Globals.StepperXCentre, 20000);
                Globals.Pos_X = Globals.StepperXCentre;
                UpdateStepperX_Click(null, null);

            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to home channel 1 on device\n" + ex);
            }
        }

        public void ChannelOneStepBackwards_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelX == null)
            {
                MessageBox.Show("Not connected to channel 1 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // We ask the device to throw an exception if the operation takes
                // longer than 20,000ms (20s).

                _stepperMotorChannelX.SetVelocityParams(0.5m, 5);

                decimal small_step = Convert.ToDecimal(StepperSmallStep.Text);

                _stepperMotorChannelX.MoveRelative(Thorlabs.MotionControl.GenericMotorCLI.MotorDirection.Backward, small_step, 20000);

                Globals.Pos_X -= small_step;
                UpdateStepperX_Click(null, null);

            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to move channel 3 on device\n" + ex);
            }
        }

        public void ChannelOneStepForwards_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelX == null)
            {
                MessageBox.Show("Not connected to channel 1 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // We ask the device to throw an exception if the operation takes
                // longer than 20,000ms (20s).
                // Is actually going to move to 5mm not 10mm since the DRV208 has 8mm of travel

                _stepperMotorChannelX.SetVelocityParams(0.5m, 5);

                decimal small_step = Convert.ToDecimal(StepperSmallStep.Text);

                _stepperMotorChannelX.MoveRelative(Thorlabs.MotionControl.GenericMotorCLI.MotorDirection.Forward, small_step, 20000);

                Globals.Pos_X += small_step;
                UpdateStepperX_Click(null, null);

            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to move channel 3 on device\n" + ex);
            }
        }

        private void StepperChannelXJumpForwards_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelX == null)
            {
                MessageBox.Show("Not connected to channel 1 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // We ask the device to throw an exception if the operation takes
                // longer than 20,000ms (20s).
                // Is actually going to move to 5mm not 10mm since the DRV208 has 8mm of travel

                _stepperMotorChannelX.SetVelocityParams(0.5m, 5);

                decimal big_step = Convert.ToDecimal(StepperBigStep.Text);

                _stepperMotorChannelX.MoveRelative(Thorlabs.MotionControl.GenericMotorCLI.MotorDirection.Forward, big_step, 20000);

                Globals.Pos_X += big_step;
                UpdateStepperX_Click(null, null);

            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to move channel 3 on device\n" + ex);
            }
        }

        private void StepperChannelXJumpBackwards_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelX == null)
            {
                MessageBox.Show("Not connected to channel 1 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // We ask the device to throw an exception if the operation takes
                // longer than 20,000ms (20s).

                _stepperMotorChannelX.SetVelocityParams(0.5m, 5);

                decimal big_step = Convert.ToDecimal(StepperBigStep.Text);

                _stepperMotorChannelX.MoveRelative(Thorlabs.MotionControl.GenericMotorCLI.MotorDirection.Backward, big_step, 20000);

                Globals.Pos_X += big_step;
                UpdateStepperX_Click(null, null);


            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to move channel 3 on device\n" + ex);
            }
        }

        private void StepperChannelXMoveTo_Click(object sender, EventArgs e)
        {
            try
            {
                decimal position = Convert.ToDecimal(StepperMoveToX.Text);

                _stepperMotorChannelX.MoveTo(position, 20000);

                Globals.Pos_X = position;
                UpdateStepperX_Click(null, null);

            }
            catch { MessageBox.Show("Make sure that the channel is connected,enabled and the position provided is within the motor range", "warning", MessageBoxButtons.OK, MessageBoxIcon.Warning); }
        }
        #endregion

        #region Channel 2 - stepper

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

        public void buttonChannelTwoDisconnect_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelY == null)
            {
                MessageBox.Show("Not connected to channel 2 on device");
                return;
            }

            _stepperMotorChannelY = null;
        }

        public void buttonChannelTwoEnable_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelY == null)
            {
                MessageBox.Show("Not connected to channel 2 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                _stepperMotorChannelY.EnableDevice();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to enable channel 2 on device\n" + ex);
            }
        }

        public void buttonChannelTwoDisable_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelY == null)
            {
                MessageBox.Show("Not connected to channel 2 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                _stepperMotorChannelY.DisableDevice();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to disable channel 2 on device\n" + ex);
            }
        }

        public void buttonChannelTwoHome_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelY == null)
            {
                MessageBox.Show("Not connected to channel 2 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // We ask the device to throw an exception if the operation takes
                // longer than 20,000ms (20s).

                _stepperMotorChannelY.SetVelocityParams(0.5m, 5);
                _stepperMotorChannelY.MoveTo(Globals.StepperYCentre, 20000);

                Globals.Pos_Y = Globals.StepperYCentre;
                UpdateStepperY_Click(null, null);

            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to home channel 2 on device\n" + ex);
            }
        }

        public void ChannelTwoStepBackwards_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelY == null)
            {
                MessageBox.Show("Not connected to channel 2 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // We ask the device to throw an exception if the operation takes
                // longer than 20,000ms (20s).

                _stepperMotorChannelY.SetVelocityParams(0.5m, 5);

                decimal small_step = Convert.ToDecimal(StepperSmallStep.Text);

                _stepperMotorChannelY.MoveRelative(Thorlabs.MotionControl.GenericMotorCLI.MotorDirection.Backward, small_step, 20000);

                Globals.Pos_Y -= small_step;
                UpdateStepperY_Click(null, null);

            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to move channel 2 on device\n" + ex);
            }
        }

        public void ChannelTwoStepForwards_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelY == null)
            {
                MessageBox.Show("Not connected to channel 2 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // We ask the device to throw an exception if the operation takes
                // longer than 20,000ms (20s).
                // Is actually going to move to 5mm not 10mm since the DRV208 has 8mm of travel

                _stepperMotorChannelY.SetVelocityParams(0.5m, 5);

                decimal small_step = Convert.ToDecimal(StepperSmallStep.Text);

                _stepperMotorChannelY.MoveRelative(Thorlabs.MotionControl.GenericMotorCLI.MotorDirection.Forward, small_step, 20000);

                Globals.Pos_Y += small_step;
                UpdateStepperY_Click(null, null);


            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to move channel 2 on device\n" + ex);
            }
        }

        private void StepperChannelYJumpForwards_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelY == null)
            {
                MessageBox.Show("Not connected to channel 2 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // We ask the device to throw an exception if the operation takes
                // longer than 20,000ms (20s).
                // Is actually going to move to 5mm not 10mm since the DRV208 has 8mm of travel

                _stepperMotorChannelY.SetVelocityParams(0.5m, 5);

                decimal big_step = Convert.ToDecimal(StepperBigStep.Text);

                _stepperMotorChannelY.MoveRelative(Thorlabs.MotionControl.GenericMotorCLI.MotorDirection.Forward, big_step, 20000);

                Globals.Pos_Y += big_step;
                UpdateStepperY_Click(null, null);


            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to move channel 3 on device\n" + ex);
            }
        }

        private void StepperChannelYJumpBackwards_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelY == null)
            {
                MessageBox.Show("Not connected to channel 2 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // We ask the device to throw an exception if the operation takes
                // longer than 20,000ms (20s).

                _stepperMotorChannelY.SetVelocityParams(0.5m, 5);

                decimal big_step = Convert.ToDecimal(StepperBigStep.Text);

                _stepperMotorChannelY.MoveRelative(Thorlabs.MotionControl.GenericMotorCLI.MotorDirection.Backward, big_step, 20000);

                Globals.Pos_Y -= big_step;
                UpdateStepperY_Click(null, null);


            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to move channel 3 on device\n" + ex);
            }
        }

        private void StepperChannelYMoveTo_Click(object sender, EventArgs e)
        {
            try
            {
                decimal position = Convert.ToDecimal(StepperMoveToY.Text);

                _stepperMotorChannelY.MoveTo(position, 20000);

                Globals.Pos_Y = position;
                UpdateStepperY_Click(null, null);


            }
            catch { MessageBox.Show("Make sure that the channel is connected,enabled and the position provided is within the motor range", "warning", MessageBoxButtons.OK, MessageBoxIcon.Warning); }
        }

        #endregion

        #region Channel 3 - stepper

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

        public void ButtonChannelThreeDisconnect_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelZ == null)
            {
                MessageBox.Show("Not connected to channel 3 on device");
                return;
            }

            _stepperMotorChannelZ = null;
        }

        public void ButtonChannelThreeEnable_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelZ == null)
            {
                MessageBox.Show("Not connected to channel 3 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                _stepperMotorChannelZ.EnableDevice();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to enable channel 3 on device\n" + ex);
            }
        }

        public void ButtonChannelThreeDisable_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelZ == null)
            {
                MessageBox.Show("Not connected to channel 3 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                _stepperMotorChannelZ.DisableDevice();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to disable channel 3 on device\n" + ex);
            }
        }

        public void ButtonChannelThreeHome_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelZ == null)
            {
                MessageBox.Show("Not connected to channel 3 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // We ask the device to throw an exception if the operation takes
                // longer than 20,000ms (20s).

                _stepperMotorChannelZ.SetVelocityParams(0.5m, 5);
                _stepperMotorChannelZ.MoveTo(0m, 20000);

                Globals.Pos_Z = Globals.StepperYCentre;
                UpdateStepperZ_Click(null, null);

            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to home channel 3 on device\n" + ex);
            }
        }

        public void ChannelThreeStepBackwards_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelZ == null)
            {
                MessageBox.Show("Not connected to channel 3 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // We ask the device to throw an exception if the operation takes
                // longer than 20,000ms (20s).

                _stepperMotorChannelZ.SetVelocityParams(0.5m, 5);

                decimal small_step = Convert.ToDecimal(StepperSmallStep.Text);

                _stepperMotorChannelZ.MoveRelative(Thorlabs.MotionControl.GenericMotorCLI.MotorDirection.Backward, small_step, 20000);

                Globals.Pos_Z -= small_step;
                UpdateStepperZ_Click(null, null);

            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to move channel 3 on device\n" + ex);
            }
        }

        public void ChannelThreeStepForwards_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelZ == null)
            {
                MessageBox.Show("Not connected to channel 3 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // We ask the device to throw an exception if the operation takes
                // longer than 20,000ms (20s).
                // Is actually going to move to 5mm not 10mm since the DRV208 has 8mm of travel

                _stepperMotorChannelZ.SetVelocityParams(0.5m, 5);

                decimal small_step = Convert.ToDecimal(StepperSmallStep.Text);

                _stepperMotorChannelZ.MoveRelative(Thorlabs.MotionControl.GenericMotorCLI.MotorDirection.Forward, small_step, 20000);

                Globals.Pos_Z += small_step;
                UpdateStepperZ_Click(null, null);

            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to move channel 3 on device\n" + ex);
            }
        }

        private void StepperChannelZJumpForwards_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelZ == null)
            {
                MessageBox.Show("Not connected to channel 3 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // We ask the device to throw an exception if the operation takes
                // longer than 20,000ms (20s).
                // Is actually going to move to 5mm not 10mm since the DRV208 has 8mm of travel

                _stepperMotorChannelZ.SetVelocityParams(0.5m, 5);

                decimal big_step = Convert.ToDecimal(StepperBigStep.Text);

                _stepperMotorChannelZ.MoveRelative(Thorlabs.MotionControl.GenericMotorCLI.MotorDirection.Forward, big_step, 20000);

                Globals.Pos_Z += big_step;
                UpdateStepperZ_Click(null, null);


            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to move channel 3 on device\n" + ex);
            }
        }

        private void StepperChannelZJumpBackwards_Click(object sender, EventArgs e)
        {
            if (_stepperMotorChannelZ == null)
            {
                MessageBox.Show("Not connected to channel 3 on device");
                return;
            }

            // All of this operation has been placed inside a "catch-all" exception
            // handler. Normally you would catch the more specific exceptions that
            // the API call might throw (details of which can be found in the
            // Kinesis .NET API document).
            try
            {
                // We ask the device to throw an exception if the operation takes
                // longer than 20,000ms (20s).

                _stepperMotorChannelZ.SetVelocityParams(0.5m, 5);

                decimal big_step = Convert.ToDecimal(StepperBigStep.Text);

                _stepperMotorChannelZ.MoveRelative(Thorlabs.MotionControl.GenericMotorCLI.MotorDirection.Backward, big_step, 20000);

                Globals.Pos_Z -= big_step;
                UpdateStepperZ_Click(null, null);

            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to move channel 3 on device\n" + ex);
            }
        }

        private void StepperChannelZMoveTo_Click(object sender, EventArgs e)
        {
            try
            {
                decimal position = Convert.ToDecimal(StepperMoveToZ.Text);

                _stepperMotorChannelZ.MoveTo(position, 20000);

                Globals.Pos_Z = position;
                UpdateStepperZ_Click(null, null);


            }
            catch { MessageBox.Show("Make sure that the channel is connected,enabled and the position provided is within the motor range", "warning", MessageBoxButtons.OK, MessageBoxIcon.Warning); }
        }

        private void StepperHomeZ_Click(object sender, EventArgs e)
        {
            try
            {
                _stepperMotorChannelZ.MoveTo(Globals.StepperZCentre, 20000);

                Globals.Pos_Z = Globals.StepperZCentre;
                UpdateStepperZ_Click(null, null);



            }
            catch { MessageBox.Show("Make sure that the channel is connected,enabled and the position provided is within the motor range", "warning", MessageBoxButtons.OK, MessageBoxIcon.Warning); }
        }





        #endregion

        
    }

    
}
