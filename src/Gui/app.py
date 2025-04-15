import sys
import os
import pandas as pd
import folium

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl


class CVRPMapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CVRP Route Visualizer")
        self.setGeometry(100, 100, 1000, 700)

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Upload button
        self.upload_button = QPushButton("Upload CSV")
        self.upload_button.clicked.connect(self.load_csv)
        self.layout.addWidget(self.upload_button)

        # Web view to display the map
        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)

        # Show a default map
        self.generate_map()

    def generate_map(self, df=None):
        if df is None:
            m = folium.Map(location=[52.52, 13.405], zoom_start=13)
            folium.Marker([52.52, 13.405], popup="Depot").add_to(m)
        else:
            m = folium.Map(location=[df['lat'].iloc[0], df['lon'].iloc[0]], zoom_start=13)
            for _, row in df.iterrows():
                folium.Marker([row['lat'], row['lon']], popup=row['name']).add_to(m)

            coords = df[['lat', 'lon']].values
            routes = [[0, 1, 2, 0]]
            for route in routes:
                folium.PolyLine([coords[i] for i in route], color="blue", weight=5).add_to(m)

        m.save("map.html")
        self.web_view.load(QUrl.fromLocalFile(os.path.abspath("map.html")))

    def load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if file_path:
            df = pd.read_csv(file_path)
            if {'name', 'lat', 'lon', 'demand'}.issubset(df.columns):
                self.generate_map(df)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CVRPMapApp()
    window.show()
    sys.exit(app.exec())