import sys
import argparse

from .core.eds import EDS, EDSSection

EDS2DCF_DESCRIPTION = 'EDS to DCF CLI tool'


def eds2dcf(sys_args=None):
    if sys_args is None:
        sys_args = sys.argv[1:]

    name = 'eds2dcf'
    parser = argparse.ArgumentParser(description=EDS2DCF_DESCRIPTION, prog=name)
    parser.add_argument('filepath', metavar='FILEPATH', help='filepath to EDS file')
    parser.add_argument('node_id', type=int, help='set the node ID')
    parser.add_argument('node_name', help='set the node name')
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

    eds = EDS()
    eds.load(args.filepath)

    section = EDSSection()
    section.header = '[DeviceComissioning]'
    section['NodeID'] = args.node_id
    section['NodeName'] = args.node_name
    section['Baudrate'] = args.baud_rate
    section['NetNumber'] = args.net_number
    section['NetworkName'] = args.network_name
    section['CANopenManager'] = args.canopen_manager
    section['LSS_SerialNumber'] = args.lss_serial_number

    eds.device_commissioning = section

    if args.output:
        eds.save(args.output, dcf=True)
    else:
        eds.save(dcf=True)
