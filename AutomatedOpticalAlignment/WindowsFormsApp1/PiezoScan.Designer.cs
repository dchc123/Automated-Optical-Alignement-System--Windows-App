
namespace Automated_Optical_Alignment
{
    partial class PiezoScan
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.groupBox6 = new System.Windows.Forms.GroupBox();
            this.DummyCheckBox2 = new System.Windows.Forms.CheckBox();
            this.ConnectionCheckBox2 = new System.Windows.Forms.CheckBox();
            this.label13 = new System.Windows.Forms.Label();
            this.ScanResolutionInput2 = new System.Windows.Forms.TextBox();
            this.label12 = new System.Windows.Forms.Label();
            this.SideLengthInput2 = new System.Windows.Forms.TextBox();
            this.ScanInfoUpdateButton2 = new System.Windows.Forms.Button();
            this.groupBox2 = new System.Windows.Forms.GroupBox();
            this.label1 = new System.Windows.Forms.Label();
            this.label4 = new System.Windows.Forms.Label();
            this.label5 = new System.Windows.Forms.Label();
            this.StepSizeLabel2 = new System.Windows.Forms.Label();
            this.ReadingsTotalLabel2 = new System.Windows.Forms.Label();
            this.ScanTimeLabel2 = new System.Windows.Forms.Label();
            this.RunScan2 = new System.Windows.Forms.Button();
            this.scan_panel = new System.Windows.Forms.Panel();
            this.groupBox6.SuspendLayout();
            this.groupBox2.SuspendLayout();
            this.SuspendLayout();
            // 
            // groupBox6
            // 
            this.groupBox6.Controls.Add(this.DummyCheckBox2);
            this.groupBox6.Controls.Add(this.ConnectionCheckBox2);
            this.groupBox6.Controls.Add(this.label13);
            this.groupBox6.Controls.Add(this.ScanResolutionInput2);
            this.groupBox6.Controls.Add(this.label12);
            this.groupBox6.Controls.Add(this.SideLengthInput2);
            this.groupBox6.Controls.Add(this.ScanInfoUpdateButton2);
            this.groupBox6.Location = new System.Drawing.Point(57, 12);
            this.groupBox6.Name = "groupBox6";
            this.groupBox6.Size = new System.Drawing.Size(172, 218);
            this.groupBox6.TabIndex = 75;
            this.groupBox6.TabStop = false;
            this.groupBox6.Text = "Piezo Scan Options";
            // 
            // DummyCheckBox2
            // 
            this.DummyCheckBox2.AutoSize = true;
            this.DummyCheckBox2.CheckAlign = System.Drawing.ContentAlignment.MiddleRight;
            this.DummyCheckBox2.Location = new System.Drawing.Point(52, 21);
            this.DummyCheckBox2.Name = "DummyCheckBox2";
            this.DummyCheckBox2.Size = new System.Drawing.Size(96, 17);
            this.DummyCheckBox2.TabIndex = 45;
            this.DummyCheckBox2.Text = "Dummy mode?";
            this.DummyCheckBox2.UseVisualStyleBackColor = true;
            // 
            // ConnectionCheckBox2
            // 
            this.ConnectionCheckBox2.AutoSize = true;
            this.ConnectionCheckBox2.CheckAlign = System.Drawing.ContentAlignment.MiddleRight;
            this.ConnectionCheckBox2.Location = new System.Drawing.Point(5, 44);
            this.ConnectionCheckBox2.Name = "ConnectionCheckBox2";
            this.ConnectionCheckBox2.Size = new System.Drawing.Size(143, 17);
            this.ConnectionCheckBox2.TabIndex = 46;
            this.ConnectionCheckBox2.Text = "Connected to hardware?";
            this.ConnectionCheckBox2.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            this.ConnectionCheckBox2.UseVisualStyleBackColor = true;
            // 
            // label13
            // 
            this.label13.AutoSize = true;
            this.label13.Location = new System.Drawing.Point(17, 82);
            this.label13.Name = "label13";
            this.label13.Size = new System.Drawing.Size(96, 26);
            this.label13.TabIndex = 50;
            this.label13.Text = "Enter scan \r\nresolution (0-100%)";
            // 
            // ScanResolutionInput2
            // 
            this.ScanResolutionInput2.Location = new System.Drawing.Point(120, 88);
            this.ScanResolutionInput2.Name = "ScanResolutionInput2";
            this.ScanResolutionInput2.Size = new System.Drawing.Size(46, 20);
            this.ScanResolutionInput2.TabIndex = 49;
            // 
            // label12
            // 
            this.label12.AutoSize = true;
            this.label12.Location = new System.Drawing.Point(6, 120);
            this.label12.Name = "label12";
            this.label12.Size = new System.Drawing.Size(108, 26);
            this.label12.TabIndex = 51;
            this.label12.Text = "Enter side length \r\nfor scan (max=20 um)";
            // 
            // SideLengthInput2
            // 
            this.SideLengthInput2.Location = new System.Drawing.Point(120, 126);
            this.SideLengthInput2.Name = "SideLengthInput2";
            this.SideLengthInput2.Size = new System.Drawing.Size(46, 20);
            this.SideLengthInput2.TabIndex = 48;
            // 
            // ScanInfoUpdateButton2
            // 
            this.ScanInfoUpdateButton2.Location = new System.Drawing.Point(61, 176);
            this.ScanInfoUpdateButton2.Name = "ScanInfoUpdateButton2";
            this.ScanInfoUpdateButton2.Size = new System.Drawing.Size(105, 23);
            this.ScanInfoUpdateButton2.TabIndex = 53;
            this.ScanInfoUpdateButton2.Text = "Update scan info";
            this.ScanInfoUpdateButton2.UseVisualStyleBackColor = true;
            this.ScanInfoUpdateButton2.Click += new System.EventHandler(this.ScanInfoUpdateButton2_Click);
            // 
            // groupBox2
            // 
            this.groupBox2.Controls.Add(this.label1);
            this.groupBox2.Controls.Add(this.label4);
            this.groupBox2.Controls.Add(this.label5);
            this.groupBox2.Controls.Add(this.StepSizeLabel2);
            this.groupBox2.Controls.Add(this.ReadingsTotalLabel2);
            this.groupBox2.Controls.Add(this.ScanTimeLabel2);
            this.groupBox2.Location = new System.Drawing.Point(57, 256);
            this.groupBox2.Name = "groupBox2";
            this.groupBox2.Size = new System.Drawing.Size(172, 100);
            this.groupBox2.TabIndex = 74;
            this.groupBox2.TabStop = false;
            this.groupBox2.Text = "Piezo Scan Info";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(4, 21);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(68, 13);
            this.label1.TabIndex = 5;
            this.label1.Text = "Time to scan";
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(4, 49);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(75, 13);
            this.label4.TabIndex = 4;
            this.label4.Text = "Readings total";
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(6, 75);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(96, 13);
            this.label5.TabIndex = 3;
            this.label5.Text = "Reading increment";
            // 
            // StepSizeLabel2
            // 
            this.StepSizeLabel2.AutoSize = true;
            this.StepSizeLabel2.Location = new System.Drawing.Point(117, 75);
            this.StepSizeLabel2.Name = "StepSizeLabel2";
            this.StepSizeLabel2.Size = new System.Drawing.Size(10, 13);
            this.StepSizeLabel2.TabIndex = 2;
            this.StepSizeLabel2.Text = "-";
            this.StepSizeLabel2.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // ReadingsTotalLabel2
            // 
            this.ReadingsTotalLabel2.AutoSize = true;
            this.ReadingsTotalLabel2.Location = new System.Drawing.Point(117, 49);
            this.ReadingsTotalLabel2.Name = "ReadingsTotalLabel2";
            this.ReadingsTotalLabel2.Size = new System.Drawing.Size(10, 13);
            this.ReadingsTotalLabel2.TabIndex = 1;
            this.ReadingsTotalLabel2.Text = "-";
            this.ReadingsTotalLabel2.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // ScanTimeLabel2
            // 
            this.ScanTimeLabel2.AutoSize = true;
            this.ScanTimeLabel2.Location = new System.Drawing.Point(117, 21);
            this.ScanTimeLabel2.Name = "ScanTimeLabel2";
            this.ScanTimeLabel2.Size = new System.Drawing.Size(10, 13);
            this.ScanTimeLabel2.TabIndex = 0;
            this.ScanTimeLabel2.Text = "-";
            this.ScanTimeLabel2.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // RunScan2
            // 
            this.RunScan2.Location = new System.Drawing.Point(83, 392);
            this.RunScan2.Name = "RunScan2";
            this.RunScan2.Size = new System.Drawing.Size(110, 41);
            this.RunScan2.TabIndex = 73;
            this.RunScan2.Text = "Run Piezo Scan";
            this.RunScan2.UseVisualStyleBackColor = true;
            this.RunScan2.Click += new System.EventHandler(this.RunScan2_Click);
            // 
            // scan_panel
            // 
            this.scan_panel.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.scan_panel.Location = new System.Drawing.Point(285, 23);
            this.scan_panel.Name = "scan_panel";
            this.scan_panel.Size = new System.Drawing.Size(503, 415);
            this.scan_panel.TabIndex = 76;
            // 
            // PiezoScan
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(800, 450);
            this.Controls.Add(this.scan_panel);
            this.Controls.Add(this.groupBox6);
            this.Controls.Add(this.groupBox2);
            this.Controls.Add(this.RunScan2);
            this.Name = "PiezoScan";
            this.Text = "PiezoScan";
            this.FormClosed += new System.Windows.Forms.FormClosedEventHandler(this.PiezoScan_FormClosed);
            this.groupBox6.ResumeLayout(false);
            this.groupBox6.PerformLayout();
            this.groupBox2.ResumeLayout(false);
            this.groupBox2.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.GroupBox groupBox6;
        private System.Windows.Forms.CheckBox DummyCheckBox2;
        private System.Windows.Forms.CheckBox ConnectionCheckBox2;
        private System.Windows.Forms.Label label13;
        public System.Windows.Forms.TextBox ScanResolutionInput2;
        private System.Windows.Forms.Label label12;
        public System.Windows.Forms.TextBox SideLengthInput2;
        private System.Windows.Forms.Button ScanInfoUpdateButton2;
        private System.Windows.Forms.GroupBox groupBox2;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.Label label5;
        public System.Windows.Forms.Label StepSizeLabel2;
        public System.Windows.Forms.Label ReadingsTotalLabel2;
        public System.Windows.Forms.Label ScanTimeLabel2;
        private System.Windows.Forms.Button RunScan2;
        private System.Windows.Forms.Panel scan_panel;
    }
}