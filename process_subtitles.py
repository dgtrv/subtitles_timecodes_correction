"""
Simple module for adapting subtitles timecodes to different video speed.

Works with .ass files. All the strings with prefix EVENT_PREFIX will be 
processed: start and end timecode will be shifted according to supplied 
sample timecode from initial file and corresponding target timecode for 
file with different video playback speed.
"""

from typing import List, Tuple

INPUT_FILENAME = ""
OUPUT_FILENAME = ""

SAMPLE_EVENT_TIMECODE_SOURCE = ""
SAMPLE_EVENT_TIMECODE_TARGET = ""

EVENT_PREFIX = "Dialogue: "


def shift(dialogue_events: List[str]) -> None:
    pass


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
    timecode = f"{hours}:{minutes:02}:{seconds:02}.{santiseconds}"
    return timecode


source_event_milliseconds = timecode_to_milliseconds(
    SAMPLE_EVENT_TIMECODE_SOURCE
)
target_event_milliseconds = timecode_to_milliseconds(
    SAMPLE_EVENT_TIMECODE_TARGET
)
speed_delta = (
    target_event_milliseconds - source_event_milliseconds
) / source_event_milliseconds


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


if __name__ == "__main__":

    with open(INPUT_FILENAME, "r") as input_file, open(
        OUPUT_FILENAME, "w"
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

            if line.startswith(EVENT_PREFIX):
                if is_previous_line_events_header:
                    raise Exception(
                        f"Found prefix {EVENT_PREFIX} before corresponding format line."
                        "Seems like subtitles file is corrupted. Cannot continue."
                    )

                if not start_timecode_position or not end_timecode_position:
                    raise Exception(
                        "To process timecodes both start and end timecodes positions"
                        "should be known. Something is wrong with events header or with format line"
                    )

                dialog_event = line[len(EVENT_PREFIX) :]
                dialog_elements: List[str] = dialog_event.split(",")
                start_timecode = dialog_elements[start_timecode_position]
                end_timecode = dialog_elements[end_timecode_position]

                start_milliseconds = timecode_to_milliseconds(start_timecode)
                end_milliseconds = timecode_to_milliseconds(end_timecode)
                start_milliseconds_corrected = int(
                    start_milliseconds * (1 + speed_delta)
                )
                end_milliseconds_corrected = int(
                    end_milliseconds * (1 + speed_delta)
                )

                start_timecode_corrected = milliseconds_to_timecode(
                    start_milliseconds_corrected
                )
                end_timecode_corrected = milliseconds_to_timecode(
                    end_milliseconds_corrected
                )

                dialog_elements[1] = start_timecode_corrected
                dialog_elements[2] = end_timecode_corrected

                dialog_event_corrected = (
                    f"{EVENT_PREFIX}{','.join(dialog_elements)}"
                )

                output_file.write(dialog_event_corrected)

                continue

            output_file.write(line)
