from process_subtitles import (
    get_video_playback_speed_delta,
    process_subtitles_file,
)

TEST_INPUT_FILE = "tests/test_input.ass"
TEST_OUTPUT_TARGET_FILE = "tests/test_target_output.ass"
EVENT_PREFIX = "Dialogue: "
SAMPLE_EVENT_TIMECODE_SOURCE = "1:03:24.92"
SAMPLE_EVENT_TIMECODE_TARGET = "1:02:48.92"


def test_process_subtitles_file(tmpdir):
    speed_delta = get_video_playback_speed_delta(
        SAMPLE_EVENT_TIMECODE_SOURCE, SAMPLE_EVENT_TIMECODE_TARGET
    )
    output_file = tmpdir.join("test_output.ass")
    process_subtitles_file(
        path_to_input_file=TEST_INPUT_FILE,
        path_to_output_file=output_file,
        event_prefix=EVENT_PREFIX,
        speed_delta=speed_delta,
    )

    with open(TEST_OUTPUT_TARGET_FILE, "r") as output_target:
        assert output_file.read() == output_target.read()
