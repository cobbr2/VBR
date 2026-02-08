#!/usr/bin/python3
# -*- coding: utf-8 -*-

from os import environ
import os.path
import sys
from os import walk
import time
import subprocess

def check_mirror_status(flac_file, mirror_format):
    # Ignore macOS metadata files
    if os.path.basename(flac_file).startswith('._'):
        return 'IGNORED'

    # .flac is 5 characters
    rel_name = os.path.relpath(flac_file, flac_dir)[:-5]

    mirror_file_name = os.path.join(mirror_format['DIR'], "{}.{}".format(rel_name, mirror_format['EXT'].lower()))
    
    if not os.path.isfile(mirror_file_name):
        print(f'Mirroring: {rel_name}.flac -> {mirror_format["EXT"]}')

        mirror_dir_name = os.path.dirname(mirror_file_name)
        if not os.path.isdir(mirror_dir_name):
            os.makedirs(mirror_dir_name)
            flac_file_dir = os.path.dirname(os.path.abspath(flac_file))
            os.chown(mirror_dir_name, os.stat(flac_file_dir).st_uid, os.stat(flac_file_dir).st_gid)
            os.chmod(mirror_dir_name, os.stat(flac_file_dir).st_mode & 0o777)

        # Added -hide_banner and -loglevel error
        mirror_command = ['/usr/bin/ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', flac_file]
        mirror_command = mirror_command + mirror_format['OPTIONS']
        mirror_command.append(mirror_file_name)
        
        result = subprocess.run(mirror_command, capture_output=True)

        if result.returncode == 0:
            if os.path.isfile(mirror_file_name):
                os.chown(mirror_file_name, os.stat(flac_file).st_uid, os.stat(flac_file).st_gid)
                os.chmod(mirror_file_name, os.stat(flac_file).st_mode & 0o777)
            return 'MIRRORED'
        else:
            print(f"Error creating {mirror_file_name}", file=sys.stderr)
            if result.stderr:
                print(result.stderr.decode(), file=sys.stderr)
            return 'ERROR'

    return 'EXISTS'

def scan_flac_dir():
    counts = {'FLAC': 0}
    start_time = time.time()
    for (dirpath, dirnames, filenames) in walk(flac_dir):
        # Skip hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for f in filenames:
            if f.endswith('.flac') and not f.startswith('._'):
                counts['FLAC'] += 1
                flac_file = os.path.join(dirpath, f)

                for mirror_format in mirror_formats:
                    rc = check_mirror_status(flac_file, format_options[mirror_format])
                    cc = f"{mirror_format}_{rc}"
                    counts[cc] = counts.get(cc, 0) + 1

    # Clean Heartbeat Output
    tasks = [f"{m}: {counts.get(m+'_MIRRORED',0)} new, {counts.get(m+'_ERROR',0)} err" for m in mirror_formats]
    print(f"Heartbeat: Scanned {counts['FLAC']} files in {time.time() - start_time:.2f}s. Tasks: {', '.join(tasks)}", flush=True)

if __name__ == "__main__":
    mirror_formats = [m for m in environ.get('MIRROR', '').strip().split(',') if m]
    if not mirror_formats:
        print("No formats to mirror specified", flush=True)
        sys.exit(1)

    flac_dir = environ.get('FLAC_DIR', '/flac')
    
    format_options = {
        'M4A': {'OPTIONS':'-c:a aac -b:a 192k -vn', 'DIR': '/m4a', 'EXT': 'm4a'},
        'MP3': {'OPTIONS':'-c:a mp3 -ab 192k -map_metadata 0', 'DIR':'/mp3', 'EXT':'mp3'},
        'OGG': {'OPTIONS':'-c:a libvorbis', 'DIR': '/ogg', 'EXT':'ogg'}
    }

    for fmat in mirror_formats:
        if fmat in format_options:
            ev_dir = f"{fmat}_DIR"
            if ev_dir in environ:
                format_options[fmat]['DIR'] = environ[ev_dir]
            
            ev_opt = f"{fmat}_OPTIONS"
            if ev_opt in environ:
                format_options[fmat]['OPTIONS'] = environ[ev_opt]
            
            format_options[fmat]['OPTIONS'] = format_options[fmat]['OPTIONS'].split()

    print(f"flac-mirror started for formats: {', '.join(mirror_formats)}", flush=True)

    while True:
        scan_flac_dir()
        time.sleep(60)
