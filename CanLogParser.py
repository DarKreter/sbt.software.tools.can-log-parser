import argparse
import sys
import os
import signal
import csv
import cantools
from CAN.CanDecoder import CanDecoder

# Call parameters
parser = argparse.ArgumentParser()
parser.add_argument("--sbt_dbc", type=str,
                    help="path to dbc file with SolarBoat IDs", required=True)
parser.add_argument("--kls_dbc", type=str,
                    help="path to dbc file with KLS frames", required=True)
args = parser.parse_args()

# Ctrl+C handler
def signal_handler(sig, frame):
    for filename in openedFiles:
        openedFiles[filename].close()
    sys.exit(0)

# config can decoder
canDecoder = CanDecoder(args.sbt_dbc,args.kls_dbc)
# dictonary with all opened files
openedFiles = dict()

# register SIGKILL handler
signal.signal(signal.SIGINT, signal_handler)
for rawFrame in cantools.logreader.Parser(sys.stdin):
    try:
        # Decode frame
        decodedFrame = canDecoder.decode_payload(rawFrame.frame_id, rawFrame.data)
        # Get SBT IDs
        sourceIDname = canDecoder.decode_sourceID_name(rawFrame.frame_id)
        paramIDname = canDecoder.decode_paramID_name(rawFrame.frame_id)

    except Exception as e:
        print("Error occurred with frame: {}#{}".format(rawFrame.frame_id, rawFrame.data))
        print("Error: {}".format(e))
        print()

    finally:
        filename = "output/{}-{}.csv".format(sourceIDname, paramIDname)
        csv_header_row = []
        csv_data_row = []

        # Open file if not opened yet
        if filename not in openedFiles:
            f = open(filename, 'a+')
            openedFiles[filename] = f
        file = openedFiles[filename]

        # Check if output format has time
        if rawFrame.timestamp != None:
            csv_header_row.append("time")
            csv_data_row.append(rawFrame.timestamp)

        # Get all frame signals
        for signal in decodedFrame:
            signalValue = "{:.3f}".format(decodedFrame[signal])
            csv_header_row.append(signal)
            csv_data_row.append(signalValue)


        # Write data to csv
        writer = csv.writer(f)
        if os.stat(filename).st_size == 0:
            writer.writerow(csv_header_row)
        writer.writerow(csv_data_row)

signal_handler(None, None)
