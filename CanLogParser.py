import argparse
import csv
import cantools
from CAN.CanDecoder import CanDecoder
from CAN.CanID_autogenerated import *

# Call parameters
parser = argparse.ArgumentParser()
parser.add_argument("--sbt_dbc", type=str,
                    help="path to dbc file with SolarBoat IDs", required=True)
parser.add_argument("--kls_dbc", type=str,
                    help="path to dbc file with KLS frames", required=True)
parser.add_argument("--log_file", type=str,
                    help="path to log file", required=True)
args = parser.parse_args()


# config can decoder
canDecoder = CanDecoder(args.sbt_dbc,args.kls_dbc)
openedFiles = dict()

with open(args.log_file, 'r') as file:
    for rawFrame in cantools.logreader.Parser(file):

        try:
            # Decode frame
            decodedFrame = canDecoder.decode_payload(rawFrame.frame_id, rawFrame.data)
            # Get SBT IDs
            sourceIDname = canDecoder.decode_sourceID_name(rawFrame.frame_id)
            paramIDname = canDecoder.decode_paramID_name(rawFrame.frame_id)

        except Exception as e:
            print("Unknown frame: {}#{}".format(rawFrame.frame_id, rawFrame.data))
            print("Error: {}".format(e))
            print()

        finally:
            filename = "output/{}-{}.csv".format(sourceIDname, paramIDname)

            if filename not in openedFiles:
                f = open(filename, 'a+')
                openedFiles[filename] = f

            file = openedFiles[filename]

            csv_header_row = ["time"]
            csv_data_row = [rawFrame.timestamp]
            for signal in decodedFrame:
                signalValue = "{:.3f}".format(decodedFrame[signal])
                csv_header_row.append(signal)
                csv_data_row.append(signalValue)

            # Write data to csv
            writer = csv.writer(file)
            if filename not in openedFiles:
                writer.writerow(csv_header_row)
            writer.writerow(csv_data_row)


    for filename in openedFiles:
        openedFiles[filename].close()
