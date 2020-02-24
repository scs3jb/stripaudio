#!/usr/bin/env python
import os
import re
import sys
import ast
import StringIO
import subprocess
import argparse

parser = argparse.ArgumentParser(description="Process some files")
parser.add_argument('directory_of_mkv', metavar='DIR', type=str)
parser.add_argument('--extract', type=bool, default=False)
parser.add_argument('--dry-run', type=bool, default=False)
parser.add_argument('--debug', type=bool, default=False)
parser.add_argument('--audio-languages', help="Audio Languages to keep", type=str,  default='eng,zha,jpn,zho,kor,tha,chi,und')
parser.add_argument('--subtitle-languages', help="Subtitle Languages to keep", type=str, default='eng,und')

args = parser.parse_args()
in_dir = args.directory_of_mkv
extract = args.extract
dry_run = args.dry_run
debug = args.debug
AUDIO_LANGUAGE = args.audio_languages.split(",")
SUBTITLE_LANGUAGE = args.subtitle_languages.split(",")

# set this to the path for mkvmerge
MKVMERGE = "/usr/bin/mkvmerge"

AUDIO_RE    = re.compile(r"Track ID (\d+): audio \([A-Z0-9_/]+\) [number:\d+ uid:\d+ codec_id:[A-Z0-9_/]+ codec_private_length:\d+ language:([a-z]{3})")
SUBTITLE_RE = re.compile(r"Track ID (\d+): subtitles \([A-Z0-9_/]+\) [number:\d+ uid:\d+ codec_id:[A-Z0-9_/]+ codec_private_length:\d+ language:([a-z]{3})(?: track_name:[a-zA-Z0-9_\\]*)? default_track:[01]{1} forced_track:([01]{1})")

print "About to process folder: %s, keeping audio: %s and subs: %s" % (in_dir, AUDIO_LANGUAGE, SUBTITLE_LANGUAGE)
print "Flags: DRY_RUN: %s EXTRACT: %s" % (dry_run, extract)
process=raw_input("Type Y to continue! ")
if process not in ('y', 'Y', 'yes', 'Yes'):
    sys.exit()

for root, dirs, files in os.walk(in_dir):
    for f in files:

        # filter out non mkv files
        if not f.endswith(".mkv"):
            continue

        # path to file
        path = os.path.join(root, f)

        print >> sys.stdout, "Starting analysis on", path, "...\n",

        # build command line
        cmd = [MKVMERGE, "--identify-verbose", path]

        # get mkv info
        mkvmerge = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = mkvmerge.communicate()
        if mkvmerge.returncode != 0:
            print >> sys.stderr, "mkvmerge failed to identify", path
            continue

        # find audio and subtitle tracks
        audio = []
        subtitle = []
        for line in StringIO.StringIO(stdout):
            m = AUDIO_RE.match(line)
            if m:
                audio.append(m.groups())
            s = SUBTITLE_RE.match(line)
            if s:
                subtitle.append(s.groups())

        # filter out files that don't need processing
        if len(audio) < 2 and len(subtitle) < 2:
            print >> sys.stderr, "nothing to do for", path
            continue

        # Let's state before
	print >> sys.stdout, "... before filtering audio: %s, subs: %s" % (len(audio),len(subtitle))
	print >> sys.stdout, "... audio: %s" % ", ".join([a[1] for a in audio])
	print >> sys.stdout, "... subs: %s" % ", ".join([s[1] for s in subtitle])

        # filter out tracks that don't match the language	
        audio_lang = filter(lambda a: a[1] in AUDIO_LANGUAGE, audio)
        subtitle_lang = filter(lambda a: a[1] in SUBTITLE_LANGUAGE, subtitle)

        # and after, as you can nuke your files here, ctrl+c if you are scared :)
	print >> sys.stdout, "... after filtering audio: %s, subs: %s" % (len(audio_lang),len(subtitle_lang))
	print >> sys.stdout, "... audio: %s" % ", ".join([a[1] for a in audio_lang])
	print >> sys.stdout, "... subs: %s" % ", ".join([s[1] for s in subtitle_lang])

        # filter out files that don't need processing
        if len(audio_lang) < 1:
            print >> sys.stderr, "this would result in no audio streams for", path
            print >> sys.stderr, "There's something up with this file!"
            continue

        # build command line
        cmd = [MKVMERGE, "-o", path + ".temp"]
        if len(audio_lang):
            cmd += ["--audio-tracks", ",".join([str(a[0]) for a in audio_lang])]
            for i in range(len(audio_lang)):
                cmd += ["--default-track", ":".join([audio_lang[i][0], "0" if i else "1"])]
        if len(subtitle_lang):
            cmd += ["--subtitle-tracks", ",".join([str(s[0]) for s in subtitle_lang])]
            for i in range(len(subtitle_lang)):
                cmd += ["--default-track", ":".join([subtitle_lang[i][0], "0"])]
        elif len(subtitle_lang) == 0:
            cmd += ["--no-subtitles"]
        cmd += [path]

        # process file
        print >> sys.stdout, "Processing", path, "...\n",
        if not debug:
            mkvmerge = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = mkvmerge.communicate()
            if mkvmerge.returncode != 0:
                print >> sys.stderr, "Failed\n"
                continue
        else:
            print >> sys.stdout, "would have run %s" % cmd
            print >> sys.stdout, "... Skipping!"
        
        print >> sys.stdout, "Succeeded"

        # overwrite file
        if not debug:
            os.remove(path)
            os.rename(path + ".temp", path)
