#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Hephaestus Mind Mapping")
        
        window = MainWindow()
        window.show()
        
        return app.exec()
    except Exception as e:
        print(f"Critical error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())