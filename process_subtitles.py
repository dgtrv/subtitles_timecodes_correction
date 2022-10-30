"""
Simple module for adapting subtitles timecodes to different video speed.

Works with .ass files. All the strings with prefix EVENT_PREFIX will be
processed: start and end timecode will be shifted according to supplied
sample timecode from initial file and corresponding target timecode for
file with different video playback speed.
"""

from os import path
from sys import argv, exit
from typing import List, Tuple

EVENT_PREFIX = "Dialogue: "


def timecode_to_milliseconds(timecode: str) -> int:
    """Convert timecode to time in milliseconds.

    Timecode format should be: h:mm:ss.centiseconds.
    One santisecond equals to 0.01 s.
    """
    hours, minutes, seconds_with_santiseconds = timecode.split(":")
    seconds, santiseconds = seconds_with_santiseconds.split(".")
    milliseconds = (
        int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    ) * 1000 + int(santiseconds) * 10
    return milliseconds


def milliseconds_to_timecode(milliseconds: int) -> str:
    """Convert time in milliseconds to timecode.

    Timecode format: h:mm:ss.centiseconds.
    One santisecond equals to 0.01 s.
    """
    hours = int(milliseconds / 3600000)
    minutes = int((milliseconds % 3600000) / 60000)
    seconds = int((milliseconds % 60000) / 1000)
    santiseconds = int((milliseconds % 1000) / 10)
    timecode = f"{hours}:{minutes:02}:{seconds:02}.{santiseconds:02}"
    return timecode


def get_start_and_end_timecodes_positions(line: str) -> Tuple[int, int]:
    """Get position of start and end timecode from event format line."""
    start_timecode_position = None
    end_timecode_position = None
    _, format_headers = line.split(":", maxsplit=1)
    for position, header in enumerate(format_headers.strip().split(",")):
        if header.strip() == "Start":
            start_timecode_position = position
        if header.strip() == "End":
            end_timecode_position = position
    if not start_timecode_position:
        raise ValueError('No entry named "Start" in events headers')
    if not end_timecode_position:
        raise ValueError('No entry named "End" in events headers')
    return start_timecode_position, end_timecode_position


def get_video_playback_speed_delta(
    source_sample_timecode: str, target_sample_timecode: str
) -> float:
    source_event_milliseconds = timecode_to_milliseconds(
        source_sample_timecode
    )
    target_event_milliseconds = timecode_to_milliseconds(
        target_sample_timecode
    )
    speed_delta = (
        target_event_milliseconds - source_event_milliseconds
    ) / source_event_milliseconds

    return speed_delta


def process_event_string(
    line: str,
    event_prefix: str,
    start_timecode_position: int,
    end_timecode_position: int,
    speed_delta: float,
) -> str:
    dialog_event = line[len(event_prefix) :]
    dialog_elements: List[str] = dialog_event.split(",")
    start_timecode = dialog_elements[start_timecode_position]
    end_timecode = dialog_elements[end_timecode_position]

    start_milliseconds = timecode_to_milliseconds(start_timecode)
    end_milliseconds = timecode_to_milliseconds(end_timecode)
    start_milliseconds_corrected = int(start_milliseconds * (1 + speed_delta))
    end_milliseconds_corrected = int(end_milliseconds * (1 + speed_delta))

    start_timecode_corrected = milliseconds_to_timecode(
        start_milliseconds_corrected
    )
    end_timecode_corrected = milliseconds_to_timecode(
        end_milliseconds_corrected
    )

    dialog_elements[1] = start_timecode_corrected
    dialog_elements[2] = end_timecode_corrected

    dialog_event_corrected = f"{event_prefix}{','.join(dialog_elements)}"

    return dialog_event_corrected


def process_subtitles_file(
    path_to_input_file,
    path_to_output_file,
    event_prefix,
    speed_delta,
):
    with open(path_to_input_file, "r") as input_file, open(
        path_to_output_file, "w"
    ) as output_file:
        is_previous_line_events_header = False
        start_timecode_position = None
        end_timecode_position = None
        for line in input_file.readlines():
            if line.strip() == "[Events]":
                is_previous_line_events_header = True

            if is_previous_line_events_header:
                if line.startswith("Format:"):
                    (
                        start_timecode_position,
                        end_timecode_position,
                    ) = get_start_and_end_timecodes_positions(line)
                    is_previous_line_events_header = False

            if line.startswith(event_prefix):
                if is_previous_line_events_header:
                    raise Exception(
                        f"Found prefix {event_prefix} before corresponding format line."
                        "Seems like subtitles file is corrupted. Cannot continue."
                    )

                if not start_timecode_position or not end_timecode_position:
                    raise Exception(
                        "To process timecodes both start and end timecodes positions"
                        "should be known. Something is wrong with events header or with format line"
                    )

                output_line = process_event_string(
                    line=line,
                    event_prefix=event_prefix,
                    start_timecode_position=start_timecode_position,
                    end_timecode_position=end_timecode_position,
                    speed_delta=speed_delta,
                )

                output_file.write(output_line)

                continue

            output_file.write(line)


if __name__ == "__main__":

    if len(argv) < 5:
        raise Exception(
            "You have to provide all the parameters:"
            "input file, output file, source sample timecode, target sample timecode."
        )

    path_to_input_file = None
    path_to_output_file = None
    source_sample_timecode = None
    target_sample_timecode = None

    for argument in argv[1:]:
        argument_name, argument_value = argument.split("=")
        if argument_name in ["-i", "--input"]:
            path_to_input_file = argument_value.strip()
            continue

        if argument_name in ["-o", "--output"]:
            path_to_output_file = argument_value
            continue

        if argument_name in ["-s", "--tc_source"]:
            source_sample_timecode = argument_value
            continue

        if argument_name in ["-t", "--tc_target"]:
            target_sample_timecode = argument_value
            continue

        raise Exception(f"Unknown argument {argument_name}")

    if not path_to_input_file:
        raise Exception("Input file path must be provided")

    if not path_to_output_file:
        raise Exception("Output file path must be provided")

    if not source_sample_timecode:
        raise Exception("Source sample timecode must be provided")

    if not target_sample_timecode:
        raise Exception("Target sample timecode must be provided")

    if path.exists(path_to_output_file):
        while True:
            user_answer = input(
                f"File {path_to_output_file} already exists. Overwrite (Y[es]/N[o])?"
            )
            if user_answer.lower() in ["y", "yes"]:
                break
            if user_answer.lower() in ["n", "no"]:
                print("Ok. Haven't touch anything.")
                exit(0)
            print('Print "Yes" or "No"\n')

    video_playback_speed_delta = get_video_playback_speed_delta(
        source_sample_timecode, target_sample_timecode
    )

    process_subtitles_file(
        path_to_input_file=path_to_input_file,
        path_to_output_file=path_to_output_file,
        event_prefix=EVENT_PREFIX,
        speed_delta=video_playback_speed_delta,
    )
