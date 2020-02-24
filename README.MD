h1. Strip Audio

This makes mkvtools available for stripping audio and subtitles from mkvs.

h3. To Build

    VERSION=0.1
    docker build -t scs3jb/stripaudio:latest -t scs3jb/stripadio:$VERSION .
    docker login
    docker push -t scs3jb/stripaudio:$VERSION
    docker push -t scs3jb/stripaudio:latest

h3. To Run

To run, I recommend putting an alias in /etc/profile.d/aliases.sh:

    alias stripdubs='docker run -v `pwd`:/cache -t -i --name stripdubs scs3jb/stripaudio:0.1 python /opt/original.py /cache && docker rm stripdubs'
    alias stripaudio='docker run -v `pwd`:/cache -t -i --name stripaudio scs3jb/stripaudio:0.1 python /opt/original.py --audio-languages=eng,und /cache && docker rm stripaudio'

Example run would look like this:

    $ docker run -v `pwd`:/cache -t -i --name stripdubs scs3jb/stripaudio:0.1 python /opt/original.py /cache && docker rm stripdubs
    About to process folder: /cache, keeping audio: ['eng', 'zha', 'jpn', 'zho', 'kor', 'tha', 'chi', 'und' ] and subs: ['eng', 'und']
    Flags: DRY_RUN: False EXTRACT: False
    Type Y to continue! Y
    Starting analysis on /cache/vhv-tbm-720p.mkv ...
    ... before filtering audio: 2, subs: 0
    ... audio: ger, eng
    ... subs:
    ... after filtering audio: 1, subs: 0
    ... audio: eng
    ... subs:
    Processing /cache/vhv-tbm-720p.mkv ...
    Succeeded
    mkvtools

The original file is replaced with the stripped one, in this case German was not on the list of keeps, so it gets removed.

Use 'und' for undefined.

h3. TODO
Where we fall over is a foreign language film with a dubbed track.  We want to keep just the native language, you'd think this was the first track, unfortunately the dubber usually put the dubbed track first.  I'm looking at you Germany, Spain, Italy and France!
Check IMDB for original languages, and strip everything else!  This will make this script safe to run.

h3. Help

Fix or Toss a Coin to your Witcher.
