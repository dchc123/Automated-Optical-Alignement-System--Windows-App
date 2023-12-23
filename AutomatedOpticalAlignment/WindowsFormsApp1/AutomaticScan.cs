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
    public partial class AutomaticScan : Form
    {
        const string SerialNumber = "70184894";

        

        MainForm mainform = new MainForm();

        public AutomaticScan()
        {
            InitializeComponent();
        }

        #region Auto Scan

        private void AutoScanButton_Click(object sender, EventArgs e)
        {
            

            var server = new NamedPipeServerStream("NPtest");  //open new named pipe

            decimal minimum_step_stepper = 0.017m;  //minimum movement for each motor
            decimal minimum_step_piezo = 0.001m;
            decimal piezo_range = 0.02m;
            decimal CentrePointXStepper = 5.435m;
            decimal CentrePointYStepper = 5.165m;
            decimal CentrePointPiezo = 0.01m;
            decimal CentrePointVarX = 0m;
            decimal CentrePointVarY = 0m;

            decimal Step_Size = 0.025m;
            decimal EdgeLength = 4; //max size to start

            int ReadingsPerEdge = Convert.ToInt32(Decimal.Round(EdgeLength / Step_Size)); //stepper motor for first iteration of scan
            if (ReadingsPerEdge % 2 == 0) { ReadingsPerEdge += 1; }                 //correcting if number is odd

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

            if (DummyCheckBox3.Checked == false)
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

            server.WaitForConnection();     //establishing connection with python
            Console.WriteLine("Connected.");

            var br = new BinaryReader(server); //binary writing and reading setup
            var bw = new BinaryWriter(server);

            int scan_attempt = 0;

            int Mode = 2;

            if (ConnectionCheckBox3.Checked) { Mode = 3; }

            byte ModeByte = Convert.ToByte(Mode);

            bw.Write(ModeByte);

            byte[] Array_Position = { 0, 0 };
            int CentreOfMatrix = 0;
            int piezo_scan_count = 0;
            int stepper_scan_count = 0;
            List<int> local_scan_positions_X = new List<int>() { 0, 1, 1, 1, 0, -1, -1, -1, 0, 0 };
            List<int> local_scan_positions_Y = new List<int>() { 1, 1, 0, -1, -1, -1, 0, 1, 1, 0 };

            while (Step_Size > minimum_step_piezo)
            {
                ReadingsPerEdge = Convert.ToInt32(Decimal.Round(EdgeLength / Step_Size)); //stepper motor for first iteration of scan
                if (ReadingsPerEdge % 2 == 0) { ReadingsPerEdge += 1; }                 //correcting if number is odd

                Globals.Serpent2(ReadingsPerEdge); // generating data and calling array for scan
                int[,] array2Dc = Globals.Serpentine();

                int array_length = (array2Dc.Length / 2);  //info for scans
                int MaxValue = array2Dc.Cast<int>().Max();
                byte ByteMaxValue = Convert.ToByte(MaxValue);
                int scale = 155 / MaxValue;
                int extra_scan_count = 0;

                Canvas_Clear();

                if (scan_attempt == 0)
                {
                    bw.Write(ByteMaxValue); //tell python size of scan 
                }

                scan_attempt += 1;

                if (Step_Size > minimum_step_stepper)
                {
                    stepper_scan_count++;
                }
                else
                {
                    piezo_scan_count++;
                }
                //tell user scan number
                Console.WriteLine("Scan Number: " + scan_attempt);



                for (int i = 0; i < array_length + 1; i++)
                {



                    try
                    {
                        // If array length is met then tell user that scan failed

                        //if (i == array_length) // WHY???
                        //{
                        //    byte[] done_command = Encoding.ASCII.GetBytes("done");  //Python exits measurement loop
                        //    bw.Write(done_command);

                        //    byte[] Highest_Average_Position = br.ReadBytes(2);
                        //    int HAP = (256*Highest_Average_Position[0] + Highest_Average_Position[1])-extra_scan_count;

                        //    CentrePointX = MainForm.MotorPositions(CentrePointX, Step_Size, array2Dc[HAP-1, 0]);
                        //    CentrePointY = MainForm.MotorPositions(CentrePointY, Step_Size, array2Dc[HAP-1, 1]);

                        //    EdgeLength = EdgeLength / 2;
                        //    Step_Size = Step_Size / 2;

                        //    break;
                        //}

                        if (scan_attempt == 1)
                        {
                            Array_Position = MainForm.ArrayPosition(MaxValue, MaxValue, array2Dc[i, 0], array2Dc[i, 1]); //generate array position for current reading and 2 next array positions for x and y axis
                            CentreOfMatrix = MaxValue;

                        }
                        else if (scan_attempt > 1)
                        {

                            Array_Position = MainForm.ArrayPosition(CentreOfMatrix, CentreOfMatrix, array2Dc[i, 0], array2Dc[i, 1]);
                            MaxValue = CentreOfMatrix;                                                                          //generate array position for current reading and 2 next array positions for x and y axis
                        }

                        decimal Xposition = 0;
                        decimal Yposition = 0;



                        if (ConnectionCheckBox3.Checked & Step_Size > minimum_step_stepper)  // select appropriate motor to use given step size
                        {
                            if (stepper_scan_count < 10)
                            {
                                Xposition = MainForm.MotorPositions(CentrePointXStepper, Step_Size, array2Dc[i, 0]);
                                Yposition = MainForm.MotorPositions(CentrePointYStepper, Step_Size, array2Dc[i, 1]);

                                mainform._stepperMotorChannelX.SetVelocityParams(10m, 5);
                                mainform._stepperMotorChannelY.SetVelocityParams(10m, 5);

                                mainform._stepperMotorChannelX.MoveTo(Xposition, 20000); //steppers
                                mainform._stepperMotorChannelY.MoveTo(Yposition, 20000);
                            }
                            if (stepper_scan_count > 10)
                            {
                                if (stepper_scan_count == 2)
                                {
                                    decimal Scale = Step_Size / 0.02m;

                                    Step_Size = Step_Size / Scale;
                                    EdgeLength = EdgeLength / Scale;
                                }

                                Xposition = MainForm.MotorPositions(CentrePointVarX, Step_Size, array2Dc[i, 0]);
                                Yposition = MainForm.MotorPositions(CentrePointVarY, Step_Size, array2Dc[i, 1]);

                                mainform._stepperMotorChannelX.SetVelocityParams(10m, 5);
                                mainform._stepperMotorChannelY.SetVelocityParams(10m, 5);

                                mainform._stepperMotorChannelX.MoveTo(Xposition, 20000); //steppers
                                mainform._stepperMotorChannelY.MoveTo(Yposition, 20000);



                                for (int k = 0; k < 10; k++)
                                {
                                    //Piezo_Move_And_Measure(array2Dc, CentrePointPiezo, Step_Size=0.05m, br, bw);

                                    decimal X_position = MainForm.MotorPositions(CentrePointPiezo, Step_Size = 0.005m, array2Dc[k, 0]);
                                    decimal Y_position = MainForm.MotorPositions(CentrePointPiezo, Step_Size = 0.005m, array2Dc[k, 1]);

                                    decimal XVoltage = MainForm.Pos2Volt(X_position);
                                    decimal YVoltage = MainForm.Pos2Volt(Y_position);

                                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);

                                    Array_Position = MainForm.ArrayPosition(CentreOfMatrix, CentreOfMatrix, array2Dc[i, 0] + array2Dc[k, 0], array2Dc[i, 1] + array2Dc[k, 1]);

                                    bw.Write(Array_Position);

                                    byte[] Current_Reading = br.ReadBytes(4);

                                    bool move_on_flag = MainForm.move_on_check(Current_Reading);

                                    if (move_on_flag)
                                    {
                                        CentrePointVarX = Xposition;
                                        CentrePointVarY = Yposition;

                                        EdgeLength = EdgeLength / (decimal)1.45;
                                        Step_Size = Step_Size / (decimal)1.45;

                                        break;
                                    }
                                }

                                Step_Size = 0.02m;
                            }

                            //stepper_scan_count++;
                        }
                        else if (Step_Size < minimum_step_stepper)
                        {

                            if (piezo_scan_count == 1 & ConnectionCheckBox3.Checked)
                            {
                                decimal Scale = EdgeLength / piezo_range;
                                EdgeLength = EdgeLength / Scale;
                                Step_Size = 0.002m;
                            }

                            if (ConnectionCheckBox3.Checked)
                            {
                                Xposition = MainForm.MotorPositions(CentrePointPiezo, Step_Size, array2Dc[i, 0]);
                                Yposition = MainForm.MotorPositions(CentrePointPiezo, Step_Size, array2Dc[i, 1]);

                                decimal XVoltage = MainForm.Pos2Volt(Xposition);
                                decimal YVoltage = MainForm.Pos2Volt(Yposition);

                                mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                                mainform._kCubePiezoY.SetOutputVoltage(YVoltage);

                            }

                            piezo_scan_count++;
                        }

                        bw.Write(Array_Position); //pass array position to python 

                        if (i > 0)
                        {
                            Canvas_JoinPoints(array2Dc[i - 1, 0], array2Dc[i - 1, 1], array2Dc[i, 0], array2Dc[i, 1], scale); // draw 2D plot
                        }

                        byte[] current_reading = br.ReadBytes(4);


                        Array.Reverse(current_reading);
                        int Current_Reading_Int = BitConverter.ToInt32(current_reading, 0);

                        if (Step_Size > minimum_step_stepper)
                        {
                            CentrePointVarX = CentrePointXStepper;
                            CentrePointVarY = CentrePointYStepper;
                        }
                        else
                        {
                            CentrePointVarX = CentrePointPiezo;
                            CentrePointVarY = CentrePointPiezo;
                        }

                        decimal target = 150m;
                        int target_temp = Convert.ToInt32(((decimal)0.5 + (((decimal)scan_attempt - 1) / 10)) * target);

                        if (ConnectionCheckBox3.Checked)
                        {
                            if (Current_Reading_Int > target_temp) // When to start a local scan
                            {
                                if (Math.Abs(array2Dc[i, 0]) == MaxValue || Math.Abs(array2Dc[i, 1]) == MaxValue)
                                {
                                    if (Math.Abs(array2Dc[i, 0]) == MaxValue & Math.Abs(array2Dc[i, 1]) == MaxValue)
                                    {
                                        run_corner_scan(array2Dc[i, 0], array2Dc[i, 1], CentrePointVarX, CentrePointVarY, Step_Size, MaxValue, scale, bw, br, ConnectionCheckBox3.Checked);
                                        extra_scan_count = extra_scan_count + 4;
                                    }
                                    else
                                    {
                                        run_edge_scan(array2Dc[i, 0], array2Dc[i, 1], CentrePointVarX, CentrePointVarY, Step_Size, MaxValue, scale, bw, br, ConnectionCheckBox3.Checked);
                                        extra_scan_count = extra_scan_count + 6;
                                    }

                                }
                                else
                                {
                                    current_reading = Run_Local_Scan(array2Dc[i, 0], array2Dc[i, 1], CentrePointPiezo, CentrePointPiezo, Step_Size, MaxValue, scale, bw, br, ConnectionCheckBox3.Checked);
                                    extra_scan_count = extra_scan_count + 10;
                                }
                            }
                        }
                        else
                        {
                            if (Current_Reading_Int % 500 == 0) // When to start a local scan
                            {
                                if (Math.Abs(array2Dc[i, 0]) == MaxValue || Math.Abs(array2Dc[i, 1]) == MaxValue)
                                {
                                    if (Math.Abs(array2Dc[i, 0]) == MaxValue & Math.Abs(array2Dc[i, 1]) == MaxValue)
                                    {
                                        run_corner_scan(array2Dc[i, 0], array2Dc[i, 1], CentrePointVarX, CentrePointVarY, Step_Size, MaxValue, scale, bw, br, ConnectionCheckBox3.Checked);
                                        extra_scan_count = extra_scan_count + 4;
                                    }
                                    else
                                    {
                                        run_edge_scan(array2Dc[i, 0], array2Dc[i, 1], CentrePointVarX, CentrePointVarY, Step_Size, MaxValue, scale, bw, br, ConnectionCheckBox3.Checked);
                                        extra_scan_count = extra_scan_count + 6;
                                    }

                                }
                                else
                                {
                                    current_reading = Run_Local_Scan(array2Dc[i, 0], array2Dc[i, 1], CentrePointPiezo, CentrePointPiezo, Step_Size, MaxValue, scale, bw, br, ConnectionCheckBox3.Checked);
                                    extra_scan_count = extra_scan_count + 10;
                                }
                            }
                        }


                        bool Move_On_Flag = MainForm.move_on_check(current_reading);

                        if (Move_On_Flag)
                        {
                            CentrePointVarX = Xposition;
                            CentrePointVarY = Yposition;

                            EdgeLength = EdgeLength / (decimal)1.45;
                            Step_Size = Step_Size / (decimal)1.45;

                            break;
                        }


                    }
                    catch (EndOfStreamException)
                    {
                        Console.WriteLine("Failed.");

                        break;                    // When client disconnects
                    }
                }
            }

            byte[] kill_command = Encoding.ASCII.GetBytes("kill");  //Python exits measurement loop
            bw.Write(kill_command);

            string ScanTime = Convert.ToString((ReadingsPerEdge * ReadingsPerEdge) / 100) + " mins";
            string ReadingsTotalLabel = Convert.ToString(ReadingsPerEdge * ReadingsPerEdge);
            string StepSizeLabel = Convert.ToString(Decimal.Round(Step_Size, 5));
            string file_name = ScanTime + " " + ReadingsTotalLabel + " " + StepSizeLabel;

            byte[] file_name_bytes = Encoding.ASCII.GetBytes(file_name);
            byte file_name_size = Convert.ToByte(file_name_bytes.Length);

            byte[] folder_number = br.ReadBytes(4);

            bw.Write(file_name_size);
            bw.Write(file_name_bytes);

            byte[] layers = br.ReadBytes(4);

            string layer_total = Convert.ToString((8 * Convert.ToUInt64(layers[0]) + 4 * Convert.ToUInt64(layers[1]) + 2 * Convert.ToUInt64(layers[2]) + Convert.ToUInt64(layers[3])) - 2);
            string foldernum = "_" + Convert.ToString(8 * Convert.ToUInt64(folder_number[0]) + 4 * Convert.ToUInt64(folder_number[1]) + 2 * Convert.ToUInt64(folder_number[2]) + Convert.ToUInt64(folder_number[3]));

            if (foldernum == "_0") { foldernum = ""; }

            file_name = "Multi-Layer-Scan" + foldernum + @"\" + file_name + "_Layer" + layer_total;

            Console.WriteLine("Client disconnected."); //close named pipe and server
            server.Close();
            server.Dispose();

            //mainform.Run(file_name); // display 3D plot

        }

        #endregion

        #region 2D drawing functions

        #region Serpentine Scan Full Draw
        public void Canvas_Draw(int[,] array2Dc)
        {

            Graphics DrawingArea = scan_panel.CreateGraphics();

            Brush red = new SolidBrush(Color.Red);
            Pen redPen = new Pen(red, 2);

            int MaxValue = array2Dc.Cast<int>().Max();

            int scale = 155 / MaxValue;

            int centreX = Convert.ToInt32(Decimal.Round(Convert.ToDecimal(scan_panel.Size.Width / 2.1)));
            int centreY = scan_panel.Size.Height / 2;

            for (int i = 0; i < (array2Dc.Length / 2) - 1; i++)
            {
                int x1 = centreX + (scale * array2Dc[i, 0]);
                int y1 = centreY - (scale * array2Dc[i, 1]);
                int x2 = centreX + (scale * array2Dc[i + 1, 0]);
                int y2 = centreY - (scale * array2Dc[i + 1, 1]);


                DrawingArea.DrawLine(redPen, x1, y1, x2, y2);
            }

        }

        #endregion

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

        #region local area scan

        public byte[] Run_Local_Scan(int Xposition, int Yposition, decimal midpointX, decimal midpointY, decimal Step_Size, int MaxValue, int scale, dynamic bw, dynamic br, bool connection_flag)
        {
            decimal minimum_step_stepper = 0.017m;
            Step_Size = 0.003m;
            int PositionX0 = Xposition;
            int PositionY0 = Yposition;

            Yposition += 1;
            decimal YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition - PositionY0);
            if (connection_flag)
            {
                decimal YVoltage = MainForm.Pos2Volt(YpositionMotor);
                mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
            }
            byte[] array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
            bw.Write(array_position);
            Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition - 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
            byte[] current_reading = br.ReadBytes(4);

            Xposition += 1;
            decimal XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition - PositionX0);
            if (connection_flag)
            {
                decimal XVoltage = MainForm.Pos2Volt(XpositionMotor);
                mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
            }
            array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
            bw.Write(array_position);
            Canvas_JoinPoints(Decimal.ToInt32(Xposition - 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
            current_reading = br.ReadBytes(4);

            Yposition -= 1;
            YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition - PositionY0);
            if (connection_flag)
            {
                decimal YVoltage = MainForm.Pos2Volt(YpositionMotor);
                mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
            }
            array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
            bw.Write(array_position);
            Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition + 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
            current_reading = br.ReadBytes(4);

            Yposition -= 1;
            YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition - PositionY0);
            if (connection_flag)
            {
                decimal YVoltage = MainForm.Pos2Volt(YpositionMotor);
                mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
            }
            array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
            bw.Write(array_position);
            Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition + 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
            current_reading = br.ReadBytes(4);

            Xposition -= 1;
            XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition - PositionX0);
            if (connection_flag)
            {
                decimal XVoltage = MainForm.Pos2Volt(XpositionMotor);
                mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
            }
            array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
            bw.Write(array_position);
            Canvas_JoinPoints(Decimal.ToInt32(Xposition + 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
            current_reading = br.ReadBytes(4);

            Xposition -= 1;
            XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition - PositionX0);
            if (connection_flag)
            {
                decimal XVoltage = MainForm.Pos2Volt(XpositionMotor);
                mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
            }
            array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
            bw.Write(array_position);
            Canvas_JoinPoints(Decimal.ToInt32(Xposition + 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
            current_reading = br.ReadBytes(4);

            Yposition += 1;
            YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition - PositionY0);
            if (connection_flag)
            {
                decimal YVoltage = MainForm.Pos2Volt(YpositionMotor);
                mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
            }
            array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
            bw.Write(array_position);
            Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition - 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
            current_reading = br.ReadBytes(4);

            Yposition += 1;
            YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition - PositionY0);
            if (connection_flag)
            {
                decimal YVoltage = MainForm.Pos2Volt(YpositionMotor);
                mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
            }
            array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
            bw.Write(array_position);
            Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition - 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
            current_reading = br.ReadBytes(4);

            Xposition += 1;
            XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition - PositionX0);
            if (connection_flag)
            {
                decimal XVoltage = MainForm.Pos2Volt(XpositionMotor);
                mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
            }
            array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
            bw.Write(array_position);
            Canvas_JoinPoints(Decimal.ToInt32(Xposition - 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
            current_reading = br.ReadBytes(4);

            Yposition -= 1;
            YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition - PositionY0);
            if (connection_flag)
            {
                decimal YVoltage = MainForm.Pos2Volt(YpositionMotor);
                mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
            }
            array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
            bw.Write(array_position);
            Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition + 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
            current_reading = br.ReadBytes(4);

            return current_reading;
        }


        public void run_edge_scan(int Xposition, int Yposition, decimal midpointX, decimal midpointY, decimal Step_Size, int MaxValue, int scale, dynamic bw, dynamic br, bool connection_flag)
        {
            decimal minimum_step_stepper = 0.017m;

            if (Xposition == MaxValue)
            {
                Yposition += 1;
                decimal YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                byte[] array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition - 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                byte[] current_reading = br.ReadBytes(4);

                Xposition -= 1;
                decimal XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition + 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Yposition -= 1;
                YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition + 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Yposition -= 1;
                YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition + 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Xposition += 1;
                XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition - 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Yposition += 1;
                YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition - 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

            }

            if (Xposition == -MaxValue)
            {
                Yposition += 1;
                decimal YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                byte[] array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition - 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                byte[] current_reading = br.ReadBytes(4);

                Xposition += 1;
                decimal XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition - 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Yposition -= 1;
                YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition + 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Yposition -= 1;
                YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition + 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Xposition -= 1;
                XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition + 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Yposition += 1;
                YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition - 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

            }

            if (Yposition == MaxValue)
            {
                Xposition += 1;
                decimal XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(XpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                byte[] array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition - 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                byte[] current_reading = br.ReadBytes(4);

                Yposition -= 1;
                decimal YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition + 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Xposition -= 1;
                XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition + 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Xposition -= 1;
                XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition + 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Yposition += 1;
                YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition - 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Xposition += 1;
                XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition - 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

            }

            if (Yposition == -MaxValue)
            {
                Xposition += 1;
                decimal XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(XpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                byte[] array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition - 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                byte[] current_reading = br.ReadBytes(4);

                Yposition += 1;
                decimal YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition - 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Xposition -= 1;
                XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition + 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Xposition -= 1;
                XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition + 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Yposition -= 1;
                YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition + 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Xposition += 1;
                XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition - 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

            }
        }

        public void run_corner_scan(int Xposition, int Yposition, decimal midpointX, decimal midpointY, decimal Step_Size, int MaxValue, int scale, dynamic bw, dynamic br, bool connection_flag)
        {

            decimal minimum_step_stepper = 0.017m;

            if (Xposition == MaxValue & Yposition == MaxValue)
            {
                Xposition -= 1;
                decimal XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(XpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                byte[] array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition + 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                byte[] current_reading = br.ReadBytes(4);

                Yposition -= 1;
                decimal YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition + 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Xposition += 1;
                XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition - 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Yposition += 1;
                YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition - 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

            }

            if (Xposition == MaxValue & Yposition == -MaxValue)
            {
                Xposition -= 1;
                decimal XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(XpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                byte[] array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition + 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                byte[] current_reading = br.ReadBytes(4);

                Yposition += 1;
                decimal YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition - 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Xposition += 1;
                XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition - 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Yposition -= 1;
                YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition + 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);


            }

            if (Yposition == -MaxValue & Xposition == -MaxValue)
            {
                Yposition += 1;
                decimal YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                byte[] array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition - 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                byte[] current_reading = br.ReadBytes(4);

                Xposition += 1;
                decimal XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition - 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Yposition -= 1;
                YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition + 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Xposition -= 1;
                XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition + 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

            }

            if (Yposition == MaxValue & Xposition == -MaxValue)
            {
                Xposition += 1;
                decimal XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(XpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                byte[] array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition - 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                byte[] current_reading = br.ReadBytes(4);

                Yposition -= 1;
                decimal YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition + 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Xposition -= 1;
                XpositionMotor = MainForm.MotorPositions(midpointX, Step_Size, Xposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelX.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal XVoltage = MainForm.Pos2Volt(Xposition);
                    mainform._kCubePiezoX.SetOutputVoltage(XVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition + 1), Decimal.ToInt32(Yposition), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

                Yposition += 1;
                YpositionMotor = MainForm.MotorPositions(midpointY, Step_Size, Yposition);
                if (Step_Size > minimum_step_stepper & connection_flag) { mainform._stepperMotorChannelY.MoveTo(YpositionMotor, 20000); }
                else if (connection_flag)
                {
                    decimal YVoltage = MainForm.Pos2Volt(Yposition);
                    mainform._kCubePiezoY.SetOutputVoltage(YVoltage);
                }
                array_position = MainForm.ArrayPosition(MaxValue, MaxValue, Xposition, Yposition);
                bw.Write(array_position);
                Canvas_JoinPoints(Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition - 1), Decimal.ToInt32(Xposition), Decimal.ToInt32(Yposition), scale);
                current_reading = br.ReadBytes(4);

            }
        }
        #endregion
    }
}
