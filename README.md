# Subtitles timecodes correction
Adapting subtitles timecodes to new video speed

## Launch:
### in console:
```python process_subtitles.py -i=path_to_inputfile -o=path_to_output_file -s=source_sample_timecode -t=target_sample_timecode```
### arguments:
- -i, --input - path to input file
- -o, --output - path to output file
- -s, --tc_source - sample line timecode for initial videofile
- -t, --tc_target - sample line timecode for new file


## Timecode format:
- h:mm:ss.centiseconds
- 1 centisecond is equal to 0.01 second.