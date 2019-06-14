from common import PKG_OFFSET, HEADER_INFO_SIZE, xor_buffer
from collections import namedtuple
import struct
from file_info import FileInfo

class BusFileHeader(FileInfo):
    """ Contains a .bus file's metadata.
    """

    def __init__(self, buffer):
        x = namedtuple("Data", "name pad offset length")
        fmt = "=256s 8s I I"
        s = x._make(struct.unpack_from(fmt, buffer))
        self.name = s.name.decode('utf-8').strip('\0')
        self.length = s.length

    @staticmethod
    def decrypt(file):
        """Decrypts the header of a .bus file.
        Keyword arguments:
        file -- the .bus file's handle
        """

        file.seek(PKG_OFFSET)
        dec_buf = xor_buffer(file.read(HEADER_INFO_SIZE))
        return BusFileHeader(dec_buf)
        
    @staticmethod
    def write(file, folder_name, num_files):
        """Writes the header of a .bus file.
        Keyword arguments:
        file -- the output .bus file  
        folder_name -- the folder that the .bus file represents
        num_files -- the number of files (only directories) that the folder contains
        """

        header_name = folder_name.replace("/", "\\")
        header_name = "..\\Data\\" + folder_name
        v = struct.pack('=256s 8s I I', 
            bytes(header_name, "utf-8"),
            bytes('\0', 'utf-8'), 
            0, 
            num_files)
        file.write(b'\x00' * 33)
        file.write(xor_buffer(v))