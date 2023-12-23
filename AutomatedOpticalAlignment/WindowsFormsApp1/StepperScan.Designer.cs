
namespace Automated_Optical_Alignment
{
    partial class StepperScan
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
            this.groupBox3 = new System.Windows.Forms.GroupBox();
            this.DummyCheckBox = new System.Windows.Forms.CheckBox();
            this.ConnectionCheckBox = new System.Windows.Forms.CheckBox();
            this.label2 = new System.Windows.Forms.Label();
            this.ScanResolutionInput = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.SideLengthInput = new System.Windows.Forms.TextBox();
            this.ScanInfoUpdateButton = new System.Windows.Forms.Button();
            this.ScanInfo = new System.Windows.Forms.GroupBox();
            this.label9 = new System.Windows.Forms.Label();
            this.label8 = new System.Windows.Forms.Label();
            this.label7 = new System.Windows.Forms.Label();
            this.StepSizeLabel = new System.Windows.Forms.Label();
            this.ReadingsTotalLabel = new System.Windows.Forms.Label();
            this.ScanTimeLabel = new System.Windows.Forms.Label();
            this.RunScan = new System.Windows.Forms.Button();
            this.scan_panel = new System.Windows.Forms.Panel();
            this.groupBox3.SuspendLayout();
            this.ScanInfo.SuspendLayout();
            this.SuspendLayout();
            // 
            // groupBox3
            // 
            this.groupBox3.Controls.Add(this.DummyCheckBox);
            this.groupBox3.Controls.Add(this.ConnectionCheckBox);
            this.groupBox3.Controls.Add(this.label2);
            this.groupBox3.Controls.Add(this.ScanResolutionInput);
            this.groupBox3.Controls.Add(this.label3);
            this.groupBox3.Controls.Add(this.SideLengthInput);
            this.groupBox3.Controls.Add(this.ScanInfoUpdateButton);
            this.groupBox3.Location = new System.Drawing.Point(37, 12);
            this.groupBox3.Name = "groupBox3";
            this.groupBox3.Size = new System.Drawing.Size(169, 230);
            this.groupBox3.TabIndex = 74;
            this.groupBox3.TabStop = false;
            this.groupBox3.Text = "Stepper Scan Options";
            // 
            // DummyCheckBox
            // 
            this.DummyCheckBox.AutoSize = true;
            this.DummyCheckBox.CheckAlign = System.Drawing.ContentAlignment.MiddleRight;
            this.DummyCheckBox.Location = new System.Drawing.Point(53, 22);
            this.DummyCheckBox.Name = "DummyCheckBox";
            this.DummyCheckBox.Size = new System.Drawing.Size(96, 17);
            this.DummyCheckBox.TabIndex = 28;
            this.DummyCheckBox.Text = "Dummy mode?";
            this.DummyCheckBox.UseVisualStyleBackColor = true;
            // 
            // ConnectionCheckBox
            // 
            this.ConnectionCheckBox.AutoSize = true;
            this.ConnectionCheckBox.CheckAlign = System.Drawing.ContentAlignment.MiddleRight;
            this.ConnectionCheckBox.Location = new System.Drawing.Point(6, 45);
            this.ConnectionCheckBox.Name = "ConnectionCheckBox";
            this.ConnectionCheckBox.Size = new System.Drawing.Size(143, 17);
            this.ConnectionCheckBox.TabIndex = 29;
            this.ConnectionCheckBox.Text = "Connected to hardware?";
            this.ConnectionCheckBox.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            this.ConnectionCheckBox.UseVisualStyleBackColor = true;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(15, 88);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(96, 26);
            this.label2.TabIndex = 33;
            this.label2.Text = "Enter scan \r\nresolution (0-100%)\r\n";
            // 
            // ScanResolutionInput
            // 
            this.ScanResolutionInput.Location = new System.Drawing.Point(117, 94);
            this.ScanResolutionInput.Name = "ScanResolutionInput";
            this.ScanResolutionInput.Size = new System.Drawing.Size(46, 20);
            this.ScanResolutionInput.TabIndex = 32;
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(7, 139);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(104, 26);
            this.label3.TabIndex = 34;
            this.label3.Text = "Enter side length\r\n for scan (max=4mm)";
            // 
            // SideLengthInput
            // 
            this.SideLengthInput.Location = new System.Drawing.Point(117, 145);
            this.SideLengthInput.Name = "SideLengthInput";
            this.SideLengthInput.Size = new System.Drawing.Size(46, 20);
            this.SideLengthInput.TabIndex = 31;
            // 
            // ScanInfoUpdateButton
            // 
            this.ScanInfoUpdateButton.Location = new System.Drawing.Point(58, 195);
            this.ScanInfoUpdateButton.Name = "ScanInfoUpdateButton";
            this.ScanInfoUpdateButton.Size = new System.Drawing.Size(105, 23);
            this.ScanInfoUpdateButton.TabIndex = 36;
            this.ScanInfoUpdateButton.Text = "Update scan info";
            this.ScanInfoUpdateButton.UseVisualStyleBackColor = true;
            this.ScanInfoUpdateButton.Click += new System.EventHandler(this.ScanInfoUpdateButton_Click);
            // 
            // ScanInfo
            // 
            this.ScanInfo.Controls.Add(this.label9);
            this.ScanInfo.Controls.Add(this.label8);
            this.ScanInfo.Controls.Add(this.label7);
            this.ScanInfo.Controls.Add(this.StepSizeLabel);
            this.ScanInfo.Controls.Add(this.ReadingsTotalLabel);
            this.ScanInfo.Controls.Add(this.ScanTimeLabel);
            this.ScanInfo.Location = new System.Drawing.Point(37, 262);
            this.ScanInfo.Name = "ScanInfo";
            this.ScanInfo.Size = new System.Drawing.Size(169, 100);
            this.ScanInfo.TabIndex = 73;
            this.ScanInfo.TabStop = false;
            this.ScanInfo.Text = "Stepper Scan Info";
            // 
            // label9
            // 
            this.label9.AutoSize = true;
            this.label9.Location = new System.Drawing.Point(4, 21);
            this.label9.Name = "label9";
            this.label9.Size = new System.Drawing.Size(68, 13);
            this.label9.TabIndex = 5;
            this.label9.Text = "Time to scan";
            // 
            // label8
            // 
            this.label8.AutoSize = true;
            this.label8.Location = new System.Drawing.Point(4, 49);
            this.label8.Name = "label8";
            this.label8.Size = new System.Drawing.Size(75, 13);
            this.label8.TabIndex = 4;
            this.label8.Text = "Readings total";
            // 
            // label7
            // 
            this.label7.AutoSize = true;
            this.label7.Location = new System.Drawing.Point(6, 75);
            this.label7.Name = "label7";
            this.label7.Size = new System.Drawing.Size(96, 13);
            this.label7.TabIndex = 3;
            this.label7.Text = "Reading increment";
            // 
            // StepSizeLabel
            // 
            this.StepSizeLabel.AutoSize = true;
            this.StepSizeLabel.Location = new System.Drawing.Point(114, 75);
            this.StepSizeLabel.Name = "StepSizeLabel";
            this.StepSizeLabel.Size = new System.Drawing.Size(10, 13);
            this.StepSizeLabel.TabIndex = 2;
            this.StepSizeLabel.Text = "-";
            this.StepSizeLabel.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // ReadingsTotalLabel
            // 
            this.ReadingsTotalLabel.AutoSize = true;
            this.ReadingsTotalLabel.Location = new System.Drawing.Point(114, 49);
            this.ReadingsTotalLabel.Name = "ReadingsTotalLabel";
            this.ReadingsTotalLabel.Size = new System.Drawing.Size(10, 13);
            this.ReadingsTotalLabel.TabIndex = 1;
            this.ReadingsTotalLabel.Text = "-";
            this.ReadingsTotalLabel.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // ScanTimeLabel
            // 
            this.ScanTimeLabel.AutoSize = true;
            this.ScanTimeLabel.Location = new System.Drawing.Point(114, 21);
            this.ScanTimeLabel.Name = "ScanTimeLabel";
            this.ScanTimeLabel.Size = new System.Drawing.Size(10, 13);
            this.ScanTimeLabel.TabIndex = 0;
            this.ScanTimeLabel.Text = "-";
            this.ScanTimeLabel.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // RunScan
            // 
            this.RunScan.Location = new System.Drawing.Point(65, 393);
            this.RunScan.Name = "RunScan";
            this.RunScan.Size = new System.Drawing.Size(110, 39);
            this.RunScan.TabIndex = 72;
            this.RunScan.Text = "Run Stepper Scan";
            this.RunScan.UseVisualStyleBackColor = true;
            this.RunScan.Click += new System.EventHandler(this.RunScan_Click);
            // 
            // scan_panel
            // 
            this.scan_panel.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.scan_panel.Location = new System.Drawing.Point(266, 24);
            this.scan_panel.Name = "scan_panel";
            this.scan_panel.Size = new System.Drawing.Size(522, 414);
            this.scan_panel.TabIndex = 75;
            // 
            // StepperScan
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(800, 450);
            this.Controls.Add(this.scan_panel);
            this.Controls.Add(this.groupBox3);
            this.Controls.Add(this.ScanInfo);
            this.Controls.Add(this.RunScan);
            this.Name = "StepperScan";
            this.Text = "StepperScan";
            this.FormClosed += new System.Windows.Forms.FormClosedEventHandler(this.StepperScan_FormClosed);
            this.groupBox3.ResumeLayout(false);
            this.groupBox3.PerformLayout();
            this.ScanInfo.ResumeLayout(false);
            this.ScanInfo.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.GroupBox groupBox3;
        private System.Windows.Forms.CheckBox DummyCheckBox;
        private System.Windows.Forms.CheckBox ConnectionCheckBox;
        private System.Windows.Forms.Label label2;
        public System.Windows.Forms.TextBox ScanResolutionInput;
        private System.Windows.Forms.Label label3;
        public System.Windows.Forms.TextBox SideLengthInput;
        private System.Windows.Forms.Button ScanInfoUpdateButton;
        private System.Windows.Forms.GroupBox ScanInfo;
        private System.Windows.Forms.Label label9;
        private System.Windows.Forms.Label label8;
        private System.Windows.Forms.Label label7;
        public System.Windows.Forms.Label StepSizeLabel;
        public System.Windows.Forms.Label ReadingsTotalLabel;
        public System.Windows.Forms.Label ScanTimeLabel;
        private System.Windows.Forms.Button RunScan;
        private System.Windows.Forms.Panel scan_panel;
    }
}