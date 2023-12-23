namespace Automated_Optical_Alignment
{
    partial class MainForm
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
            this.buttonDisconnect = new System.Windows.Forms.Button();
            this.buttonConnect = new System.Windows.Forms.Button();
            this.Centre = new System.Windows.Forms.Button();
            this.Motor_Control_Panel = new System.Windows.Forms.Button();
            this.Stepper_Scan = new System.Windows.Forms.Button();
            this.Automatic_Scan = new System.Windows.Forms.Button();
            this.Piezo_Scan = new System.Windows.Forms.Button();
            this.Expand_Button = new System.Windows.Forms.Button();
            this.Results_Directory = new System.Windows.Forms.TextBox();
            this.Save_As_Button = new System.Windows.Forms.Button();
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.ExpandIsometric = new System.Windows.Forms.Button();
            this.GPIBAddress = new System.Windows.Forms.TextBox();
            this.UpdateGPIB = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // buttonDisconnect
            // 
            this.buttonDisconnect.Location = new System.Drawing.Point(56, 51);
            this.buttonDisconnect.Name = "buttonDisconnect";
            this.buttonDisconnect.Size = new System.Drawing.Size(174, 32);
            this.buttonDisconnect.TabIndex = 2;
            this.buttonDisconnect.Text = "Disconnect";
            this.buttonDisconnect.UseVisualStyleBackColor = true;
            this.buttonDisconnect.Click += new System.EventHandler(this.buttonDisconnect_Click);
            // 
            // buttonConnect
            // 
            this.buttonConnect.Location = new System.Drawing.Point(56, 20);
            this.buttonConnect.Name = "buttonConnect";
            this.buttonConnect.Size = new System.Drawing.Size(174, 33);
            this.buttonConnect.TabIndex = 1;
            this.buttonConnect.Text = "Connect";
            this.buttonConnect.UseVisualStyleBackColor = true;
            this.buttonConnect.Click += new System.EventHandler(this.buttonConnect_Click);
            // 
            // Centre
            // 
            this.Centre.Location = new System.Drawing.Point(56, 80);
            this.Centre.Name = "Centre";
            this.Centre.Size = new System.Drawing.Size(174, 32);
            this.Centre.TabIndex = 20;
            this.Centre.Text = "Home and Centre";
            this.Centre.UseVisualStyleBackColor = true;
            this.Centre.Click += new System.EventHandler(this.Centre_Click);
            // 
            // Motor_Control_Panel
            // 
            this.Motor_Control_Panel.Location = new System.Drawing.Point(56, 240);
            this.Motor_Control_Panel.Name = "Motor_Control_Panel";
            this.Motor_Control_Panel.Size = new System.Drawing.Size(174, 36);
            this.Motor_Control_Panel.TabIndex = 66;
            this.Motor_Control_Panel.Text = "Motor Control Panel";
            this.Motor_Control_Panel.UseVisualStyleBackColor = true;
            this.Motor_Control_Panel.Click += new System.EventHandler(this.Motor_Control_Panel_Click);
            // 
            // Stepper_Scan
            // 
            this.Stepper_Scan.Location = new System.Drawing.Point(56, 312);
            this.Stepper_Scan.Name = "Stepper_Scan";
            this.Stepper_Scan.Size = new System.Drawing.Size(174, 39);
            this.Stepper_Scan.TabIndex = 67;
            this.Stepper_Scan.Text = "Stepper Scan";
            this.Stepper_Scan.UseVisualStyleBackColor = true;
            this.Stepper_Scan.Click += new System.EventHandler(this.Stepper_Scan_Click);
            // 
            // Automatic_Scan
            // 
            this.Automatic_Scan.Enabled = false;
            this.Automatic_Scan.Location = new System.Drawing.Point(56, 377);
            this.Automatic_Scan.Name = "Automatic_Scan";
            this.Automatic_Scan.Size = new System.Drawing.Size(174, 36);
            this.Automatic_Scan.TabIndex = 68;
            this.Automatic_Scan.Text = "Automatic Scan";
            this.Automatic_Scan.UseVisualStyleBackColor = true;
            this.Automatic_Scan.Click += new System.EventHandler(this.Automatic_Scan_Click);
            // 
            // Piezo_Scan
            // 
            this.Piezo_Scan.Location = new System.Drawing.Point(56, 347);
            this.Piezo_Scan.Name = "Piezo_Scan";
            this.Piezo_Scan.Size = new System.Drawing.Size(174, 35);
            this.Piezo_Scan.TabIndex = 69;
            this.Piezo_Scan.Text = "Piezo Scan";
            this.Piezo_Scan.UseVisualStyleBackColor = true;
            this.Piezo_Scan.Click += new System.EventHandler(this.Piezo_Scan_Click);
            // 
            // Expand_Button
            // 
            this.Expand_Button.Location = new System.Drawing.Point(56, 481);
            this.Expand_Button.Name = "Expand_Button";
            this.Expand_Button.Size = new System.Drawing.Size(174, 34);
            this.Expand_Button.TabIndex = 70;
            this.Expand_Button.Text = "Expand Top Down View";
            this.Expand_Button.UseVisualStyleBackColor = true;
            this.Expand_Button.Click += new System.EventHandler(this.Expand_Button_Click);
            // 
            // Results_Directory
            // 
            this.Results_Directory.Location = new System.Drawing.Point(292, 495);
            this.Results_Directory.Name = "Results_Directory";
            this.Results_Directory.Size = new System.Drawing.Size(756, 20);
            this.Results_Directory.TabIndex = 71;
            // 
            // Save_As_Button
            // 
            this.Save_As_Button.Enabled = false;
            this.Save_As_Button.Location = new System.Drawing.Point(1054, 495);
            this.Save_As_Button.Name = "Save_As_Button";
            this.Save_As_Button.Size = new System.Drawing.Size(120, 20);
            this.Save_As_Button.TabIndex = 72;
            this.Save_As_Button.Text = "Save Results As...";
            this.Save_As_Button.UseVisualStyleBackColor = true;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("Microsoft YaHei UI", 15.75F, ((System.Drawing.FontStyle)((System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic))), System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label1.Location = new System.Drawing.Point(434, 23);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(168, 28);
            this.label1.TabIndex = 75;
            this.label1.Text = "Isometric View";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Font = new System.Drawing.Font("Microsoft YaHei UI", 15.75F, ((System.Drawing.FontStyle)((System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic))), System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label2.Location = new System.Drawing.Point(904, 23);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(130, 28);
            this.label2.TabIndex = 76;
            this.label2.Text = "Aerial View";
            // 
            // ExpandIsometric
            // 
            this.ExpandIsometric.Location = new System.Drawing.Point(56, 449);
            this.ExpandIsometric.Name = "ExpandIsometric";
            this.ExpandIsometric.Size = new System.Drawing.Size(174, 36);
            this.ExpandIsometric.TabIndex = 77;
            this.ExpandIsometric.Text = "Expand Isometric View";
            this.ExpandIsometric.UseVisualStyleBackColor = true;
            this.ExpandIsometric.Click += new System.EventHandler(this.ExpandIsometric_Click);
            // 
            // GPIBAddress
            // 
            this.GPIBAddress.Location = new System.Drawing.Point(56, 155);
            this.GPIBAddress.Name = "GPIBAddress";
            this.GPIBAddress.Size = new System.Drawing.Size(174, 20);
            this.GPIBAddress.TabIndex = 78;
            this.GPIBAddress.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // UpdateGPIB
            // 
            this.UpdateGPIB.Location = new System.Drawing.Point(56, 175);
            this.UpdateGPIB.Name = "UpdateGPIB";
            this.UpdateGPIB.Size = new System.Drawing.Size(174, 23);
            this.UpdateGPIB.TabIndex = 79;
            this.UpdateGPIB.Text = "Update GPIB Address";
            this.UpdateGPIB.UseVisualStyleBackColor = true;
            this.UpdateGPIB.Click += new System.EventHandler(this.UpdateGPIB_Click);
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.SystemColors.Info;
            this.ClientSize = new System.Drawing.Size(1183, 532);
            this.Controls.Add(this.UpdateGPIB);
            this.Controls.Add(this.GPIBAddress);
            this.Controls.Add(this.ExpandIsometric);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.Save_As_Button);
            this.Controls.Add(this.Results_Directory);
            this.Controls.Add(this.Expand_Button);
            this.Controls.Add(this.Piezo_Scan);
            this.Controls.Add(this.Automatic_Scan);
            this.Controls.Add(this.Stepper_Scan);
            this.Controls.Add(this.Motor_Control_Panel);
            this.Controls.Add(this.Centre);
            this.Controls.Add(this.buttonDisconnect);
            this.Controls.Add(this.buttonConnect);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.Name = "MainForm";
            this.Text = "Optical Alignment Application";
            this.Load += new System.EventHandler(this.MainForm_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button buttonDisconnect;
        private System.Windows.Forms.Button buttonConnect;
        private System.Windows.Forms.Button Centre;
        private System.Windows.Forms.Button Motor_Control_Panel;
        private System.Windows.Forms.Button Stepper_Scan;
        private System.Windows.Forms.Button Automatic_Scan;
        private System.Windows.Forms.Button Piezo_Scan;
        private System.Windows.Forms.Button Expand_Button;
        public System.Windows.Forms.TextBox Results_Directory;
        private System.Windows.Forms.Button Save_As_Button;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Button ExpandIsometric;
        private System.Windows.Forms.TextBox GPIBAddress;
        private System.Windows.Forms.Button UpdateGPIB;
    }
}

