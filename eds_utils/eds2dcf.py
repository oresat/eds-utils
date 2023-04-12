import os
import sys
import argparse

from .core import str2int
from .core.file_io.read_eds import read_eds
from .core.file_io.write_eds import write_eds

EDS2DCF_DESCRIPTION = 'Convert a EDS file to a DCF file'


def eds2dcf(sys_args=None):
    if sys_args is None:
        sys_args = sys.argv[1:]

    parser = argparse.ArgumentParser(description=EDS2DCF_DESCRIPTION, prog='eds2dcf')
    parser.add_argument('filepath', metavar='FILEPATH', help='file path to EDS file')
    parser.add_argument('node_id', metavar='NODE_ID', help='set the node ID')
    parser.add_argument('node_name', metavar='NODE_NAME', help='set the node name')
    parser.add_argument('-b', '--baud-rate', type=int, default=1000,
                        help='set the baud rate (in kbps)')
    parser.add_argument('-j', '--net-number', type=int, default=0, help='set the net number')
    parser.add_argument('-k', '--network-name', default='', help='set the network name')
    parser.add_argument('-m', '--canopen-manager', action='store_true',
                        help='set a CANopen manager')
    parser.add_argument('-l', '--lss-serial-number', type=int, default=0,
                        help='set the LSS serial number')
    parser.add_argument('-o', '--output', default='', help='output file path')
    args = parser.parse_args(sys_args)

    try:
        eds, errors = read_eds(args.filepath)
    except FileNotFoundError as exc:
        print(exc)
        sys.exit(1)

    eds.device_commissioning.node_id = str2int(args.node_id)
    eds.device_commissioning.node_name = args.node_name
    eds.device_commissioning.baud_rate = args.baud_rate
    eds.device_commissioning.net_number = args.net_number
    eds.device_commissioning.network_name = args.network_name
    eds.device_commissioning.canopen_manager = args.canopen_manager
    eds.device_commissioning.lss_serialnumber = args.lss_serial_number

    if args.output:
        write_eds(eds, file_path=args.output, dcf=True)
    else:
        path = os.path.dirname(os.path.abspath(args.filepath))
        file_name = os.path.basename(args.filepath)
        write_eds(eds, file_path=f'{path}/{file_name}', dcf=True)
