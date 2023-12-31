from __headers__ import *

class TimeType(Enum):
    UTC0 = 'UTC0'
    epoch = 'epoch'

# Call parameters
parser = argparse.ArgumentParser()
parser.add_argument("--sbt_dbc", type=str,
                    help="path to dbc file with SolarBoat IDs", required=True)
parser.add_argument("--kls_dbc", type=str,
                    help="path to dbc file with KLS frames", required=True)
parser.add_argument("--time_type", type=TimeType, choices=list(TimeType), default=TimeType.epoch,
                    help="time format: \"UTC0\" or \"epoch\"")
args = parser.parse_args()

# Ctrl+C handler
def signal_handler(sig, frame):
    for filename in openedFiles:
        openedFiles[filename].close()
    sys.exit(0)

# config can decoder
canDecoder = CanDecoder(args.sbt_dbc, args.kls_dbc)
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
            # Write time in requested style
            if args.time_type == TimeType.UTC0:
                time = rawFrame.timestamp
            else:
                time = datetime.timestamp(rawFrame.timestamp)

            csv_header_row.append("time")
            csv_data_row.append(time)

        # Get all frame signals
        for signal in decodedFrame:
            signalValue = "{:.8f}".format(decodedFrame[signal])
            csv_header_row.append(signal)
            csv_data_row.append(signalValue)


        # Write data to csv
        writer = csv.writer(file)
        # If file is empty
        if os.stat(filename).st_size == 0:
            writer.writerow(csv_header_row)
        writer.writerow(csv_data_row)

        file.flush()

signal_handler(None, None)
