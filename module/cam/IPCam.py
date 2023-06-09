from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from threading import Thread
from PySide6.QtGui import QImage, QPixmap
import cv2
from module import create_filename
from module.ImageTool import cupture_face
from logger import logger


class IPCam(Thread):
    lnk_connect: str = None
    qLabel: QLabel = None
    net_work_error: bool = False

    def __init__(self, parent=None) -> None:
        Thread.__init__(self, parent)
        self.status = True
        self.cap = True

    def run(self) -> None:
        logger.info("srarting take image from ip cam")
        self.net_work_error = False
        try:
            self.cap = cv2.VideoCapture()

            if 'rtsp' in self.lnk_connect:
                self.cap.open(self.lnk_connect)

            while self.status:

                if 'http' in self.lnk_connect:
                    self.cap.open(self.lnk_connect)

                if not self.cap.isOpened():
                    raise ConnectionError
                
                ret, frame = self.cap.read()
                if not ret: continue

                color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                h, w, ch = color_frame.shape
                img = QImage(color_frame.data, w, h,
                             ch * w, QImage.Format_RGB888)
                
                
                label_geometry = self.qLabel.geometry()
                h, w = label_geometry.height()-20, label_geometry.width()-20
                
                self.__scaled_img = QPixmap.fromImage(
                    img.scaled(h, w, Qt.KeepAspectRatio))

                self.qLabel.setPixmap(self.__scaled_img)

            # "http://admin:admin102030@192.168.1.108/cgi-bin/snapshot.cgi?2"\

        except ConnectionError:
            logger.error("Нет сети или не правильная строка подключения")
            logger.info("stop take image from ip cam")

            self.status = False
            self.qLabel.setText(
                'Нет сети или не правильная строка подключения')
        except RuntimeError:
            self.status = False

    def stop_cam(self):
        logger.info("stop take image from ip cam")
        self.cap.release()
        self.status = False
        cv2.destroyAllWindows()
        self.join()

    def cupture_image(self, qLabel: QLabel) -> str:
        name_file = create_filename()
        qLabel.setPixmap(self.__scaled_img)
        self.__scaled_img.save(name_file, 'jpg')
        self.stop_cam()
        face_file_name = create_filename('face')
        cupture_face(name_file, face_file_name)
        return name_file
