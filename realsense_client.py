import chenserver
from realsense_server_code import *
import cv2
import pickle
import struct
import time
class EtherSenseClient(chenserver.AsyncClient):
    def __init__(self, address, port):
        super().__init__(address=address,port=port)
        self.remainingBytes = 0
        self.buffer = bytearray()

    def getDepthImage(self):
        self.runtask(self.__getDepthImage)

    def getRGBImage(self):
        self.runtask(self.__getRGBImage)

    def getPointCloud(self):
        self.runtask(self.__getPointCloud)

    async def __getDepthImage(self):
        while not self.writer.is_closing():
            await self.handle_write(str(READ_DEPTH_IMG))
            await self.handle_read(self.handle_img_frame)

    async def __getRGBImage(self):
        while not self.writer.is_closing():
            await self.handle_write(str(READ_RGB_IMG))
            await self.handle_read(self.handle_img_frame)

    async def __getPointCloud(self):
        while not self.writer.is_closing():
            await self.handle_write(str(READ_PTC))
            await self.handle_read(self.handle_pointcloud_frame)

    async def handle_write(self, message):
        if self.writer is not None:
            print(f'Send: {message!r}')
            self.writer.write(message.encode())
            await self.writer.drain()

    async def handle_read(self, callback):
        if self.remainingBytes == 0:
            # get the expected frame size
            self.frame_length = struct.unpack('<I', await self.reader.read(4))[0]
            self.timestamp = struct.unpack('<d', await self.reader.read(8))
            self.remainingBytes = self.frame_length
        # request the frame data until the frame is completely in buffer
        data = await self.reader.read(self.remainingBytes)
        self.buffer += data
        self.remainingBytes -= len(data)
        # once the frame is fully recived, process/display it
        if len(self.buffer) == self.frame_length:
            callback()


    def handle_img_frame(self):
        # convert the frame from string to numerical data
        imdata = pickle.loads(self.buffer)
        # print(imdata)
        bigDepth = cv2.resize(imdata, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        cv2.putText(bigDepth, str(self.timestamp), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (65536), 2, cv2.LINE_AA)
        cv2.imshow("window", bigDepth)
        cv2.waitKey(1)
        self.buffer = bytearray()

    def handle_pointcloud_frame(self):
        # convert the frame from string to numerical data
        imdata = pickle.loads(self.buffer)
        print(imdata.shape)
        # bigDepth = cv2.resize(imdata, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        # cv2.putText(bigDepth, str(self.timestamp), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (65536), 2, cv2.LINE_AA)
        # cv2.imshow("window", bigDepth)
        # cv2.waitKey(1)
        self.buffer = bytearray()


client = EtherSenseClient(address="localhost",port=8888)
cv2.namedWindow("window")
# client.getPointCloud()
client.getDepthImage()
# client.getRGBImage()
# client.close()
