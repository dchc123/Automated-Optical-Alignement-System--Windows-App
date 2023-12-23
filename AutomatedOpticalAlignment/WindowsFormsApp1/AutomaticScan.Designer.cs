
namespace Automated_Optical_Alignment
{
    partial class AutomaticScan
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
            this.textBox2 = new System.Windows.Forms.TextBox();
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.label6 = new System.Windows.Forms.Label();
            this.label10 = new System.Windows.Forms.Label();
            this.ConnectionCheckBox3 = new System.Windows.Forms.CheckBox();
            this.DummyCheckBox3 = new System.Windows.Forms.CheckBox();
            this.AutoScanButton = new System.Windows.Forms.Button();
            this.scan_panel = new System.Windows.Forms.Panel();
            this.SuspendLayout();
            // 
            // textBox2
            // 
            this.textBox2.Location = new System.Drawing.Point(93, 171);
            this.textBox2.Name = "textBox2";
            this.textBox2.Size = new System.Drawing.Size(50, 20);
            this.textBox2.TabIndex = 81;
            // 
            // textBox1
            // 
            this.textBox1.Location = new System.Drawing.Point(93, 115);
            this.textBox1.Name = "textBox1";
            this.textBox1.Size = new System.Drawing.Size(50, 20);
            this.textBox1.TabIndex = 80;
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Location = new System.Drawing.Point(66, 93);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(122, 13);
            this.label6.TabIndex = 75;
            this.label6.Text = "Collimator Diameter (mm)";
            // 
            // label10
            // 
            this.label10.AutoSize = true;
            this.label10.Location = new System.Drawing.Point(59, 155);
            this.label10.Name = "label10";
            this.label10.Size = new System.Drawing.Size(133, 13);
            this.label10.TabIndex = 76;
            this.label10.Text = "Target Area Diameter (mm)";
            // 
            // ConnectionCheckBox3
            // 
            this.ConnectionCheckBox3.AutoSize = true;
            this.ConnectionCheckBox3.CheckAlign = System.Drawing.ContentAlignment.MiddleRight;
            this.ConnectionCheckBox3.Location = new System.Drawing.Point(45, 256);
            this.ConnectionCheckBox3.Name = "ConnectionCheckBox3";
            this.ConnectionCheckBox3.Size = new System.Drawing.Size(143, 17);
            this.ConnectionCheckBox3.TabIndex = 79;
            this.ConnectionCheckBox3.Text = "Connected to hardware?";
            this.ConnectionCheckBox3.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            this.ConnectionCheckBox3.UseVisualStyleBackColor = true;
            // 
            // DummyCheckBox3
            // 
            this.DummyCheckBox3.AutoSize = true;
            this.DummyCheckBox3.CheckAlign = System.Drawing.ContentAlignment.MiddleRight;
            this.DummyCheckBox3.Location = new System.Drawing.Point(83, 219);
            this.DummyCheckBox3.Name = "DummyCheckBox3";
            this.DummyCheckBox3.Size = new System.Drawing.Size(96, 17);
            this.DummyCheckBox3.TabIndex = 78;
            this.DummyCheckBox3.Text = "Dummy mode?";
            this.DummyCheckBox3.UseVisualStyleBackColor = true;
            // 
            // AutoScanButton
            // 
            this.AutoScanButton.Location = new System.Drawing.Point(69, 304);
            this.AutoScanButton.Name = "AutoScanButton";
            this.AutoScanButton.Size = new System.Drawing.Size(110, 41);
            this.AutoScanButton.TabIndex = 77;
            this.AutoScanButton.Text = "Start Auto-Scan";
            this.AutoScanButton.UseVisualStyleBackColor = true;
            this.AutoScanButton.Click += new System.EventHandler(this.AutoScanButton_Click);
            // 
            // scan_panel
            // 
            this.scan_panel.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.scan_panel.Location = new System.Drawing.Point(269, 22);
            this.scan_panel.Name = "scan_panel";
            this.scan_panel.Size = new System.Drawing.Size(520, 417);
            this.scan_panel.TabIndex = 82;
            // 
            // AutomaticScan
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(800, 450);
            this.Controls.Add(this.scan_panel);
            this.Controls.Add(this.textBox2);
            this.Controls.Add(this.textBox1);
            this.Controls.Add(this.label6);
            this.Controls.Add(this.label10);
            this.Controls.Add(this.ConnectionCheckBox3);
            this.Controls.Add(this.DummyCheckBox3);
            this.Controls.Add(this.AutoScanButton);
            this.Name = "AutomaticScan";
            this.Text = "AutomaticScan";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.TextBox textBox2;
        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.Label label10;
        private System.Windows.Forms.CheckBox ConnectionCheckBox3;
        private System.Windows.Forms.CheckBox DummyCheckBox3;
        private System.Windows.Forms.Button AutoScanButton;
        private System.Windows.Forms.Panel scan_panel;
    }
}