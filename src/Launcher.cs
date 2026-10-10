using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

namespace PotatoYTLauncher {
    static class Program {
        [STAThread]
        static void Main() {
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string scriptPath = Path.Combine(baseDir, "src", "main.py");

            if (!File.Exists(scriptPath)) {
                MessageBox.Show("Không tìm thấy file mã nguồn tại:\n" + scriptPath, "PotatoYT-Mini Launcher", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            // Tìm pythonw.exe (chạy ngầm không hiện cửa sổ cmd đen)
            string pythonPath = "";
            string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            
            string[] candidatePaths = new string[] {
                Path.Combine(localAppData, @"Programs\Python\Python312\pythonw.exe"),
                Path.Combine(localAppData, @"Programs\Python\Python311\pythonw.exe"),
                Path.Combine(localAppData, @"Programs\Python\Python310\pythonw.exe"),
                Path.Combine(localAppData, @"Programs\Python\Python312\python.exe"),
                Path.Combine(localAppData, @"Programs\Python\Python311\python.exe")
            };

            foreach (string p in candidatePaths) {
                if (File.Exists(p)) {
                    pythonPath = p;
                    break;
                }
            }

            // Nếu không có trong LocalAppData, thử tìm trong PATH
            if (string.IsNullOrEmpty(pythonPath)) {
                pythonPath = "pythonw.exe";
            }

            ProcessStartInfo psi = new ProcessStartInfo();
            psi.FileName = pythonPath;
            psi.Arguments = "\"" + scriptPath + "\"";
            psi.WorkingDirectory = baseDir;
            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;
            psi.WindowStyle = ProcessWindowStyle.Hidden;

            try {
                Process.Start(psi);
            } catch (Exception ex) {
                // Thử lại với python.exe thông thường nếu pythonw thất bại
                try {
                    psi.FileName = "python.exe";
                    Process.Start(psi);
                } catch {
                    MessageBox.Show("Không thể khởi động Python:\n" + ex.Message + "\n\nVui lòng đảm bảo máy tính đã cài đặt Python 3.10 trở lên.", "PotatoYT-Mini Lỗi", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }
    }
}
