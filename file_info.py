from common import xor_buffer, FILE_INFO_SIZE
from collections import namedtuple
import struct

class FileInfo:
    """ Contains meta about a single file contained in a .bus file.
    """

    offset = 0
    name = ""
    length = 0
    encrypted = True

    def __init__(self, buffer):
        x = namedtuple(
            "Data", "name pad offset length unk_01 encrypted unk_03 unk_04")
        fmt = "=256s 8s I I b ? b b"
        s = x._make(struct.unpack_from(fmt, buffer))
        self.name = s.name.decode("utf-8").strip('\0')
        self.length = s.length
        self.encrypted = s.encrypted
        self.offset = s.offset
    
    @staticmethod
    def decrypt_header(file, offset):
        """Decrypts the header of a file.
        file -- the .bus file's handle
        offset -- the offset into the file where the header has been written
        """

        file.seek(offset)
        dec_buf = xor_buffer(file.read(FILE_INFO_SIZE))
        return FileInfo(dec_buf)

    def decrypt_contents(self, file, offset):
        """Decrypts the contents of a PackFile.
        file -- the .bus file's handle
        offset -- The offset in bytes into the file, relative to the first file
        """

        file.seek(offset)
        dec_buf = None
        if(self.encrypted):
            dec_buf = xor_buffer(file.read(self.length))
        else:
            dec_buf = file.read(self.length)
        return dec_buf