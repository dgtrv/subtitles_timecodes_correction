"""
Simple module for adapting subtitles timecodes to different video speed.

Works with .ass files. All the strings with prefix EVENT_PREFIX will be 
processed: start and end timecode will be shifted according to supplied 
sample timecode from initial file and corresponding target timecode for 
file with different video playback speed.
"""

from typing import List

INPUT_FILENAME = ""
OUPUT_FILENAME = ""

SAMPLE_EVENT_TIMECODE_SOURCE = ""
SAMPLE_EVENT_TIMECODE_TARGET = ""

EVENT_PREFIX = "Dialogue: "


def shift(dialogue_events: List[str]) -> None:
    pass


def timecode_to_milliseconds(timecode: str) -> int:
    hours, minutes, seconds_with_santiseconds = timecode.split(":")
    seconds, santiseconds = seconds_with_santiseconds.split(".")
    milliseconds = (
        int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    ) * 1000 + int(santiseconds) * 10
    return milliseconds


def milliseconds_to_timecode(milliseconds: int) -> str:
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


if __name__ == "__main__":

    with open(INPUT_FILENAME, "r") as input_file, open(
        OUPUT_FILENAME, "w"
    ) as output_file:
        for line in input_file.readlines():
            if line.startswith(EVENT_PREFIX):
                dialog_event = line[len(EVENT_PREFIX) :]
                dialog_elements: List[str] = dialog_event.split(
                    ",", maxsplit=3
                )
                _, start_timecode, end_timecode, _ = dialog_elements

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
