import socket
import sys
import json
import time
import traceback
import ast
import numpy as np
import matplotlib.pyplot as plt
import argparse

def main(args):
    plt.ion()
    figure, ax = plt.subplots(figsize=(10, 8))
    x = np.array(range(-60,61,5))
    y = np.zeros([len(x)])
    line1, = ax.plot(x, y)
    plt.ylim((0,600))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    save_fp = sys.argv[1]
    fout = open(save_fp, 'wb')

    try:
        # Connect to wil6210_server via TCP socket
        server_addr = (args.server_ip, args.server_port)
        print('Connecting')
        sock.connect(server_addr)
        buf_len = 10240

        # Send command
        data = {};
        print('Sending start scan command...')
        data['cmd'] = 'start_scan'
        data['args'] = {}

        m2 = json.dumps(data).encode('utf-8')

        # Send command
        data = {};
        print('Sending per beam rss command...')
        data['cmd'] = 'per_beam_rss_v2x'
        data['args'] = {}

        m = json.dumps(data).encode('utf-8')
        d_last = b''
        skip_cnt = 0
        write_cnt = 0

        while True:
            sock.sendall(m2)
            d = b''
            while True:
                d_tmp = sock.recv(buf_len)
                d = d + d_tmp
                if not d_tmp or d_tmp[-1] == 41 or d_tmp[-1] == 93 or d_tmp[-1] == 125:
                    break

            sock.sendall(m)
            d = b''
            while True:
                d_tmp = sock.recv(buf_len)
                d = d + d_tmp
                if not d_tmp or d_tmp[-1] == 41 or d_tmp[-1] == 93 or d_tmp[-1] == 125:
                    break

            time.sleep(0.1)
            if d_last == d:
                skip_cnt += 1
                # print('Skip %d replicate RSS.\n' % skip_cnt)
                continue
            else:
                skip_cnt = 0
                write_cnt += 1
                d_last = d

            d_dict = d.decode("UTF-8")
            d_dict = ast.literal_eval(d_dict)
            # print('\033c\r')
            print('Write %d RSS.\n' % write_cnt)
            print(d_dict['snr_data'])
            np.array(d_dict['snr_data']).astype('int32').tofile(fout) 

            snr_data = np.array(d_dict['snr_data'])
            line1.set_xdata(x)
            line1.set_ydata(snr_data[14:39])
            # line1.set_ydata(snr_data[14:31])
            figure.canvas.draw()
            figure.canvas.flush_events()
            time.sleep(0.1)

    except Exception as e:
        traceback.print_exc()
        print(e)
    finally:
        print('connection close')
        sock.close()

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Collect per beam RSS trace')
    parser.add_argument('--server_ip', type=str, default='192.168.137.101', help='The IP address of client radio')
    parser.add_argument('--server_port', type=int, default=10001, help='Port number of the Python server')
    args = parser.parse_args()

    main(args)