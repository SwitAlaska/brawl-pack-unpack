from bus_file_header import BusFileHeader
from common import PKG_OFFSET, HEADER_INFO_SIZE, FILE_INFO_SIZE
from file_info import FileInfo
from pack_file import PackFile

from pathlib import Path, PurePath
from collections import namedtuple

import struct
import argparse
import xml.dom.minidom
import xml.sax.saxutils

def unpack(file_name, beautify_xml):
    """Unpacks a .bus file.
    Keyword arguments:
    file -- the .bus file's name
    beautify_xml -- whether XML files' output should be beautified.
    """

    with open(file_name, "rb") as input:
        print("Unpacking: {}".format(file_name))
        header = BusFileHeader.decrypt(input)
        files = []
        for i in range(header.length):
            offset = PKG_OFFSET + HEADER_INFO_SIZE + i * FILE_INFO_SIZE
            file = FileInfo.decrypt_header(input, offset)
            files.append(file)

        rdptr = 0
        for file in files:

            print("Unpacking: {}".format(file.name))
            offset = PKG_OFFSET + HEADER_INFO_SIZE + header.length * FILE_INFO_SIZE + rdptr
            decrypted = file.decrypt_contents(input, offset)
            path = Path(file.name)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(file.name, "w+b") as output_file:
                output_file.write(decrypted)

            rdptr += file.length
            if beautify_xml and file.name.split(".")[-1] == "xml":
                dom = xml.dom.minidom.parse(file.name)
                with open(file.name, "w+b") as output_file:
                    output_file.write(dom.toprettyxml(encoding="utf-8"))


def pack(path_name):
    """Packs a folder into a .bus file.
    Keyword arguments:
    path_name -- the folder's path
    """

    path_name = path_name.strip("/")
    path = Path("data/" + path_name)
    if not path.exists() or not path.is_dir():
        raise Exception("Folder doesn't exist or is not a directory")

    output_file_name = path_name.replace("/", "_") + ".bus"
    print("Packing: {}".format(output_file_name))
    pfs = []
    files = [f for f in path.glob("*")]

    for file in files:
        if(file.is_dir()):
            pack(path_name + "/" + file.name)
        else:
            with open(file.absolute(), "rb") as ifs:
                buf = ifs.read()
                pf = PackFile(file.name, buf)
                pfs.append(pf)

    with open(output_file_name, "w+b") as ofs:
        BusFileHeader.write(ofs, path_name, len(pfs))
        accumulator = 0
        for pack_file in pfs:
            pack_file.write_header(ofs, path_name, accumulator)
            accumulator += len(pack_file.buffer)

        for pack_file in pfs:
            pack_file.write_contents(ofs)


def cmd_pack(args):
    """Handles the "pack" sub-command.
    Keyword arguments:
    args -- the command's arguments
    """

    pack(args.path_name)


def cmd_unpack(args):
    """Handles the "unpack" sub-command.
    Keyword arguments:
    args -- the command's arguments
    """
    path = Path(".")
    files = [f for f in path.glob("*") if f.suffix == ".bus"]
    if args.folder_name != ".":
        files = [f for f in files if f.name.lower().startswith(args.folder_name)]

    for file in files:
        unpack(file, args.beautify_xml)


def main():

    parser = argparse.ArgumentParser(description="Unpack/pack .bus files")
    subparsers = parser.add_subparsers()

    parser_pack = subparsers.add_parser(
        "pack", help="Pack a folder into .bus files")
    parser_pack.add_argument(
        'path_name',
        type=str,
        help='For example: script, bg, ...'
    )
    parser_pack.set_defaults(func=cmd_pack)

    parser_unpack = subparsers.add_parser(
        "unpack", help="Unpack all .bus files")
    parser_unpack.add_argument(
        "-f"
        "--folder",
        type=str,
        dest="folder_name",
        required=False,
        default=".",
        help="The folder's name (for example: XManDB) (case insensitive)"
    )
    parser_unpack.add_argument(
        '-x'
        '--beautify_xml',
        dest="beautify_xml",
        action="store_true",
        required=False,
        help='Prettify XML output'
    )
    parser_unpack.set_defaults(func=cmd_unpack)

    args = parser.parse_args()
    try:
        _func = args.func
    except AttributeError:
        parser.print_help()
    args.func(args)


if __name__ == "__main__":
    main()
