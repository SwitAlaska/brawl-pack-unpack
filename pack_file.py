from common import xor_buffer
import struct

class PackFile:
    """ Contains information on a file that is going to be packed.
    """

    def __init__(self, name, buf):
        self.name = name
        self.buffer = buf
        self.not_nif = self.name.split(".")[-1] != "nif"

    def write_header(self, file, path_name, offset):
        """Writes the header of a PackFile.
        Keyword arguments:
        file -- the .bus file's handle
        path_name -- the file's parent folders
        offset -- The offset in bytes into the file, relative to the first file
        """

        header_file_name = path_name + "/" + self.name

        # We don't want to encrypt .nif files

        fmt = '=256s 8s I I b ? b b'
        v = struct.pack(fmt, 
            bytes(header_file_name, 'utf-8'), 
            bytes('\0', 'utf-8'), 
            offset, 
            len(self.buffer), 
            0, 
            self.not_nif, 
            0, 
            0)
        file.write(xor_buffer(v))

    def write_contents(self, file):
        """Writes the contents of a PackFile.
        file -- the .bus file's handle
        """

        if self.not_nif:
            file.write(xor_buffer(self.buffer))
        else:
            file.write(self.buffer)